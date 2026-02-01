//! Grapheme pool for storing grapheme cluster bytes with reusable IDs. Aligns OpenTUI grapheme.zig.
//! Simplified: single size class (max 128 bytes per grapheme).

#![allow(dead_code)]

// Encoding flags for char buffer entries (u32). Aligns grapheme.zig.
pub const CHAR_FLAG_GRAPHEME: u32 = 0x8000_0000;
pub const CHAR_FLAG_CONTINUATION: u32 = 0xC000_0000;
pub const CHAR_EXT_RIGHT_SHIFT: u32 = 28;
pub const CHAR_EXT_LEFT_SHIFT: u32 = 26;
pub const CHAR_EXT_MASK: u32 = 0x3;
pub const GRAPHEME_ID_MASK: u32 = 0x03FF_FFFF;
const CLASS_BITS: u32 = 3;
const GENERATION_BITS: u32 = 7;
const SLOT_BITS: u32 = 16;
const CLASS_MASK: u32 = (1 << CLASS_BITS) - 1;
const GENERATION_MASK: u32 = (1 << GENERATION_BITS) - 1;
const SLOT_MASK: u32 = (1 << SLOT_BITS) - 1;

const MAX_GRAPHEME_BYTES: usize = 128;
const SLOTS_PER_PAGE: u32 = 64;

#[repr(C)]
struct SlotHeader {
    len: u16,
    refcount: u32,
    generation: u32,
    is_owned: u32,
}

const SLOT_HEADER_SIZE: usize = std::mem::size_of::<SlotHeader>();
const SLOT_SIZE: usize = SLOT_HEADER_SIZE + MAX_GRAPHEME_BYTES;

/// Grapheme pool ID (opaque u32). Aligns OpenTUI GraphemePool.IdPayload.
pub type IdPayload = u32;

/// Simplified grapheme pool (single size class). Aligns OpenTUI grapheme.zig GraphemePool.
pub struct GraphemePool {
    slots: Vec<u8>,
    free_list: Vec<u32>,
    num_slots: u32,
}

impl GraphemePool {
    pub fn new() -> Self {
        GraphemePool {
            slots: Vec::new(),
            free_list: Vec::new(),
            num_slots: 0,
        }
    }

    fn slot_ptr_mut(&mut self, slot_index: u32) -> *mut u8 {
        let offset = (slot_index as usize) * SLOT_SIZE;
        self.slots.as_mut_ptr().wrapping_add(offset)
    }

    fn slot_ptr(&self, slot_index: u32) -> *const u8 {
        let offset = (slot_index as usize) * SLOT_SIZE;
        self.slots.as_ptr().wrapping_add(offset)
    }

    fn grow(&mut self) {
        let add_bytes = SLOT_SIZE * (SLOTS_PER_PAGE as usize);
        self.slots.resize(self.slots.len() + add_bytes, 0);
        for i in 0..SLOTS_PER_PAGE {
            self.free_list.push(self.num_slots + i);
        }
        self.num_slots += SLOTS_PER_PAGE;
    }

    fn pack_id(_class_id: u32, slot_index: u32, generation: u32) -> IdPayload {
        ((generation & GENERATION_MASK) << SLOT_BITS) | (slot_index & SLOT_MASK)
    }

    fn unpack_id(id: IdPayload) -> (u32, u32) {
        let slot_index = id & SLOT_MASK;
        let generation = (id >> SLOT_BITS) & GENERATION_MASK;
        (slot_index, generation)
    }

    /// Allocate a slot and copy bytes. Returns grapheme ID.
    pub fn alloc(&mut self, bytes: &[u8]) -> Result<IdPayload, &'static str> {
        if bytes.len() > MAX_GRAPHEME_BYTES {
            return Err("grapheme too long");
        }
        if self.free_list.is_empty() {
            self.grow();
        }
        let slot_index = self.free_list.pop().unwrap();
        let p = self.slot_ptr_mut(slot_index);
        let header_ptr = p as *mut SlotHeader;
        let header = unsafe { &mut *header_ptr };
        let new_generation = (header.generation + 1) & GENERATION_MASK;
        header.len = bytes.len() as u16;
        header.refcount = 0;
        header.generation = new_generation;
        header.is_owned = 1;
        let data_ptr = unsafe { p.add(SLOT_HEADER_SIZE) };
        unsafe {
            std::ptr::copy_nonoverlapping(bytes.as_ptr(), data_ptr, bytes.len());
        }
        Ok(Self::pack_id(0, slot_index, new_generation))
    }

    pub fn incref(&mut self, id: IdPayload) -> Result<(), &'static str> {
        let (slot_index, generation) = Self::unpack_id(id);
        if slot_index >= self.num_slots {
            return Err("invalid id");
        }
        let p = self.slot_ptr_mut(slot_index);
        let header = unsafe { &mut *(p as *mut SlotHeader) };
        if header.generation != generation {
            return Err("wrong generation");
        }
        header.refcount = header.refcount.wrapping_add(1);
        Ok(())
    }

    pub fn decref(&mut self, id: IdPayload) -> Result<(), &'static str> {
        let (slot_index, generation) = Self::unpack_id(id);
        if slot_index >= self.num_slots {
            return Err("invalid id");
        }
        let p = self.slot_ptr_mut(slot_index);
        let header = unsafe { &mut *(p as *mut SlotHeader) };
        if header.refcount == 0 {
            return Err("invalid id (zero refcount)");
        }
        if header.generation != generation {
            return Err("wrong generation");
        }
        header.refcount = header.refcount.wrapping_sub(1);
        if header.refcount == 0 {
            self.free_list.push(slot_index);
        }
        Ok(())
    }

    pub fn get(&self, id: IdPayload) -> Result<String, &'static str> {
        let (slot_index, generation) = Self::unpack_id(id);
        if slot_index >= self.num_slots {
            return Err("invalid id");
        }
        let p = self.slot_ptr(slot_index);
        let header = unsafe { &*(p as *const SlotHeader) };
        if header.generation != generation {
            return Err("wrong generation");
        }
        let data_ptr = unsafe { p.add(SLOT_HEADER_SIZE) };
        let len = header.len as usize;
        let bytes = unsafe { std::slice::from_raw_parts(data_ptr, len) };
        String::from_utf8(bytes.to_vec()).map_err(|_| "invalid utf8")
    }

    pub fn get_refcount(&self, id: IdPayload) -> Result<u32, &'static str> {
        let (slot_index, generation) = Self::unpack_id(id);
        if slot_index >= self.num_slots {
            return Err("invalid id");
        }
        let p = self.slot_ptr(slot_index);
        let header = unsafe { &*(p as *const SlotHeader) };
        if header.generation != generation {
            return Err("wrong generation");
        }
        Ok(header.refcount)
    }
}

impl Default for GraphemePool {
    fn default() -> Self {
        Self::new()
    }
}

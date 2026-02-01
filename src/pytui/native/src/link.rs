//! Link pool for URL strings with reusable IDs. Aligns OpenTUI link.zig.

use pyo3::prelude::*;

const GEN_BITS: u32 = 8;
const SLOT_BITS: u32 = 16;
const GEN_MASK: u32 = (1 << GEN_BITS) - 1;
const SLOT_MASK: u32 = (1 << SLOT_BITS) - 1;
pub const MAX_URL_LENGTH: usize = 512;

#[repr(C)]
struct SlotHeader {
    len: u32,
    refcount: u32,
    generation: u32,
}

/// Link pool for storing URL strings with reusable IDs. Aligns OpenTUI link.zig LinkPool.
#[pyclass]
pub struct LinkPool {
    slot_capacity: u32,
    slots_per_page: u32,
    slot_size_bytes: usize,
    slots: Vec<u8>,
    free_list: Vec<u32>,
    num_slots: u32,
}

impl LinkPool {
    fn slot_ptr(&mut self, slot_index: u32) -> *mut u8 {
        let offset = (slot_index as usize) * self.slot_size_bytes;
        self.slots.as_mut_ptr().wrapping_add(offset)
    }

    fn slot_ptr_const(&self, slot_index: u32) -> *const u8 {
        let offset = (slot_index as usize) * self.slot_size_bytes;
        self.slots.as_ptr().wrapping_add(offset)
    }

    fn pack_id(slot_index: u32, generation: u32) -> PyResult<u32> {
        if slot_index > SLOT_MASK {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: out of memory"));
        }
        Ok(((generation & GEN_MASK) << SLOT_BITS) | (slot_index & SLOT_MASK))
    }

    fn unpack_id(id: u32) -> (u32, u32) {
        let slot_index = id & SLOT_MASK;
        let generation = (id >> SLOT_BITS) & GEN_MASK;
        (slot_index, generation)
    }

    fn grow(&mut self) -> PyResult<()> {
        let add_bytes = self.slot_size_bytes * (self.slots_per_page as usize);
        self.slots.resize(self.slots.len() + add_bytes, 0);
        for i in 0..self.slots_per_page {
            self.free_list.push(self.num_slots + i);
        }
        self.num_slots += self.slots_per_page;
        Ok(())
    }
}

#[pymethods]
impl LinkPool {
    #[new]
    pub(crate) fn new() -> Self {
        let slot_capacity = MAX_URL_LENGTH as u32;
        let slots_per_page = 64;
        let slot_size_bytes = std::mem::size_of::<SlotHeader>() + (slot_capacity as usize);
        LinkPool {
            slot_capacity,
            slots_per_page,
            slot_size_bytes,
            slots: Vec::new(),
            free_list: Vec::new(),
            num_slots: 0,
        }
    }

    pub(crate) fn alloc(&mut self, url: &str) -> PyResult<u32> {
        let url_bytes = url.as_bytes();
        if url_bytes.len() > self.slot_capacity as usize {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: URL too long"));
        }
        if self.free_list.is_empty() {
            self.grow()?;
        }
        let slot_index = self.free_list.pop().unwrap();
        let p = self.slot_ptr(slot_index);
        let header_ptr = p as *mut SlotHeader;
        let new_generation = unsafe { ((*header_ptr).generation + 1) & GEN_MASK };
        unsafe {
            *header_ptr = SlotHeader {
                len: url_bytes.len() as u32,
                refcount: 0,
                generation: new_generation,
            };
            let data_ptr = p.add(std::mem::size_of::<SlotHeader>());
            std::ptr::copy_nonoverlapping(url_bytes.as_ptr(), data_ptr, url_bytes.len());
        }
        Self::pack_id(slot_index, new_generation)
    }

    pub(crate) fn incref(&mut self, id: u32) -> PyResult<()> {
        let (slot_index, generation) = Self::unpack_id(id);
        if slot_index >= self.num_slots {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: invalid id"));
        }
        let p = self.slot_ptr(slot_index);
        let header_ptr = p as *mut SlotHeader;
        let header = unsafe { &mut *header_ptr };
        if header.generation != generation {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: wrong generation"));
        }
        header.refcount = header.refcount.wrapping_add(1);
        Ok(())
    }

    pub(crate) fn decref(&mut self, id: u32) -> PyResult<()> {
        let (slot_index, generation) = Self::unpack_id(id);
        if slot_index >= self.num_slots {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: invalid id"));
        }
        let p = self.slot_ptr(slot_index);
        let header_ptr = p as *mut SlotHeader;
        let header = unsafe { &mut *header_ptr };
        if header.refcount == 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "LinkPool: invalid id (zero refcount)",
            ));
        }
        if header.generation != generation {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: wrong generation"));
        }
        header.refcount = header.refcount.wrapping_sub(1);
        if header.refcount == 0 {
            self.free_list.push(slot_index);
        }
        Ok(())
    }

    pub(crate) fn get(&self, id: u32) -> PyResult<String> {
        let (slot_index, generation) = Self::unpack_id(id);
        if slot_index >= self.num_slots {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: invalid id"));
        }
        let p = self.slot_ptr_const(slot_index);
        let header_ptr = p as *const SlotHeader;
        let header = unsafe { &*header_ptr };
        if header.generation != generation {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: wrong generation"));
        }
        let data_ptr = unsafe { p.add(std::mem::size_of::<SlotHeader>()) };
        let len = header.len as usize;
        let bytes = unsafe { std::slice::from_raw_parts(data_ptr, len) };
        String::from_utf8(bytes.to_vec()).map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    pub(crate) fn get_refcount(&self, id: u32) -> PyResult<u32> {
        let (slot_index, generation) = Self::unpack_id(id);
        if slot_index >= self.num_slots {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: invalid id"));
        }
        let p = self.slot_ptr_const(slot_index);
        let header_ptr = p as *const SlotHeader;
        let header = unsafe { &*header_ptr };
        if header.generation != generation {
            return Err(pyo3::exceptions::PyValueError::new_err("LinkPool: wrong generation"));
        }
        Ok(header.refcount)
    }
}

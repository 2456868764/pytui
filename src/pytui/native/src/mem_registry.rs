//! Memory buffer registry. Aligns OpenTUI mem-registry.zig.

#![allow(dead_code)]

/// Memory buffer slot. Aligns OpenTUI MemBuffer.
struct MemBuffer {
    data: Vec<u8>,
    active: bool,
}

/// Registry for multiple memory buffers (max 255 slots). Aligns OpenTUI MemRegistry.
pub struct MemRegistry {
    buffers: Vec<MemBuffer>,
    free_slots: Vec<u8>,
}

impl MemRegistry {
    pub fn new() -> Self {
        MemRegistry {
            buffers: Vec::new(),
            free_slots: Vec::new(),
        }
    }

    /// Register a buffer. owned: if true, caller transfers ownership (we copy in Rust). Returns slot id.
    pub fn register(&mut self, data: &[u8], _owned: bool) -> Result<u8, &'static str> {
        if let Some(&id) = self.free_slots.last() {
            self.free_slots.pop();
            let idx = id as usize;
            self.buffers[idx] = MemBuffer {
                data: data.to_vec(),
                active: true,
            };
            return Ok(id);
        }
        if self.buffers.len() >= 255 {
            return Err("MemRegistry: out of memory");
        }
        let id = self.buffers.len() as u8;
        self.buffers.push(MemBuffer {
            data: data.to_vec(),
            active: true,
        });
        Ok(id)
    }

    /// Get buffer by id. Returns None if invalid or inactive.
    pub fn get(&self, id: u8) -> Option<&[u8]> {
        let idx = id as usize;
        if idx >= self.buffers.len() {
            return None;
        }
        let buf = &self.buffers[idx];
        if !buf.active {
            return None;
        }
        Some(&buf.data)
    }

    /// Replace buffer at id.
    pub fn replace(&mut self, id: u8, data: &[u8], _owned: bool) -> Result<(), &'static str> {
        let idx = id as usize;
        if idx >= self.buffers.len() {
            return Err("MemRegistry: invalid id");
        }
        let buf = &mut self.buffers[idx];
        if !buf.active {
            return Err("MemRegistry: invalid id");
        }
        buf.data = data.to_vec();
        Ok(())
    }

    /// Unregister slot and add to free list.
    pub fn unregister(&mut self, id: u8) -> Result<(), &'static str> {
        let idx = id as usize;
        if idx >= self.buffers.len() {
            return Err("MemRegistry: invalid id");
        }
        let buf = &mut self.buffers[idx];
        if !buf.active {
            return Err("MemRegistry: invalid id");
        }
        buf.active = false;
        buf.data.clear();
        self.free_slots.push(id);
        Ok(())
    }

    pub fn clear(&mut self) {
        for b in &mut self.buffers {
            b.active = false;
            b.data.clear();
        }
        self.free_slots.clear();
        for i in 0..self.buffers.len() {
            self.free_slots.push(i as u8);
        }
    }

    pub fn get_used_slots(&self) -> usize {
        self.buffers.iter().filter(|b| b.active).count()
    }

    /// Free slots = 255 - len(buffers) + len(free_slots). Zig: 255 - buffers.len + free_slots.len.
    pub fn get_free_slots(&self) -> usize {
        255usize.saturating_sub(self.buffers.len()).saturating_add(self.free_slots.len())
    }
}

impl Default for MemRegistry {
    fn default() -> Self {
        Self::new()
    }
}

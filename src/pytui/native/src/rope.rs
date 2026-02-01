//! Rope adapter over ropey. Aligns OpenTUI rope.zig (character-based API).
//! Zig Rope is generic over item type; we expose a char/string rope via ropey.

#![allow(dead_code)]

use ropey::Rope as RopeyRope;

/// Rope adapter wrapping ropey. Aligns OpenTUI rope.zig Rope (char-based).
pub struct Rope {
    inner: RopeyRope,
}

impl Rope {
    /// Create empty rope. Aligns Zig Rope.init.
    pub fn new() -> Self {
        Rope {
            inner: RopeyRope::new(),
        }
    }

    /// Create rope from string. Aligns Zig from_slice / from_item for text.
    pub fn from_str(s: &str) -> Self {
        Rope {
            inner: RopeyRope::from_str(s),
        }
    }

    /// Number of characters (excluding sentinel). Aligns Zig count().
    pub fn count(&self) -> usize {
        self.inner.len_chars()
    }

    /// Insert string at character index. Aligns Zig insert / insert_slice.
    pub fn insert(&mut self, char_index: usize, s: &str) {
        if char_index > self.inner.len_chars() {
            return;
        }
        let _ = self.inner.try_insert(char_index, s);
    }

    /// Delete range [start, end) in character indices. Aligns Zig delete_range.
    pub fn delete_range(&mut self, start: usize, end: usize) {
        if start >= end || end > self.inner.len_chars() {
            return;
        }
        self.inner.remove(start..end);
    }

    /// Get slice as string. Aligns Zig slice(start, end).
    pub fn slice(&self, start: usize, end: usize) -> String {
        let len = self.inner.len_chars();
        let start = start.min(len);
        let end = end.min(len);
        if start >= end {
            return String::new();
        }
        self.inner.slice(start..end).to_string()
    }

    /// Get character at index (as string). Aligns Zig get(index).
    pub fn get(&self, char_index: usize) -> Option<String> {
        if char_index >= self.inner.len_chars() {
            return None;
        }
        Some(self.inner.char(char_index).to_string())
    }

    /// Full content as string.
    pub fn to_string(&self) -> String {
        self.inner.to_string()
    }
}

impl Default for Rope {
    fn default() -> Self {
        Self::new()
    }
}

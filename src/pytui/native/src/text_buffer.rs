//! Text buffer (rope-based). Aligns OpenTUI text-buffer.zig simplified.

use pyo3::prelude::*;

#[pyclass]
pub struct TextBuffer {
    pub rope: ropey::Rope,
}

#[pymethods]
impl TextBuffer {
    #[new]
    fn new(text: Option<&str>) -> Self {
        let rope = match text {
            Some(t) => ropey::Rope::from_str(t),
            None => ropey::Rope::new(),
        };
        TextBuffer { rope }
    }

    fn insert(&mut self, idx: usize, text: &str) -> PyResult<()> {
        if idx <= self.rope.len_chars() {
            self.rope.insert(idx, text);
            Ok(())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
        }
    }

    fn delete(&mut self, start: usize, end: usize) -> PyResult<()> {
        if start <= end && end <= self.rope.len_chars() {
            self.rope.remove(start..end);
            Ok(())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Invalid range"))
        }
    }

    fn to_string(&self) -> String {
        self.rope.to_string()
    }

    fn len_chars(&self) -> usize {
        self.rope.len_chars()
    }

    fn len_lines(&self) -> usize {
        self.rope.len_lines()
    }

    fn line(&self, line_idx: usize) -> PyResult<String> {
        if line_idx < self.rope.len_lines() {
            Ok(self.rope.line(line_idx).to_string())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err(
                "Line index out of bounds",
            ))
        }
    }
}

//! pytui_native - Rust extension for pytui (Cell, Buffer, TextBuffer)

use pyo3::prelude::*;

#[pyclass]
#[derive(Clone, Debug)]
pub struct Cell {
    #[pyo3(get, set)]
    pub char: String,
    #[pyo3(get, set)]
    pub fg: (u8, u8, u8, u8),
    #[pyo3(get, set)]
    pub bg: (u8, u8, u8, u8),
    #[pyo3(get, set)]
    pub bold: bool,
    #[pyo3(get, set)]
    pub italic: bool,
    #[pyo3(get, set)]
    pub underline: bool,
}

#[pymethods]
impl Cell {
    #[new]
    fn new() -> Self {
        Cell {
            char: " ".to_string(),
            fg: (255, 255, 255, 255),
            bg: (0, 0, 0, 0),
            bold: false,
            italic: false,
            underline: false,
        }
    }
}

#[pyclass]
pub struct Buffer {
    width: usize,
    height: usize,
    cells: Vec<Cell>,
}

#[pymethods]
impl Buffer {
    #[new]
    fn new(width: usize, height: usize) -> Self {
        let cells = vec![Cell::new(); width * height];
        Buffer {
            width,
            height,
            cells,
        }
    }

    fn set_cell(&mut self, x: usize, y: usize, cell: Cell) -> PyResult<()> {
        if x < self.width && y < self.height {
            let idx = y * self.width + x;
            self.cells[idx] = cell;
            Ok(())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
        }
    }

    fn get_cell(&self, x: usize, y: usize) -> PyResult<Cell> {
        if x < self.width && y < self.height {
            let idx = y * self.width + x;
            Ok(self.cells[idx].clone())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
        }
    }

    fn draw_text(&mut self, text: &str, x: usize, y: usize, fg: (u8, u8, u8, u8)) {
        for (i, ch) in text.chars().enumerate() {
            if x + i >= self.width {
                break;
            }
            let idx = y * self.width + (x + i);
            if idx < self.cells.len() {
                self.cells[idx].char = ch.to_string();
                self.cells[idx].fg = fg;
            }
        }
    }

    fn clear(&mut self) {
        for cell in &mut self.cells {
            *cell = Cell::new();
        }
    }

    fn char_width(&self, ch: &str) -> usize {
        use unicode_width::UnicodeWidthChar;
        ch.chars().next().map(|c| c.width().unwrap_or(1)).unwrap_or(0)
    }
}

#[pyclass]
pub struct TextBuffer {
    rope: ropey::Rope,
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

#[pymodule]
fn pytui_native(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<Cell>()?;
    m.add_class::<Buffer>()?;
    m.add_class::<TextBuffer>()?;
    Ok(())
}

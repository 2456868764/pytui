//! Buffer (cell grid) and diff output. Aligns OpenTUI buffer.zig.

use crate::cell::{cell_eq, cell_to_ansi_sgr, Cell};
use pyo3::prelude::*;
use std::fmt::Write;

#[pyclass]
pub struct Buffer {
    width: usize,
    height: usize,
    cells: Vec<Cell>,
}

#[pymethods]
impl Buffer {
    #[new]
    pub(crate) fn new(width: usize, height: usize) -> Self {
        let cells = vec![Cell::new(); width * height];
        Buffer {
            width,
            height,
            cells,
        }
    }

    pub(crate) fn set_cell(&mut self, x: usize, y: usize, cell: Cell) -> PyResult<()> {
        if x < self.width && y < self.height {
            let idx = y * self.width + x;
            self.cells[idx] = cell;
            Ok(())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
        }
    }

    pub(crate) fn get_cell(&self, x: usize, y: usize) -> PyResult<Cell> {
        if x < self.width && y < self.height {
            let idx = y * self.width + x;
            Ok(self.cells[idx].clone())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
        }
    }

    pub(crate) fn draw_text(&mut self, text: &str, x: usize, y: usize, fg: (u8, u8, u8, u8)) {
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

    pub(crate) fn clear(&mut self) {
        for cell in &mut self.cells {
            *cell = Cell::new();
        }
    }

    pub(crate) fn clear_with_bg(&mut self, r: u8, g: u8, b: u8, a: u8) {
        let bg = (r, g, b, a);
        for cell in &mut self.cells {
            cell.char = " ".to_string();
            cell.fg = (255, 255, 255, 255);
            cell.bg = bg;
            cell.bold = false;
            cell.italic = false;
            cell.underline = false;
        }
    }

    pub(crate) fn get_width(&self) -> usize {
        self.width
    }

    pub(crate) fn get_height(&self) -> usize {
        self.height
    }

    fn char_width(&self, ch: &str) -> usize {
        use unicode_width::UnicodeWidthChar;
        ch.chars().next().map(|c| c.width().unwrap_or(1)).unwrap_or(0)
    }

    pub(crate) fn fill_rect(&mut self, x: usize, y: usize, w: usize, h: usize, cell: Cell) -> PyResult<()> {
        let x_end = (x + w).min(self.width);
        let y_end = (y + h).min(self.height);
        for py in y..y_end {
            for px in x..x_end {
                let idx = py * self.width + px;
                self.cells[idx] = cell.clone();
            }
        }
        Ok(())
    }

    pub(crate) fn resize(&mut self, width: usize, height: usize) -> PyResult<()> {
        if width == 0 || height == 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "width and height must be positive",
            ));
        }
        let mut new_cells = vec![Cell::new(); width * height];
        let copy_w = self.width.min(width);
        let copy_h = self.height.min(height);
        for y in 0..copy_h {
            for x in 0..copy_w {
                let old_idx = y * self.width + x;
                let new_idx = y * width + x;
                new_cells[new_idx] = self.cells[old_idx].clone();
            }
        }
        self.width = width;
        self.height = height;
        self.cells = new_cells;
        Ok(())
    }

    /// Diff this buffer against other and return ANSI sequence. Used by renderer.
    /// When full_repaint is true, prepend CURSOR_HOME and CLEAR_SCREEN.
    pub fn diff_and_output_ansi(&self, other: &Buffer, full_repaint: bool) -> PyResult<String> {
        if self.width != other.width || self.height != other.height {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "buffers must have same dimensions",
            ));
        }
        let mut out = String::new();
        if full_repaint {
            out.push_str("\x1b[H");
            out.push_str("\x1b[2J");
        }
        let mut cur_fg: Option<(u8, u8, u8, u8)> = None;
        let mut cur_bg: Option<(u8, u8, u8, u8)> = None;
        let mut cur_bold = false;
        let mut cur_italic = false;
        let mut cur_underline = false;

        for y in 0..self.height {
            for x in 0..self.width {
                let idx = y * self.width + x;
                let back = &self.cells[idx];
                let front = &other.cells[idx];
                let changed = full_repaint || !cell_eq(back, front);
                if !changed {
                    continue;
                }
                let _ = write!(out, "\x1b[{};{}H", y + 1, x + 1);
                let need_fg = cur_fg != Some(back.fg);
                let need_bg = cur_bg != Some(back.bg);
                let need_attr =
                    cur_bold != back.bold || cur_italic != back.italic || cur_underline != back.underline;
                if need_fg || need_bg || need_attr {
                    cell_to_ansi_sgr(back, &mut out);
                    cur_fg = Some(back.fg);
                    cur_bg = Some(back.bg);
                    cur_bold = back.bold;
                    cur_italic = back.italic;
                    cur_underline = back.underline;
                }
                out.push_str(&back.char);
            }
        }
        Ok(out)
    }
}

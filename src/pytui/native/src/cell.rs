//! Cell type and SGR output. Aligns OpenTUI buffer.zig cell representation.

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

/// Compare two cells. Used by buffer diff. Aligns OpenTUI cell equality.
pub fn cell_eq(a: &Cell, b: &Cell) -> bool {
    a.char == b.char
        && a.fg == b.fg
        && a.bg == b.bg
        && a.bold == b.bold
        && a.italic == b.italic
        && a.underline == b.underline
}

/// Append SGR sequence for cell to out. Aligns OpenTUI cell-to-SGR output.
pub fn cell_to_ansi_sgr(cell: &Cell, out: &mut String) {
    let mut parts: Vec<String> = Vec::new();
    if cell.bold {
        parts.push("1".to_string());
    }
    if cell.italic {
        parts.push("3".to_string());
    }
    if cell.underline {
        parts.push("4".to_string());
    }
    let (fr, fg, fb, fa) = cell.fg;
    if fa > 0 {
        parts.push(format!("38;2;{};{};{}", fr, fg, fb));
    }
    let (br, bg, bb, ba) = cell.bg;
    if ba > 0 {
        parts.push(format!("48;2;{};{};{}", br, bg, bb));
    }
    if parts.is_empty() {
        out.push_str("\x1b[0m");
    } else {
        out.push_str("\x1b[");
        out.push_str(&parts.join(";"));
        out.push('m');
    }
}

#[pymethods]
impl Cell {
    #[new]
    pub(crate) fn new() -> Self {
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

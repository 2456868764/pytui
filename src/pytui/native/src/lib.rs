//! pytui_native - Rust extension for pytui (Cell, Buffer, TextBuffer, CliRenderer, LinkPool).
//! Aligns OpenTUI zig core: buffer, cell, renderer, terminal, link, ansi, text_buffer (ropey).

use pyo3::prelude::*;

mod geometry;
mod utils;
mod utf8;
mod grapheme;
mod rope;
mod mem_registry;
mod syntax_style;
mod terminal;
mod ansi;
mod link;
mod cell;
mod buffer;
mod renderer;
mod text_buffer;

#[cfg(test)]
mod tests;

// Re-export Python-facing types and functions for the pymodule.
pub(crate) use ansi::{attributes_with_link, get_link_id_from_attributes};
pub(crate) use buffer::Buffer;
pub(crate) use cell::Cell;
pub(crate) use link::LinkPool;
pub(crate) use renderer::CliRenderer;
pub(crate) use text_buffer::TextBuffer;

#[pymodule]
fn pytui_native(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<Cell>()?;
    m.add_class::<Buffer>()?;
    m.add_class::<CliRenderer>()?;
    m.add_class::<TextBuffer>()?;
    m.add_class::<LinkPool>()?;
    m.add_function(pyo3::wrap_pyfunction!(attributes_with_link, m)?)?;
    m.add_function(pyo3::wrap_pyfunction!(get_link_id_from_attributes, m)?)?;
    Ok(())
}

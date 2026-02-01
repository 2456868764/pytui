//! ANSI constants and TextAttributes (link_id in attributes). Aligns OpenTUI ansi.zig.

#![allow(dead_code)]

use pyo3::prelude::*;

// --- Constants for attribute bit packing (aligns ansi.zig TextAttributes) ---
const ATTRIBUTE_BASE_MASK: u32 = 0xFF;
const LINK_ID_SHIFT: u32 = 8;
const LINK_ID_PAYLOAD_MASK: u32 = (1u32 << 24) - 1;
const LINK_ID_MASK: u32 = LINK_ID_PAYLOAD_MASK << LINK_ID_SHIFT;

/// ANSI escape sequences. Aligns OpenTUI ansi.zig ANSI struct.
pub mod ansi {
    /// Reset all attributes
    pub const RESET: &str = "\x1b[0m";
    /// Clear screen
    pub const CLEAR: &str = "\x1b[2J";
    /// Cursor home
    pub const HOME: &str = "\x1b[H";
    /// Clear and home
    pub const CLEAR_AND_HOME: &str = "\x1b[H\x1b[2J";
    /// Hide cursor
    pub const HIDE_CURSOR: &str = "\x1b[?25l";
    /// Show cursor
    pub const SHOW_CURSOR: &str = "\x1b[?25h";
    /// Default cursor style
    pub const DEFAULT_CURSOR_STYLE: &str = "\x1b[0 q";
    /// Cursor block
    pub const CURSOR_BLOCK: &str = "\x1b[2 q";
    pub const CURSOR_BLOCK_BLINK: &str = "\x1b[1 q";
    pub const CURSOR_LINE: &str = "\x1b[6 q";
    pub const CURSOR_LINE_BLINK: &str = "\x1b[5 q";
    pub const CURSOR_UNDERLINE: &str = "\x1b[4 q";
    pub const CURSOR_UNDERLINE_BLINK: &str = "\x1b[3 q";
    /// Text attributes
    pub const BOLD: &str = "\x1b[1m";
    pub const DIM: &str = "\x1b[2m";
    pub const ITALIC: &str = "\x1b[3m";
    pub const UNDERLINE: &str = "\x1b[4m";
    pub const BLINK: &str = "\x1b[5m";
    pub const INVERSE: &str = "\x1b[7m";
    pub const HIDDEN: &str = "\x1b[8m";
    pub const STRIKETHROUGH: &str = "\x1b[9m";
    /// Terminal capability queries
    pub const XTVERSION: &str = "\x1b[>0q";
    pub const CSI_U_QUERY: &str = "\x1b[?u";
    /// Tmux DCS passthrough
    pub const TMUX_DCS_START: &str = "\x1bPtmux;";
    pub const TMUX_DCS_END: &str = "\x1b\\";
}

/// Text attribute flags (base 8 bits). Aligns OpenTUI ansi.zig TextAttributes.
pub mod text_attributes {
    pub const NONE: u8 = 0;
    pub const BOLD: u8 = 1 << 0;
    pub const DIM: u8 = 1 << 1;
    pub const ITALIC: u8 = 1 << 2;
    pub const UNDERLINE: u8 = 1 << 3;
    pub const BLINK: u8 = 1 << 4;
    pub const INVERSE: u8 = 1 << 5;
    pub const HIDDEN: u8 = 1 << 6;
    pub const STRIKETHROUGH: u8 = 1 << 7;
}

/// Extract base 8 bits from attribute value. Aligns ansi.zig TextAttributes.getBaseAttributes.
#[inline]
pub fn get_base_attributes(attr: u32) -> u8 {
    (attr & ATTRIBUTE_BASE_MASK) as u8
}

/// Check if attribute value has a link. Aligns ansi.zig TextAttributes.hasLink.
#[inline]
pub fn has_link(attr: u32) -> bool {
    get_link_id_from_attributes(attr) != 0
}

/// Pack link_id into base attributes (bits 8–31). Aligns OpenTUI ansi.zig TextAttributes.setLinkId.
#[pyfunction]
pub fn attributes_with_link(base_attributes: u32, link_id: u32) -> u32 {
    let base = base_attributes & ATTRIBUTE_BASE_MASK;
    let link_bits = (link_id & LINK_ID_PAYLOAD_MASK) << LINK_ID_SHIFT;
    base | link_bits
}

/// Extract link_id from attribute value. Aligns OpenTUI ansi.zig TextAttributes.getLinkId.
#[pyfunction]
pub fn get_link_id_from_attributes(attr: u32) -> u32 {
    (attr & LINK_ID_MASK) >> LINK_ID_SHIFT
}

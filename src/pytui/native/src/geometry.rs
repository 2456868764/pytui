//! Geometry types. Aligns OpenTUI buffer.zig ClipRect.

/// Clip rect for hit-grid scissor. Aligns OpenTUI buffer.zig ClipRect.
#[derive(Clone, Copy, Debug)]
pub struct ClipRect {
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
}

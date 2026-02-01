//! Utility types and conversions. Aligns OpenTUI utils.zig.

#![allow(dead_code)]

/// RGBA color type (4 f32 values). Aligns OpenTUI utils.zig RGBA.
pub type Rgba = [f32; 4];

/// Convert a slice of at least 4 f32 values into an RGBA color.
/// Aligns OpenTUI utils.zig f32PtrToRGBA.
#[inline]
pub fn f32_slice_to_rgba(slice: &[f32]) -> Rgba {
    [
        slice[0],
        slice[1],
        slice[2],
        slice.get(3).copied().unwrap_or(1.0),
    ]
}

/// Convert four f32 components to RGBA.
#[inline]
pub fn rgba(r: f32, g: f32, b: f32, a: f32) -> Rgba {
    [r, g, b, a]
}

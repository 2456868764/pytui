//! UTF-8 text width, line breaks, and grapheme helpers. Aligns OpenTUI utf8.zig.
//! Uses unicode_width for character width (wcwidth-style).

#![allow(dead_code)]

use unicode_width::UnicodeWidthChar;

/// Method for calculating grapheme width. Aligns OpenTUI utf8.zig WidthMethod.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum WidthMethod {
    Wcwidth,
    Unicode,
    NoZwj,
}

/// Check if a byte slice contains only printable ASCII (32..126).
/// Aligns OpenTUI utf8.zig isAsciiOnly. Empty string returns false.
pub fn is_ascii_only(text: &[u8]) -> bool {
    if text.is_empty() {
        return false;
    }
    for &b in text {
        if b < 32 || b > 126 {
            return false;
        }
    }
    true
}

/// Line break kind. Aligns OpenTUI utf8.zig LineBreakKind.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LineBreakKind {
    Lf,
    Cr,
    Crlf,
}

/// Line break at byte position. Aligns OpenTUI utf8.zig LineBreak.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct LineBreak {
    pub pos: usize,
    pub kind: LineBreakKind,
}

/// Find line breaks in text. Aligns OpenTUI utf8.zig findLineBreaks.
pub fn find_line_breaks(text: &[u8]) -> Vec<LineBreak> {
    let mut result = Vec::new();
    let mut pos = 0;
    let mut prev_was_cr = false;
    while pos < text.len() {
        let b = text[pos];
        if b == b'\n' {
            if pos > 0 && text[pos - 1] == b'\r' {
                if prev_was_cr {
                    prev_was_cr = false;
                    pos += 1;
                    continue;
                }
            }
            let kind = if pos > 0 && text[pos - 1] == b'\r' {
                LineBreakKind::Crlf
            } else {
                LineBreakKind::Lf
            };
            result.push(LineBreak { pos, kind });
        } else if b == b'\r' {
            if pos + 1 < text.len() && text[pos + 1] == b'\n' {
                result.push(LineBreak {
                    pos: pos + 1,
                    kind: LineBreakKind::Crlf,
                });
                pos += 1;
            } else {
                result.push(LineBreak {
                    pos,
                    kind: LineBreakKind::Cr,
                });
            }
        }
        prev_was_cr = b == b'\r';
        pos += 1;
    }
    result
}

/// Decode one UTF-8 codepoint at pos. Returns (codepoint, byte_len). Assumes valid UTF-8.
#[inline]
pub fn decode_utf8_unchecked(text: &[u8], pos: usize) -> (u32, u8) {
    if pos >= text.len() {
        return (0xFFFD, 1);
    }
    let b0 = text[pos];
    if b0 < 0x80 {
        return (b0 as u32, 1);
    }
    if b0 < 0xE0 {
        if pos + 1 >= text.len() {
            return (0xFFFD, 1);
        }
        let cp = ((b0 & 0x1F) as u32) << 6 | (text[pos + 1] & 0x3F) as u32;
        return (cp, 2);
    }
    if b0 < 0xF0 {
        if pos + 2 >= text.len() {
            return (0xFFFD, 1);
        }
        let cp = ((b0 & 0x0F) as u32) << 12
            | ((text[pos + 1] & 0x3F) as u32) << 6
            | (text[pos + 2] & 0x3F) as u32;
        return (cp, 3);
    }
    if pos + 3 >= text.len() {
        return (0xFFFD, 1);
    }
    let cp = ((b0 & 0x07) as u32) << 18
        | ((text[pos + 1] & 0x3F) as u32) << 12
        | ((text[pos + 2] & 0x3F) as u32) << 6
        | (text[pos + 3] & 0x3F) as u32;
    (cp, 4)
}

/// Width of one codepoint (tab = tab_width columns). Wcwidth-style.
fn char_width(cp: u32, tab_width: u8) -> u32 {
    if cp == b'\t' as u32 {
        return tab_width as u32;
    }
    char::from_u32(cp)
        .and_then(UnicodeWidthChar::width)
        .map(|w| w as u32)
        .unwrap_or(1)
}

/// Get display width at byte offset (single grapheme/codepoint in wcwidth mode).
/// Aligns OpenTUI utf8.zig getWidthAt (simplified wcwidth path).
pub fn get_width_at(text: &[u8], byte_offset: usize, tab_width: u8, _method: WidthMethod) -> u32 {
    if byte_offset >= text.len() {
        return 0;
    }
    let (cp, _len) = decode_utf8_unchecked(text, byte_offset);
    char_width(cp, tab_width)
}

/// Calculate total display width of text. Simplified (wcwidth per codepoint).
pub fn calculate_text_width(
    text: &[u8],
    tab_width: u8,
    _is_ascii_only: bool,
    method: WidthMethod,
) -> u32 {
    let mut pos = 0;
    let mut total: u32 = 0;
    while pos < text.len() {
        let (cp, len) = decode_utf8_unchecked(text, pos);
        total += char_width(cp, tab_width);
        pos += len as usize;
    }
    let _ = method;
    total
}

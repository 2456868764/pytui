//! Terminal capability and cursor state. Aligns OpenTUI terminal.zig.

use std::fmt::Write;

/// Cursor style. Aligns OpenTUI terminal.zig CursorStyle.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CursorStyle {
    Block,
    Line,
    Underline,
}

/// Terminal capability and cursor state. Aligns OpenTUI terminal.zig Terminal (internal, not pyclass).
#[derive(Clone, Debug)]
pub struct Terminal {
    pub cursor_x: u32,
    pub cursor_y: u32,
    pub cursor_visible: bool,
    pub cursor_style: CursorStyle,
    pub cursor_blinking: bool,
    pub cursor_color: [f32; 4],
    pub term_name: String,
    pub term_version: String,
    pub from_xtversion: bool,
    pub kitty_keyboard: bool,
    pub kitty_graphics: bool,
    pub sgr_pixels: bool,
    pub sync: bool,
    pub bracketed_paste: bool,
    pub focus_tracking: bool,
    pub explicit_width: bool,
    pub scaled_text: bool,
}

impl Default for Terminal {
    fn default() -> Self {
        Terminal {
            cursor_x: 1,
            cursor_y: 1,
            cursor_visible: true,
            cursor_style: CursorStyle::Block,
            cursor_blinking: false,
            cursor_color: [1.0, 1.0, 1.0, 1.0],
            term_name: String::new(),
            term_version: String::new(),
            from_xtversion: false,
            kitty_keyboard: false,
            kitty_graphics: false,
            sgr_pixels: false,
            sync: false,
            bracketed_paste: false,
            focus_tracking: false,
            explicit_width: false,
            scaled_text: false,
        }
    }
}

impl Terminal {
    pub fn new() -> Self {
        Self::default()
    }

    fn parse_xtversion(&mut self, term_str: &str) {
        let term_str = term_str.trim();
        if term_str.is_empty() {
            return;
        }
        if let Some(paren_pos) = term_str.find('(') {
            self.term_name = term_str[..paren_pos].to_string();
            if let Some(close_off) = term_str[paren_pos..].find(')') {
                let ver_start = paren_pos + 1;
                let ver_end = paren_pos + close_off;
                self.term_version = term_str[ver_start..ver_end].to_string();
            }
        } else if let Some(space_pos) = term_str.find(' ') {
            self.term_name = term_str[..space_pos].to_string();
            self.term_version = term_str[space_pos + 1..].to_string();
        } else {
            self.term_name = term_str.to_string();
            self.term_version.clear();
        }
        self.from_xtversion = true;
    }

    pub fn process_capability_response(&mut self, response: &str) {
        let prefix = "\x1bP>|";
        let suffix = "\x1b\\";
        if let Some(pos) = response.find(prefix) {
            let start = pos + prefix.len();
            if let Some(end_off) = response[start..].find(suffix) {
                let term_str = &response[start..start + end_off];
                self.parse_xtversion(term_str);
            }
        }

        if response.contains("1016;2$y") {
            self.sgr_pixels = true;
        }
        if response.contains("2026;1$y") || response.contains("2026;2$y") {
            self.sync = true;
        }
        if response.contains("1004;1$y") || response.contains("1004;2$y") {
            self.focus_tracking = true;
        }
        if response.contains("2004;1$y") || response.contains("2004;2$y") {
            self.bracketed_paste = true;
        }

        if let Some(pos) = response.find("\x1b[1;") {
            let after = response.get(pos + 4..).unwrap_or("");
            let mut end = 0usize;
            for c in after.chars() {
                if c.is_ascii_digit() {
                    end += c.len_utf8();
                } else {
                    break;
                }
            }
            if end > 0 && after.get(end..).map(|s| s.starts_with('R')).unwrap_or(false) {
                if let Ok(col) = after[..end].parse::<u16>() {
                    if col >= 2 {
                        self.explicit_width = true;
                    }
                    if col >= 3 {
                        self.scaled_text = true;
                    }
                }
            }
        }

        if response.contains("kitty") {
            self.kitty_keyboard = true;
            self.kitty_graphics = true;
            self.bracketed_paste = true;
        }

        if response.contains("\x1b[?") && response.contains('u') {
            let bytes = response.as_bytes();
            let mut i = 0;
            while i + 4 < bytes.len() {
                if bytes[i] == b'\x1b'
                    && i + 1 < bytes.len()
                    && bytes[i + 1] == b'['
                    && i + 2 < bytes.len()
                    && bytes[i + 2] == b'?'
                {
                    let mut num_end = i + 3;
                    while num_end < bytes.len() && bytes[num_end].is_ascii_digit() {
                        num_end += 1;
                    }
                    if num_end > i + 3 && num_end < bytes.len() && bytes[num_end] == b'u' {
                        self.kitty_keyboard = true;
                        break;
                    }
                }
                i += 1;
            }
        }
    }

    pub fn set_cursor_position(&mut self, x: u32, y: u32, visible: bool) {
        self.cursor_x = x.max(1);
        self.cursor_y = y.max(1);
        self.cursor_visible = visible;
    }

    pub fn set_cursor_style(&mut self, style: CursorStyle, blinking: bool) {
        self.cursor_style = style;
        self.cursor_blinking = blinking;
    }

    pub fn set_cursor_color(&mut self, r: f32, g: f32, b: f32, a: f32) {
        self.cursor_color = [r, g, b, a];
    }

    pub fn cursor_position_ansi(&self) -> String {
        let mut out = String::new();
        if self.cursor_visible {
            out.push_str("\x1b[?25h");
        } else {
            out.push_str("\x1b[?25l");
        }
        let _ = write!(out, "\x1b[{};{}H", self.cursor_y, self.cursor_x);
        out
    }

    pub fn cursor_style_ansi(&self) -> String {
        match (self.cursor_style, self.cursor_blinking) {
            (CursorStyle::Block, false) => "\x1b[2 q".to_string(),
            (CursorStyle::Block, true) => "\x1b[1 q".to_string(),
            (CursorStyle::Line, false) => "\x1b[6 q".to_string(),
            (CursorStyle::Line, true) => "\x1b[5 q".to_string(),
            (CursorStyle::Underline, false) => "\x1b[4 q".to_string(),
            (CursorStyle::Underline, true) => "\x1b[3 q".to_string(),
        }
    }

    pub fn cursor_color_ansi(&self) -> String {
        let r = (self.cursor_color[0].clamp(0.0, 1.0) * 255.0) as u8;
        let g = (self.cursor_color[1].clamp(0.0, 1.0) * 255.0) as u8;
        let b = (self.cursor_color[2].clamp(0.0, 1.0) * 255.0) as u8;
        format!("\x1b]12;#{:02x}{:02x}{:02x}\x07", r, g, b)
    }

    pub fn set_terminal_title_ansi(&self, title: &str) -> String {
        format!("\x1b]0;{}\x07", title)
    }

    pub fn clear_terminal_ansi(&self) -> String {
        "\x1b[H\x1b[2J".to_string()
    }

    pub fn get_cursor_x(&self) -> u32 {
        self.cursor_x
    }
    pub fn get_cursor_y(&self) -> u32 {
        self.cursor_y
    }
    pub fn get_cursor_visible(&self) -> bool {
        self.cursor_visible
    }
    pub fn get_cursor_style(&self) -> (CursorStyle, bool) {
        (self.cursor_style, self.cursor_blinking)
    }
    pub fn get_cursor_color(&self) -> [f32; 4] {
        self.cursor_color
    }
    pub fn get_terminal_name(&self) -> &str {
        &self.term_name
    }
    pub fn get_terminal_version(&self) -> &str {
        &self.term_version
    }
    pub fn get_from_xtversion(&self) -> bool {
        self.from_xtversion
    }
    pub fn get_kitty_keyboard(&self) -> bool {
        self.kitty_keyboard
    }
    pub fn get_kitty_graphics(&self) -> bool {
        self.kitty_graphics
    }

    #[cfg(test)]
    pub fn set_term_info_for_test(&mut self, name: &str, version: &str) {
        self.term_name = name.to_string();
        self.term_version = version.to_string();
        self.from_xtversion = false;
    }
}

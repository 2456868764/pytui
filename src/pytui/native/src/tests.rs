//! Unit tests. Aligns OpenTUI zig tests (buffer_test, renderer_test, terminal_test, link).
//! Structure: tests::buffer_test, tests::renderer_test, tests::terminal_test, tests::link_test, tests::ansi_test.

#![cfg(test)]

use crate::ansi::{attributes_with_link, get_link_id_from_attributes};
use crate::buffer::Buffer;
use crate::cell::Cell;
use crate::grapheme::GraphemePool;
use crate::link::LinkPool;
use crate::mem_registry::MemRegistry;
use crate::renderer::CliRenderer;
use crate::rope::Rope;
use crate::syntax_style::SyntaxStyle;
use crate::utf8;
use pyo3::prelude::*;

/// Shared helper: run closure with GIL. Used by all test submodules.
pub fn with_py<F, R>(f: F) -> R
where
    F: FnOnce(Python<'_>) -> R,
{
    pyo3::prepare_freethreaded_python();
    Python::with_gil(f)
}

// =============================================================================
// buffer_test — Aligns: opentui/packages/core/src/zig/tests/buffer_test.zig
// =============================================================================

pub mod buffer_test {
    use super::*;

    /// Aligns: buffer_test.zig - "OptimizedBuffer - init and deinit"
    #[test]
    fn init_and_dimensions() {
        let buf = Buffer::new(10, 10);
        assert_eq!(buf.get_width(), 10);
        assert_eq!(buf.get_height(), 10);
    }

    /// Aligns: buffer_test.zig - "OptimizedBuffer - clear fills with default char"
    #[test]
    fn clear_fills_with_default() {
        with_py(|_py| {
            let mut buf = Buffer::new(5, 5);
            buf.clear();
            for y in 0..5 {
                for x in 0..5 {
                    let cell = buf.get_cell(x, y).unwrap();
                    assert_eq!(cell.char, " ");
                }
            }
        });
    }

    /// Aligns: buffer_test.zig - set/get cell (Buffer API)
    #[test]
    fn set_cell_get_cell() {
        with_py(|_py| {
            let mut buf = Buffer::new(5, 5);
            let mut cell = Cell::new();
            cell.char = "H".to_string();
            cell.fg = (255, 0, 0, 255);
            buf.set_cell(0, 0, cell).unwrap();
            let got = buf.get_cell(0, 0).unwrap();
            assert_eq!(got.char, "H");
            assert_eq!(got.fg, (255, 0, 0, 255));
        });
    }

    /// Aligns: buffer_test.zig - "OptimizedBuffer - drawText with ASCII"
    #[test]
    fn draw_text_ascii() {
        with_py(|_py| {
            let mut buf = Buffer::new(20, 5);
            buf.clear();
            buf.draw_text("Hello", 0, 0, (255, 255, 255, 255));
            assert_eq!(buf.get_cell(0, 0).unwrap().char, "H");
            assert_eq!(buf.get_cell(1, 0).unwrap().char, "e");
            assert_eq!(buf.get_cell(4, 0).unwrap().char, "o");
        });
    }

    /// Aligns: buffer_test.zig - fillRect
    #[test]
    fn fill_rect() {
        with_py(|_py| {
            let mut buf = Buffer::new(10, 10);
            let mut cell = Cell::new();
            cell.char = "x".to_string();
            buf.fill_rect(2, 2, 3, 3, cell).unwrap();
            for dy in 0..3 {
                for dx in 0..3 {
                    assert_eq!(buf.get_cell(2 + dx, 2 + dy).unwrap().char, "x");
                }
            }
        });
    }

    /// Aligns: buffer_test.zig - "OptimizedBuffer - cells are initialized after resize grow"
    #[test]
    fn resize() {
        with_py(|_py| {
            let mut buf = Buffer::new(5, 5);
            let mut cell = Cell::new();
            cell.char = "a".to_string();
            buf.set_cell(0, 0, cell).unwrap();
            buf.resize(10, 10).unwrap();
            assert_eq!(buf.get_width(), 10);
            assert_eq!(buf.get_height(), 10);
            assert_eq!(buf.get_cell(0, 0).unwrap().char, "a");
        });
    }

    /// Buffer diff output - full repaint
    #[test]
    fn diff_and_output_ansi_full_repaint() {
        with_py(|_py| {
            let back = Buffer::new(3, 3);
            let front = Buffer::new(3, 3);
            let out = back.diff_and_output_ansi(&front, true).unwrap();
            assert!(out.contains("\x1b[H"));
            assert!(out.contains("\x1b[2J"));
        });
    }

    /// Buffer diff output - differing cell
    #[test]
    fn diff_and_output_ansi_differing_cell() {
        with_py(|_py| {
            let mut back = Buffer::new(4, 4);
            let front = Buffer::new(4, 4);
            let mut cell = Cell::new();
            cell.char = "X".to_string();
            back.set_cell(1, 1, cell).unwrap();
            let out = back.diff_and_output_ansi(&front, false).unwrap();
            assert!(!out.is_empty());
            assert!(out.contains("X"));
        });
    }

    /// clearWithBg
    #[test]
    fn clear_with_bg() {
        with_py(|_py| {
            let mut buf = Buffer::new(3, 3);
            buf.clear_with_bg(10, 20, 30, 255);
            let c = buf.get_cell(0, 0).unwrap();
            assert_eq!(c.bg, (10, 20, 30, 255));
            assert_eq!(c.char, " ");
        });
    }
}

// =============================================================================
// renderer_test — Aligns: opentui/packages/core/src/zig/tests/renderer_test.zig
// =============================================================================

pub mod renderer_test {
    use super::*;

    /// Aligns: renderer_test.zig - "renderer - create and destroy"
    #[test]
    fn create_and_dimensions() {
        with_py(|py| {
            let r = CliRenderer::new(py, 80, 24).unwrap();
            assert_eq!(r.get_width(), 80);
            assert_eq!(r.get_height(), 24);
        });
    }

    /// Aligns: renderer_test.zig - "renderer - simple text rendering to currentRenderBuffer"
    #[test]
    fn get_next_buffer_draw_then_render() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            let next = r.get_next_buffer(py);
            next.as_ref(py).borrow_mut().draw_text("Hi", 0, 0, (255, 255, 255, 255));
            let out = r.render(py, false).unwrap();
            assert!(!out.is_empty());
            let current = r.get_current_buffer(py);
            let cell = current.as_ref(py).borrow().get_cell(0, 0).unwrap();
            assert_eq!(cell.char, "H");
            let cell1 = current.as_ref(py).borrow().get_cell(1, 0).unwrap();
            assert_eq!(cell1.char, "i");
        });
    }

    /// Aligns: renderer_test.zig - "renderer - multi-line text rendering"
    #[test]
    fn multi_line_rendering() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            let next = r.get_next_buffer(py);
            next.as_ref(py).borrow_mut().draw_text("L1", 0, 0, (255, 255, 255, 255));
            next.as_ref(py).borrow_mut().draw_text("L2", 0, 1, (255, 255, 255, 255));
            next.as_ref(py).borrow_mut().draw_text("L3", 0, 2, (255, 255, 255, 255));
            r.render(py, false).unwrap();
            let current = r.get_current_buffer(py);
            assert_eq!(current.as_ref(py).borrow().get_cell(0, 0).unwrap().char, "L");
            assert_eq!(current.as_ref(py).borrow().get_cell(0, 1).unwrap().char, "L");
            assert_eq!(current.as_ref(py).borrow().get_cell(0, 2).unwrap().char, "L");
        });
    }

    /// Hit grid: add region and check hit
    #[test]
    fn hit_grid_add_and_check_hit() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 20, 10).unwrap();
            r.add_to_hit_grid(2, 1, 5, 3, 42);
            r.render(py, false).unwrap();
            assert_eq!(r.check_hit(3, 2), 42);
            assert_eq!(r.check_hit(2, 1), 42);
            assert_eq!(r.check_hit(0, 0), 0);
            assert_eq!(r.check_hit(100, 100), 0);
        });
    }

    #[test]
    fn hit_grid_later_overwrites_earlier() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 20, 10).unwrap();
            r.add_to_hit_grid(0, 0, 10, 5, 1);
            r.add_to_hit_grid(3, 2, 4, 2, 2);
            r.render(py, false).unwrap();
            assert_eq!(r.check_hit(1, 1), 1);
            assert_eq!(r.check_hit(4, 3), 2);
            assert_eq!(r.check_hit(5, 3), 2);
        });
    }

    #[test]
    fn hit_grid_clear_current() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 10, 10).unwrap();
            r.add_to_hit_grid(0, 0, 5, 5, 7);
            r.render(py, false).unwrap();
            assert_eq!(r.check_hit(2, 2), 7);
            r.clear_current_hit_grid();
            assert_eq!(r.check_hit(2, 2), 0);
        });
    }

    #[test]
    fn hit_grid_scissor_clips() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 20, 10).unwrap();
            r.hit_grid_push_scissor_rect(2, 1, 8, 5);
            r.add_to_hit_grid(0, 0, 20, 10, 1);
            r.render(py, false).unwrap();
            assert_eq!(r.check_hit(0, 0), 0);
            assert_eq!(r.check_hit(5, 3), 1);
            r.hit_grid_pop_scissor_rect();
        });
    }

    #[test]
    fn hit_grid_clear_scissor_rects() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 10, 10).unwrap();
            r.hit_grid_push_scissor_rect(0, 0, 5, 5);
            r.hit_grid_clear_scissor_rects();
            r.add_to_hit_grid(0, 0, 10, 10, 1);
            r.render(py, false).unwrap();
            assert_eq!(r.check_hit(7, 7), 1);
        });
    }

    /// Aligns: renderer_test.zig - "renderer - resize updates dimensions"
    #[test]
    fn resize() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 10, 10).unwrap();
            r.resize(py, 20, 15).unwrap();
            assert_eq!(r.get_width(), 20);
            assert_eq!(r.get_height(), 15);
        });
    }

    /// Debug overlay set/get
    #[test]
    fn debug_overlay_set_and_get() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            let (enabled, corner) = r.get_debug_overlay();
            assert!(!enabled);
            assert_eq!(corner, 3);
            r.set_debug_overlay(true, 0).unwrap();
            let (enabled, corner) = r.get_debug_overlay();
            assert!(enabled);
            assert_eq!(corner, 0);
            r.set_debug_overlay(false, 2).unwrap();
            let (enabled, corner) = r.get_debug_overlay();
            assert!(!enabled);
            assert_eq!(corner, 2);
        });
    }

    /// dumpStdoutBuffer after render
    #[test]
    fn dump_stdout_buffer_after_render() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 10, 5).unwrap();
            r.get_next_buffer(py).as_ref(py).borrow_mut().draw_text("X", 0, 0, (255, 255, 255, 255));
            let _ = r.render(py, false).unwrap();
            let ts = 12345_i64;
            r.dump_stdout_buffer(ts).unwrap();
            let path = format!("buffer_dump/stdout_buffer_{}.txt", ts);
            let content = std::fs::read_to_string(&path).unwrap();
            assert!(content.contains("Stdout Buffer Output"));
            assert!(content.contains("Last Rendered ANSI Output"));
            assert!(content.contains("X") || content.contains("1;1H"));
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_dir("buffer_dump");
        });
    }

    /// dumpBuffers creates files
    #[test]
    fn dump_buffers_creates_files() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 8, 4).unwrap();
            r.get_next_buffer(py).as_ref(py).borrow_mut().draw_text("A", 0, 0, (255, 255, 255, 255));
            let _ = r.render(py, false).unwrap();
            let ts = 99999_i64;
            r.dump_buffers(py, ts).unwrap();
            let current_path = format!("buffer_dump/current_buffer_{}.txt", ts);
            let next_path = format!("buffer_dump/next_buffer_{}.txt", ts);
            let stdout_path = format!("buffer_dump/stdout_buffer_{}.txt", ts);
            assert!(std::path::Path::new(&current_path).exists());
            assert!(std::path::Path::new(&next_path).exists());
            assert!(std::path::Path::new(&stdout_path).exists());
            let current_content = std::fs::read_to_string(&current_path).unwrap();
            assert!(current_content.contains("current Buffer (8x4)"));
            let _ = std::fs::remove_file(&current_path);
            let _ = std::fs::remove_file(&next_path);
            let _ = std::fs::remove_file(&stdout_path);
            let _ = std::fs::remove_dir("buffer_dump");
        });
    }
}

// =============================================================================
// terminal_test — Aligns: opentui/packages/core/src/zig/tests/terminal_test.zig
// =============================================================================

pub mod terminal_test {
    use super::*;

    /// Aligns: terminal_test.zig - "parseXtversion - kitty format"
    #[test]
    fn parse_xtversion_kitty_format() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.process_capability_response("\x1bP>|kitty(0.40.1)\x1b\\");
            assert_eq!(r.get_terminal_name(), "kitty");
            assert_eq!(r.get_terminal_version(), "0.40.1");
            assert!(r.get_from_xtversion());
        });
    }

    /// Aligns: terminal_test.zig - "parseXtversion - ghostty format"
    #[test]
    fn parse_xtversion_ghostty_format() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.process_capability_response("\x1bP>|ghostty 1.1.3\x1b\\");
            assert_eq!(r.get_terminal_name(), "ghostty");
            assert_eq!(r.get_terminal_version(), "1.1.3");
            assert!(r.get_from_xtversion());
        });
    }

    /// Aligns: terminal_test.zig - "parseXtversion - tmux format"
    #[test]
    fn parse_xtversion_tmux_format() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.process_capability_response("\x1bP>|tmux 3.5a\x1b\\");
            assert_eq!(r.get_terminal_name(), "tmux");
            assert_eq!(r.get_terminal_version(), "3.5a");
            assert!(r.get_from_xtversion());
        });
    }

    /// Aligns: terminal_test.zig - "parseXtversion - with prefix data"
    #[test]
    fn parse_xtversion_with_prefix_data() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.process_capability_response("\x1b[1;1R\x1bP>|tmux 3.5a\x1b\\");
            assert_eq!(r.get_terminal_name(), "tmux");
            assert_eq!(r.get_terminal_version(), "3.5a");
            assert!(r.get_from_xtversion());
        });
    }

    /// Aligns: terminal_test.zig - "parseXtversion - full kitty response"
    #[test]
    fn parse_xtversion_full_kitty_response() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.process_capability_response("\x1b[?1016;2$y\x1b[?2027;0$y\x1b[?2031;2$y\x1b[?1004;1$y\x1b[?2026;2$y\x1b[1;2R\x1b[1;3R\x1bP>|kitty(0.40.1)\x1b\\\x1b[?0u\x1b_Gi=1;EINVAL:Zero width/height not allowed\x1b\\\x1b[?62;c");
            assert_eq!(r.get_terminal_name(), "kitty");
            assert_eq!(r.get_terminal_version(), "0.40.1");
            assert!(r.get_from_xtversion());
            assert!(r.get_kitty_keyboard());
            assert!(r.get_kitty_graphics());
        });
    }

    /// Aligns: terminal_test.zig - "parseXtversion - full ghostty response"
    #[test]
    fn parse_xtversion_full_ghostty_response() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.process_capability_response("\x1b[?1016;1$y\x1b[?2027;1$y\x1b[?2031;2$y\x1b[?1004;1$y\x1b[?2004;2$y\x1b[?2026;2$y\x1b[1;1R\x1b[1;1R\x1bP>|ghostty 1.1.3\x1b\\\x1b[?0u\x1b_Gi=1;OK\x1b\\\x1b[?62;22c");
            assert_eq!(r.get_terminal_name(), "ghostty");
            assert_eq!(r.get_terminal_version(), "1.1.3");
            assert!(r.get_from_xtversion());
        });
    }

    /// Aligns: terminal_test.zig - "environment variables - should be overridden by xtversion"
    #[test]
    fn environment_overridden_by_xtversion() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.set_terminal_info_for_test("vscode", "1.0.0");
            assert_eq!(r.get_terminal_name(), "vscode");
            assert_eq!(r.get_terminal_version(), "1.0.0");
            assert!(!r.get_from_xtversion());
            r.process_capability_response("\x1bP>|kitty(0.40.1)\x1b\\");
            assert_eq!(r.get_terminal_name(), "kitty");
            assert_eq!(r.get_terminal_version(), "0.40.1");
            assert!(r.get_from_xtversion());
        });
    }

    /// Aligns: terminal_test.zig - "parseXtversion - terminal name only"
    #[test]
    fn parse_xtversion_name_only() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.process_capability_response("\x1bP>|wezterm\x1b\\");
            assert_eq!(r.get_terminal_name(), "wezterm");
            assert_eq!(r.get_terminal_version(), "");
            assert!(r.get_from_xtversion());
        });
    }

    /// Aligns: terminal_test.zig - "parseXtversion - empty response"
    #[test]
    fn parse_xtversion_empty_response() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.process_capability_response("\x1bP>|\x1b\\");
            assert!(r.get_terminal_name().is_empty());
            assert!(r.get_terminal_version().is_empty());
            assert!(!r.get_from_xtversion());
        });
    }

    #[test]
    fn cursor_position() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.set_cursor_position(10, 5, true);
            let (x, y, visible) = r.get_cursor_position();
            assert_eq!(x, 10);
            assert_eq!(y, 5);
            assert!(visible);
            r.set_cursor_position(1, 1, false);
            let (x, y, visible) = r.get_cursor_position();
            assert_eq!(x, 1);
            assert_eq!(y, 1);
            assert!(!visible);
        });
    }

    #[test]
    fn cursor_style() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.set_cursor_style("block", false).unwrap();
            let (style, blink) = r.get_cursor_style();
            assert_eq!(style, "block");
            assert!(!blink);
            r.set_cursor_style("line", true).unwrap();
            let (style, blink) = r.get_cursor_style();
            assert_eq!(style, "line");
            assert!(blink);
            r.set_cursor_style("underline", false).unwrap();
            let (style, _) = r.get_cursor_style();
            assert_eq!(style, "underline");
        });
    }

    #[test]
    fn cursor_color() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.set_cursor_color(0.5, 0.0, 1.0, 1.0);
            let (r_, g, b, a): (f32, f32, f32, f32) = r.get_cursor_color();
            assert!((r_ - 0.5).abs() < 1e-5);
            assert!((g - 0.0).abs() < 1e-5);
            assert!((b - 1.0).abs() < 1e-5);
            assert!((a - 1.0).abs() < 1e-5);
        });
    }

    #[test]
    fn cursor_position_ansi() {
        with_py(|py| {
            let r = CliRenderer::new(py, 80, 24).unwrap();
            let ansi = r.cursor_position_ansi();
            assert!(ansi.contains("\x1b[?25h"));
            assert!(ansi.contains("\x1b[1;1H"));
        });
    }

    #[test]
    fn cursor_style_ansi() {
        with_py(|py| {
            let mut r = CliRenderer::new(py, 80, 24).unwrap();
            r.set_cursor_style("block", false).unwrap();
            assert!(r.cursor_style_ansi().contains("2 q"));
            r.set_cursor_style("line", true).unwrap();
            assert!(r.cursor_style_ansi().contains("5 q"));
        });
    }

    #[test]
    fn set_title_ansi() {
        with_py(|py| {
            let r = CliRenderer::new(py, 80, 24).unwrap();
            let ansi = r.set_terminal_title_ansi("My App");
            assert_eq!(ansi, "\x1b]0;My App\x07");
        });
    }

    #[test]
    fn clear_terminal_ansi() {
        with_py(|py| {
            let r = CliRenderer::new(py, 80, 24).unwrap();
            let ansi = r.clear_terminal_ansi();
            assert_eq!(ansi, "\x1b[H\x1b[2J");
        });
    }
}

// =============================================================================
// link_test — Aligns: opentui link.zig (LinkPool; tests exercised via buffer/renderer in Zig)
// =============================================================================

pub mod link_test {
    use super::*;

    #[test]
    fn alloc_and_get() {
        with_py(|_py| {
            let mut pool = LinkPool::new();
            let id = pool.alloc("https://example.com").unwrap();
            assert!(id != 0);
            let url = pool.get(id).unwrap();
            assert_eq!(url, "https://example.com");
        });
    }

    #[test]
    fn incref_decref_refcount() {
        with_py(|_py| {
            let mut pool = LinkPool::new();
            let id = pool.alloc("https://a.example").unwrap();
            assert_eq!(pool.get_refcount(id).unwrap(), 0);
            pool.incref(id).unwrap();
            assert_eq!(pool.get_refcount(id).unwrap(), 1);
            pool.incref(id).unwrap();
            assert_eq!(pool.get_refcount(id).unwrap(), 2);
            pool.decref(id).unwrap();
            assert_eq!(pool.get_refcount(id).unwrap(), 1);
            pool.decref(id).unwrap();
            assert_eq!(pool.get(id).unwrap(), "https://a.example");
        });
    }

    /// Aligns: buffer_test.zig - "OptimizedBuffer - link reuse after free"
    #[test]
    fn reuse_after_decref_to_zero() {
        with_py(|_py| {
            let mut pool = LinkPool::new();
            let id1 = pool.alloc("url1").unwrap();
            pool.incref(id1).unwrap();
            pool.decref(id1).unwrap();
            let id2 = pool.alloc("url2").unwrap();
            assert_eq!(pool.get(id2).unwrap(), "url2");
            assert!(pool.get(id1).is_err());
        });
    }

    #[test]
    fn url_too_long() {
        with_py(|_py| {
            let mut pool = LinkPool::new();
            let long = "x".repeat(600);
            let res = pool.alloc(&long);
            assert!(res.is_err());
        });
    }
}

// =============================================================================
// rope_test — Aligns: opentui/packages/core/src/zig/tests/rope_test.zig
// =============================================================================

pub mod rope_test {
    use super::*;

    /// Aligns: rope_test.zig - "Rope - can initialize with arena allocator"
    #[test]
    fn init_empty() {
        let rope = Rope::new();
        assert_eq!(rope.count(), 0);
    }

    /// Aligns: rope_test.zig - "Rope - from_slice creates rope from multiple items"
    #[test]
    fn from_str_creates_rope() {
        let rope = Rope::from_str("abc");
        assert_eq!(rope.count(), 3);
        assert_eq!(rope.slice(0, 3), "abc");
    }

    #[test]
    fn insert_at_beginning() {
        let mut rope = Rope::from_str("bc");
        rope.insert(0, "a");
        assert_eq!(rope.to_string(), "abc");
    }

    #[test]
    fn delete_range() {
        let mut rope = Rope::from_str("hello");
        rope.delete_range(1, 4);
        assert_eq!(rope.to_string(), "ho");
    }

    #[test]
    fn get_out_of_bounds_returns_none() {
        let rope = Rope::from_str("x");
        assert!(rope.get(100).is_none());
    }
}

// =============================================================================
// mem_registry_test — Aligns: opentui/packages/core/src/zig/tests/mem-registry_test.zig
// =============================================================================

pub mod mem_registry_test {
    use super::*;

    /// Aligns: mem-registry_test.zig - "MemRegistry - init and deinit"
    #[test]
    fn init_and_deinit() {
        let reg = MemRegistry::new();
        assert_eq!(reg.get_used_slots(), 0);
        assert_eq!(reg.get_free_slots(), 255);
    }

    /// Aligns: "MemRegistry - register owned memory"
    #[test]
    fn register_owned_memory() {
        let mut reg = MemRegistry::new();
        let id = reg.register(b"Hello, World!", true).unwrap();
        assert_eq!(id, 0);
        assert_eq!(reg.get_used_slots(), 1);
        assert_eq!(reg.get_free_slots(), 254);
        assert_eq!(reg.get(id).unwrap(), b"Hello, World!");
    }

    #[test]
    fn register_multiple_buffers() {
        let mut reg = MemRegistry::new();
        let id1 = reg.register(b"First", false).unwrap();
        let id2 = reg.register(b"Second", false).unwrap();
        let id3 = reg.register(b"Third", false).unwrap();
        assert_eq!(id1, 0);
        assert_eq!(id2, 1);
        assert_eq!(id3, 2);
        assert_eq!(reg.get_used_slots(), 3);
        assert_eq!(reg.get(id1).unwrap(), b"First");
        assert_eq!(reg.get(id2).unwrap(), b"Second");
        assert_eq!(reg.get(id3).unwrap(), b"Third");
    }

    #[test]
    fn get_invalid_id_returns_none() {
        let mut reg = MemRegistry::new();
        let _ = reg.register(b"Test", false).unwrap();
        assert!(reg.get(1).is_none());
        assert!(reg.get(255).is_none());
    }

    #[test]
    fn unregister_and_reuse() {
        let mut reg = MemRegistry::new();
        let id = reg.register(b"X", false).unwrap();
        reg.unregister(id).unwrap();
        assert_eq!(reg.get_used_slots(), 0);
        let id2 = reg.register(b"Y", false).unwrap();
        assert_eq!(id2, id);
        assert_eq!(reg.get(id2).unwrap(), b"Y");
    }
}

// =============================================================================
// syntax_style_test — Aligns: opentui/packages/core/src/zig/tests/syntax-style_test.zig
// =============================================================================

pub mod syntax_style_test {
    use super::*;

    /// Aligns: syntax-style_test.zig - "SyntaxStyle - init and deinit"
    #[test]
    fn init_and_deinit() {
        let style = SyntaxStyle::new();
        assert_eq!(style.get_style_count(), 0);
    }

    /// Aligns: "SyntaxStyle - register simple style"
    #[test]
    fn register_simple_style() {
        let mut style = SyntaxStyle::new();
        let fg: [f32; 4] = [1.0, 0.0, 0.0, 1.0];
        let id = style.register_style("keyword", Some(fg), None, 0);
        assert!(id > 0);
        assert_eq!(style.get_style_count(), 1);
    }

    #[test]
    fn register_style_with_fg_and_bg() {
        let mut style = SyntaxStyle::new();
        let fg: [f32; 4] = [1.0, 0.0, 0.0, 1.0];
        let bg: [f32; 4] = [0.0, 0.0, 0.0, 1.0];
        let id = style.register_style("string", Some(fg), Some(bg), 0);
        assert!(id > 0);
        let def = style.resolve_by_id(id).unwrap();
        assert!(def.fg.is_some());
        assert!(def.bg.is_some());
    }

    #[test]
    fn resolve_by_name() {
        let mut style = SyntaxStyle::new();
        let fg: [f32; 4] = [0.0, 1.0, 0.0, 1.0];
        let id = style.register_style("comment", Some(fg), None, 0);
        assert_eq!(style.resolve_by_name("comment"), Some(id));
        assert!(style.get_style_by_name("comment").is_some());
    }

    #[test]
    fn merge_styles() {
        let mut style = SyntaxStyle::new();
        let fg1: [f32; 4] = [1.0, 0.0, 0.0, 1.0];
        let fg2: [f32; 4] = [0.0, 0.0, 1.0, 1.0];
        let id1 = style.register_style("a", Some(fg1), None, 1);
        let id2 = style.register_style("b", Some(fg2), None, 2);
        let merged = style.merge_styles(&[id1, id2]);
        assert_eq!(merged.attributes, 3);
        assert!(merged.fg.is_some());
    }
}

// =============================================================================
// utf8_test — Aligns: opentui/packages/core/src/zig/tests/utf8_test.zig
// =============================================================================

pub mod utf8_test {
    use super::*;

    /// Aligns: utf8_test.zig - "isAsciiOnly: empty string"
    #[test]
    fn is_ascii_only_empty_string() {
        assert!(!utf8::is_ascii_only(b""));
    }

    /// Aligns: utf8_test.zig - "isAsciiOnly: simple ASCII"
    #[test]
    fn is_ascii_only_simple_ascii() {
        assert!(utf8::is_ascii_only(b"Hello, World!"));
        assert!(utf8::is_ascii_only(b"The quick brown fox"));
        assert!(utf8::is_ascii_only(b"0123456789"));
    }

    /// Aligns: utf8_test.zig - "isAsciiOnly: control chars rejected"
    #[test]
    fn is_ascii_only_control_chars_rejected() {
        assert!(!utf8::is_ascii_only(b"Hello\tWorld"));
        assert!(!utf8::is_ascii_only(b"Hello\nWorld"));
        assert!(!utf8::is_ascii_only(b"\x00"));
    }

    /// Aligns: utf8_test.zig - "isAsciiOnly: Unicode rejected"
    #[test]
    fn is_ascii_only_unicode_rejected() {
        assert!(!utf8::is_ascii_only("Hello 👋".as_bytes()));
        assert!(!utf8::is_ascii_only("café".as_bytes()));
    }

    #[test]
    fn find_line_breaks_lf() {
        let breaks = utf8::find_line_breaks(b"a\nb\nc");
        assert_eq!(breaks.len(), 2);
        assert_eq!(breaks[0].pos, 1);
        assert!(matches!(breaks[0].kind, utf8::LineBreakKind::Lf));
        assert_eq!(breaks[1].pos, 3);
    }

    #[test]
    fn get_width_at_ascii() {
        let w = utf8::get_width_at(b"x", 0, 8, utf8::WidthMethod::Wcwidth);
        assert_eq!(w, 1);
    }
}

// =============================================================================
// grapheme_test — Aligns: opentui/packages/core/src/zig/tests/grapheme_test.zig
// =============================================================================

pub mod grapheme_test {
    use super::*;

    #[test]
    fn alloc_and_get() {
        let mut pool = GraphemePool::new();
        let id = pool.alloc("a".as_bytes()).unwrap();
        let s = pool.get(id).unwrap();
        assert_eq!(s, "a");
    }

    #[test]
    fn incref_decref_refcount() {
        let mut pool = GraphemePool::new();
        let id = pool.alloc("x".as_bytes()).unwrap();
        assert_eq!(pool.get_refcount(id).unwrap(), 0);
        pool.incref(id).unwrap();
        assert_eq!(pool.get_refcount(id).unwrap(), 1);
        pool.incref(id).unwrap();
        assert_eq!(pool.get_refcount(id).unwrap(), 2);
        pool.decref(id).unwrap();
        assert_eq!(pool.get_refcount(id).unwrap(), 1);
        pool.decref(id).unwrap();
        assert_eq!(pool.get(id).unwrap(), "x");
    }
}

// =============================================================================
// ansi_test — Aligns: ansi.zig TextAttributes setLinkId/getLinkId (attributes_with_link)
// =============================================================================

pub mod ansi_test {
    use super::*;

    #[test]
    fn attributes_with_link_and_get_link_id() {
        assert_eq!(get_link_id_from_attributes(attributes_with_link(0, 0)), 0);
        assert_eq!(get_link_id_from_attributes(attributes_with_link(1, 100)), 100);
        let attr = attributes_with_link(0xFF, 0x123456);
        assert_eq!(attr & 0xFF, 0xFF);
        assert_eq!(get_link_id_from_attributes(attr), 0x123456);
    }
}

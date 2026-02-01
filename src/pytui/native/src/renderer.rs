//! CLI renderer: double buffering, hit grid, terminal, debug overlay. Aligns OpenTUI renderer.zig.

use crate::buffer::Buffer;
use crate::geometry::ClipRect;
use crate::terminal::{CursorStyle, Terminal};
use pyo3::prelude::*;
use std::io::Write as IoWrite;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum DebugOverlayCorner {
    TopLeft = 0,
    TopRight = 1,
    BottomLeft = 2,
    BottomRight = 3,
}

#[pyclass]
pub struct CliRenderer {
    next_buffer: Py<Buffer>,
    current_buffer: Py<Buffer>,
    width: usize,
    height: usize,
    render_offset: u32,
    background_color: (u8, u8, u8, u8),
    frame_count: u64,
    current_hit_grid: Vec<u32>,
    next_hit_grid: Vec<u32>,
    hit_scissor_stack: Vec<ClipRect>,
    terminal: Terminal,
    debug_overlay_enabled: bool,
    debug_overlay_corner: u8,
    last_rendered_output: String,
}

impl CliRenderer {
    fn get_current_hit_scissor_rect(&self) -> Option<ClipRect> {
        self.hit_scissor_stack.last().copied()
    }

    fn clip_rect_to_hit_scissor(
        &self,
        x: i32,
        y: i32,
        width: u32,
        height: u32,
    ) -> Option<ClipRect> {
        let scissor = match self.get_current_hit_scissor_rect() {
            Some(s) => s,
            None => {
                return Some(ClipRect {
                    x,
                    y,
                    width,
                    height,
                });
            }
        };
        let rect_end_x = x + width as i32;
        let rect_end_y = y + height as i32;
        let scissor_end_x = scissor.x + scissor.width as i32;
        let scissor_end_y = scissor.y + scissor.height as i32;
        let intersect_x = x.max(scissor.x);
        let intersect_y = y.max(scissor.y);
        let intersect_end_x = rect_end_x.min(scissor_end_x);
        let intersect_end_y = rect_end_y.min(scissor_end_y);
        if intersect_x >= intersect_end_x || intersect_y >= intersect_end_y {
            return None;
        }
        Some(ClipRect {
            x: intersect_x,
            y: intersect_y,
            width: (intersect_end_x - intersect_x) as u32,
            height: (intersect_end_y - intersect_y) as u32,
        })
    }
}

#[pymethods]
impl CliRenderer {
    #[new]
    pub(crate) fn new(py: Python<'_>, width: usize, height: usize) -> PyResult<Self> {
        if width == 0 || height == 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "width and height must be positive",
            ));
        }
        let next_buf = Buffer::new(width, height);
        let current_buf = Buffer::new(width, height);
        let next_py = Py::new(py, next_buf)?;
        let current_py = Py::new(py, current_buf)?;
        let hit_size = width * height;
        let current_hit_grid = vec![0u32; hit_size];
        let next_hit_grid = vec![0u32; hit_size];
        Ok(CliRenderer {
            next_buffer: next_py,
            current_buffer: current_py,
            width,
            height,
            render_offset: 0,
            background_color: (0, 0, 0, 0),
            frame_count: 0,
            current_hit_grid,
            next_hit_grid,
            hit_scissor_stack: Vec::new(),
            terminal: Terminal::new(),
            debug_overlay_enabled: false,
            debug_overlay_corner: DebugOverlayCorner::BottomRight as u8,
            last_rendered_output: String::new(),
        })
    }

    pub(crate) fn get_next_buffer(&self, py: Python<'_>) -> Py<Buffer> {
        self.next_buffer.clone_ref(py)
    }

    pub(crate) fn get_current_buffer(&self, py: Python<'_>) -> Py<Buffer> {
        self.current_buffer.clone_ref(py)
    }

    pub(crate) fn get_width(&self) -> usize {
        self.width
    }

    pub(crate) fn get_height(&self) -> usize {
        self.height
    }

    fn get_render_offset(&self) -> u32 {
        self.render_offset
    }

    fn set_render_offset(&mut self, offset: u32) {
        self.render_offset = offset;
    }

    fn set_background_color(&mut self, r: u8, g: u8, b: u8, a: u8) {
        self.background_color = (r, g, b, a);
    }

    pub(crate) fn resize(&mut self, py: Python<'_>, width: usize, height: usize) -> PyResult<()> {
        if width == 0 || height == 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "width and height must be positive",
            ));
        }
        self.next_buffer.as_ref(py).borrow_mut().resize(width, height)?;
        self.current_buffer.as_ref(py).borrow_mut().resize(width, height)?;
        let new_hit_size = width * height;
        if new_hit_size > self.current_hit_grid.len() {
            self.current_hit_grid.resize(new_hit_size, 0);
            self.next_hit_grid.resize(new_hit_size, 0);
        }
        self.width = width;
        self.height = height;
        Ok(())
    }

    pub(crate) fn render(&mut self, py: Python<'_>, _force: bool) -> PyResult<String> {
        let full_repaint = self.frame_count == 0;
        let next_guard = self.next_buffer.as_ref(py).borrow();
        let current_guard = self.current_buffer.as_ref(py).borrow();
        let out = next_guard.diff_and_output_ansi(&current_guard, full_repaint)?;
        drop(current_guard);
        drop(next_guard);

        std::mem::swap(&mut self.next_buffer, &mut self.current_buffer);
        let (r, g, b, a) = self.background_color;
        self.next_buffer.as_ref(py).borrow_mut().clear_with_bg(r, g, b, a);
        self.frame_count = self.frame_count.saturating_add(1);
        std::mem::swap(&mut self.current_hit_grid, &mut self.next_hit_grid);
        self.next_hit_grid.fill(0);
        self.hit_scissor_stack.clear();
        self.last_rendered_output = out.clone();
        Ok(out)
    }

    pub(crate) fn add_to_hit_grid(&mut self, x: i32, y: i32, width: u32, height: u32, id: u32) {
        let Some(clipped) = self.clip_rect_to_hit_scissor(x, y, width, height) else {
            return;
        };
        let start_x = clipped.x.max(0) as usize;
        let start_y = clipped.y.max(0) as usize;
        let end_x = (clipped.x + clipped.width as i32).min(self.width as i32).max(0) as usize;
        let end_y = (clipped.y + clipped.height as i32).min(self.height as i32).max(0) as usize;
        if start_x >= end_x || start_y >= end_y {
            return;
        }
        for row in start_y..end_y {
            let row_start = row * self.width;
            for col in start_x..end_x {
                let idx = row_start + col;
                if idx < self.next_hit_grid.len() {
                    self.next_hit_grid[idx] = id;
                }
            }
        }
    }

    pub(crate) fn check_hit(&self, x: u32, y: u32) -> u32 {
        if x >= self.width as u32 || y >= self.height as u32 {
            return 0;
        }
        let idx = (y as usize) * self.width + (x as usize);
        self.current_hit_grid.get(idx).copied().unwrap_or(0)
    }

    pub(crate) fn clear_current_hit_grid(&mut self) {
        self.current_hit_grid.fill(0);
    }

    pub(crate) fn hit_grid_push_scissor_rect(&mut self, x: i32, y: i32, width: u32, height: u32) {
        let rect = if let Some(_scissor) = self.get_current_hit_scissor_rect() {
            match self.clip_rect_to_hit_scissor(x, y, width, height) {
                Some(clipped) => clipped,
                None => ClipRect {
                    x: 0,
                    y: 0,
                    width: 0,
                    height: 0,
                },
            }
        } else {
            ClipRect { x, y, width, height }
        };
        self.hit_scissor_stack.push(rect);
    }

    pub(crate) fn hit_grid_pop_scissor_rect(&mut self) {
        self.hit_scissor_stack.pop();
    }

    pub(crate) fn hit_grid_clear_scissor_rects(&mut self) {
        self.hit_scissor_stack.clear();
    }

    fn update_stats(&mut self, _overall_frame_time_ms: f64, _fps: u32, _frame_callback_time_ms: f64) {
    }

    pub(crate) fn set_cursor_position(&mut self, x: u32, y: u32, visible: bool) {
        self.terminal.set_cursor_position(x, y, visible);
    }

    pub(crate) fn set_cursor_style(&mut self, style: &str, blinking: bool) -> PyResult<()> {
        let s = match style {
            "block" => CursorStyle::Block,
            "line" => CursorStyle::Line,
            "underline" => CursorStyle::Underline,
            _ => {
                return Err(pyo3::exceptions::PyValueError::new_err(
                    "style must be 'block', 'line', or 'underline'",
                ));
            }
        };
        self.terminal.set_cursor_style(s, blinking);
        Ok(())
    }

    pub(crate) fn set_cursor_color(&mut self, r: f32, g: f32, b: f32, a: f32) {
        self.terminal.set_cursor_color(r, g, b, a);
    }

    pub(crate) fn get_cursor_position(&self) -> (u32, u32, bool) {
        (
            self.terminal.get_cursor_x(),
            self.terminal.get_cursor_y(),
            self.terminal.get_cursor_visible(),
        )
    }

    pub(crate) fn get_cursor_style(&self) -> (String, bool) {
        let (style, blinking) = self.terminal.get_cursor_style();
        let name = match style {
            CursorStyle::Block => "block",
            CursorStyle::Line => "line",
            CursorStyle::Underline => "underline",
        };
        (name.to_string(), blinking)
    }

    pub(crate) fn get_cursor_color(&self) -> (f32, f32, f32, f32) {
        let c = self.terminal.get_cursor_color();
        (c[0], c[1], c[2], c[3])
    }

    pub(crate) fn cursor_position_ansi(&self) -> String {
        self.terminal.cursor_position_ansi()
    }

    pub(crate) fn cursor_style_ansi(&self) -> String {
        self.terminal.cursor_style_ansi()
    }

    fn cursor_color_ansi(&self) -> String {
        self.terminal.cursor_color_ansi()
    }

    pub(crate) fn set_terminal_title_ansi(&self, title: &str) -> String {
        self.terminal.set_terminal_title_ansi(title)
    }

    pub(crate) fn clear_terminal_ansi(&self) -> String {
        self.terminal.clear_terminal_ansi()
    }

    pub(crate) fn process_capability_response(&mut self, response: &str) {
        self.terminal.process_capability_response(response);
    }

    pub(crate) fn get_terminal_name(&self) -> String {
        self.terminal.get_terminal_name().to_string()
    }

    pub(crate) fn get_terminal_version(&self) -> String {
        self.terminal.get_terminal_version().to_string()
    }

    pub(crate) fn get_from_xtversion(&self) -> bool {
        self.terminal.get_from_xtversion()
    }

    pub(crate) fn get_kitty_keyboard(&self) -> bool {
        self.terminal.get_kitty_keyboard()
    }

    pub(crate) fn get_kitty_graphics(&self) -> bool {
        self.terminal.get_kitty_graphics()
    }

    #[cfg(test)]
    pub(crate) fn set_terminal_info_for_test(&mut self, name: &str, version: &str) {
        self.terminal.set_term_info_for_test(name, version);
    }

    pub(crate) fn set_debug_overlay(&mut self, enabled: bool, corner: u8) -> PyResult<()> {
        if corner > 3 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "corner must be 0=topLeft, 1=topRight, 2=bottomLeft, 3=bottomRight",
            ));
        }
        self.debug_overlay_enabled = enabled;
        self.debug_overlay_corner = corner;
        Ok(())
    }

    pub(crate) fn get_debug_overlay(&self) -> (bool, u8) {
        (self.debug_overlay_enabled, self.debug_overlay_corner)
    }

    pub(crate) fn dump_buffers(&self, py: Python<'_>, timestamp: i64) -> PyResult<()> {
        let dir = "buffer_dump";
        std::fs::create_dir_all(dir).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
        self.dump_single_buffer(py, self.current_buffer.clone_ref(py), "current", timestamp)?;
        self.dump_single_buffer(py, self.next_buffer.clone_ref(py), "next", timestamp)?;
        self.dump_stdout_buffer(timestamp)?;
        Ok(())
    }

    pub(crate) fn dump_stdout_buffer(&self, timestamp: i64) -> PyResult<()> {
        let dir = "buffer_dump";
        std::fs::create_dir_all(dir).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
        let path = format!("{}/stdout_buffer_{}.txt", dir, timestamp);
        let mut f = std::fs::File::create(&path).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
        let _ = write!(f, "Stdout Buffer Output (timestamp: {}):\n", timestamp);
        let _ = f.write_all(b"Last Rendered ANSI Output:\n");
        let _ = f.write_all(b"================\n");
        if self.last_rendered_output.is_empty() {
            let _ = f.write_all(b"(no output rendered yet)\n");
        } else {
            let _ = f.write_all(self.last_rendered_output.as_bytes());
        }
        let _ = f.write_all(b"\n================\n");
        let _ = write!(f, "Buffer size: {} bytes\n", self.last_rendered_output.len());
        f.flush().map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
        Ok(())
    }

    fn dump_single_buffer(&self, py: Python<'_>, buffer: Py<Buffer>, buffer_name: &str, timestamp: i64) -> PyResult<()> {
        let dir = "buffer_dump";
        std::fs::create_dir_all(dir).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
        let path = format!("{}/{}_buffer_{}.txt", dir, buffer_name, timestamp);
        let mut f = std::fs::File::create(&path).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
        let guard = buffer.as_ref(py).borrow();
        let _ = write!(f, "{} Buffer ({}x{}):\n", buffer_name, self.width, self.height);
        let _ = f.write_all(b"Characters:\n");
        for y in 0..self.height {
            for x in 0..self.width {
                let ch = guard.get_cell(x, y).map(|c| c.char.chars().next().unwrap_or(' ')).unwrap_or(' ');
                let _ = write!(f, "{}", ch);
            }
            let _ = f.write_all(b"\n");
        }
        f.flush().map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
        Ok(())
    }
}

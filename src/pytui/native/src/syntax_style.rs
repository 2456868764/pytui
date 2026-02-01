//! Syntax style definitions (theme). Aligns OpenTUI syntax-style.zig.
//! RGBA from utils; no EventEmitter in minimal version.

#![allow(dead_code)]

use std::collections::HashMap;

/// RGBA color for style. Aligns OpenTUI StyleDefinition fg/bg.
pub type Rgba = [f32; 4];

/// Style definition. Aligns OpenTUI syntax-style.zig StyleDefinition.
#[derive(Clone, Debug, PartialEq)]
pub struct StyleDefinition {
    pub fg: Option<Rgba>,
    pub bg: Option<Rgba>,
    pub attributes: u32,
}

/// Syntax style registry (name -> id -> definition). Aligns OpenTUI SyntaxStyle.
pub struct SyntaxStyle {
    name_to_id: HashMap<String, u32>,
    id_to_style: HashMap<u32, StyleDefinition>,
    next_id: u32,
}

impl SyntaxStyle {
    pub fn new() -> Self {
        SyntaxStyle {
            name_to_id: HashMap::new(),
            id_to_style: HashMap::new(),
            next_id: 1,
        }
    }

    /// Register or update style by name. Returns style id.
    pub fn register_style(
        &mut self,
        name: &str,
        fg: Option<Rgba>,
        bg: Option<Rgba>,
        attributes: u32,
    ) -> u32 {
        let def = StyleDefinition {
            fg,
            bg,
            attributes,
        };
        if let Some(&id) = self.name_to_id.get(name) {
            self.id_to_style.insert(id, def);
            return id;
        }
        let id = self.next_id;
        self.next_id += 1;
        self.name_to_id.insert(name.to_string(), id);
        self.id_to_style.insert(id, def);
        id
    }

    pub fn resolve_by_id(&self, id: u32) -> Option<StyleDefinition> {
        self.id_to_style.get(&id).cloned()
    }

    pub fn resolve_by_name(&self, name: &str) -> Option<u32> {
        self.name_to_id.get(name).copied()
    }

    pub fn get_style_by_name(&self, name: &str) -> Option<StyleDefinition> {
        let id = self.resolve_by_name(name)?;
        self.resolve_by_id(id)
    }

    /// Merge multiple styles (later fg/bg override; attributes OR'd). Aligns Zig mergeStyles.
    pub fn merge_styles(&self, ids: &[u32]) -> StyleDefinition {
        let mut merged = StyleDefinition {
            fg: None,
            bg: None,
            attributes: 0,
        };
        for &id in ids {
            if let Some(s) = self.resolve_by_id(id) {
                if s.fg.is_some() {
                    merged.fg = s.fg;
                }
                if s.bg.is_some() {
                    merged.bg = s.bg;
                }
                merged.attributes |= s.attributes;
            }
        }
        merged
    }

    pub fn get_style_count(&self) -> usize {
        self.id_to_style.len()
    }
}

impl Default for SyntaxStyle {
    fn default() -> Self {
        Self::new()
    }
}

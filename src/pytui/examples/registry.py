# Registry of example demos. Aligns with opentui/packages/core/src/examples/index.ts.
# See docs/examples-implementation-plan.md for implementation plan and steps.

from __future__ import annotations

from typing import Callable

# (run, destroy, description); run/destroy receive renderer; None = not implemented / N/A
ExampleEntry = tuple[Callable | None, Callable | None, str]

try:
    from pytui.examples.simple_layout_example import destroy as _simple_layout_destroy, run as _simple_layout_run
except ImportError:
    _simple_layout_run = None  # type: ignore[misc, assignment]
    _simple_layout_destroy = None  # type: ignore[misc, assignment]

try:
    from pytui.examples.input_demo import destroy as _input_demo_destroy, run as _input_demo_run
except ImportError:
    _input_demo_run = None  # type: ignore[misc, assignment]
    _input_demo_destroy = None  # type: ignore[misc, assignment]

try:
    from pytui.examples.input_select_layout_demo import destroy as _input_select_destroy, run as _input_select_run
except ImportError:
    _input_select_run = None  # type: ignore[misc, assignment]
    _input_select_destroy = None  # type: ignore[misc, assignment]

try:
    from pytui.examples.select_demo import destroy as _select_demo_destroy, run as _select_demo_run
except ImportError:
    _select_demo_run = None  # type: ignore[misc, assignment]
    _select_demo_destroy = None  # type: ignore[misc, assignment]

try:
    from pytui.examples.tab_select_demo import destroy as _tab_select_demo_destroy, run as _tab_select_demo_run
except ImportError:
    _tab_select_demo_run = None  # type: ignore[misc, assignment]
    _tab_select_demo_destroy = None  # type: ignore[misc, assignment]

try:
    from pytui.examples.key_input_demo import destroy as _key_input_demo_destroy, run as _key_input_demo_run
except ImportError:
    _key_input_demo_run = None  # type: ignore[misc, assignment]
    _key_input_demo_destroy = None  # type: ignore[misc, assignment]

try:
    from pytui.examples.slider_demo import destroy as _slider_demo_destroy, run as _slider_demo_run
except ImportError:
    _slider_demo_run = None  # type: ignore[misc, assignment]
    _slider_demo_destroy = None  # type: ignore[misc, assignment]

try:
    from pytui.examples.styled_text_demo import destroy as _styled_text_demo_destroy, run as _styled_text_demo_run
except ImportError:
    _styled_text_demo_run = None  # type: ignore[misc, assignment]
    _styled_text_demo_destroy = None  # type: ignore[misc, assignment]

EXAMPLES: dict[str, ExampleEntry] = {
    # Phase 1 - Layout & basic controls
    "simple-layout": (_simple_layout_run, _simple_layout_destroy, "Flex layout: horizontal/vertical/centered/three-column"),
    "input-demo": (_input_demo_run, _input_demo_destroy, "Multiple inputs, Tab navigation, validation"),
    "input-select-layout": (_input_select_run, _input_select_destroy, "Input + Select layout together"),
    "select-demo": (_select_demo_run, _select_demo_destroy, "Select list with keyboard nav and descriptions"),
    "tab-select-demo": (_tab_select_demo_run, _tab_select_demo_destroy, "Tab selection with arrows and descriptions"),
    "slider-demo": (_slider_demo_run, _slider_demo_destroy, "Horizontal/vertical sliders with value display"),
    "styled-text-demo": (_styled_text_demo_run, _styled_text_demo_destroy, "Styled text with colors and formatting"),
    # Phase 2 - Text & highlighting
    "text-node-demo": (None, None, "TextNode API for complex styled text"),
    "text-wrap": (None, None, "Text wrapping and resizable content"),
    "link-demo": (None, None, "OSC 8 hyperlinks (when terminal supports)"),
    "extmarks-demo": (None, None, "Virtual extmarks and cursor skip ranges"),
    "opacity-example": (None, None, "Box opacity and animated transitions"),
    "code-demo": (None, None, "Code viewer with line numbers and syntax highlight"),
    "diff-demo": (None, None, "Unified/split diff with syntax highlight"),
    "hast-syntax-highlighting-demo": (None, None, "HAST to syntax-highlighted chunks"),
    "editor-demo": (None, None, "Full text editor with Textarea"),
    # Phase 3 - Interaction & scroll
    "console-demo": (None, None, "Interactive console with clickable log levels"),
    "mouse-interaction-demo": (None, None, "Mouse trails and clickable cells"),
    "text-selection-demo": (None, None, "Text selection across renderables"),
    "ascii-font-selection-demo": (None, None, "ASCII font character-level selection"),
    "scroll-example": (None, None, "ScrollBox with Box/ASCIIFont children"),
    "sticky-scroll-example": (None, None, "Sticky scroll at content edges"),
    "nested-zindex-demo": (None, None, "Nested z-index behavior"),
    "relative-positioning-demo": (None, None, "Child positions relative to parent"),
    "transparency-demo": (None, None, "Alpha blending and transparency"),
    # Phase 4 - Composition & system
    "vnode-composition-demo": (None, None, "Box(Box(Box(children))) composition"),
    "full-unicode-demo": (None, None, "Complex graphemes and draggable boxes"),
    "live-state-demo": (None, None, "Live renderable lifecycle"),
    "opentui-demo": (None, None, "Multi-tab combined demo"),
    "ascii-font-demo": (None, None, "ASCII fonts with various colors"),
    "terminal-palette-demo": (None, None, "256-color palette detection"),
    "key-input-demo": (_key_input_demo_run, _key_input_demo_destroy, "Key input debug: press keys to see parsed output"),
    "keypress-debug-demo": (_key_input_demo_run, _key_input_demo_destroy, "Keypress event debug tool (same as key-input-demo)"),
    "split-mode-demo": (None, None, "Renderer confined to bottom area (experimental)"),
    "timeline-example": (None, None, "Timeline animation and sync"),
    # N/A - GPU/Physics (placeholder only)
    "golden-star-demo": (None, None, "N/A (GPU): 3D golden star + particles"),
    "fractal-shader-demo": (None, None, "N/A (GPU): Fractal shader"),
    "shader-cube-demo": (None, None, "N/A (GPU): 3D shader cube"),
    "lights-phong-demo": (None, None, "N/A (GPU): Phong lighting"),
    "physx-planck-2d-demo": (None, None, "N/A (Physics): Planck 2D"),
    "physx-rapier-2d-demo": (None, None, "N/A (Physics): Rapier 2D"),
    "static-sprite-demo": (None, None, "N/A (GPU): Static sprite"),
    "sprite-animation-demo": (None, None, "N/A (GPU): Sprite animation"),
    "sprite-particle-generator-demo": (None, None, "N/A (GPU): Particle sprites"),
    "framebuffer-demo": (None, None, "N/A (GPU): Framebuffer"),
    "texture-loading-demo": (None, None, "N/A (GPU): Texture loading"),
}


def get_example_names() -> list[str]:
    return list(EXAMPLES.keys())


def run_example(name: str, renderer) -> bool:
    """Run example by name. Returns True if an implementation ran, False if N/A or not found."""
    entry = EXAMPLES.get(name)
    if not entry:
        return False
    run, _destroy, _desc = entry
    if run is None:
        return False
    run(renderer)
    return True


def destroy_example(name: str, renderer) -> None:
    entry = EXAMPLES.get(name)
    if not entry:
        return
    _run, destroy, _desc = entry
    if destroy is not None:
        destroy(renderer)

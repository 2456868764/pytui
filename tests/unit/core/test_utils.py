# tests/unit/core/test_utils.py - Aligns with OpenTUI core/utils.ts
"""core.utils 单元测试：create_text_attributes, attributes_with_link, get_link_id, visualize_renderable_tree."""

import pytest

pytest.importorskip("pytui.core.utils")


class TestCreateTextAttributes:
    def test_empty_defaults_to_none(self):
        from pytui.core.utils import create_text_attributes
        from pytui.core.types import TextAttributes

        assert create_text_attributes() == TextAttributes.NONE

    def test_bold(self):
        from pytui.core.utils import create_text_attributes
        from pytui.core.types import TextAttributes

        assert create_text_attributes(bold=True) == TextAttributes.BOLD

    def test_combined_attributes(self):
        from pytui.core.utils import create_text_attributes
        from pytui.core.types import TextAttributes

        attrs = create_text_attributes(bold=True, italic=True, underline=True)
        assert (attrs & TextAttributes.BOLD) == TextAttributes.BOLD
        assert (attrs & TextAttributes.ITALIC) == TextAttributes.ITALIC
        assert (attrs & TextAttributes.UNDERLINE) == TextAttributes.UNDERLINE

    def test_all_attributes(self):
        from pytui.core.utils import create_text_attributes
        from pytui.core.types import TextAttributes

        attrs = create_text_attributes(
            bold=True,
            italic=True,
            underline=True,
            dim=True,
            blink=True,
            inverse=True,
            hidden=True,
            strikethrough=True,
        )
        assert (attrs & TextAttributes.BOLD) != 0
        assert (attrs & TextAttributes.ITALIC) != 0
        assert (attrs & TextAttributes.UNDERLINE) != 0
        assert (attrs & TextAttributes.DIM) != 0
        assert (attrs & TextAttributes.BLINK) != 0
        assert (attrs & TextAttributes.INVERSE) != 0
        assert (attrs & TextAttributes.HIDDEN) != 0
        assert (attrs & TextAttributes.STRIKETHROUGH) != 0


class TestAttributesWithLink:
    def test_base_only(self):
        from pytui.core.utils import ATTRIBUTE_BASE_MASK, attributes_with_link, get_link_id

        base = 1  # BOLD
        out = attributes_with_link(base, 0)
        assert (out & ATTRIBUTE_BASE_MASK) == base
        assert get_link_id(out) == 0

    def test_link_id_encoded(self):
        from pytui.core.utils import get_link_id, attributes_with_link

        base = 2
        link_id = 100
        out = attributes_with_link(base, link_id)
        assert get_link_id(out) == 100

    def test_get_link_id_zero_for_no_link(self):
        from pytui.core.utils import get_link_id
        from pytui.core.types import TextAttributes

        assert get_link_id(TextAttributes.BOLD) == 0


class TestVisualizeRenderableTree:
    def test_visualize_renderable_tree_prints(self, mock_context, capsys):
        from pytui.core.renderable import Renderable
        from pytui.core.utils import visualize_renderable_tree

        class DummyRenderable(Renderable):
            def render_self(self, buffer):
                pass

        root = DummyRenderable(mock_context)
        child = DummyRenderable(mock_context)
        root.add(child)
        visualize_renderable_tree(root, max_depth=2)
        out = capsys.readouterr().out
        assert root.id in out
        assert child.id in out

    def test_visualize_max_depth(self, mock_context, capsys):
        from pytui.core.renderable import Renderable
        from pytui.core.utils import visualize_renderable_tree

        class DummyRenderable(Renderable):
            def render_self(self, buffer):
                pass

        root = DummyRenderable(mock_context)
        visualize_renderable_tree(root, max_depth=0)
        out = capsys.readouterr().out
        assert "max depth reached" in out

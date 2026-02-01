# tests/unit/components/test_text_node.py

import pytest

pytest.importorskip("pytui.components.text_node")


class TestTextNode:
    def test_plain_content(self, mock_context, buffer_40x20):
        from pytui.components.text_node import TextNode

        node = TextNode(mock_context, {"content": "hi", "width": 10, "height": 1})
        node.x, node.y, node.width, node.height = 0, 0, 10, 1
        node.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "h"
        assert buffer_40x20.get_cell(1, 0).char == "i"

    def test_spans_bold_italic(self, mock_context, buffer_40x20):
        from pytui.components.text_node import TextNode, bold, italic

        node = TextNode(
            mock_context,
            {
                "spans": [bold("B"), italic("I")],
                "width": 10,
                "height": 1,
            },
        )
        node.x, node.y, node.width, node.height = 0, 0, 10, 1
        node.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "B"
        assert buffer_40x20.get_cell(0, 0).bold is True
        assert buffer_40x20.get_cell(1, 0).char == "I"
        assert buffer_40x20.get_cell(1, 0).italic is True

    def test_line_break(self, mock_context, buffer_40x20):
        from pytui.components.text_node import TextNode, line_break, Span

        node = TextNode(
            mock_context,
            {"spans": [Span("a"), line_break(), Span("b")], "width": 5, "height": 2},
        )
        node.x, node.y, node.width, node.height = 0, 0, 5, 2
        node.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "a"
        assert buffer_40x20.get_cell(0, 1).char == "b"

    def test_link_span(self, mock_context, buffer_40x20):
        from pytui.components.text_node import TextNode, link

        node = TextNode(
            mock_context,
            {"spans": [link("click", "https://x.org")], "width": 10, "height": 1},
        )
        node.x, node.y, node.width, node.height = 0, 0, 10, 1
        node.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "c"
        assert buffer_40x20.get_cell(4, 0).char == "k"

    def test_spans_strikethrough_dim_reverse_blink(self, mock_context, buffer_40x20):
        from pytui.components.text_node import TextNode, blink, dim, reverse, strikethrough

        node = TextNode(
            mock_context,
            {
                "spans": [
                    strikethrough("S"),
                    dim("D"),
                    reverse("R"),
                    blink("B"),
                ],
                "width": 10,
                "height": 1,
            },
        )
        node.x, node.y, node.width, node.height = 0, 0, 10, 1
        node.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "S"
        assert buffer_40x20.get_cell(0, 0).strikethrough is True
        assert buffer_40x20.get_cell(1, 0).char == "D"
        assert buffer_40x20.get_cell(1, 0).dim is True
        assert buffer_40x20.get_cell(2, 0).char == "R"
        assert buffer_40x20.get_cell(2, 0).reverse is True
        assert buffer_40x20.get_cell(3, 0).char == "B"
        assert buffer_40x20.get_cell(3, 0).blink is True

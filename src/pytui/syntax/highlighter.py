# pytui.syntax.highlighter - syntax highlighting (optional tree-sitter)


from __future__ import annotations

from typing import Any

# (text, token_type)
TokenSpan = tuple[str, str]

# tree-sitter 节点 type -> 主题 token 类型
TS_TYPE_TO_TOKEN: dict[str, str] = {
    "keyword": "keyword",
    "string": "string",
    "comment": "comment",
    "number": "number",
    "identifier": "plain",
    "type": "plain",
    "property_identifier": "plain",
    "call": "function",
    "function_definition": "function",
    "method_definition": "function",
    "decorator": "keyword",
    "escape_sequence": "string",
    "true": "keyword",
    "false": "keyword",
    "none": "keyword",
}


def _node_type_to_token(ts_type: str) -> str:
    """将 tree-sitter 节点类型映射到主题 token 类型。"""
    if ts_type in TS_TYPE_TO_TOKEN:
        return TS_TYPE_TO_TOKEN[ts_type]
    if "keyword" in ts_type or ts_type in ("and", "or", "not", "in", "is"):
        return "keyword"
    if "string" in ts_type or "literal" in ts_type:
        return "string"
    if "comment" in ts_type:
        return "comment"
    if "number" in ts_type:
        return "number"
    if "function" in ts_type or "call" in ts_type:
        return "function"
    return "plain"


def highlight(code: str, language: str = "python") -> list[TokenSpan]:
    """将代码按 token 高亮，返回 [(text, token_type), ...]。
    使用 syntax.languages 的 Parser 驱动；无 tree-sitter 或语言不可用时返回整段 plain。
    """
    try:
        from pytui.syntax.languages import get_parser
    except ImportError:
        return [(code, "plain")]

    parser = get_parser(language)
    if parser is None:
        return [(code, "plain")]

    raw = code.encode("utf-8")
    tree = parser.parse(raw)
    if tree is None or tree.root_node is None:
        return [(code, "plain")]

    out: list[TokenSpan] = []
    cursor = 0

    def walk(node: Any) -> None:
        nonlocal cursor
        if node.child_count == 0:
            start = node.start_byte
            end = node.end_byte
            if start > cursor:
                gap = raw[cursor:start].decode("utf-8", errors="replace")
                if gap:
                    out.append((gap, "plain"))
            text = raw[start:end].decode("utf-8", errors="replace")
            if text:
                token_type = _node_type_to_token(node.type or "")
                out.append((text, token_type))
            cursor = end
        else:
            for i in range(node.child_count):
                child = node.child(i)
                if child is not None:
                    walk(child)

    walk(tree.root_node)
    if cursor < len(raw):
        out.append((raw[cursor:].decode("utf-8", errors="replace"), "plain"))
    return out if out else [(code, "plain")]

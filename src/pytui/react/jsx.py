# pytui.react.jsx - create_element (h)、类型映射到 Renderable

from __future__ import annotations

from typing import Any

# 虚拟节点：dict with type, props, children
# type 为 str 时映射到内置组件（text, box, input, select, ...），为 type 时表示自定义 Component
Element = dict[str, Any]
# children 可为 str（文本）或 Element 或 列表
Children = str | Element | list[str | Element] | None


def create_element(
    type_: str | type,
    props: dict[str, Any] | None = None,
    *children: Any,
) -> Element:
    """创建虚拟节点。type_ 为 'text'|'box'|'input'|'select'|... 或 Component 子类。"""
    props = props or {}
    # 展平 children，过滤 None
    flat: list[str | Element] = []
    for c in children:
        if c is None:
            continue
        if isinstance(c, (list, tuple)):
            for x in c:
                if x is None:
                    continue
                if isinstance(x, dict) and "type" in x:
                    flat.append(x)
                else:
                    flat.append(str(x))
        elif isinstance(c, dict) and "type" in c:
            flat.append(c)
        else:
            flat.append(str(c))
    # 单子且为字符串时，常作为 content
    if len(flat) == 1 and isinstance(flat[0], str) and "content" not in props:
        props = {**props, "content": flat[0]}
        flat = []
    elif len(flat) > 1 and all(isinstance(x, str) for x in flat):
        props = {**props, "content": "".join(flat)}
        flat = []
    return {"type": type_, "props": props, "children": flat}


def h(
    type_: str | type,
    props: dict[str, Any] | None = None,
    *children: Any,
) -> Element:
    """create_element 的简写。"""
    return create_element(type_, props, *children)

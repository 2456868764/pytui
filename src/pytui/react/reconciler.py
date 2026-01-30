# pytui.react.reconciler - 树 diff、挂载/更新/卸载

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pytui.components.ascii_font import ASCIIFont
from pytui.components.box import Box
from pytui.components.code import Code
from pytui.components.diff import Diff
from pytui.components.frame_buffer import FrameBuffer
from pytui.components.input import Input
from pytui.components.line_number import LineNumber
from pytui.components.scrollbar import ScrollBar
from pytui.components.scrollbox import Scrollbox
from pytui.components.select import Select
from pytui.components.slider import Slider
from pytui.components.tab_select import TabSelect
from pytui.components.text import Text
from pytui.components.text_node import TextNode
from pytui.core.renderable import Renderable
from pytui.react import hooks as hooks_module
from pytui.react.component import Component

# 内置 type 字符串 -> Renderable 类
TYPE_MAP = {
    "text": Text,
    "text_node": TextNode,
    "ascii_font": ASCIIFont,
    "box": Box,
    "input": Input,
    "select": Select,
    "tab_select": TabSelect,
    "slider": Slider,
    "scrollbar": ScrollBar,
    "scrollbox": Scrollbox,
    "line_number": LineNumber,
    "code": Code,
    "diff": Diff,
    "frame_buffer": FrameBuffer,
}

# 声明式 onXxx：挂载时从 props 剥离并绑定到 Renderable 事件
EVENT_PROPS = ("onInput", "onChange", "onSelect", "onSelectionChanged", "onScroll")


def _bind_event_props(renderable: Renderable, props: dict) -> None:
    """将 props 中的 onXxx 绑定到对应组件的 emit 事件。"""
    event_map = [
        ("onInput", "input"),
        ("onChange", "change"),
        ("onSelect", "select"),
        ("onSelectionChanged", "selection_changed"),
        ("onScroll", "scroll"),
    ]
    for prop_name, event_name in event_map:
        cb = props.get(prop_name)
        if callable(cb):
            renderable.on(event_name, cb)


def _is_component_type(type_: Any) -> bool:
    return isinstance(type_, type) and issubclass(type_, Component)


def _create_host_renderable(ctx: Any, element: dict) -> Renderable:
    type_ = element["type"]
    props = element.get("props") or {}
    cls = TYPE_MAP.get(type_)
    if cls is None:
        raise ValueError(f"Unknown element type: {type_!r}")
    options = {k: v for k, v in props.items() if k not in EVENT_PROPS}
    if "children" in element and element["children"] and isinstance(element["children"][0], str):
        options.setdefault("content", element["children"][0])
    return cls(ctx, options)


def _apply_props(renderable: Renderable, props: dict) -> None:
    """将 props 应用到已有 Renderable（如 Text.set_content）。跳过 onXxx，不覆盖事件绑定。"""
    for k, v in props.items():
        if k in EVENT_PROPS:
            continue
        if hasattr(renderable, f"set_{k}"):
            getattr(renderable, f"set_{k}")(v)
        elif hasattr(renderable, k):
            setattr(renderable, k, v)


def _mount(element: dict, parent: Renderable, index: int | None = None) -> tuple[Any, int]:
    """挂载一个虚拟节点到 parent，返回 (instance, 占用的子节点数)。"""
    type_ = element["type"]
    props = element.get("props") or {}
    children_el = element.get("children") or []

    if _is_component_type(type_):
        comp = type_(parent.ctx, props)
        # 注册更新回调：重渲染该组件的输出
        def on_update() -> None:
            _update_component_output(comp, parent, comp._react_child_insts)

        if comp._on_update is None:
            comp._on_update = []
        comp._on_update.append(on_update)

        prev = hooks_module._current_component
        hooks_module._current_component = comp
        comp._hook_index = 0
        try:
            tree = comp.render()
            # 执行 useEffect（简易：每次 render 后执行）
            for item in getattr(comp, "_effect_list", []) or []:
                if item and item[0]:
                    item[0]()
        finally:
            hooks_module._current_component = prev

        if not isinstance(tree, dict):
            tree = {"type": "box", "props": {}, "children": []}
        if isinstance(tree, list):
            tree = {"type": "box", "props": {}, "children": tree}

        # 挂载整棵 tree（如 box）到 parent，而不是只挂载 tree 的 children
        next_idx = index if index is not None else len(parent.children)
        inst, count = _mount(tree, parent, next_idx)
        child_insts = [(tree, inst)]
        comp._react_child_insts = child_insts
        return (("component", comp, child_insts), count)

    # Host
    r = _create_host_renderable(parent.ctx, element)
    _bind_event_props(r, props)
    next_idx = index if index is not None else len(parent.children)
    parent.add(r, next_idx)
    if props.get("focused") is True and callable(getattr(r, "focus", None)):
        r.focus()

    child_insts: list[tuple[Any, Any]] = []
    for el in children_el:
        if isinstance(el, str):
            continue
        inst, _ = _mount(el, r)
        child_insts.append((el, inst))
    r._react_children = child_insts
    return ((element, r), 1)


def _unmount(inst: Any, parent: Renderable) -> None:
    """从 parent 卸载 instance。"""
    if isinstance(inst, tuple) and len(inst) == 2 and isinstance(inst[1], Renderable):
        # Host: (element, renderable)
        _, r = inst
        if getattr(r, "focused", False) and callable(getattr(r, "blur", None)):
            r.blur()
        for _, c in getattr(r, "_react_children", []):
            _unmount(c, r)
        parent.remove(r)
    elif isinstance(inst, tuple) and len(inst) == 3 and inst[0] == "component":
        _, comp, child_insts = inst
        comp._on_update = []
        for _, c in child_insts:
            _unmount(c, parent)


def _get_renderables(inst: Any) -> list[Renderable]:
    """收集 instance 对应的所有 Renderable（用于从 parent 按顺序移除）。"""
    if isinstance(inst, tuple) and len(inst) == 2 and isinstance(inst[1], Renderable):
        return [inst[1]]
    if isinstance(inst, tuple) and len(inst) == 3 and inst[0] == "component":
        out: list[Renderable] = []
        for _, c in inst[2]:
            out.extend(_get_renderables(c))
        return out
    return []


def _update_component_output(comp: Component, parent: Renderable, old_child_insts: list[tuple[Any, Any]]) -> None:
    """用 comp.render() 的新树替换旧输出。"""
    # 先按树结构卸载旧输出（会调用 blur() 等，避免 keypress 等监听器累积）
    for _, inst in old_child_insts:
        _unmount(inst, parent)

    # 旧输出已从 parent 移除，取当前 children 长度作为挂载起点
    start_idx = len(parent.children)

    prev = hooks_module._current_component
    hooks_module._current_component = comp
    comp._hook_index = 0
    try:
        tree = comp.render()
    finally:
        hooks_module._current_component = prev

    if not isinstance(tree, dict):
        tree = {"type": "box", "props": {}, "children": []}
    # 挂载整棵树（如 box）到 parent，而不是只挂载 tree 的子节点，否则会丢失 Box 导致布局错乱、Input 无尺寸
    inst, cnt = _mount(tree, parent, start_idx)
    comp._react_child_insts = [(tree, inst)]
    if hasattr(parent.ctx, "renderer") and parent.ctx.renderer:
        parent.ctx.renderer.schedule_render()


def reconcile(elements: Any, container: Renderable) -> None:
    """将虚拟节点树挂载/更新到 container。elements 可为单节点或列表。"""
    if elements is None:
        elements = []
    if isinstance(elements, dict):
        elements = [elements]
    old = getattr(container, "_react_children", None) or []
    # 先卸载旧的
    for _, inst in old:
        _unmount(inst, container)
    container._react_children = []
    # 再挂载新的
    idx = 0
    for el in elements:
        if isinstance(el, dict):
            inst, cnt = _mount(el, container, idx)
            container._react_children.append((el, inst))
            idx += cnt


def create_reconciler(ctx: Any) -> Callable[[Any, Renderable], None]:
    """创建绑定 ctx 的 reconcile 函数（可选）。"""
    def reconcile_to_container(elements: Any, container: Renderable) -> None:
        reconcile(elements, container)

    return reconcile_to_container

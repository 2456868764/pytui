# pytui.react.reconciler - 树 diff、挂载/更新/卸载 (aligns OpenTUI host-config + reconciler)

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pytui.core.renderable import Renderable
from pytui.react import hooks as hooks_module
from pytui.react.catalogue import TEXT_NODE_KEYS, get_component_catalogue
from pytui.react.component import Component
from pytui.react.error_boundary import ErrorBoundary
from pytui.react.text_components import TextChunkRenderable
from pytui.react.utils_id import get_next_id

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


def _get_child_host_context(host_context: dict, type_: str) -> dict:
    """Align OpenTUI getChildHostContext: is_inside_text for text and text-node keys."""
    is_inside = host_context.get("is_inside_text", False) or (type_ == "text" or type_ in TEXT_NODE_KEYS)
    return {**host_context, "is_inside_text": is_inside}


def _create_host_renderable(ctx: Any, element: dict, host_context: dict | None = None) -> Renderable:
    """Create host instance from catalogue; enforce text-node keys inside text. Aligns OpenTUI createInstance."""
    host_context = host_context or {}
    type_ = element["type"]
    if type_ in TEXT_NODE_KEYS and not host_context.get("is_inside_text"):
        raise ValueError(f'Component of type "{type_}" must be created inside of a text node')
    props = element.get("props") or {}
    components = get_component_catalogue()
    cls = components.get(type_)
    if cls is None:
        raise ValueError(f"Unknown component type: {type_!r}")
    el_id = get_next_id(type_)
    options = {k: v for k, v in props.items() if k not in EVENT_PROPS}
    options["id"] = el_id
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


def _mount(
    element: dict,
    parent: Renderable,
    index: int | None = None,
    host_context: dict | None = None,
) -> tuple[Any, int]:
    """挂载一个虚拟节点到 parent，返回 (instance, 占用的子节点数)。"""
    host_context = host_context or {"is_inside_text": False}
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
            for item in getattr(comp, "_effect_list", []) or []:
                if item and item[0]:
                    item[0]()
        except Exception as e:
            if isinstance(comp, ErrorBoundary):
                comp.set_error(e)
                tree = comp.render()
            else:
                raise
        finally:
            hooks_module._current_component = prev

        if not isinstance(tree, dict):
            tree = {"type": "box", "props": {}, "children": []}
        if isinstance(tree, list):
            tree = {"type": "box", "props": {}, "children": tree}

        next_idx = index if index is not None else len(parent.children)
        try:
            inst, count = _mount(tree, parent, next_idx, host_context)
        except Exception as e:
            if isinstance(comp, ErrorBoundary):
                comp.set_error(e)
                tree = comp.render()
                if not isinstance(tree, dict):
                    tree = {"type": "box", "props": {}, "children": []}
                if isinstance(tree, list):
                    tree = {"type": "box", "props": {}, "children": tree}
                inst, count = _mount(tree, parent, next_idx, host_context)
            else:
                raise
        child_insts = [(tree, inst)]
        comp._react_child_insts = child_insts
        return (("component", comp, child_insts), count)

    # Host
    r = _create_host_renderable(parent.ctx, element, host_context)
    _bind_event_props(r, props)
    next_idx = index if index is not None else len(parent.children)
    parent.add(r, next_idx)
    if props.get("focused") is True and callable(getattr(r, "focus", None)):
        r.focus()

    child_ctx = _get_child_host_context(host_context, type_)
    child_insts: list[tuple[Any, Any]] = []
    for el in children_el:
        if isinstance(el, str):
            if type_ == "text":
                chunk = TextChunkRenderable(parent.ctx, el)
                r.add(chunk)
                child_insts.append(({"__text": el}, chunk))
            continue
        inst, _ = _mount(el, r, None, child_ctx)
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


def create_root(renderer: Any) -> Any:
    """Create a root for rendering a React tree with the given CLI renderer.
    Aligns OpenTUI createRoot(renderer). Returns object with render(node) and unmount()."""
    from pytui.react.app import set_app_context
    from pytui.react.error_boundary import ErrorBoundary
    from pytui.react.jsx import h

    set_app_context(key_handler=getattr(renderer, "keyboard", None), renderer=renderer)
    root_container = getattr(renderer, "root", None)
    if root_container is None:
        root_container = getattr(renderer, "context", None) and getattr(renderer.context, "root", None)
    if root_container is None:
        raise ValueError("renderer must have .root or .context.root")

    _react_children: list[Any] = []

    def cleanup() -> None:
        nonlocal _react_children
        for _, inst in _react_children:
            _unmount(inst, root_container)
        _react_children = []
        if hasattr(renderer, "schedule_render"):
            renderer.schedule_render()

    def render(node: Any) -> None:
        nonlocal _react_children
        wrapped = h(ErrorBoundary, {"children": node})
        for _, inst in _react_children:
            _unmount(inst, root_container)
        _react_children = []
        inst, _cnt = _mount(wrapped, root_container, None, {"is_inside_text": False})
        _react_children.append((wrapped, inst))
        if hasattr(renderer, "schedule_render"):
            renderer.schedule_render()

    return type("Root", (), {"render": render, "unmount": cleanup})()


def flush_sync(fn: Callable[[], None] | None = None) -> None:
    """Flush synchronous work. Aligns OpenTUI flushSync. No-op in custom reconciler; optional fn()."""
    if fn is not None:
        fn()

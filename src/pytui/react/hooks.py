# pytui.react.hooks - useState, useEffect, useKeyboard, useOnResize, useTerminalDimensions, useTimeline (align OpenTUI hooks)

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

# 当前正在渲染的组件（由 reconciler 在 render 前设置）
_current_component: Any | None = None


def _get_component() -> Any:
    if _current_component is None:
        raise RuntimeError("useState/useEffect must be called during component render")
    return _current_component


def useState(initial: Any) -> tuple[Any, Callable[[Any], None]]:  # noqa: N802
    """useState(initial) -> [value, set_value]。按调用顺序与组件 state 列表对应。
    set_value 支持函数式更新：set_value(lambda prev: new) 可避免闭包陈旧值。"""
    comp = _get_component()
    if not hasattr(comp, "_hook_state_list"):
        comp._hook_state_list = []
    if not hasattr(comp, "_hook_index"):
        comp._hook_index = 0
    idx = comp._hook_index
    comp._hook_index += 1
    if idx >= len(comp._hook_state_list):
        comp._hook_state_list.append(initial)

    value = comp._hook_state_list[idx]

    def set_value(new_val: Any) -> None:
        if callable(new_val):
            comp._hook_state_list[idx] = new_val(comp._hook_state_list[idx])
        else:
            comp._hook_state_list[idx] = new_val
        comp.update()

    return value, set_value


def useEffect(  # noqa: N802
    effect: Callable[[], Callable[[], None] | None],
    deps: list[Any] | None = None,
) -> None:
    """useEffect(effect, deps?)：在 render 提交后执行 effect；deps 变化时重新执行（简易：每次 render 后执行）。"""
    comp = _get_component()
    if not hasattr(comp, "_effect_list"):
        comp._effect_list = []
    if not hasattr(comp, "_hook_index"):
        comp._hook_index = 0
    idx = comp._hook_index
    comp._hook_index += 1
    # 存储 (effect, deps) 供 reconciler 在 commit 阶段执行
    while idx >= len(comp._effect_list):
        comp._effect_list.append(None)
    comp._effect_list[idx] = (effect, deps)


def useRenderer(ctx: Any | None = None) -> Any:  # noqa: N802
    """useRenderer(ctx?) -> renderer. Aligns OpenTUI useRenderer(); uses use_app_context() or ctx when passed (backward compat)."""
    _get_component()
    if ctx is not None:
        return getattr(ctx, "renderer", ctx)
    from pytui.react.app import use_app_context
    app_ctx = use_app_context()
    renderer = app_ctx.get("renderer")
    if renderer is None:
        raise RuntimeError("Renderer not found.")
    return renderer


def useOnResize(callback: Callable[[int, int], None], ctx: Any | None = None) -> Any:  # noqa: N802
    """useOnResize(callback, ctx?) -> subscribe to resize; returns renderer. Aligns OpenTUI useOnResize()."""
    renderer = useRenderer(ctx)
    stable = useEvent(callback)

    def setup() -> None:
        def on_resize(w: int, h: int) -> None:
            stable(w, h)
        renderer.events.on("resize", on_resize)
        def cleanup() -> None:
            renderer.events.remove_listener("resize", on_resize)
        return cleanup
    useEffect(setup, [])
    return renderer


def useTerminalDimensions(ctx: Any | None = None) -> tuple[int, int]:  # noqa: N802
    """useTerminalDimensions(ctx?) -> (width, height). Aligns OpenTUI useTerminalDimensions()."""
    renderer = useRenderer(ctx)
    w, h = renderer.width, renderer.height
    dimensions, set_dimensions = useState({"width": w, "height": h})

    def on_resize(nw: int, nh: int) -> None:
        set_dimensions({"width": nw, "height": nh})
    useOnResize(on_resize, ctx)
    return (dimensions["width"], dimensions["height"])


def useResize(ctx: Any | None = None) -> tuple[int, int]:  # noqa: N802
    """useResize(ctx?) -> (width, height). Subscribes to resize; pass ctx for backward compat. Aligns OpenTUI useOnResize + state."""
    return useTerminalDimensions(ctx)


def useEvent(fn: Callable[..., Any]) -> Callable[..., Any]:  # noqa: N802
    """useEvent(fn) -> 稳定引用的包装函数；每次 render 时 fn 更新为最新闭包，调用时执行最新 fn。
    用于在 useEffect(setup, []) 中注册的 handler，避免闭包陈旧值；调用方无需把 fn 放入 deps。"""
    comp = _get_component()
    if not hasattr(comp, "_useEvent_fns"):
        comp._useEvent_fns = []
    if not hasattr(comp, "_useEvent_wrappers"):
        comp._useEvent_wrappers = []
    if not hasattr(comp, "_hook_index"):
        comp._hook_index = 0
    idx = comp._hook_index
    comp._hook_index += 1
    while idx >= len(comp._useEvent_fns):
        comp._useEvent_fns.append(None)
        comp._useEvent_wrappers.append(None)
    comp._useEvent_fns[idx] = fn
    if comp._useEvent_wrappers[idx] is None:

        def make_wrapper(i: int) -> Callable[..., Any]:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                f = getattr(comp, "_useEvent_fns", [None])[i]
                if f is not None:
                    return f(*args, **kwargs)
                return None

            return wrapper

        comp._useEvent_wrappers[idx] = make_wrapper(idx)
    return comp._useEvent_wrappers[idx]


def useKeyboard(  # noqa: N802
    handler_or_ctx: Callable[[Any], None] | Any = None,
    options: dict[str, Any] | None = None,
) -> Any:
    """useKeyboard(handler, options?) -> subscribe to keypress (and keyrelease if options.release).
    Legacy: useKeyboard(ctx) returns renderer.events. Aligns OpenTUI useKeyboard(handler, { release?: boolean })."""
    _get_component()
    # Backward compat: useKeyboard(ctx) returns events
    if options is None and not callable(handler_or_ctx) and handler_or_ctx is not None:
        renderer = getattr(handler_or_ctx, "renderer", handler_or_ctx)
        return getattr(renderer, "events", renderer)
    handler = handler_or_ctx
    if handler is None:
        raise TypeError("useKeyboard(handler, options?) or useKeyboard(ctx)")
    from pytui.react.app import use_app_context
    options = options or {}
    release = options.get("release", False)
    ctx = use_app_context()
    key_handler = ctx.get("key_handler")
    if key_handler is None and getattr(handler_or_ctx, "renderer", None) is not None:
        key_handler = getattr(handler_or_ctx.renderer, "keyboard", None)
    stable = useEvent(handler)

    def setup() -> None:
        if key_handler is None:
            return
        key_handler.on("keypress", stable)
        if release:
            key_handler.on("keyrelease", stable)
        def cleanup() -> None:
            key_handler.remove_listener("keypress", stable)
            if release:
                key_handler.remove_listener("keyrelease", stable)
        return cleanup
    useEffect(setup, [key_handler, release])


def useTimeline(options: dict[str, Any] | Any | None = None) -> Any:  # noqa: N802
    """useTimeline(options?) -> Timeline. Aligns OpenTUI useTimeline(options); engine.register, play if not autoplay.
    Legacy: useTimeline(ctx) treated as useTimeline({})."""
    from pytui.core.animation import engine
    from pytui.core.animation import Timeline
    opts = options if isinstance(options, dict) else {}
    timeline = Timeline(opts)

    def setup() -> None:
        if not opts.get("autoplay", True):
            timeline.play()
        engine.register(timeline)
        def cleanup() -> None:
            timeline.pause()
            engine.unregister(timeline)
        return cleanup
    useEffect(setup, [])
    return timeline

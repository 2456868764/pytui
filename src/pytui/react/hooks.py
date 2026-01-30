# pytui.react.hooks - useState、useEffect（简易实现）

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


def useRenderer(ctx: Any) -> Any:  # noqa: N802
    """useRenderer(ctx) -> renderer。便捷获取当前渲染器。"""
    _get_component()
    return ctx.renderer


def useResize(ctx: Any) -> tuple[int, int]:  # noqa: N802
    """useResize(ctx) -> (width, height)。随窗口 resize 更新。"""
    _get_component()
    w, h = ctx.renderer.width, ctx.renderer.height
    size, set_size = useState((w, h))

    def setup() -> None:
        def on_resize(nw: int, nh: int) -> None:
            set_size((nw, nh))

        ctx.renderer.events.on("resize", on_resize)

    useEffect(setup, [])
    return size


def useKeyboard(ctx: Any) -> Any:  # noqa: N802
    """useKeyboard(ctx) -> events。用于在 useEffect 中 events.on('keypress', handler)。"""
    _get_component()
    return ctx.renderer.events


def useTimeline(ctx: Any) -> dict[str, Any]:  # noqa: N802
    """useTimeline(ctx) -> { elapsed, pause, resume }。
    每帧更新 elapsed（秒，自挂载起）；pause/resume 可暂停计时。与 core 动画解耦，仅依赖 renderer 的 frame 事件。"""
    comp = _get_component()
    start_time_ref: list[float] = [time.time()]
    paused_ref: list[bool] = [False]
    elapsed, set_elapsed = useState(0.0)

    def setup() -> None:
        if getattr(comp, "_timeline_registered", False):
            return
        comp._timeline_registered = True
        start_time_ref[0] = time.time()

        def on_frame(now: float) -> None:
            if not paused_ref[0]:
                set_elapsed(now - start_time_ref[0])

        ctx.renderer.events.on("frame", on_frame)

    useEffect(setup, [])

    def pause() -> None:
        paused_ref[0] = True

    def resume() -> None:
        paused_ref[0] = False

    return {"elapsed": elapsed, "pause": pause, "resume": resume}

# pytui.react.component - 声明式组件基类

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pytui.core.renderer import RenderContext


class Component:
    """声明式组件基类：props、state、set_state、update() 触发重渲染。"""

    def __init__(self, ctx: RenderContext, props: dict[str, Any] | None = None) -> None:
        self.ctx = ctx
        self.props = props or {}
        self.state: dict[str, Any] = {}
        self._on_update: list[Callable[[], None]] | None = None  # reconciler 注册的回调

    def set_state(self, partial: dict[str, Any] | None = None, *, updater: callable | None = None) -> None:
        """更新 state 并触发重渲染。"""
        if updater is not None:
            self.state = {**self.state, **updater(self.state)}
        elif partial is not None:
            self.state = {**self.state, **partial}
        self.update()

    def update(self) -> None:
        """通知 reconciler 需要重渲染（由 set_state 或外部调用）。"""
        if self._on_update:
            for cb in self._on_update:
                cb()

    def render(self) -> Any:
        """子类实现：返回虚拟节点树（由 create_element / h 构建）。"""
        raise NotImplementedError("Component.render() must be overridden")

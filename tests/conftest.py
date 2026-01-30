# tests/conftest.py
"""共享 pytest fixtures。运行测试前需先安装包: pip install -e ."""

import pytest


@pytest.fixture
def buffer_10x5():
    """10x5 缓冲区，用于渲染测试（纯 Python 模式，不依赖 native）。"""
    try:
        from pytui.core.buffer import OptimizedBuffer
    except ImportError:
        pytest.skip("pytui 未安装，请先执行: pip install -e .")
    return OptimizedBuffer(10, 5, use_native=False)


@pytest.fixture
def buffer_40x20():
    """40x20 缓冲区，用于较大布局测试。"""
    try:
        from pytui.core.buffer import OptimizedBuffer
    except ImportError:
        pytest.skip("pytui 未安装，请先执行: pip install -e .")
    return OptimizedBuffer(40, 20, use_native=False)


@pytest.fixture
def mock_renderer():
    """带固定尺寸的 mock 渲染器。"""
    from unittest.mock import MagicMock
    renderer = MagicMock()
    renderer.width = 40
    renderer.height = 20
    return renderer


@pytest.fixture
def mock_context(mock_renderer):
    """带 mock renderer 的 RenderContext。"""
    try:
        from pytui.core.renderer import RenderContext
    except ImportError:
        pytest.skip("pytui 未安装，请先执行: pip install -e .")
    return RenderContext(renderer=mock_renderer)

# pytui.testing - 无 TTY 测试设施：TestRenderer、Mock 输入、快照

from pytui.testing.mock_keys import create_mock_keys
from pytui.testing.mock_mouse import create_mock_mouse
from pytui.testing.snapshot import assert_buffer_snapshot, buffer_snapshot_lines
from pytui.testing.test_renderer import MockTerminal, create_test_renderer

__all__ = [
    "create_test_renderer",
    "MockTerminal",
    "create_mock_keys",
    "create_mock_mouse",
    "buffer_snapshot_lines",
    "assert_buffer_snapshot",
]

"""nirice 核心基础设施：XDG 路径、子进程封装与配置编辑工具。"""

from nirice.core.backup import backup_file
from nirice.core.paths import XDGPaths
from nirice.core.process import pkill, run, run_capture, run_quiet, which
from nirice.core.toml_edit import format_value, get_key, set_key

__all__ = [
    "XDGPaths",
    "backup_file",
    "run",
    "run_capture",
    "run_quiet",
    "pkill",
    "which",
    "format_value",
    "get_key",
    "set_key",
]

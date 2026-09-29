"""nirice 核心基础设施：XDG 路径、子进程封装与配置编辑工具。"""

from nirice.core.paths import XDGPaths
from nirice.core.process import pkill, run, run_capture, run_quiet, which
from nirice.core.toml_edit import find_section, format_value, get_key, set_key

__all__ = [
    "XDGPaths",
    "run",
    "run_capture",
    "run_quiet",
    "pkill",
    "which",
    "format_value",
    "find_section",
    "get_key",
    "set_key",
]

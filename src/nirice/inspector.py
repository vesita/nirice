"""Niri + Noctalia Wayland 桌面环境诊断器。"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field

from nirice.core import run_capture
from nirice.niri import NiriController
from nirice.noctalia import NoctaliaController
from nirice.terminal import TerminalController


@dataclass
class DesktopReport:
    """Wayland 桌面全要素诊断数据结构。"""

    session_type: str
    compositor_version: str
    compositor_running: bool
    shell_version: str
    shell_running: bool
    bar_position: str
    theme_palette: str
    theme_mode: str
    enabled_templates: list[str] = field(default_factory=list)
    niri_fragments: dict[str, str] = field(default_factory=dict)
    keybind_count: int = 0
    installed_terminals: list[str] = field(default_factory=list)
    starship_installed: bool = False
    fastfetch_installed: bool = False
    kitty_managed_by_noctalia: bool = False
    font_ready: bool = False
    font_detail: str = ""


def _font_status() -> tuple[bool, str]:
    """检查 Nerd Font 可用性。"""
    if not shutil.which("fc-list"):
        return False, "缺少 fontconfig（fc-list）"
    try:
        result = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, check=False)
    except OSError as exc:
        return False, f"字体查询失败: {exc}"
    output = result.stdout.lower()
    if "meslolgs nerd font" in output:
        return True, "MesloLGS Nerd Font 已安装"
    if "nerd font" in output:
        return True, "已检测到通用 Nerd Font"
    return False, "缺少 Nerd Font（Powerline 图标与胶囊提示符需要）"


def _count_keybinds(text: str) -> int:
    """统计 binds 块内的绑定条数。

    niri 的绑定可能是多行块，也可能写成单行 `Mod+X { action; }`，
    因此按 binds 块内部的花括号数量计数，而不是按行尾字符。
    """
    if "binds {" not in text:
        return 0
    body = text.split("binds {", 1)[1]
    body = body.rsplit("}", 1)[0] if "}" in body else body
    return body.count("{")


class DesktopInspector:
    """诊断 Niri 合成器、Noctalia 外壳与终端生态的当前状态。"""

    def __init__(
        self,
        niri: NiriController | None = None,
        noctalia: NoctaliaController | None = None,
        terminal: TerminalController | None = None,
    ) -> None:
        self.niri = niri or NiriController()
        self.noctalia = noctalia or NoctaliaController()
        self.term = terminal or TerminalController(noctalia=self.noctalia)

    def _noctalia_version(self) -> str:
        if not self.noctalia.noctalia_bin:
            return "未安装"
        ok, out = run_capture([self.noctalia.noctalia_bin, "--version"], timeout=5)
        if not ok or not out:
            return "未知版本"
        return out.splitlines()[0]

    def inspect(self) -> DesktopReport:
        """执行全方位诊断并返回结构化报告。"""
        font_ok, font_detail = _font_status()
        fragments = self.niri.diff_fragments()
        keybinds = self.niri.read_fragment("keybinds.kdl") or ""
        keybind_count = _count_keybinds(keybinds)

        detected = self.term.detect_installed_terminals()
        # 「已安装」以二进制为准：只剩配置目录的（例如卸载后残留的 alacritty）不算装了。
        # detect_installed_terminals 连配置目录一起算，是为了决定「要不要写配置」，语义不同。
        installed = [
            key.capitalize()
            for key in detected
            if key not in ("starship", "fastfetch") and shutil.which(key)
        ]

        enabled_templates = self.noctalia.get_enabled_templates()
        palette, mode = self.noctalia.get_theme()

        return DesktopReport(
            session_type=os.environ.get("XDG_SESSION_TYPE", "未知").upper(),
            compositor_version=self.niri.get_version(),
            compositor_running=self.niri.is_running(),
            shell_version=self._noctalia_version(),
            shell_running=self.noctalia.is_running(),
            bar_position=self.noctalia.get_bar_position(),
            theme_palette=palette,
            theme_mode=mode,
            enabled_templates=enabled_templates,
            niri_fragments=fragments,
            keybind_count=keybind_count,
            installed_terminals=installed,
            starship_installed=detected.get("starship", False),
            fastfetch_installed=detected.get("fastfetch", False),
            kitty_managed_by_noctalia="kitty" in enabled_templates,
            font_ready=font_ok,
            font_detail=font_detail,
        )

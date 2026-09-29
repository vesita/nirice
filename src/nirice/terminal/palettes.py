"""Built-in high-quality terminal color palettes for nirice."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TerminalPalette:
    """Represents a 16-color ANSI terminal color palette plus UI/cursor/selection colors."""

    name: str
    display_name: str
    background: str
    foreground: str
    dim_foreground: str = ""
    bright_foreground: str = ""
    cursor: str = ""
    cursor_text: str = ""
    selection_bg: str = ""
    selection_fg: str = ""

    # Normal ANSI colors (0-7)
    black: str = "#000000"
    red: str = "#ff0000"
    green: str = "#00ff00"
    yellow: str = "#ffff00"
    blue: str = "#0000ff"
    magenta: str = "#ff00ff"
    cyan: str = "#00ffff"
    white: str = "#ffffff"

    # Bright ANSI colors (8-15)
    bright_black: str = "#555555"
    bright_red: str = "#ff5555"
    bright_green: str = "#55ff55"
    bright_yellow: str = "#ffff55"
    bright_blue: str = "#5555ff"
    bright_magenta: str = "#ff55ff"
    bright_cyan: str = "#55ffff"
    bright_white: str = "#ffffff"

    is_dark: bool = True

    def __post_init__(self) -> None:
        if not self.dim_foreground:
            self.dim_foreground = self.bright_black
        if not self.bright_foreground:
            self.bright_foreground = self.foreground
        if not self.cursor:
            self.cursor = self.cyan if self.is_dark else self.blue
        if not self.cursor_text:
            self.cursor_text = self.background
        if not self.selection_bg:
            self.selection_bg = self.bright_black if self.is_dark else self.bright_white
        if not self.selection_fg:
            self.selection_fg = self.foreground

    def to_ansi_list(self) -> list[str]:
        """Returns 16 ANSI colors in order (0 to 15)."""
        return [
            self.black,
            self.red,
            self.green,
            self.yellow,
            self.blue,
            self.magenta,
            self.cyan,
            self.white,
            self.bright_black,
            self.bright_red,
            self.bright_green,
            self.bright_yellow,
            self.bright_blue,
            self.bright_magenta,
            self.bright_cyan,
            self.bright_white,
        ]


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """将十六进制颜色值 (#RRGGBB 或 #RGB) 转换为 (R, G, B) 整数元组。

    非法输入（长度不符或含非十六进制字符）一律返回 (0, 0, 0)，不抛异常。
    """
    clean = hex_color.lstrip("#")
    if len(clean) == 3:
        clean = "".join(ch * 2 for ch in clean)
    if len(clean) != 6:
        return (0, 0, 0)
    try:
        return (int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16))
    except ValueError:
        return (0, 0, 0)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """将 (R, G, B) 转换为 #RRGGBB 字符串。"""
    return f"#{r:02X}{g:02X}{b:02X}"

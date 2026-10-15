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

"""终端与 Shell 支持：调色板、Kitty 主题、提示符与各终端后端。"""

from nirice.terminal.catalog import DEFAULT_PALETTE, TERMINAL_PALETTES
from nirice.terminal.controller import TerminalController
from nirice.terminal.palettes import TerminalPalette

__all__ = [
    "TerminalController",
    "TerminalPalette",
    "TERMINAL_PALETTES",
    "DEFAULT_PALETTE",
]

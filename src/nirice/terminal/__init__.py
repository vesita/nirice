"""终端与 Shell 支持：调色板、Kitty 主题、提示符与各终端后端。"""

from nirice.terminal.catalog import TERMINAL_PALETTES
from nirice.terminal.controller import TerminalController
from nirice.terminal.palettes import TerminalPalette, hex_to_rgb, rgb_to_hex

__all__ = [
    "TerminalController",
    "TerminalPalette",
    "TERMINAL_PALETTES",
    "hex_to_rgb",
    "rgb_to_hex",
]

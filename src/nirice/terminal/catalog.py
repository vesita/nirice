"""终端调色板注册表（聚合浅色与暗色定义）。"""

from __future__ import annotations

from nirice.terminal.palettes import TerminalPalette
from nirice.terminal.palettes_dark import (
    CACHY_NORD,
    CATPPUCCIN_MOCHA,
    DRACULA,
    ORCHIS_DARK,
    TOKYO_NIGHT,
)
from nirice.terminal.palettes_extra import (
    EMERALD_DARK,
    GRUVBOX_DARK,
    GRUVBOX_LIGHT,
    ONE_DARK,
    ONE_LIGHT,
    ROSE_PINE,
    SOLARIZED_DARK,
    SOLARIZED_LIGHT,
)
from nirice.terminal.palettes_light import (
    CATPPUCCIN_LATTE,
    CYAN_LIGHT,
    NORD_LIGHT,
    ORCHIS_LIGHT,
)

TERMINAL_PALETTES: dict[str, TerminalPalette] = {
    "cachy-nord": CACHY_NORD,
    "nord-dark": CACHY_NORD,
    "nord-light": NORD_LIGHT,
    "cyan-light": CYAN_LIGHT,
    "cachy-cyan-light": CYAN_LIGHT,
    "catppuccin-mocha": CATPPUCCIN_MOCHA,
    "catppuccin-latte": CATPPUCCIN_LATTE,
    "tokyo-night": TOKYO_NIGHT,
    "dracula": DRACULA,
    "gruvbox-dark": GRUVBOX_DARK,
    "gruvbox-light": GRUVBOX_LIGHT,
    "rose-pine": ROSE_PINE,
    "orchis-dark": ORCHIS_DARK,
    "orchis-light": ORCHIS_LIGHT,
    "emerald-dark": EMERALD_DARK,
    "one-dark": ONE_DARK,
    "one-light": ONE_LIGHT,
    "solarized-dark": SOLARIZED_DARK,
    "solarized-light": SOLARIZED_LIGHT,
}

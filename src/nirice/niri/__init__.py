"""Niri 合成器支持：配置片段、快捷键、动效方案与控制器。"""

from nirice.niri.animations import ANIMATION_PRESETS
from nirice.niri.catalog import MANAGED_FRAGMENTS
from nirice.niri.controller import FragmentResult, NiriController
from nirice.niri.fragments import CONFIG_KDL, DISPLAY_KDL
from nirice.niri.keybinds import KEYBINDS_KDL

__all__ = [
    "NiriController",
    "FragmentResult",
    "ANIMATION_PRESETS",
    "KEYBINDS_KDL",
    "CONFIG_KDL",
    "DISPLAY_KDL",
    "MANAGED_FRAGMENTS",
]

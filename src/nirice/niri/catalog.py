"""Niri 受管配置片段的聚合清单。

把「片段内容定义」（animations / keybinds / fragments）与「受管清单」分离，
避免内容模块之间互相引用。
"""

from __future__ import annotations

from nirice.niri.animations import ARCTIC_ANIMATIONS
from nirice.niri.fragments import (
    AUTOSTART_KDL,
    CONFIG_KDL,
    DISPLAY_KDL,
    INPUT_KDL,
    LAYOUT_KDL,
    MISC_KDL,
    RULES_KDL,
)
from nirice.niri.keybinds import KEYBINDS_KDL

# 由 nirice 接管的 cfg/*.kdl 清单：文件名 -> 内容
MANAGED_FRAGMENTS: dict[str, str] = {
    "animation.kdl": ARCTIC_ANIMATIONS,
    "autostart.kdl": AUTOSTART_KDL,
    "keybinds.kdl": KEYBINDS_KDL,
    "input.kdl": INPUT_KDL,
    "layout.kdl": LAYOUT_KDL,
    "rules.kdl": RULES_KDL,
    "misc.kdl": MISC_KDL,
}

__all__ = [
    "MANAGED_FRAGMENTS",
    "ARCTIC_ANIMATIONS",
    "KEYBINDS_KDL",
    "CONFIG_KDL",
    "DISPLAY_KDL",
    "AUTOSTART_KDL",
    "INPUT_KDL",
    "LAYOUT_KDL",
    "RULES_KDL",
    "MISC_KDL",
]

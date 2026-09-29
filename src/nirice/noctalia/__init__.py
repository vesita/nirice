"""Noctalia 桌面外壳支持：状态栏、主题与模板渲染。"""

from nirice.noctalia.controller import NoctaliaController
from nirice.noctalia.templates import (
    BAR_POSITIONS,
    PANEL_IDS,
    RENDERED_ARTIFACTS,
    TEMPLATE_FOR_APP,
    THEME_MODES,
)

__all__ = [
    "NoctaliaController",
    "BAR_POSITIONS",
    "THEME_MODES",
    "PANEL_IDS",
    "TEMPLATE_FOR_APP",
    "RENDERED_ARTIFACTS",
]

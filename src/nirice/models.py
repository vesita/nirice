"""nirice / nirice 的跨领域数据模型。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AnimationPreset:
    """Niri 合成器动效方案（承载 `animations { ... }` 的 KDL 片段）。"""

    name: str
    description: str
    animations_kdl: str
    notes: list[str] = field(default_factory=list)


@dataclass
class RicePreset:
    """整合式桌面美化方案：Niri 动效 + Noctalia 外壳主题 + 终端回退调色板。"""

    name: str
    description: str
    is_dark: bool = True
    noctalia_palette: str | None = None
    noctalia_mode: str | None = None
    animation_preset: str = "arctic"
    terminal_palette: str | None = None
    notes: list[str] = field(default_factory=list)

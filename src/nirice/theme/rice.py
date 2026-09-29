"""整合式 Rice 预设：Niri 动效 + Noctalia 外壳主题 + 终端回退调色板。

注意：终端配色默认交给 Noctalia 模板自动生成，
`terminal_palette` 仅在 Noctalia 不可用时作为回退。
"""

from __future__ import annotations

from nirice.models import RicePreset

CACHY_NORD_LIGHT = RicePreset(
    name="CachyOS Nord Glacier Light",
    description="CachyOS + Noctalia 默认的 Nord 雪暴浅色（冰青强调色 + 磨砂毛玻璃）",
    is_dark=False,
    noctalia_palette="Nord",
    noctalia_mode="light",
    animation_preset="arctic",
    terminal_palette="nord-light",
    notes=[
        "配色由 Noctalia 模板统一渲染到 kitty / starship / niri / GTK / Qt，主题切换全生态联动。",
        "Kitty 显式使用 MesloLGS Nerd Font，规避 CJK 字体导致的 ASCII 双倍字距。",
        "背景模糊由 Niri 合成器完成，Kitty 只负责 0.78 透明度。",
    ],
)

CACHY_NORD_DARK = RicePreset(
    name="CachyOS Arctic Nord Dark",
    description="北极光深邃暗色（Nord Polar Night + Frost 强调色）",
    is_dark=True,
    noctalia_palette="Nord",
    noctalia_mode="dark",
    animation_preset="arctic",
    terminal_palette="cachy-nord",
    notes=["经典的 Nord 暗色，长时间编码护眼。"],
)

CATPPUCCIN_LATTE = RicePreset(
    name="Catppuccin Latte",
    description="柔和奶油浅色，暖白底色搭配粉彩强调色",
    is_dark=False,
    noctalia_palette="Catppuccin Latte",
    noctalia_mode="light",
    animation_preset="arctic",
    terminal_palette="catppuccin-latte",
    notes=["低对比度护眼浅色，适合明亮环境。"],
)

CATPPUCCIN_MOCHA = RicePreset(
    name="Catppuccin Mocha",
    description="经典摩卡粉彩暗色",
    is_dark=True,
    noctalia_palette="Catppuccin Mocha",
    noctalia_mode="dark",
    animation_preset="arctic",
    terminal_palette="catppuccin-mocha",
    notes=["最流行的柔和暗色配色。"],
)

TOKYO_NIGHT = RicePreset(
    name="Tokyo Night",
    description="东京之夜霓虹暗色，深蓝底 + 荧光青",
    is_dark=True,
    noctalia_palette="Tokyo Night",
    noctalia_mode="dark",
    animation_preset="snappy",
    terminal_palette="tokyo-night",
    notes=["高对比霓虹风，搭配更快的动效更利落。"],
)

GRUVBOX_DARK = RicePreset(
    name="Gruvbox Dark",
    description="复古暖调暗色，温润不刺眼",
    is_dark=True,
    noctalia_palette="Gruvbox",
    noctalia_mode="dark",
    animation_preset="arctic",
    terminal_palette="gruvbox-dark",
    notes=["复古配色，适合长时间阅读。"],
)

DRACULA = RicePreset(
    name="Dracula",
    description="经典暗夜紫与粉色高亮",
    is_dark=True,
    noctalia_palette="Dracula",
    noctalia_mode="dark",
    animation_preset="arctic",
    terminal_palette="dracula",
    notes=["高对比冷峻紫色系。"],
)

ONE_LIGHT = RicePreset(
    name="Atom One Light",
    description="清爽明亮的 Atom One 浅色",
    is_dark=False,
    noctalia_palette="Atom One Light",
    noctalia_mode="light",
    animation_preset="arctic",
    terminal_palette="one-light",
    notes=["中性浅色，适合与浅色壁纸搭配。"],
)

RICE_PRESETS: dict[str, RicePreset] = {
    "nord-light": CACHY_NORD_LIGHT,
    "cachy-nord-light": CACHY_NORD_LIGHT,
    "cachy-nord": CACHY_NORD_DARK,
    "nord-dark": CACHY_NORD_DARK,
    "catppuccin-latte": CATPPUCCIN_LATTE,
    "catppuccin-mocha": CATPPUCCIN_MOCHA,
    "tokyo-night": TOKYO_NIGHT,
    "gruvbox-dark": GRUVBOX_DARK,
    "dracula": DRACULA,
    "one-light": ONE_LIGHT,
}

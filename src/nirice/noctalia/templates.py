"""Noctalia 的常量定义：状态栏位置、主题模式、面板 ID 与模板映射。"""

from __future__ import annotations

BAR_POSITIONS = ("top", "bottom", "left", "right")
THEME_MODES = ("dark", "light")

# Noctalia 的 bar 是命名 bar：真正的配置小节是 [bar.<name>]，
# 顶层 [bar] 只承载 order = [...]。默认 bar 名为 default。
DEFAULT_BAR_NAME = "default"

# `noctalia msg panel-toggle <id>` 实际支持的面板
PANEL_IDS = (
    "launcher",
    "control-center",
    "wallpaper",
    "session",
    "clipboard",
    "tray-drawer",
    "polkit",
)

# 软件 -> Noctalia 内置模板 id
TEMPLATE_FOR_APP: dict[str, str] = {
    "kitty": "kitty",
    "alacritty": "alacritty",
    "ghostty": "ghostty",
    "foot": "foot",
    "wezterm": "wezterm",
    "starship": "starship",
    "niri": "niri",
    "gtk3": "gtk3",
    "gtk4": "gtk4",
    "qt": "qt",
    "btop": "btop",
    "cava": "cava",
}

# 官方模板清单文件（模板 id 的权威来源）
BUILTIN_MANIFEST = "/usr/share/noctalia/assets/templates/builtin.toml"

# 由 Noctalia 渲染的产物路径，用于验证
RENDERED_ARTIFACTS: dict[str, str] = {
    "niri": "~/.config/niri/noctalia.kdl",
    "kitty": "~/.config/kitty/themes/noctalia.conf",
    "alacritty": "~/.config/alacritty/themes/noctalia.toml",
    "gtk3": "~/.config/gtk-3.0/noctalia.css",
    "gtk4": "~/.config/gtk-4.0/noctalia.css",
    "starship": "~/.config/starship.toml",
}

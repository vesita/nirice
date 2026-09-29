"""根据调色板动态生成 Shell 提示符 (Starship) 与系统硬件信息看板 (Fastfetch) 配置模板。"""

from __future__ import annotations

import json
from dataclasses import dataclass

from nirice.terminal.palettes import TerminalPalette


@dataclass(frozen=True)
class LanguageCapsuleSpec:
    """软件 / 编程语言胶囊配置元数据。"""

    module: str
    symbol: str
    brand_color: str
    icon_fg: str = "#FFFFFF"
    light_bg: str | None = None
    light_fg: str | None = None
    var_template: str = "$version"


# 官方品牌原生配色注册表 (Brand-Authentic Capsule Registry)
SOFTWARE_CAPSULES: list[LanguageCapsuleSpec] = [
    LanguageCapsuleSpec("c", "", "#00599C", light_bg="#E6F0FA", light_fg="#004B87", var_template="$name($version)"),
    LanguageCapsuleSpec("rust", "", "#F74C00", light_bg="#FFECE6", light_fg="#C43A00"),
    LanguageCapsuleSpec("golang", "", "#00ADD8", light_bg="#E0F7FA", light_fg="#007D9C"),
    LanguageCapsuleSpec("python", "", "#3776AB", icon_fg="#FFD43B", light_bg="#E8F2FA", light_fg="#205C90"),
    LanguageCapsuleSpec("nodejs", "", "#5FA04E", light_bg="#F0FDF4", light_fg="#2E6E1F"),
    LanguageCapsuleSpec("bun", "", "#FBF0DF", icon_fg="#333333", light_bg="#FDF6EC", light_fg="#D97706"),
    LanguageCapsuleSpec("deno", "🦕", "#000000", light_bg="#F3F4F6", light_fg="#111827"),
    LanguageCapsuleSpec("java", "", "#ED8B00", light_bg="#FFF3E0", light_fg="#C44800"),
    LanguageCapsuleSpec("kotlin", "", "#7F52FF", light_bg="#F3E8FF", light_fg="#6B21A8"),
    LanguageCapsuleSpec("zig", "", "#F7A41D", light_bg="#FFF8E8", light_fg="#B86F00"),
    LanguageCapsuleSpec("lua", "", "#000080", light_bg="#E8EAF6", light_fg="#000080"),
    LanguageCapsuleSpec("php", "", "#777BB4", light_bg="#F0F1F9", light_fg="#5A5E96"),
    LanguageCapsuleSpec("ruby", "", "#CC342D", light_bg="#FDE8E8", light_fg="#A61C16"),
    LanguageCapsuleSpec("dart", "", "#0175C2", light_bg="#E1F5FE", light_fg="#0277BD"),
    LanguageCapsuleSpec("elixir", "", "#4B275F", light_bg="#F3E5F5", light_fg="#4A148C"),
    LanguageCapsuleSpec(
        "docker_context", "", "#2496ED", light_bg="#E8F4FD", light_fg="#0D6EFD", var_template="$context"
    ),
]


def _palette_refs(palette: TerminalPalette) -> dict[str, str]:
    """把调色板映射为 Starship 调色板变量名 -> 十六进制值。"""
    pill_bg = palette.selection_bg if palette.is_dark else "#FFFFFF"
    return {
        "text": palette.foreground,
        "base": pill_bg,
        "blue": palette.blue,
        "red": palette.red,
        "green": palette.green,
        "yellow": palette.yellow,
        "cyan": palette.cyan,
        "magenta": palette.magenta,
        "white": palette.white,
        "black": palette.black,
        "overlay1": "#4C566A" if palette.is_dark else "#CBD5E1",
        "subtext0": palette.dim_foreground or palette.bright_black,
    }


def generate_starship_config(palette: TerminalPalette, use_noctalia_palette: bool = False) -> str:
    """生成一体化极简浮动胶囊 Starship 布局。

    颜色一律通过 Starship 调色板变量引用：
    - `use_noctalia_palette=True` 时引用 Noctalia 模板生成的 `noctalia` 调色板，
      使提示符配色随外壳主题自动联动；
    - 否则内联一份 `nirice` 调色板，保证无 Noctalia 时也能正常工作。
    """
    refs = _palette_refs(palette)
    palette_name = "noctalia" if use_noctalia_palette else "nirice"

    module_formats = "\n".join(f"${spec.module}\\" for spec in SOFTWARE_CAPSULES)
    module_sections: list[str] = []
    for spec in SOFTWARE_CAPSULES:
        module_sections.append(
            f"""[{spec.module}]
symbol = "{spec.symbol}"
style = "fg:text bg:base bold"
format = "[│ ](fg:overlay1 bg:base)[{spec.symbol} ](fg:{spec.brand_color} bg:base)[{spec.var_template} ]($style)"
"""
        )
    rendered_modules = "\n".join(module_sections)

    if use_noctalia_palette:
        palette_block = '# 配色由 Noctalia 模板写入的 [palettes.noctalia] 提供。\npalette = "noctalia"\n'
    else:
        entries = "\n".join(f'{key} = "{value}"' for key, value in refs.items())
        palette_block = f'palette = "nirice"\n\n[palettes.nirice]\n{entries}\n'

    return f"""# Starship 提示符 - 一体化浮动胶囊布局，由 nirice 生成（配色: {palette_name}）

{palette_block}
format = \"\"\"
$directory\\
$git_branch\\
$git_status\\
{module_formats}
$cmd_duration\\
$character
\"\"\"

command_timeout = 800

[directory]
style = "fg:text bg:base bold"
format = "[](base)[  ](fg:cyan bg:base)[$path ]($style)"
truncation_length = 3
truncation_symbol = "…/"

[git_branch]
symbol = ""
style = "fg:text bg:base bold"
format = "[│ ](fg:overlay1 bg:base)[$symbol ](fg:blue bg:base)[$branch ]($style)"

[git_status]
style = "fg:yellow bg:base"
format = "([$all_status$ahead_behind ]($style))"

{rendered_modules}
[cmd_duration]
min_time = 500
style = "fg:subtext0 bg:base bold"
format = "[│ ](fg:overlay1 bg:base)[⏱ ](fg:yellow bg:base)[$duration ]($style)"

[character]
success_symbol = "[ ](fg:base)[❯](bold blue)"
error_symbol = "[ ](fg:base)[❯](bold red)"
"""


def extract_noctalia_palette_block(text: str) -> str:
    """从既有 starship.toml 中提取 Noctalia 写入的调色板块（含 markers），保留给合并写回。"""
    begin = "# >>> NOCTALIA STARSHIP PALETTE >>>"
    end = "# <<< NOCTALIA STARSHIP PALETTE <<<"
    if begin not in text or end not in text:
        return ""
    start = text.index(begin)
    stop = text.index(end) + len(end)
    return text[start:stop]


def generate_fastfetch_config(palette: TerminalPalette) -> str:
    """生成匹配调色板色彩的极简美观 Fastfetch config.jsonc 配置文件。"""
    key_color = "cyan" if palette.is_dark else "blue"
    title_color = "blue" if palette.is_dark else "cyan"

    config = {
        "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
        "logo": {
            "type": "small",
            "padding": {
                "top": 1,
                "left": 2,
                "right": 3,
            },
        },
        "display": {
            "separator": " 󰄾 ",
            "color": {
                "keys": key_color,
                "title": title_color,
            },
        },
        "modules": [
            "title",
            "separator",
            {
                "type": "os",
                "key": "OS",
                "format": "{3} {12}",
            },
            {
                "type": "host",
                "key": "Host",
            },
            {
                "type": "kernel",
                "key": "Kernel",
            },
            {
                "type": "uptime",
                "key": "Uptime",
            },
            {
                "type": "wm",
                "key": "WM",
                "format": "{2} ({3})",
            },
            {
                "type": "theme",
                "key": "Theme",
            },
            {
                "type": "icons",
                "key": "Icons",
            },
            {
                "type": "terminal",
                "key": "Term",
            },
            {
                "type": "terminalfont",
                "key": "Font",
            },
            {
                "type": "cpu",
                "key": "CPU",
            },
            {
                "type": "gpu",
                "key": "GPU",
            },
            {
                "type": "memory",
                "key": "Memory",
            },
            "break",
            "colors",
        ],
    }
    return json.dumps(config, indent=2) + "\n"

"""根据调色板动态生成 Shell 提示符 (Starship) 与系统硬件信息看板 (Fastfetch) 配置模板。"""

from __future__ import annotations

import json
from dataclasses import dataclass

from nirice.terminal.palettes import TerminalPalette

# Noctalia 官方 starship 模板：其 [palettes.noctalia] 的名字集合必须与
# nirice 回退调色板的键名完全一致，否则同一 format 在两套来源下会渲染出不同结果。
NOCTALIA_STARSHIP_TEMPLATE = "/usr/share/noctalia/assets/templates/starship/starship.toml"


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
    """把调色板映射为与 Noctalia starship 模板**同名同语义**的变量。

    名称必须与 Noctalia 的 starship 模板逐一对齐，否则同一个 format 字符串
    在「Noctalia 配色」与「nirice 回退配色」两套来源下会得到不同结果。
    Noctalia 的映射为：base/surface0 = 终端背景，surface1/overlay0 = ANSI 黑，
    overlay1/subtext0 = 亮黑，subtext1 = ANSI 白，text = 前景。
    """
    return {
        "text": palette.foreground,
        "base": palette.background,
        "surface0": palette.background,
        "surface1": palette.black,
        "overlay0": palette.black,
        "overlay1": palette.bright_black,
        "subtext0": palette.bright_black,
        "subtext1": palette.white,
        "blue": palette.blue,
        "red": palette.red,
        "green": palette.green,
        "yellow": palette.yellow,
        "cyan": palette.cyan,
        "magenta": palette.magenta,
        "white": palette.white,
        "black": palette.black,
    }


# 胶囊配色预设：三要素在**浅色与深色主题下的对比度都 >= 4.2**（除 frost 外，
# 由 tests 保证）。pill=胶囊底色，ink=胶囊上的文字色，divider=分隔线色。
@dataclass(frozen=True)
class CapsuleStyle:
    """胶囊配色三要素：pill=底色，ink=胶囊上的文字色，divider=分隔线色。"""

    pill: str
    ink: str
    divider: str
    description: str
    # 该方案承诺的最低对比度（浅色/深色主题都要满足）。
    # 4.2 = 清晰可读；3.0 = 柔和方案（胶囊字为 bold，可接受）。
    min_contrast: float = 4.2


CAPSULE_PRESETS: dict[str, CapsuleStyle] = {
    "glacier": CapsuleStyle(
        "cyan",
        "surface1",
        "surface1",
        "冰青主题色（4.35 / 5.03）—— 呼应 Nord Frost 的青色强调",
        4.2,
    ),
    "ink": CapsuleStyle(
        "text",
        "base",
        "surface1",
        "反白最高对比（7.95 / 9.25）—— 黑白强对比",
        4.2,
    ),
    "amber": CapsuleStyle(
        "yellow",
        "surface1",
        "surface1",
        "暖琥珀（4.29 / 6.44）",
        4.2,
    ),
    "moss": CapsuleStyle(
        "green",
        "surface1",
        "surface1",
        "苔绿（4.26 / 4.94）",
        4.2,
    ),
    "slate": CapsuleStyle(
        "overlay1",
        "base",
        "surface1",
        "中性石板（6.40 / 3.32）—— 素雅低调，深色主题下偏柔和",
        3.0,
    ),
    "frost": CapsuleStyle(
        "blue",
        "surface1",
        "overlay0",
        "霜蓝（3.70 / 3.70）—— 柔和低对比",
        3.0,
    ),
}
DEFAULT_CAPSULE = "glacier"


def generate_starship_config(
    palette: TerminalPalette,
    use_noctalia_palette: bool = False,
    capsule: str = DEFAULT_CAPSULE,
) -> str:
    """生成浮动胶囊 Starship 布局。

    颜色一律通过 Starship 调色板变量引用：
    - `use_noctalia_palette=True` 时引用 Noctalia 模板生成的 `noctalia` 调色板，
      使提示符配色随外壳主题自动联动；
    - 否则内联一份 `nirice` 调色板，保证无 Noctalia 时也能正常工作。

    `capsule` 选择配色预设，见 CAPSULE_PRESETS。
    """
    refs = _palette_refs(palette)
    style = CAPSULE_PRESETS.get(capsule, CAPSULE_PRESETS[DEFAULT_CAPSULE])
    pill, ink, divider = style.pill, style.ink, style.divider

    module_formats = "\n".join(f"${spec.module}\\" for spec in SOFTWARE_CAPSULES)
    module_sections: list[str] = []
    for spec in SOFTWARE_CAPSULES:
        module_sections.append(
            f"""[{spec.module}]
symbol = "{spec.symbol}"
style = "fg:{ink} bg:{pill}"
format = "[ │ ](fg:{divider} bg:{pill})[{spec.symbol} ](fg:{ink} bg:{pill})[{spec.var_template} ](fg:{ink} bg:{pill})"
"""
        )
    rendered_modules = "\n".join(module_sections)

    if use_noctalia_palette:
        palette_block = '# 配色由 Noctalia 模板写入的 [palettes.noctalia] 提供。\npalette = "noctalia"\n'
    else:
        entries = "\n".join(f'{key} = "{value}"' for key, value in refs.items())
        palette_block = f'palette = "nirice"\n\n[palettes.nirice]\n{entries}\n'

    return f"""# Starship 提示符 - 浮动胶囊布局，由 nirice 生成
# 配色预设: {capsule} —— {style.description}
#
# ⚠️ 胶囊底色绝不能用 base：Noctalia 的 base 就等于终端背景色，
#    会让整个胶囊和背景融为一体、完全看不见。
#    修改配色请改 src/nirice/terminal/prompt.py 的 CAPSULE_PRESETS，
#    然后执行 `nirice terminal set-starship` 重新生成。

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
style = "fg:{ink} bg:{pill} bold"
format = "[]({pill})[ 󰣇 ](fg:{ink} bg:{pill} bold)[│](fg:{divider} bg:{pill})[ $path ]($style)"
truncation_length = 3
truncation_symbol = "…/"

[git_branch]
symbol = ""
style = "fg:{ink} bg:{pill} bold"
format = "[ │ ](fg:{divider} bg:{pill})[$symbol ](fg:{ink} bg:{pill})[$branch ]($style)"

[git_status]
style = "fg:{ink} bg:{pill}"
format = "([ $all_status$ahead_behind ](fg:{ink} bg:{pill}))"

{rendered_modules}
[cmd_duration]
min_time = 500
style = "fg:{ink} bg:{pill} bold"
format = "[ │ ](fg:{divider} bg:{pill})[⏱ ](fg:{ink} bg:{pill})[$duration ]($style)"

[character]
success_symbol = "[ ](fg:{pill})[❯](bold blue)"
error_symbol = "[ ](fg:{pill})[❯](bold red)"
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
    """生成匹配调色板色彩的极简美观 Fastfetch config.jsonc 配置文件。

    宽度是硬约束：niri 新建列的默认宽度是工作区的一半，在 1920×1080 / 1.25 缩放下
    约等于 73 列。默认的 CPU / GPU 输出带频率与核心数，整块会到 87 列而折行，
    一折行左侧 logo 就被挤乱，因此这两个模块只取型号名，压到 69 列。
    """
    key_color = "cyan" if palette.is_dark else "blue"
    title_color = "blue" if palette.is_dark else "cyan"

    # 逐模块着色，让键名列呈现一条彩虹而不是整块单色。
    # 只用浅色主题下对比度足够的四个色（blue 3.70 / green 4.26 / yellow 4.29 / cyan 4.35）。
    accents = ("blue", "cyan", "green", "yellow")
    pending = list(accents) * 4

    def spec(kind: str, key: str, **extra: str) -> dict[str, str]:
        return {"type": kind, "key": key, "keyColor": pending.pop(0), **extra}

    config = {
        "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
        "logo": {
            "type": "small",
            "padding": {
                "top": 1,
                "left": 2,
                "right": 2,
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
            spec("os", "OS", format="{3} {12}"),
            spec("host", "Host"),
            spec("kernel", "Kernel"),
            spec("uptime", "Uptime"),
            spec("wm", "WM", format="{2} ({3})"),
            spec("theme", "Theme"),
            # 刻意不列 icons：该模块要能读到 GTK 图标主题，本机只有 css、没有 settings.ini，
            # fastfetch 会报 "No icons could be found" 并让整行消失。
            spec("terminal", "Term"),
            spec("terminalfont", "Font"),
            spec("cpu", "CPU", format="{1}"),
            spec("gpu", "GPU", format="{1} {2}"),
            spec("memory", "Memory"),
            "break",
            "colors",
        ],
    }
    return json.dumps(config, indent=2) + "\n"

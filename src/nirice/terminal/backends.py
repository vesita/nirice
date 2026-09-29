"""各终端模拟器的**回退**配色写入器。

仅在 Noctalia 模板不可用（未安装/未启用对应模板）时才会被调用；
正常路径下配色由 Noctalia 统一渲染。
"""

from __future__ import annotations

import re
from pathlib import Path

from nirice.terminal.palettes import TerminalPalette


def alacritty(config_dir: Path, pal: TerminalPalette, dry_run: bool) -> tuple[bool, str]:
    """写入 Alacritty 主题文件并确保 import 引用。"""
    if dry_run:
        return True, f"[演练模拟] 将为 Alacritty 应用调色板: {pal.name}"

    alacritty_dir = config_dir / "alacritty"
    themes_dir = alacritty_dir / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    (themes_dir / "nirice.toml").write_text(_alacritty_theme(pal), encoding="utf-8")

    config_path = alacritty_dir / "alacritty.toml"
    import_line = 'import = ["~/.config/alacritty/themes/nirice.toml"]'
    try:
        if config_path.exists():
            content = config_path.read_text(encoding="utf-8")
            if "themes/nirice.toml" not in content:
                if "[general]" in content:
                    content = content.replace("[general]", f"[general]\n{import_line}", 1)
                else:
                    content = f"[general]\n{import_line}\n\n" + content
                config_path.write_text(content, encoding="utf-8")
        else:
            config_path.write_text(
                f"[general]\n{import_line}\nlive_config_reload = true\n\n"
                "[window]\nopacity = 0.88\npadding = { x = 8, y = 8 }\n\n"
                '[font]\nsize = 11.5\nnormal = { family = "MesloLGS Nerd Font", style = "Regular" }\n',
                encoding="utf-8",
            )
    except OSError as exc:
        return False, f"更新 Alacritty 配置失败: {exc}"
    return True, f"Alacritty 配色已设置为 '{pal.name}'。"


def _alacritty_theme(pal: TerminalPalette) -> str:
    return f"""[colors.primary]
background = "{pal.background}"
foreground = "{pal.foreground}"
dim_foreground = "{pal.dim_foreground}"
bright_foreground = "{pal.bright_foreground}"

[colors.cursor]
text = "{pal.cursor_text}"
cursor = "{pal.cursor}"

[colors.selection]
text = "{pal.selection_fg}"
background = "{pal.selection_bg}"

[colors.normal]
black = "{pal.black}"
red = "{pal.red}"
green = "{pal.green}"
yellow = "{pal.yellow}"
blue = "{pal.blue}"
magenta = "{pal.magenta}"
cyan = "{pal.cyan}"
white = "{pal.white}"

[colors.bright]
black = "{pal.bright_black}"
red = "{pal.bright_red}"
green = "{pal.bright_green}"
yellow = "{pal.bright_yellow}"
blue = "{pal.bright_blue}"
magenta = "{pal.bright_magenta}"
cyan = "{pal.bright_cyan}"
white = "{pal.bright_white}"
"""


def ghostty(config_dir: Path, pal: TerminalPalette, dry_run: bool) -> tuple[bool, str]:
    """写入 Ghostty 主题并在 config 中启用。"""
    if dry_run:
        return True, f"[演练模拟] 将为 Ghostty 应用调色板: {pal.name}"

    ghostty_dir = config_dir / "ghostty"
    themes_dir = ghostty_dir / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    (themes_dir / f"nirice-{pal.name}").write_text(_ghostty_theme(pal), encoding="utf-8")

    config_path = ghostty_dir / "config"
    try:
        if config_path.exists():
            text = re.sub(r"theme\s*=\s*.*", f"theme = nirice-{pal.name}", config_path.read_text(encoding="utf-8"))
            if f"theme = nirice-{pal.name}" not in text:
                text = f"theme = nirice-{pal.name}\n" + text
            config_path.write_text(text, encoding="utf-8")
        else:
            config_path.write_text(f"theme = nirice-{pal.name}\nbackground-opacity = 0.94\n", encoding="utf-8")
    except OSError as exc:
        return False, f"更新 Ghostty 配置失败: {exc}"
    return True, f"Ghostty 主题已设置为 'nirice-{pal.name}'。"


def _ghostty_theme(pal: TerminalPalette) -> str:
    lines = [
        "# Ghostty theme - managed by nirice",
        f"background = {pal.background}",
        f"foreground = {pal.foreground}",
        f"cursor-color = {pal.cursor}",
        f"cursor-text = {pal.cursor_text}",
        f"selection-background = {pal.selection_bg}",
        f"selection-foreground = {pal.selection_fg}",
    ]
    for index, color in enumerate(pal.to_ansi_list()):
        lines.append(f"palette = {index}={color}")
    return "\n".join(lines) + "\n"


def foot(config_dir: Path, pal: TerminalPalette, dry_run: bool) -> tuple[bool, str]:
    """写入 Foot 的 [colors] 小节。"""
    if dry_run:
        return True, f"[演练模拟] 将为 Foot 应用调色板: {pal.name}"

    foot_dir = config_dir / "foot"
    foot_dir.mkdir(parents=True, exist_ok=True)
    config_path = foot_dir / "foot.ini"
    ansi = pal.to_ansi_list()
    body = "\n".join(
        [f"regular{i}={c.lstrip('#')}" for i, c in enumerate(ansi[:8])]
        + [f"bright{i}={c.lstrip('#')}" for i, c in enumerate(ansi[8:])]
    )
    block = (
        "[colors]\n"
        "alpha=0.94\n"
        f"background={pal.background.lstrip('#')}\n"
        f"foreground={pal.foreground.lstrip('#')}\n"
        f"{body}\n"
    )
    try:
        if config_path.exists():
            stripped = re.sub(
                r"\[colors.*?(\n\[|\Z)", r"\1", config_path.read_text(encoding="utf-8"), flags=re.DOTALL
            ).strip()
            config_path.write_text(stripped + "\n\n" + block, encoding="utf-8")
        else:
            config_path.write_text(
                "# Foot Configuration - managed by nirice\n"
                "[main]\nfont=MesloLGS Nerd Font:size=11.5\npad=8x8\n\n" + block,
                encoding="utf-8",
            )
    except OSError as exc:
        return False, f"更新 Foot 配置失败: {exc}"
    return True, f"Foot 主题已设置为 '{pal.name}'。"


def wezterm(config_dir: Path, pal: TerminalPalette, dry_run: bool) -> tuple[bool, str]:
    """写入 WezTerm 配色方案文件。"""
    if dry_run:
        return True, f"[演练模拟] 将为 WezTerm 应用调色板: {pal.name}"

    colors_dir = config_dir / "wezterm" / "colors"
    colors_dir.mkdir(parents=True, exist_ok=True)
    ansi = pal.to_ansi_list()
    theme = (
        "[colors]\n"
        f'background = "{pal.background}"\n'
        f'foreground = "{pal.foreground}"\n'
        f'cursor_bg = "{pal.cursor}"\n'
        f'cursor_fg = "{pal.cursor_text}"\n'
        f'selection_bg = "{pal.selection_bg}"\n'
        f'selection_fg = "{pal.selection_fg}"\n\n'
        "ansi = [\n" + "".join(f'  "{c}",\n' for c in ansi[:8]) + "]\n\n"
        "brights = [\n" + "".join(f'  "{c}",\n' for c in ansi[8:]) + "]\n"
    )
    try:
        (colors_dir / f"nirice-{pal.name}.toml").write_text(theme, encoding="utf-8")
    except OSError as exc:
        return False, f"更新 WezTerm 配置失败: {exc}"
    return True, f"WezTerm 主题已写入 'nirice-{pal.name}'。"


def zellij(config_dir: Path, pal: TerminalPalette, dry_run: bool) -> tuple[bool, str]:
    """写入 Zellij 主题并设为当前主题。"""
    if dry_run:
        return True, f"[演练模拟] 将为 Zellij 应用调色板: {pal.name}"

    zellij_dir = config_dir / "zellij"
    themes_dir = zellij_dir / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    theme_kdl = f"""themes {{
    "nirice-{pal.name}" {{
        fg "{pal.foreground}"
        bg "{pal.background}"
        black "{pal.black}"
        red "{pal.red}"
        green "{pal.green}"
        yellow "{pal.yellow}"
        blue "{pal.blue}"
        magenta "{pal.magenta}"
        cyan "{pal.cyan}"
        white "{pal.white}"
        orange "{pal.bright_red}"
    }}
}}
"""
    try:
        (themes_dir / f"nirice-{pal.name}.kdl").write_text(theme_kdl, encoding="utf-8")
        config_file = zellij_dir / "config.kdl"
        if config_file.exists():
            text = config_file.read_text(encoding="utf-8")
            if re.search(r"^theme\s+", text, flags=re.MULTILINE):
                text = re.sub(r'^theme\s+["\'].*?["\']', f'theme "nirice-{pal.name}"', text, flags=re.MULTILINE)
            else:
                text = f'theme "nirice-{pal.name}"\n' + text
            config_file.write_text(text, encoding="utf-8")
        else:
            config_file.write_text(f'theme "nirice-{pal.name}"\ndefault_layout "compact"\n', encoding="utf-8")
    except OSError as exc:
        return False, f"更新 Zellij 配置失败: {exc}"
    return True, f"Zellij 主题已设置为 'nirice-{pal.name}'。"


BACKENDS = {
    "alacritty": alacritty,
    "ghostty": ghostty,
    "foot": foot,
    "wezterm": wezterm,
    "zellij": zellij,
}

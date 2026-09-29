"""终端层测试：调色板、Kitty 美学/配色分层、各终端后端与提示符生成。"""

from __future__ import annotations

from pathlib import Path

from nirice.noctalia import NoctaliaController
from nirice.terminal import TERMINAL_PALETTES, TerminalController, backends, hex_to_rgb, rgb_to_hex
from nirice.terminal.kitty import render_kitty_aesthetics, render_kitty_conf, render_kitty_theme
from nirice.terminal.prompt import (
    CAPSULE_PRESETS,
    DEFAULT_CAPSULE,
    _palette_refs,
    generate_starship_config,
)

# 胶囊里使用的 Arch 图标（Material Design 版，Nerd Fonts 中形体最大的一种）
ARCH_GLYPH = "\U000f08c7"  # md-arch，实测形体最大


def _controller(xdg: dict[str, Path], dry_run: bool = False) -> TerminalController:
    noctalia = NoctaliaController(home_dir=xdg["home"], binary="")
    return TerminalController(dry_run=dry_run, home_dir=xdg["home"], noctalia=noctalia)


# ==================== 调色板 ====================


def test_color_utilities() -> None:
    assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
    assert hex_to_rgb("#FFF") == (255, 255, 255)
    assert hex_to_rgb("nope") == (0, 0, 0)
    assert hex_to_rgb("#GGGGGG") == (0, 0, 0)
    assert rgb_to_hex(46, 52, 64) == "#2E3440"


def test_nord_light_palette_is_curated_light() -> None:
    pal = TERMINAL_PALETTES["nord-light"]
    assert pal.is_dark is False
    assert len(pal.to_ansi_list()) == 16
    assert pal.to_ansi_list()[0] == pal.black
    assert pal.to_ansi_list()[15] == pal.bright_white


def test_catalog_includes_aliases() -> None:
    for key in ("nord-light", "cachy-nord", "catppuccin-latte", "catppuccin-mocha", "dracula"):
        assert key in TERMINAL_PALETTES


# ==================== Kitty 分层 ====================


def test_aesthetics_contain_no_colors() -> None:
    """美学层不得写死颜色，否则会与 Noctalia 渲染的配色打架。"""
    aesthetic = render_kitty_aesthetics()
    assert "font_family" in aesthetic
    assert "MesloLGS Nerd Font" in aesthetic
    assert "background_opacity" in aesthetic
    for forbidden in ("color0", "background ", "foreground ", "active_tab_background"):
        assert forbidden not in aesthetic, f"美学层不应包含 {forbidden!r}"


def test_kitty_font_and_spacing_use_modern_options() -> None:
    """kitty 0.49 弃用了 adjust_*，且必须显式指定终端字体。"""
    aesthetic = render_kitty_aesthetics()

    assert "adjust_column_width" not in aesthetic, "adjust_column_width 已被 kitty 弃用"
    assert "adjust_line_height" not in aesthetic, "adjust_line_height 已被 kitty 弃用"
    assert "modify_font cell_width 100%" in aesthetic
    assert "modify_font cell_height 105%" in aesthetic

    # 不显式指定字体就会落到 monospace → Noto Sans Mono CJK（ASCII 步进仅 0.5em）
    assert "font_family      MesloLGS Nerd Font Mono" in aesthetic
    assert "font_family      monospace" not in aesthetic
    # kitty 的 font_family 是单个 FontSpec，多行时只有最后一行生效，
    # 因此绝不能靠重复写 font_family 来做 CJK 回退。
    assert aesthetic.count("font_family      ") == 1, "font_family 只能出现一次"


def test_tab_bar_is_pinned_to_top() -> None:
    """kitty 默认 tab_bar_edge 是 bottom，必须显式改成 top。"""
    aesthetic = render_kitty_aesthetics()
    assert "tab_bar_edge top" in aesthetic
    assert "tab_bar_edge bottom" not in aesthetic
    assert "tab_bar_style powerline" in aesthetic


def test_kitty_conf_includes_are_mode_dependent() -> None:
    with_noctalia = render_kitty_conf(use_noctalia=True)
    assert "include nirice.conf" in with_noctalia
    assert "include themes/noctalia.conf" in with_noctalia

    fallback = render_kitty_conf(use_noctalia=False)
    assert "include nirice-theme.conf" in fallback
    assert "themes/noctalia.conf" not in fallback


def test_kitty_fallback_theme_renders_palette() -> None:
    pal = TERMINAL_PALETTES["nord-light"]
    theme = render_kitty_theme(pal)
    assert f"background            {pal.background}" in theme
    assert f"color0  {pal.black}" in theme


def test_apply_kitty_falls_back_without_noctalia(xdg: dict[str, Path]) -> None:
    ctl = _controller(xdg)
    ok, message = ctl.apply_kitty()
    assert ok and "nirice 调色板" in message

    kitty_dir = xdg["config"] / "kitty"
    assert (kitty_dir / "nirice.conf").exists()
    assert (kitty_dir / "nirice-theme.conf").exists()
    assert "include nirice.conf" in (kitty_dir / "kitty.conf").read_text(encoding="utf-8")


def test_apply_kitty_rejects_unknown_palette(xdg: dict[str, Path]) -> None:
    ok, message = _controller(xdg).apply_kitty("nope")
    assert not ok and "未知" in message


# ==================== 各终端后端 ====================


def test_backends_generate_expected_files(xdg: dict[str, Path]) -> None:
    pal = TERMINAL_PALETTES["cachy-nord"]
    config = xdg["config"]

    ok, _ = backends.alacritty(config, pal, dry_run=False)
    assert ok and (config / "alacritty" / "themes" / "nirice.toml").exists()

    ok, _ = backends.ghostty(config, pal, dry_run=False)
    assert ok and (config / "ghostty" / "themes" / f"nirice-{pal.name}").exists()

    ok, _ = backends.foot(config, pal, dry_run=False)
    assert ok and "[colors]" in (config / "foot" / "foot.ini").read_text(encoding="utf-8")

    ok, _ = backends.wezterm(config, pal, dry_run=False)
    assert ok and (config / "wezterm" / "colors" / f"nirice-{pal.name}.toml").exists()

    ok, _ = backends.zellij(config, pal, dry_run=False)
    assert ok
    assert f'theme "nirice-{pal.name}"' in (config / "zellij" / "config.kdl").read_text(encoding="utf-8")


def test_backends_dry_run_writes_nothing(xdg: dict[str, Path]) -> None:
    pal = TERMINAL_PALETTES["cachy-nord"]
    ok, _ = backends.alacritty(xdg["config"], pal, dry_run=True)
    assert ok
    assert not (xdg["config"] / "alacritty").exists()


# ==================== 提示符 ====================


def test_starship_uses_palette_indirection() -> None:
    pal = TERMINAL_PALETTES["nord-light"]

    inline = generate_starship_config(pal, use_noctalia_palette=False)
    assert 'palette = "nirice"' in inline
    assert "[palettes.nirice]" in inline
    assert pal.blue in inline

    external = generate_starship_config(pal, use_noctalia_palette=True)
    assert 'palette = "noctalia"' in external
    assert "[palettes.nirice]" not in external
    assert f"bg:{CAPSULE_PRESETS[DEFAULT_CAPSULE].pill}" in external


def test_capsule_pill_is_not_the_terminal_background() -> None:
    """回归：Noctalia 的 base 就等于终端背景色，用它当胶囊底色会让胶囊完全隐形。"""
    for name, style in CAPSULE_PRESETS.items():
        assert style.pill != "base", f"{name} 的底色是 base，会与终端背景融为一体"
    cfg = generate_starship_config(TERMINAL_PALETTES["nord-light"], use_noctalia_palette=True)
    assert "bg:base" not in cfg, "base 是终端背景色，不能作为胶囊底色"


def _contrast(fg_hex: str, bg_hex: str) -> float:
    """WCAG 相对亮度对比度。"""

    def channel(value: int) -> float:
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    def luminance(color: str) -> float:
        h = color.lstrip("#")
        r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
        return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

    hi, lo = sorted((luminance(fg_hex), luminance(bg_hex)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_every_capsule_preset_is_readable_in_both_themes() -> None:
    """每个预设都要兑现它自己声明的 min_contrast。

    彩色预设（glacier/amber/moss）是按 **Noctalia 实际生成的调色板**设计的 ——
    其浅色主题下 accent 偏亮（cyan=#7BB3C3、yellow=#C5A565），才能与深色墨水
    配成高对比。nirice 自带的回退调色板里这些 accent 偏暗，所以只有 ink 是
    跨调色板安全的选择（见下一个测试）。
    """
    noctalia_light = {
        "base": "#eceff4",
        "text": "#414858",
        "surface1": "#3b4252",
        "overlay1": "#4c566a",
        "cyan": "#7bb3c3",
        "yellow": "#c5a565",
        "green": "#96b17f",
        "blue": "#81a1c1",
    }
    noctalia_dark = {
        "base": "#2e3440",
        "text": "#d8dee9",
        "surface1": "#3b4252",
        "overlay1": "#7684a0",
        "cyan": "#88c0d0",
        "yellow": "#ebcb8b",
        "green": "#a3be8c",
        "blue": "#81a1c1",
    }
    for mode, palette in (("light", noctalia_light), ("dark", noctalia_dark)):
        for name, style in CAPSULE_PRESETS.items():
            ratio = _contrast(palette[style.ink], palette[style.pill])
            assert ratio >= style.min_contrast, (
                f"{name} 在 Noctalia {mode} 主题下对比度仅 {ratio:.2f}，低于其声明的 {style.min_contrast}"
            )


def test_ink_preset_is_safe_across_palette_sources() -> None:
    """ink 只依赖「前景 / 背景」两个角色，因此在两套调色板下都成立。"""
    sources = {
        "light": _palette_refs(TERMINAL_PALETTES["nord-light"]),
        "dark": _palette_refs(TERMINAL_PALETTES["cachy-nord"]),
    }
    style = CAPSULE_PRESETS["ink"]
    for mode, refs in sources.items():
        ratio = _contrast(refs[style.ink], refs[style.pill])
        assert ratio >= style.min_contrast, f"ink 在 nirice {mode} 调色板下对比度仅 {ratio:.2f}"

"""Noctalia 控制器测试：settings.toml 外科手术式编辑与模板管理。"""

from __future__ import annotations

from pathlib import Path

from nirice.noctalia import NoctaliaController


def _controller(xdg: dict[str, Path], dry_run: bool = False) -> NoctaliaController:
    return NoctaliaController(dry_run=dry_run, home_dir=xdg["home"], binary="")


def _seed_settings(xdg: dict[str, Path]) -> Path:
    settings = xdg["state"] / "noctalia" / "settings.toml"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(
        "config_version = 14\n\n"
        '[dock]\nposition = "left"\n\n'
        '[theme]\nbuiltin = "Nord"\nmode = "light"\n\n'
        '[wallpaper.default]\npath = "/usr/share/noctalia/assets/wallpaper.png"\n',
        encoding="utf-8",
    )
    return settings


def test_read_defaults_when_no_settings(xdg: dict[str, Path]) -> None:
    ctl = _controller(xdg)
    assert ctl.get_bar_position() == "top"
    assert ctl.get_theme() == ("Nord", "dark")
    assert ctl.get_enabled_templates() == []


def test_set_bar_position_persists_and_is_idempotent(xdg: dict[str, Path]) -> None:
    _seed_settings(xdg)
    ctl = _controller(xdg)

    ok, _ = ctl.set_bar_position("left")
    assert ok
    assert ctl.get_bar_position() == "left"
    assert 'position = "left"' in (xdg["state"] / "noctalia" / "settings.toml").read_text(encoding="utf-8")

    ok, message = ctl.set_bar_position("left")
    assert ok and "已在" in message


def test_bar_position_must_use_named_bar_section(xdg: dict[str, Path]) -> None:
    """回归：bar 是命名 bar，写顶层 [bar] 会被 Noctalia 静默忽略。"""
    _seed_settings(xdg)
    ctl = _controller(xdg)
    ctl.set_bar_position("left")

    text = (xdg["state"] / "noctalia" / "settings.toml").read_text(encoding="utf-8")
    assert "[bar.default]" in text
    # 顶层 [bar] 不能带 position
    assert "[bar]\nposition" not in text


def test_legacy_top_level_bar_position_is_dropped(xdg: dict[str, Path]) -> None:
    """早期版本误写到顶层 [bar] 的 position 应被清理。"""
    settings = xdg["state"] / "noctalia" / "settings.toml"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text('[bar]\nposition = "left"\n\n[dock]\nposition = "left"\n', encoding="utf-8")

    assert _controller(xdg).drop_legacy_bar_position() is True
    text = settings.read_text(encoding="utf-8")
    assert "position" not in text.split("[dock]")[0], "顶层 [bar] 的 position 应被删除"
    assert "[dock]" in text and 'position = "left"' in text


def test_set_bar_position_rejects_invalid_value(xdg: dict[str, Path]) -> None:
    _seed_settings(xdg)
    ok, message = _controller(xdg).set_bar_position("diagonal")
    assert not ok
    assert "无效" in message


def test_existing_sections_are_preserved(xdg: dict[str, Path]) -> None:
    settings = _seed_settings(xdg)
    _controller(xdg).set_bar_position("right")

    text = settings.read_text(encoding="utf-8")
    assert "[dock]" in text and "[theme]" in text and "[wallpaper.default]" in text
    assert text.index("[bar.default]") > text.index("[dock]")


def test_set_theme_updates_palette_and_mode(xdg: dict[str, Path]) -> None:
    _seed_settings(xdg)
    ctl = _controller(xdg)

    ok, _ = ctl.set_theme(palette="Catppuccin Mocha", mode="dark")
    assert ok
    assert ctl.get_theme() == ("Catppuccin Mocha", "dark")

    ok, message = ctl.set_theme(mode="sepia")
    assert not ok and "无效主题模式" in message


def test_theme_templates_roundtrip(xdg: dict[str, Path]) -> None:
    _seed_settings(xdg)
    ctl = _controller(xdg)

    ok, _ = ctl.set_enabled_templates(["kitty", "starship"])
    assert ok
    assert ctl.get_enabled_templates() == ["kitty", "starship"]

    text = (xdg["state"] / "noctalia" / "settings.toml").read_text(encoding="utf-8")
    assert "[theme.templates]" in text
    assert 'builtin_ids = ["kitty", "starship"]' in text


def test_enable_templates_in_dry_run_writes_nothing(xdg: dict[str, Path]) -> None:
    settings = _seed_settings(xdg)
    before = settings.read_text(encoding="utf-8")
    ctl = _controller(xdg, dry_run=True)

    ok, message = ctl.enable_templates(["kitty"])
    assert ok and "演练模拟" in message
    assert settings.read_text(encoding="utf-8") == before


def test_backup_created_on_change(xdg: dict[str, Path]) -> None:
    _seed_settings(xdg)
    ctl = _controller(xdg)
    ctl.set_bar_position("bottom")
    assert list(ctl.backup_dir.rglob("settings.toml")), "修改前应产生备份"


def test_unknown_template_is_rejected_when_manifest_present(xdg: dict[str, Path]) -> None:
    _seed_settings(xdg)
    ctl = _controller(xdg)
    if not ctl.available_builtin_templates():
        return  # 未安装 Noctalia 时跳过
    ok, message = ctl.set_enabled_templates(["definitely-not-a-template"])
    assert not ok and "未知模板" in message

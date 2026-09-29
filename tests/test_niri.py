"""Niri 控制器测试：配置片段读写、差异比对、备份与应用。"""

from __future__ import annotations

from pathlib import Path

from nirice.niri import ANIMATION_PRESETS, NiriController
from nirice.niri.catalog import MANAGED_FRAGMENTS


def _controller(xdg: dict[str, Path]) -> NiriController:
    # binary="" 模拟「未安装 niri」，避免测试触碰真实合成器
    return NiriController(dry_run=False, home_dir=xdg["home"], config_dir=xdg["config"], binary="")


def test_managed_fragments_cover_expected_files() -> None:
    assert set(MANAGED_FRAGMENTS) == {
        "animation.kdl",
        "autostart.kdl",
        "keybinds.kdl",
        "input.kdl",
        "layout.kdl",
        "rules.kdl",
        "misc.kdl",
    }
    assert "spawn-at-startup" in MANAGED_FRAGMENTS["autostart.kdl"]


def test_keybinds_meet_user_requirements() -> None:
    """用户明确要求的快捷键必须存在。"""
    binds = MANAGED_FRAGMENTS["keybinds.kdl"]
    assert "Mod+T" in binds and 'spawn "kitty"' in binds
    assert "maximize-column" in binds
    assert "Mod+R" in binds
    assert "center-column" in binds
    assert "move-column-to-first" in binds
    assert "move-column-to-last" in binds
    # niri 一键只允许一个动作，侧边吸附必须走 spawn-sh 串联
    assert "niri msg action" in binds


def test_animation_presets_are_valid_kdl_blocks() -> None:
    assert {"arctic", "snappy", "silky", "instant"} <= set(ANIMATION_PRESETS)
    for preset in ANIMATION_PRESETS.values():
        assert preset.animations_kdl.strip().startswith("animations {")
        assert preset.animations_kdl.strip().endswith("}")


def test_fragment_write_diff_and_idempotence(xdg: dict[str, Path]) -> None:
    ctl = _controller(xdg)

    assert ctl.diff_fragments()["layout.kdl"] == "missing"

    result = ctl.write_fragment("layout.kdl", "layout { gaps 16 }\n")
    assert result.ok and result.created and result.changed
    assert (ctl.cfg_dir / "layout.kdl").read_text(encoding="utf-8") == "layout { gaps 16 }\n"

    again = ctl.write_fragment("layout.kdl", "layout { gaps 16 }\n")
    assert again.ok and not again.changed

    modified = ctl.write_fragment("layout.kdl", "layout { gaps 24 }\n")
    assert modified.changed
    assert ctl.diff_fragments()["layout.kdl"] == "changed"


def test_backup_is_created_before_overwrite(xdg: dict[str, Path]) -> None:
    ctl = _controller(xdg)
    ctl.write_fragment("misc.kdl", "// v1\n", backup=False)
    ctl.write_fragment("misc.kdl", "// v2\n", backup=True)

    backups = list(ctl.backup_dir.rglob("misc.kdl"))
    assert backups, "覆盖前应产生备份"
    assert backups[-1].read_text(encoding="utf-8") == "// v1\n"


def test_apply_all_creates_root_and_skips_requested(xdg: dict[str, Path]) -> None:
    ctl = _controller(xdg)
    results = ctl.apply_all(skip=["keybinds.kdl"], backup=False)
    names = {r.name for r in results}

    assert "keybinds.kdl" not in names
    assert "config.kdl" in names
    assert "display.kdl" in names
    assert (ctl.niri_dir / "config.kdl").exists()
    assert not (ctl.cfg_dir / "keybinds.kdl").exists()
    assert 'include "noctalia.kdl"' in (ctl.niri_dir / "config.kdl").read_text(encoding="utf-8")


def test_display_fragment_is_never_overwritten(xdg: dict[str, Path]) -> None:
    ctl = _controller(xdg)
    ctl.cfg_dir.mkdir(parents=True, exist_ok=True)
    custom = 'output "eDP-1" {\n    scale 1.25\n}\n'
    (ctl.cfg_dir / "display.kdl").write_text(custom, encoding="utf-8")

    result = ctl.ensure_display_fragment()
    assert not result.changed and not result.created
    assert (ctl.cfg_dir / "display.kdl").read_text(encoding="utf-8") == custom


def test_dry_run_writes_nothing(xdg: dict[str, Path]) -> None:
    ctl = NiriController(dry_run=True, home_dir=xdg["home"], config_dir=xdg["config"], binary="")
    results = ctl.apply_all(backup=False)
    assert all(r.changed for r in results)
    assert not (ctl.niri_dir / "config.kdl").exists()


def test_validate_without_binary_reports_error(xdg: dict[str, Path]) -> None:
    ok, message = _controller(xdg).validate()
    assert not ok
    assert "niri" in message

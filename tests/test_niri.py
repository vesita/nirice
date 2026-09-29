"""Niri 控制器测试：配置片段读写、差异比对、备份与应用。"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from nirice.niri import ANIMATION_PRESETS, NiriController
from nirice.niri.catalog import MANAGED_FRAGMENTS


def _binding_combos(text: str) -> list[str]:
    """提取 binds 块中每个绑定的规范化按键组合（排序修饰键）。"""
    body = text.split("binds {", 1)[1].rsplit("}", 1)[0]
    combos: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or "{" not in line:
            continue
        # 形式为 `Mod+X <可选选项> { action; }`，取第一段即按键组合
        keys = line.split("{", 1)[0].strip().split()
        if keys:
            combos.append("+".join(sorted(part.upper() for part in keys[0].split("+"))))
    return combos


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


def test_keybinds_have_no_duplicate_combinations() -> None:
    """niri 中修饰键顺序无意义，Mod+A+B 与 Mod+B+A 是同一个键，必须查重。"""
    combos = _binding_combos(MANAGED_FRAGMENTS["keybinds.kdl"])
    assert len(combos) > 50, f"应解析出大量绑定，实际 {len(combos)}"
    duplicates = sorted({c for c in combos if combos.count(c) > 1})
    assert not duplicates, f"存在重复的按键组合: {duplicates}"


def test_default_column_width_is_not_forced() -> None:
    """刻意不设置 default-column-width，保持 niri 原生开窗宽度。"""
    layout = MANAGED_FRAGMENTS["layout.kdl"]
    assert "preset-window-heights" in layout
    active = [ln for ln in layout.splitlines() if ln.strip().startswith("default-column-width")]
    assert not active, "default-column-width 只应以注释形式存在"


@pytest.mark.skipif(shutil.which("niri") is None, reason="需要已安装 niri 才能做真实语法校验")
def test_keybinds_pass_real_niri_validate(tmp_path: Path) -> None:
    """用 niri 自己的解析器验证快捷键块 —— 重复绑定就是被它抓出来的。"""
    config = tmp_path / "config.kdl"
    config.write_text(MANAGED_FRAGMENTS["keybinds.kdl"], encoding="utf-8")

    result = subprocess.run(
        ["niri", "validate", "-c", str(config)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


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

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
    """用户明确要求保留的快捷键必须存在。"""
    binds = MANAGED_FRAGMENTS["keybinds.kdl"]
    assert "Mod+T" in binds and 'spawn "kitty"' in binds
    assert "Mod+Q" in binds and "close-window" in binds
    assert "Mod+R" in binds and "switch-preset-column-width" in binds
    assert "Mod+D" in binds and "panel-toggle launcher" in binds
    assert "Mod+V" in binds and "panel-toggle clipboard" in binds
    assert "focus-workspace-up" in binds and "focus-workspace-down" in binds
    assert "fullscreen-window" in binds


def test_in_column_navigation_has_no_arrow_equivalent() -> None:
    """列内窗口导航只能靠 K/J —— 方向键那两组管的是跨列与跨工作区。

    所以 K/J 不是 HJKL 别名，删掉它们会彻底失去列内切窗口与调序的能力。
    """
    body = MANAGED_FRAGMENTS["keybinds.kdl"].split("binds {", 1)[1].rsplit("}", 1)[0]
    lines = [ln.strip() for ln in body.splitlines()]
    lines = [ln for ln in lines if ln and not ln.startswith("//")]

    def action_of(combo: str) -> str:
        match = next(ln for ln in lines if ln.startswith(f"{combo} "))
        return match.split("{", 1)[1].split(";", 1)[0].strip()

    assert action_of("Mod+K") == "focus-window-up"
    assert action_of("Mod+J") == "focus-window-down"
    assert action_of("Mod+Ctrl+K") == "move-window-up"
    assert action_of("Mod+Ctrl+J") == "move-window-down"
    # 方向键承载的是另一层语义，两组不可互换
    assert action_of("Mod+Up") == "focus-workspace-up"
    assert action_of("Mod+Down") == "focus-workspace-down"


def test_animation_presets_are_valid_kdl_blocks() -> None:
    assert {"arctic", "snappy", "silky", "instant"} <= set(ANIMATION_PRESETS)
    for preset in ANIMATION_PRESETS.values():
        assert preset.animations_kdl.strip().startswith("animations {")
        assert preset.animations_kdl.strip().endswith("}")


def test_keybinds_have_no_duplicate_combinations() -> None:
    """niri 中修饰键顺序无意义，Mod+A+B 与 Mod+B+A 是同一个键，必须查重。"""
    combos = _binding_combos(MANAGED_FRAGMENTS["keybinds.kdl"])
    assert len(combos) > 30, f"应解析出大量绑定，实际 {len(combos)}"
    duplicates = sorted({c for c in combos if combos.count(c) > 1})
    assert not duplicates, f"存在重复的按键组合: {duplicates}"


def test_every_keybind_has_a_chinese_overlay_title() -> None:
    """niri 的 overlay 文案是硬编码英文且没有本地化文件，必须逐条给中文标题。

    少写一条，Mod+/ 弹出的总览里就会出现英文混排。
    """
    import re as _re

    body = MANAGED_FRAGMENTS["keybinds.kdl"].split("binds {", 1)[1].rsplit("}", 1)[0]
    missing: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or "{" not in line:
            continue
        if "hotkey-overlay-title=" not in line:
            missing.append(line.split("{", 1)[0].strip())
        elif not _re.search(r"[\u4e00-\u9fff]", line):
            missing.append(f"{line.split('{', 1)[0].strip()} (标题非中文)")
    assert not missing, f"以下绑定缺少中文标题，overlay 会显示英文: {missing}"


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

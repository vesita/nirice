"""Niri 控制器测试：配置片段读写、差异比对、备份与应用。"""

from __future__ import annotations

import re
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


# niri 里 Mod 是 Super 的别名，都算修饰键
_MODIFIERS = {"MOD", "SUPER", "CTRL", "ALT", "SHIFT"}


def _binding_actions(text: str) -> dict[str, str]:
    """提取 binds 块中「按键组合 -> 动作名」映射，忽略注释行。"""
    body = text.split("binds {", 1)[1].rsplit("}", 1)[0]
    actions: dict[str, str] = {}
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or "{" not in line:
            continue
        head, _, tail = line.partition("{")
        combo = head.strip().split()[0]
        actions[combo] = tail.split(";", 1)[0].strip()
    return actions


def _binding_titles(text: str) -> dict[str, str]:
    """提取 binds 块中「按键组合 -> hotkey-overlay-title」映射。

    带 `hotkey-overlay-title=null` 的绑定是刻意从总览里隐去的，不收录。
    """
    body = text.split("binds {", 1)[1].rsplit("}", 1)[0]
    titles: dict[str, str] = {}
    marker = re.compile(r'hotkey-overlay-title="([^"]*)"')
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or "{" not in line:
            continue
        head = line.split("{", 1)[0]
        match = marker.search(head)
        if match:
            titles[head.split()[0]] = match.group(1)
    return titles


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
    actions = _binding_actions(binds)

    assert "Mod+T" in binds and 'spawn "kitty"' in binds
    assert "Mod+Q" in binds and "close-window" in binds
    # Mod+R 要的是"最大化窗口"，不是循环列宽
    assert actions["Mod+R"] == "maximize-column"
    assert "Mod+D" in binds and "panel-toggle launcher" in binds
    assert "Mod+V" in binds and "panel-toggle clipboard" in binds
    assert "focus-workspace-up" in binds and "focus-workspace-down" in binds
    # 全屏已按用户要求移除
    assert "fullscreen-window" not in binds


def test_in_column_navigation_has_no_arrow_equivalent() -> None:
    """列内窗口导航只能靠 K/J —— 方向键那两组管的是跨列与跨工作区。

    所以 K/J 不是 HJKL 别名，删掉它们会彻底失去列内切窗口的能力。
    """
    actions = _binding_actions(MANAGED_FRAGMENTS["keybinds.kdl"])

    assert actions["Mod+K"] == "focus-window-up"
    assert actions["Mod+J"] == "focus-window-down"
    # 方向键承载的是另一层语义，两组不可互换
    assert actions["Mod+Up"] == "focus-workspace-up"
    assert actions["Mod+Down"] == "focus-workspace-down"


def test_only_single_modifier_bindings() -> None:
    """用户只用单修饰键组合，两个及以上修饰键（Mod+Shift / Mod+Ctrl / Ctrl+Alt）一律不绑。"""
    offenders: list[str] = []
    for combo in _binding_combos(MANAGED_FRAGMENTS["keybinds.kdl"]):
        mods = [part for part in combo.split("+") if part in _MODIFIERS]
        if len(mods) > 1:
            offenders.append(combo)
    assert not offenders, f"存在二级及以上组合键: {offenders}"


def test_alignment_bindings() -> None:
    """居中与贴边：niri 没有原生"贴边"动作，靠 move-column-to-first/last 把列移到边界。"""
    actions = _binding_actions(MANAGED_FRAGMENTS["keybinds.kdl"])

    assert actions["Mod+C"] == "center-column"
    assert actions["Mod+Z"] == "move-column-to-first"
    assert actions["Mod+X"] == "move-column-to-last"


def test_readme_keybind_table_matches_preset() -> None:
    """README 的快捷键表是预设的一份副本，必须逐条一致。

    预设才是唯一的事实源；这张表一旦与它分叉，文档就会开始骗人。
    """
    readme = Path(__file__).resolve().parents[1] / "README.md"
    section = readme.read_text(encoding="utf-8").split("## ⌨️ 默认快捷键设计", 1)[1]
    section = section.split("### Kitty", 1)[0]
    rows = [line for line in section.splitlines() if line.startswith("|")][2:]

    titles = _binding_titles(MANAGED_FRAGMENTS["keybinds.kdl"])
    assert len(rows) == len(titles), f"README 表格 {len(rows)} 行，预设 {len(titles)} 条绑定"

    cells = [line.split("|") for line in rows]
    assert [c[2].strip() for c in cells] == [f"`{combo}`" for combo in titles], "README 的按键列与预设不一致"
    assert [c[3].strip() for c in cells] == list(titles.values()), "README 的动作列与预设标题不一致"


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
    """总览里出现的绑定必须有中文标题。

    niri 的 overlay 文案是硬编码英文且没有本地化文件，少写一条就会出现英文混排。
    不想出现在总览里的绑定（如 XF86 硬件功能键）必须显式写
    `hotkey-overlay-title=null`，那才算「已处理」，而不是漏写。
    """
    body = MANAGED_FRAGMENTS["keybinds.kdl"].split("binds {", 1)[1].rsplit("}", 1)[0]
    missing: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or "{" not in line:
            continue
        if "hotkey-overlay-title=null" in line:
            continue  # 显式从总览隐去
        if "hotkey-overlay-title=" not in line:
            missing.append(line.split("{", 1)[0].strip())
        elif not re.search(r"[\u4e00-\u9fff]", line):
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

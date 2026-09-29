"""CLI 冒烟测试：命令树完整性与只读命令可执行。"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from nirice.cli import app

runner = CliRunner()


def test_root_help_lists_all_groups() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for group in ("status", "doctor", "install", "niri", "shell", "terminal", "theme", "snapshot", "migrate"):
        assert group in result.output


def test_niri_subcommands_present() -> None:
    result = runner.invoke(app, ["niri", "--help"])
    assert result.exit_code == 0
    for command in ("apply", "check", "reload", "diff", "keybinds", "animation", "outputs", "workspaces"):
        assert command in result.output


def test_shell_subcommands_present() -> None:
    result = runner.invoke(app, ["shell", "--help"])
    assert result.exit_code == 0
    for command in ("status", "reload", "theme", "panel", "bar", "templates"):
        assert command in result.output


def test_terminal_list_contains_palettes() -> None:
    result = runner.invoke(app, ["terminal", "list"])
    assert result.exit_code == 0
    assert "nord-light" in result.output
    assert "cachy-nord" in result.output


def test_terminal_export_palette() -> None:
    result = runner.invoke(app, ["terminal", "export-palette", "dracula"])
    assert result.exit_code == 0
    assert "Dracula" in result.output


def test_terminal_export_unknown_palette_fails() -> None:
    result = runner.invoke(app, ["terminal", "export-palette", "not-a-palette"])
    assert result.exit_code == 1


def test_theme_list_contains_rice_presets() -> None:
    result = runner.invoke(app, ["theme", "list"])
    assert result.exit_code == 0
    assert "nord-light" in result.output
    assert "catppuccin-mocha" in result.output


def test_niri_animations_listing() -> None:
    result = runner.invoke(app, ["niri", "animations"])
    assert result.exit_code == 0
    for preset in ("arctic", "snappy", "silky", "instant"):
        assert preset in result.output


def test_niri_keybinds_listing() -> None:
    """展示表必须由 binds 块实时解析，不能是会与预设分叉的硬编码副本。"""
    import re

    from nirice.niri.catalog import MANAGED_FRAGMENTS

    result = runner.invoke(app, ["niri", "keybinds"])
    assert result.exit_code == 0
    assert "Mod + R" in result.output

    titles = re.findall(r'hotkey-overlay-title="([^"]+)"', MANAGED_FRAGMENTS["keybinds.kdl"])
    assert titles, "预设中应存在中文标题"
    # 去掉换行，避免 rich 单元格折行导致误判
    flat = result.output.replace("\n", "")
    missing = [title for title in titles if title not in flat]
    assert not missing, f"快捷键总览缺少以下条目: {missing}"


def test_niri_keybinds_dump(tmp_path: Path) -> None:
    target = tmp_path / "keybinds.kdl"
    result = runner.invoke(app, ["niri", "keybinds", "--dump", str(target)])
    assert result.exit_code == 0
    assert "binds {" in target.read_text(encoding="utf-8")


def test_niri_apply_dry_run_writes_nothing(xdg: dict[str, Path]) -> None:
    result = runner.invoke(app, ["niri", "apply", "--dry-run"])
    assert result.exit_code == 0
    assert "演练模拟" in result.output
    assert not (xdg["config"] / "niri" / "config.kdl").exists()


def test_niri_apply_with_unknown_animation_fails(xdg: dict[str, Path]) -> None:
    result = runner.invoke(app, ["niri", "apply", "--animation", "nope", "--dry-run"])
    assert result.exit_code == 1


def test_shell_bar_position_reads_default(xdg: dict[str, Path]) -> None:
    result = runner.invoke(app, ["shell", "bar", "position"])
    assert result.exit_code == 0
    assert "top" in result.output


def test_shell_bar_position_writes(xdg: dict[str, Path]) -> None:
    result = runner.invoke(app, ["shell", "bar", "position", "left"])
    assert result.exit_code == 0
    settings = (xdg["state"] / "noctalia" / "settings.toml").read_text(encoding="utf-8")
    assert 'position = "left"' in settings


def test_shell_bar_position_rejects_invalid(xdg: dict[str, Path]) -> None:
    result = runner.invoke(app, ["shell", "bar", "position", "sideways"])
    assert result.exit_code == 0
    assert "无效" in result.output


def test_migrate_plan_runs(xdg: dict[str, Path]) -> None:
    result = runner.invoke(app, ["migrate", "plan"])
    assert result.exit_code == 0
    assert "迁移检测" in result.output

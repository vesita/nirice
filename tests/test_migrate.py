"""迁移规划器测试：KDE 残留检测与可逆归档。"""

from __future__ import annotations

from pathlib import Path

from nirice.system import MigrationPlanner
from nirice.system import installer as installer_module
from nirice.system.kde_data import KDE_CONFIG_FILES


def test_plan_has_expected_phases(xdg: dict[str, Path], monkeypatch) -> None:
    # 「缺失组件」这一步只在真有组件缺失时才生成。测试不能依赖宿主机装没装
    # noctalia / gnome-keyring —— 那样同一份代码在不同机器上会给出不同结果。
    # 这里强制一个必需组件探测失败，让阶段 1 的出现变成确定性的。
    original = installer_module.DependencyHelper.package_defs

    def defs_with_one_missing(self):
        defs = original(self)
        for definition in defs:
            if definition.essential:
                definition.probes = (lambda: False,)
                break
        return defs

    monkeypatch.setattr(installer_module.DependencyHelper, "package_defs", defs_with_one_missing)

    plan = MigrationPlanner(home_dir=xdg["home"]).build_plan()
    phases = list(plan.grouped())

    assert any("补齐 Niri 组件" in p for p in phases)
    assert any("接管配置" in p for p in phases)
    assert any("校验" in p for p in phases)
    assert plan.steps, "计划不应为空"


def test_plan_never_auto_removes_packages(xdg: dict[str, Path]) -> None:
    """卸载 KDE 软件包必须是不可自动执行的步骤。"""
    plan = MigrationPlanner(home_dir=xdg["home"]).build_plan()
    for step in plan.steps:
        if step.command and " -Rns " in step.command:
            assert step.auto is False, "卸载步骤不应被标记为可自动执行"


def test_detects_planted_kde_configs(xdg: dict[str, Path]) -> None:
    config = xdg["config"]
    (config / "kdeglobals").write_text("[General]\n", encoding="utf-8")
    (config / "kwinrc").write_text("[Plugins]\n", encoding="utf-8")
    (config / "autostart").mkdir(parents=True, exist_ok=True)
    (config / "autostart" / "kdeconnect.desktop").write_text("[Desktop Entry]\nName=KDE Connect\n", encoding="utf-8")

    planner = MigrationPlanner(home_dir=xdg["home"])
    found = planner.detect_kde_configs()

    assert any("kdeglobals" in item for item in found)
    assert any("kwinrc" in item for item in found)
    assert any("kdeconnect" in item for item in found)


def test_clean_configs_archives_without_deleting(xdg: dict[str, Path]) -> None:
    config = xdg["config"]
    (config / "kdeglobals").write_text("[General]\n", encoding="utf-8")
    (config / "kwinrc").write_text("[Plugins]\n", encoding="utf-8")

    planner = MigrationPlanner(home_dir=xdg["home"])
    results = planner.clean_kde_configs(dry_run=False)

    assert results and all(ok for _, ok, _ in results)
    assert not (config / "kdeglobals").exists(), "原位置应已移走"

    archive = xdg["cache"] / "nirice" / "kde-leftovers" / ".config"
    assert (archive / "kdeglobals").exists(), "归档中应能找回"


def test_clean_configs_dry_run_keeps_files(xdg: dict[str, Path]) -> None:
    (xdg["config"] / "kdeglobals").write_text("[General]\n", encoding="utf-8")
    planner = MigrationPlanner(home_dir=xdg["home"])

    results = planner.clean_kde_configs(dry_run=True)
    assert results
    assert (xdg["config"] / "kdeglobals").exists(), "演练模拟不得移动文件"


def test_kde_config_list_covers_core_files() -> None:
    for expected in ("kdeglobals", "kwinrc", "plasmarc", "ksplashrc"):
        assert expected in KDE_CONFIG_FILES

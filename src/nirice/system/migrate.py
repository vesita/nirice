"""KDE → Niri 迁移规划器。

检测 KDE 残留与 Niri 生态缺口，生成分阶段可执行计划。
删除 KDE 软件包这类不可逆操作只输出命令，绝不自动执行。
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from nirice.core import XDGPaths
from nirice.system import installer as installer_module
from nirice.system.kde_data import (
    KDE_AUTOSTART_TAGS,
    KDE_CONFIG_FILES,
    KDE_DATA_DIRS,
    KDE_PACKAGES,
)


@dataclass
class MigrationStep:
    """迁移计划中的单个步骤。"""

    phase: str
    title: str
    detail: str
    command: str | None = None
    essential: bool = False
    done: bool = False
    auto: bool = False

    @property
    def status_icon(self) -> str:
        if self.done:
            return "✓"
        return "!" if self.essential else "·"


@dataclass
class MigrationPlan:
    """完整迁移计划。"""

    steps: list[MigrationStep] = field(default_factory=list)
    detected_kde_packages: list[str] = field(default_factory=list)
    detected_kde_configs: list[str] = field(default_factory=list)
    missing_niri_packages: list[str] = field(default_factory=list)
    missing_portal_conf: bool = False

    @property
    def pending_essential(self) -> list[MigrationStep]:
        return [s for s in self.steps if s.essential and not s.done]

    def grouped(self) -> dict[str, list[MigrationStep]]:
        grouped: dict[str, list[MigrationStep]] = {}
        for step in self.steps:
            grouped.setdefault(step.phase, []).append(step)
        return grouped


class MigrationPlanner:
    """检测 KDE 残留与 Niri 组件缺口，生成迁移计划。"""

    def __init__(self, home_dir: Path | None = None) -> None:
        self.paths = XDGPaths.resolve(home_dir)
        self.home = self.paths.home
        self.config_dir = self.paths.config
        self.data_dir = self.paths.data
        self.helper = installer_module.DependencyHelper(home_dir=self.home)

    # ==================== 检测 ====================

    @staticmethod
    def _pacman_installed(name: str) -> bool:
        if not shutil.which("pacman"):
            return False
        result = subprocess.run(["pacman", "-Qq", name], capture_output=True, text=True, check=False)
        return result.returncode == 0

    def detect_kde_packages(self) -> list[str]:
        return [pkg for pkg in KDE_PACKAGES if self._pacman_installed(pkg)]

    def detect_kde_configs(self) -> list[str]:
        found: list[str] = []
        for name in KDE_CONFIG_FILES:
            if (self.config_dir / name).exists():
                found.append(f"~/.config/{name}")
        for name in KDE_DATA_DIRS:
            if (self.data_dir / name).exists():
                found.append(f"~/.local/share/{name}")

        autostart = self.config_dir / "autostart"
        if autostart.exists():
            for entry in sorted(autostart.glob("*.desktop")):
                try:
                    content = entry.read_text(encoding="utf-8", errors="ignore").lower()
                except OSError:
                    continue
                if any(tag in content for tag in KDE_AUTOSTART_TAGS):
                    found.append(f"~/.config/autostart/{entry.name}")
        return found

    def has_niri_portal_conf(self) -> bool:
        return Path("/usr/share/xdg-desktop-portal/niri-portals.conf").exists()

    def has_wayland_session(self) -> bool:
        return any(
            Path(p).exists()
            for p in (
                "/usr/share/wayland-sessions/niri.desktop",
                "/usr/local/share/wayland-sessions/niri.desktop",
            )
        )

    def current_session(self) -> str:
        return os.environ.get("XDG_CURRENT_DESKTOP", os.environ.get("DESKTOP_SESSION", "未知"))

    # ==================== 计划 ====================

    def build_plan(self) -> MigrationPlan:
        plan = MigrationPlan()
        plan.detected_kde_packages = self.detect_kde_packages()
        plan.detected_kde_configs = self.detect_kde_configs()
        plan.missing_portal_conf = not self.has_niri_portal_conf()

        statuses = self.helper.check_all()
        plan.missing_niri_packages = [s.name for s in statuses if not s.installed and s.essential]
        installer = self.helper.installer_command()

        for status in statuses:
            if status.installed:
                continue
            plan.steps.append(
                MigrationStep(
                    phase="1 · 补齐 Niri 组件",
                    title=status.name,
                    detail=f"[{status.category}] {status.description}",
                    command=status.install_command,
                    essential=status.essential,
                    auto=True,
                )
            )

        if plan.missing_portal_conf:
            plan.steps.append(
                MigrationStep(
                    phase="1 · 补齐 Niri 组件",
                    title="niri-portals.conf",
                    detail="缺少门户路由配置，截图/文件选择器/屏幕共享会失效",
                    command=f"{installer} xdg-desktop-portal-gnome xdg-desktop-portal-gtk",
                    essential=True,
                    auto=True,
                )
            )

        if not self.has_wayland_session():
            plan.steps.append(
                MigrationStep(
                    phase="1 · 补齐 Niri 组件",
                    title="niri 会话入口",
                    detail="/usr/share/wayland-sessions/niri.desktop 不存在，显示管理器里选不到 Niri",
                    command=f"{installer} niri",
                    essential=True,
                    auto=True,
                )
            )

        plan.steps.extend(
            [
                MigrationStep(
                    "2 · 接管配置",
                    "生成 Niri 分片配置",
                    "写入 animation/keybinds/input/layout/rules/misc 与主入口 config.kdl",
                    "nirice niri apply",
                    essential=True,
                    auto=True,
                ),
                MigrationStep(
                    "2 · 接管配置",
                    "启用 Noctalia 模板",
                    "让 kitty / starship / niri / GTK / Qt 配色随外壳主题自动生成",
                    "nirice shell templates enable",
                    auto=True,
                ),
                MigrationStep(
                    "2 · 接管配置",
                    "状态栏位置与主题",
                    "把 Noctalia 状态栏移动到左侧并设定 Nord 浅色主题",
                    "nirice shell bar position left",
                    auto=True,
                ),
                MigrationStep(
                    "2 · 接管配置",
                    "Kitty 美学层",
                    "字体 / 磨砂 / 圆角药丸 Tab / 快捷键（配色仍由 Noctalia 提供）",
                    "nirice terminal set-kitty",
                    auto=True,
                ),
            ]
        )

        if plan.detected_kde_configs:
            plan.steps.append(
                MigrationStep(
                    phase="3 · 清理 KDE 残留",
                    title=f"归档 {len(plan.detected_kde_configs)} 个 KDE 配置项",
                    detail="移动到 ~/.cache/nirice/kde-leftovers/，可随时找回（不删除）",
                    command="nirice migrate clean-configs",
                    auto=True,
                )
            )
        if plan.detected_kde_packages:
            plan.steps.append(
                MigrationStep(
                    phase="3 · 清理 KDE 残留",
                    title=f"卸载 {len(plan.detected_kde_packages)} 个 KDE 软件包",
                    detail="不可逆操作，nirice 只给出命令，请确认后自行执行",
                    command=f"{installer} -Rns {' '.join(plan.detected_kde_packages)}",
                    auto=False,
                )
            )

        plan.steps.extend(
            [
                MigrationStep(
                    "4 · 校验",
                    "校验 Niri 配置语法",
                    "niri validate 检查生成的分片配置",
                    "nirice niri check",
                    essential=True,
                    auto=True,
                ),
                MigrationStep(
                    "4 · 校验",
                    "重新登录 Niri 会话",
                    "注销后在显示管理器选择 Niri，验证状态栏、终端与快捷键",
                    None,
                    essential=True,
                    auto=False,
                ),
            ]
        )
        return plan

    # ==================== 清理 ====================

    def clean_kde_configs(self, dry_run: bool = False) -> list[tuple[str, bool, str]]:
        """把 KDE 残留配置归档到 ~/.cache/nirice/kde-leftovers/（可逆）。"""
        archive_root = self.paths.cache_path("nirice", "kde-leftovers")
        results: list[tuple[str, bool, str]] = []

        candidates: list[Path] = [
            self.config_dir / name for name in KDE_CONFIG_FILES if (self.config_dir / name).exists()
        ]
        candidates += [self.data_dir / name for name in KDE_DATA_DIRS if (self.data_dir / name).exists()]

        for path in candidates:
            if dry_run:
                results.append((str(path), True, "[演练模拟] 将归档"))
                continue
            relative = path.relative_to(self.home) if str(path).startswith(str(self.home)) else Path(path.name)
            dest = archive_root / relative
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=True)
                shutil.move(str(path), str(dest))
                results.append((str(path), True, f"已归档到 {dest}"))
            except OSError as exc:
                results.append((str(path), False, f"归档失败: {exc}"))
        return results

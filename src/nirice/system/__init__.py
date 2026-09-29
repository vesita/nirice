"""系统层支持：依赖审计、包安装与 KDE → Niri 迁移。"""

from nirice.system.installer import DependencyHelper, DoctorReport, PackageStatus, ShellHookStatus
from nirice.system.migrate import MigrationPlan, MigrationPlanner, MigrationStep

__all__ = [
    "DependencyHelper",
    "DoctorReport",
    "PackageStatus",
    "ShellHookStatus",
    "MigrationPlanner",
    "MigrationPlan",
    "MigrationStep",
]

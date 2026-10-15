"""写前备份：把即将被覆盖的文件复制到 XDG 缓存目录，并裁剪过旧备份。"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from nirice.core.paths import XDGPaths

# 每个备份目录保留的时间戳份数
BACKUP_KEEP = 20


def _prune(backup_dir: Path, keep: int) -> None:
    if not backup_dir.exists():
        return
    for stale in sorted((d for d in backup_dir.iterdir() if d.is_dir()), reverse=True)[keep:]:
        shutil.rmtree(stale, ignore_errors=True)


def backup_file(src: Path, label: str, *, paths: XDGPaths | None = None, keep: int = BACKUP_KEEP) -> Path | None:
    """把 src 备份到 `<cache>/nirice/backups/<label>/<时间戳>/<原名>`，只保留最近 keep 份。

    源文件不存在或复制失败时返回 None，调用方继续执行覆盖。
    """
    if not src.exists():
        return None
    backup_dir = (paths or XDGPaths.resolve()).backup_path(label)
    target_dir = backup_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / src.name
    try:
        shutil.copy2(src, dest)
    except OSError:
        return None
    _prune(backup_dir, keep)
    return dest

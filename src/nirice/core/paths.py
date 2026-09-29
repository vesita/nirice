"""XDG 基础目录的统一解析，避免各控制器重复拼路径。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class XDGPaths:
    """一次解析、全局复用的 XDG 目录集合。"""

    home: Path
    config: Path
    data: Path
    state: Path
    cache: Path

    @classmethod
    def resolve(cls, home: Path | None = None) -> XDGPaths:
        """按 XDG 规范解析目录，未设置环境变量时回退到标准默认值。"""
        resolved_home = home or Path.home()
        return cls(
            home=resolved_home,
            config=Path(os.environ.get("XDG_CONFIG_HOME", str(resolved_home / ".config"))),
            data=Path(os.environ.get("XDG_DATA_HOME", str(resolved_home / ".local" / "share"))),
            state=Path(os.environ.get("XDG_STATE_HOME", str(resolved_home / ".local" / "state"))),
            cache=Path(os.environ.get("XDG_CACHE_HOME", str(resolved_home / ".cache"))),
        )

    def config_path(self, *parts: str) -> Path:
        return self.config.joinpath(*parts)

    def data_path(self, *parts: str) -> Path:
        return self.data.joinpath(*parts)

    def state_path(self, *parts: str) -> Path:
        return self.state.joinpath(*parts)

    def cache_path(self, *parts: str) -> Path:
        return self.cache.joinpath(*parts)

    def backup_path(self, *parts: str) -> Path:
        """nirice/nirice 的统一备份根目录。"""
        return self.cache_path("nirice", "backups", *parts)

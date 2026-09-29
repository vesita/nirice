"""pytest 公共夹具：把 XDG 目录重定向到临时路径，保证测试不污染真实环境。"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    """隔离 HOME 与全部 XDG 目录。"""
    home = tmp_path / "home"
    paths = {
        "home": home,
        "config": home / ".config",
        "data": home / ".local" / "share",
        "state": home / ".local" / "state",
        "cache": home / ".cache",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(paths["config"]))
    monkeypatch.setenv("XDG_DATA_HOME", str(paths["data"]))
    monkeypatch.setenv("XDG_STATE_HOME", str(paths["state"]))
    monkeypatch.setenv("XDG_CACHE_HOME", str(paths["cache"]))
    return paths

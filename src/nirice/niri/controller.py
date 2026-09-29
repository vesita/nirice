"""Niri 合成器控制器：配置片段管理、校验、热重载与实时状态查询。"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from nirice.core import XDGPaths, run_capture, which
from nirice.niri.catalog import MANAGED_FRAGMENTS
from nirice.niri.fragments import CONFIG_KDL, DISPLAY_KDL

BACKUP_KEEP = 20


@dataclass
class FragmentResult:
    """单个配置片段的写入结果。"""

    name: str
    path: Path
    changed: bool
    created: bool
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error

    def describe(self) -> str:
        if self.error:
            return f"失败: {self.error}"
        if self.created:
            return "已创建"
        if self.changed:
            return "已更新"
        return "已是最新"


class NiriController:
    """管理 `~/.config/niri` 下的分片配置，并驱动 niri 校验与热重载。"""

    def __init__(
        self,
        dry_run: bool = False,
        home_dir: Path | None = None,
        config_dir: Path | None = None,
        binary: str | None = None,
    ) -> None:
        self.dry_run = dry_run
        self.paths = XDGPaths.resolve(home_dir)
        self.home = self.paths.home
        override = config_dir or self.paths.config
        self.niri_dir = override / "niri"
        self.cfg_dir = self.niri_dir / "cfg"
        self.backup_dir = self.paths.backup_path("niri")
        self.niri_bin = binary if binary is not None else which("niri")

    # ==================== 运行状态与实时查询 ====================

    def is_installed(self) -> bool:
        return bool(self.niri_bin)

    def is_running(self) -> bool:
        ok, _ = self._niri(["msg", "version"])
        return ok

    def get_version(self) -> str:
        ok, out = self._niri(["msg", "version"])
        if ok:
            for line in out.splitlines():
                if line.lower().startswith("compositor version"):
                    return line.split(":", 1)[1].strip()
        return "已安装（未运行）" if self.niri_bin else "未安装"

    def get_outputs(self) -> dict[str, Any]:
        """查询显示器输出（`niri msg --json outputs`）。"""
        return self._json(["--json", "outputs"], default={})

    def get_workspaces(self) -> list[dict[str, Any]]:
        """查询工作区列表（`niri msg --json workspaces`）。"""
        return self._json(["--json", "workspaces"], default=[])

    def get_focused_output(self) -> str:
        data = self._json(["--json", "focused-output"], default={})
        return data.get("name", "") if isinstance(data, dict) else ""

    def _niri(self, args: list[str], timeout: int = 5) -> tuple[bool, str]:
        if not self.niri_bin:
            return False, "未找到 niri 可执行文件"
        return run_capture([self.niri_bin, *args], timeout=timeout)

    def _json(self, args: list[str], default: Any) -> Any:
        ok, out = self._niri(args)
        if not ok:
            return default
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            return default

    # ==================== 校验与重载 ====================

    def validate(self, config_path: Path | None = None) -> tuple[bool, str]:
        """调用 `niri validate` 校验配置语法。"""
        target = config_path or (self.niri_dir / "config.kdl")
        if not self.niri_bin:
            return False, "未找到 niri，无法校验配置"
        if not target.exists():
            return False, f"配置文件不存在: {target}"
        ok, out = self._niri(["validate", "-c", str(target)], timeout=15)
        return (True, "配置语法校验通过") if ok else (False, out)

    def reload(self) -> tuple[bool, str]:
        """热重载 niri 配置（无需注销）。"""
        if self.dry_run:
            return True, "[演练模拟] 已请求 niri 热重载"
        ok, out = self._niri(["msg", "action", "load-config-file"])
        if ok:
            return True, "niri 配置已热重载"
        return False, f"niri 热重载失败: {out or '未检测到运行中的 niri'}"

    def run_action(self, action: str, *args: str) -> tuple[bool, str]:
        """执行单个 niri 动作（如 center-column）。"""
        if self.dry_run:
            return True, f"[演练模拟] niri 动作: {action}"
        return self._niri(["msg", "action", action, *args])

    # ==================== 配置片段读写 ====================

    def fragment_path(self, name: str) -> Path:
        return self.cfg_dir / name

    def read_fragment(self, name: str) -> str | None:
        path = self.fragment_path(name)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8", errors="ignore")

    def diff_fragments(self, fragments: dict[str, str] | None = None) -> dict[str, str]:
        """比较目标片段与磁盘现状，返回 {文件名: missing|changed|same}。"""
        targets = fragments if fragments is not None else MANAGED_FRAGMENTS
        status: dict[str, str] = {}
        for name, content in targets.items():
            current = self.read_fragment(name)
            if current is None:
                status[name] = "missing"
            elif current.rstrip("\n") != content.rstrip("\n"):
                status[name] = "changed"
            else:
                status[name] = "same"
        return status

    def backup_file(self, path: Path) -> Path | None:
        """把即将被覆盖的文件备份到 ~/.cache/nirice/backups/niri/<时间戳>/。"""
        if not path.exists():
            return None
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = self.backup_dir / stamp
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / path.name
        try:
            shutil.copy2(path, dest)
        except OSError:
            return None
        self._prune_backups()
        return dest

    def _prune_backups(self) -> None:
        if not self.backup_dir.exists():
            return
        dirs = sorted((d for d in self.backup_dir.iterdir() if d.is_dir()), reverse=True)
        for stale in dirs[BACKUP_KEEP:]:
            shutil.rmtree(stale, ignore_errors=True)

    def _write_text(self, path: Path, content: str, backup: bool) -> str | None:
        """写文件，成功返回 None，失败返回错误信息。"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if backup and path.exists():
                self.backup_file(path)
            normalized = content if content.endswith("\n") else content + "\n"
            path.write_text(normalized, encoding="utf-8")
        except OSError as exc:
            return str(exc)
        return None

    def write_fragment(self, name: str, content: str, backup: bool = True) -> FragmentResult:
        """写入单个受管片段（内容未变化时不动磁盘）。"""
        path = self.fragment_path(name)
        current = self.read_fragment(name)
        if current is not None and current.rstrip("\n") == content.rstrip("\n"):
            return FragmentResult(name, path, changed=False, created=False)
        if self.dry_run:
            return FragmentResult(name, path, changed=True, created=current is None)
        error = self._write_text(path, content, backup)
        return FragmentResult(name, path, changed=not error, created=current is None, error=error or "")

    def write_root_config(self, backup: bool = True) -> FragmentResult:
        """写入 `config.kdl` 主入口。"""
        return self._write_named("config.kdl", self.niri_dir / "config.kdl", CONFIG_KDL, backup)

    def ensure_display_fragment(self) -> FragmentResult:
        """仅在缺失时创建 display.kdl —— 该文件与硬件绑定，绝不覆盖。"""
        path = self.fragment_path("display.kdl")
        if path.exists():
            return FragmentResult("display.kdl", path, changed=False, created=False)
        if self.dry_run:
            return FragmentResult("display.kdl", path, changed=True, created=True)
        error = self._write_text(path, DISPLAY_KDL, backup=False)
        return FragmentResult("display.kdl", path, changed=not error, created=True, error=error or "")

    def _write_named(self, name: str, path: Path, content: str, backup: bool) -> FragmentResult:
        current = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else None
        if current is not None and current.rstrip("\n") == content.rstrip("\n"):
            return FragmentResult(name, path, changed=False, created=False)
        if self.dry_run:
            return FragmentResult(name, path, changed=True, created=current is None)
        error = self._write_text(path, content, backup)
        return FragmentResult(name, path, changed=not error, created=current is None, error=error or "")

    def apply_all(
        self,
        fragments: dict[str, str] | None = None,
        skip: list[str] | None = None,
        backup: bool = True,
    ) -> list[FragmentResult]:
        """应用全部受管片段 + 主入口，返回每个文件的结果。"""
        targets = dict(fragments if fragments is not None else MANAGED_FRAGMENTS)
        skip_set = {s.strip() for s in (skip or [])}

        results = [
            self.write_fragment(name, content, backup=backup)
            for name, content in targets.items()
            if name not in skip_set
        ]
        if "config.kdl" not in skip_set:
            results.append(self.write_root_config(backup=backup))
        if "display.kdl" not in skip_set:
            results.append(self.ensure_display_fragment())
        return results

    def dump_keybinds(self, destination: Path | None = None) -> Path:
        """导出当前快捷键配置，供用户手工定制。"""
        dest = destination or (self.niri_dir / "keybinds.kdl")
        content = self.read_fragment("keybinds.kdl") or MANAGED_FRAGMENTS["keybinds.kdl"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        return dest

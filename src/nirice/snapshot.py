"""配置快照与跨机器迁移引擎（Niri + Noctalia 生态）。

打包范围聚焦「换机后真正需要带走的东西」：
Niri 分片配置、Noctalia 设置（含状态栏位置与模板开关）、终端与 Shell 配置。
"""

from __future__ import annotations

import io
import json
import os
import shutil
import socket
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Any

from nirice.core import XDGPaths, pkill, run_quiet, which
from nirice.system import DependencyHelper

# (类别, 相对路径)；类别决定解包时的目标根目录
TRACKED_TARGETS: list[tuple[str, str]] = [
    # 1. Niri 合成器（config.kdl + cfg/ 分片 + noctalia 自动生成的配色 include）
    ("config", "niri"),
    # 2. Noctalia：settings.toml 里存着状态栏位置、主题与模板开关
    ("state", "noctalia/settings.toml"),
    ("config", "noctalia"),
    # 3. 终端
    ("config", "kitty"),
    ("config", "alacritty"),
    ("config", "ghostty"),
    ("config", "foot"),
    ("config", "wezterm"),
    ("config", "zellij"),
    # 4. Shell 与提示符
    ("config", "starship.toml"),
    ("config", "fastfetch"),
    ("config", "fish/config.fish"),
    ("config", "fish/conf.d"),
    ("config", "fish/functions"),
    # 5. 桌面集成
    ("config", "gtk-3.0"),
    ("config", "gtk-4.0"),
    ("config", "environment.d"),
    ("config", "xdg-desktop-portal"),
    ("config", "fcitx5"),
    ("config", "mimeapps.list"),
    ("home", ".vscode/argv.json"),
]

CATEGORY_ROOTS = {
    "config": "config",
    "data": "data",
    "state": "state",
    "home": "home",
}


class SnapshotManager:
    """把 Niri/Noctalia/终端配置打包为便携快照，并可在新机器上无损还原。"""

    def __init__(self, dry_run: bool = False, home_dir: Path | None = None) -> None:
        self.dry_run = dry_run
        self.paths = XDGPaths.resolve(home_dir)
        self.home = self.paths.home
        self.config_dir = self.paths.config
        self.data_dir = self.paths.data
        self.state_dir = self.paths.state
        self.backup_dir = self.paths.backup_path("snapshot")
        self.installer = DependencyHelper(home_dir=self.home)

    # ==================== 路径解析 ====================

    def _resolve_source(self, category: str, rel_path: str) -> Path:
        root = {
            "config": self.config_dir,
            "data": self.data_dir,
            "state": self.state_dir,
            "home": self.home,
        }.get(category)
        return (root or self.home) / rel_path

    def _resolve_target(self, category: str) -> Path | None:
        if category not in CATEGORY_ROOTS:
            return None
        return {
            "config": self.config_dir,
            "data": self.data_dir,
            "state": self.state_dir,
            "home": self.home,
        }[category]

    # ==================== 打包 ====================

    def create_snapshot(self, output_path: Path | None = None, name: str | None = None) -> Path:
        """把受管配置打包为压缩快照（.pmz）。"""
        now = datetime.now()
        profile_name = name or f"niri_rice_{now.strftime('%Y%m%d_%H%M%S')}"

        if output_path is None:
            output_dir = Path.cwd() / "snapshots"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{profile_name}.pmz"
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        metadata: dict[str, Any] = {
            "name": profile_name,
            "created_at": now.isoformat(),
            "hostname": socket.gethostname(),
            "scope": "Niri + Noctalia Rice (niri config, noctalia settings, kitty & terminal configs)",
            "files": [],
        }

        with tarfile.open(output_path, "w:gz") as tar:
            for category, rel_path in TRACKED_TARGETS:
                src = self._resolve_source(category, rel_path)
                if src.exists():
                    tar.add(src, arcname=f"{category}/{rel_path}", recursive=True)

            # 记录归档中的真实成员（目录目标会展开为多个文件）
            metadata["files"] = [name for name in tar.getnames() if name != "metadata.json"]

            meta_bytes = json.dumps(metadata, indent=2, ensure_ascii=False).encode("utf-8")
            tarinfo = tarfile.TarInfo(name="metadata.json")
            tarinfo.size = len(meta_bytes)
            tarinfo.mtime = int(now.timestamp())
            tar.addfile(tarinfo, io.BytesIO(meta_bytes))

        return output_path

    def inspect_snapshot(self, snapshot_path: Path) -> dict[str, Any]:
        """读取快照元数据与文件清单，不落盘。"""
        if not snapshot_path.exists():
            raise FileNotFoundError(f"未找到快照: {snapshot_path}")
        with tarfile.open(snapshot_path, "r:gz") as tar:
            try:
                meta_file = tar.extractfile("metadata.json")
                if meta_file:
                    return json.loads(meta_file.read().decode("utf-8"))
            except KeyError:
                pass
            return {"files": tar.getnames()}

    # ==================== 还原 ====================

    def restore_snapshot(
        self,
        snapshot_path: Path,
        create_backup: bool = True,
        install_deps: bool = False,
        wire_shell_hooks: bool = True,
    ) -> list[str]:
        """把快照还原到当前用户环境，并在可用时热重载各组件。"""
        if not snapshot_path.exists():
            raise FileNotFoundError(f"未找到快照: {snapshot_path}")

        restored_items: list[str] = []

        if install_deps and not self.dry_run:
            missing = self.installer.missing_packages(essential_only=True)
            if missing:
                self.installer.install_packages(missing)

        if create_backup and not self.dry_run:
            self._backup_current()

        with tarfile.open(snapshot_path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name == "metadata.json":
                    continue
                parts = Path(member.name).parts
                if not parts:
                    continue
                base = self._resolve_target(parts[0])
                if base is None:
                    continue
                self._extract_member(tar, member, base / Path(*parts[1:]), restored_items)

        if not self.dry_run:
            self.reload_components(wire_shell_hooks)
        return restored_items

    def _backup_current(self) -> None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_dir / f"backup_before_{stamp}"
        for category, rel_path in TRACKED_TARGETS:
            src = self._resolve_source(category, rel_path)
            if not src.exists():
                continue
            dst = backup_dir / category / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                if src.is_dir():
                    shutil.copytree(src, dst, symlinks=True, ignore_dangling_symlinks=True, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst, follow_symlinks=False)
            except OSError:
                continue

    def _extract_member(self, tar: tarfile.TarFile, member: tarfile.TarInfo, dest: Path, restored: list[str]) -> None:
        restored.append(str(dest))
        if self.dry_run:
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        if member.isdir():
            dest.mkdir(parents=True, exist_ok=True)
        elif member.issym():
            if dest.is_symlink() or dest.exists():
                try:
                    dest.unlink()
                except OSError:
                    pass
            try:
                os.symlink(member.linkname, dest)
            except OSError:
                pass
        elif member.isreg():
            extracted = tar.extractfile(member)
            if extracted:
                dest.write_bytes(extracted.read())

    # ==================== 热重载 ====================

    def reload_components(self, wire_shell_hooks: bool = True) -> None:
        """让还原后的配置立即生效，全部使用各软件官方的重载机制。"""
        if wire_shell_hooks:
            self.installer.inject_shell_hooks(["fish", "zsh", "bash"])

        if which("noctalia"):
            run_quiet(["noctalia", "msg", "config-reload"], timeout=8)
            run_quiet(["noctalia", "msg", "templates-apply"], timeout=15)

        if which("niri"):
            run_quiet(["niri", "msg", "action", "load-config-file"], timeout=8)

        pkill("-USR1", "kitty")

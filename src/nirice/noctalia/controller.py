"""Noctalia 桌面外壳控制器：状态栏、主题、模板渲染与消息总线。"""

from __future__ import annotations

import json
import shutil
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

from nirice.core import XDGPaths, format_value, get_key, run_capture, set_key, which
from nirice.noctalia.templates import (
    BAR_POSITIONS,
    BUILTIN_MANIFEST,
    PANEL_IDS,
    TEMPLATE_FOR_APP,
    THEME_MODES,
)


class NoctaliaController:
    """管理 Noctalia 外壳的状态栏布局与主题，并通过 `noctalia msg` 实时生效。"""

    def __init__(
        self,
        dry_run: bool = False,
        home_dir: Path | None = None,
        binary: str | None = None,
    ) -> None:
        self.dry_run = dry_run
        self.paths = XDGPaths.resolve(home_dir)
        self.home = self.paths.home
        self.state_dir = self.paths.state_path("noctalia")
        self.config_dir = self.paths.config_path("noctalia")
        self.settings_path = self.state_dir / "settings.toml"
        self.config_path = self.config_dir / "config.toml"
        self.backup_dir = self.paths.backup_path("noctalia")
        self.noctalia_bin = binary if binary is not None else which("noctalia")

    # ==================== 基础状态 ====================

    def is_installed(self) -> bool:
        return bool(self.noctalia_bin)

    def is_running(self) -> bool:
        ok, _ = self.msg("status")
        return ok

    def read_settings(self) -> dict[str, Any]:
        """解析 settings.toml（不存在或损坏时返回空字典）。"""
        if not self.settings_path.exists():
            return {}
        try:
            with self.settings_path.open("rb") as handle:
                return tomllib.load(handle)
        except (tomllib.TOMLDecodeError, OSError):
            return {}

    def get_bar_position(self) -> str:
        return self.read_settings().get("bar", {}).get("position", "top")

    def get_dock_position(self) -> str:
        return self.read_settings().get("dock", {}).get("position", "left")

    def get_theme(self) -> tuple[str, str]:
        theme = self.read_settings().get("theme", {})
        return theme.get("builtin", "Nord"), theme.get("mode", "dark")

    # ==================== settings.toml 写入 ====================

    def _ensure_settings_file(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if not self.settings_path.exists():
            self.settings_path.write_text("", encoding="utf-8")

    def _backup(self) -> Path | None:
        if not self.settings_path.exists():
            return None
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = self.backup_dir / stamp
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / self.settings_path.name
        try:
            shutil.copy2(self.settings_path, dest)
        except OSError:
            return None
        return dest

    def write_setting(self, section: str, key: str, value: Any) -> tuple[bool, str]:
        """写入 settings.toml 中的单个键；值未变化时不动磁盘。"""
        if self.dry_run:
            return True, f"[演练模拟] 将设置 [{section}] {key} = {format_value(value)}"
        try:
            self._ensure_settings_file()
            original = self.settings_path.read_text(encoding="utf-8")
            existing = get_key(original, section, key)
            if existing in (format_value(value), str(value)):
                return True, f"[{section}] {key} 已是最新值"
            updated = set_key(original, section, key, value)
            if updated != original:
                self._backup()
                self.settings_path.write_text(updated, encoding="utf-8")
            return True, f"已设置 [{section}] {key} = {format_value(value)}"
        except OSError as exc:
            return False, f"写入 Noctalia 设置失败: {exc}"

    # ==================== 语义化操作 ====================

    def set_bar_position(self, position: str) -> tuple[bool, str]:
        """把状态栏移动到指定屏幕边缘。"""
        pos = position.strip().lower()
        if pos not in BAR_POSITIONS:
            return False, f"无效的状态栏位置 '{position}'，可选: {', '.join(BAR_POSITIONS)}"
        if self.settings_path.exists() and self.get_bar_position() == pos:
            return True, f"状态栏已在 '{pos}' 位置"
        return self.write_setting("bar", "position", pos)

    def set_dock_position(self, position: str) -> tuple[bool, str]:
        pos = position.strip().lower()
        if pos not in BAR_POSITIONS:
            return False, f"无效的 Dock 位置 '{position}'，可选: {', '.join(BAR_POSITIONS)}"
        return self.write_setting("dock", "position", pos)

    def set_theme(self, palette: str | None = None, mode: str | None = None) -> tuple[bool, str]:
        """设置内置配色方案与明暗模式。"""
        messages: list[str] = []
        if palette:
            ok, msg = self.write_setting("theme", "builtin", palette)
            if not ok:
                return False, msg
            messages.append(f"配色={palette}")
        if mode:
            mode_lower = mode.strip().lower()
            if mode_lower not in THEME_MODES:
                return False, f"无效主题模式 '{mode}'，可选: {', '.join(THEME_MODES)}"
            ok, msg = self.write_setting("theme", "mode", mode_lower)
            if not ok:
                return False, msg
            messages.append(f"模式={mode_lower}")
        if not messages:
            return False, "未指定配色或模式"
        return True, "Noctalia 主题已更新（" + "，".join(messages) + "）"

    def toggle_panel(self, panel_id: str) -> tuple[bool, str]:
        if panel_id not in PANEL_IDS:
            return False, f"未知面板 '{panel_id}'，可用: {', '.join(PANEL_IDS)}"
        return self.msg("panel-toggle", panel_id)

    # ==================== 主题模板 ====================

    def available_builtin_templates(self) -> dict[str, str]:
        """列出内置模板 {id: 显示名}，以官方 builtin.toml 为准。"""
        manifest = Path(BUILTIN_MANIFEST)
        if not manifest.exists():
            return {}
        try:
            with manifest.open("rb") as handle:
                data = tomllib.load(handle)
        except (tomllib.TOMLDecodeError, OSError):
            return {}
        return {key: value.get("name", key) for key, value in data.get("catalog", {}).items()}

    def get_enabled_templates(self) -> list[str]:
        ids = self.read_settings().get("theme", {}).get("templates", {}).get("builtin_ids", [])
        return list(ids) if isinstance(ids, list) else []

    def set_enabled_templates(self, ids: list[str]) -> tuple[bool, str]:
        known = self.available_builtin_templates()
        unknown = [i for i in ids if i not in known]
        if unknown and known:
            return False, f"未知模板 {unknown}；可用: {', '.join(sorted(known))}"
        if self.settings_path.exists() and self.get_enabled_templates() == list(ids):
            return True, "模板列表已是最新"
        ok, msg = self.write_setting("theme.templates", "builtin_ids", list(ids))
        if not ok:
            return False, msg
        return True, f"已启用 Noctalia 模板: {', '.join(ids) or '(无)'}"

    def apply_templates(self) -> tuple[bool, str]:
        """让 Noctalia 依据当前配色渲染所有已启用模板。"""
        return self.msg("templates-apply")

    def enable_templates(self, ids: list[str], reload: bool = True) -> tuple[bool, str]:
        """启用模板并立即渲染生效。"""
        known = self.available_builtin_templates()
        if known:
            ids = [i for i in ids if i in known]
        ok, msg = self.set_enabled_templates(ids)
        if not ok:
            return False, msg
        if self.dry_run:
            return True, f"[演练模拟] {msg}"
        if reload:
            reload_ok, reload_msg = self.reload()
            if not reload_ok:
                return False, f"启用模板后重载失败: {reload_msg}"
        apply_ok, apply_msg = self.apply_templates()
        if not apply_ok:
            return False, f"模板渲染失败: {apply_msg}"
        return True, f"{msg}；已渲染生效"

    def template_for_app(self, app: str) -> str | None:
        return TEMPLATE_FOR_APP.get(app)

    # ==================== 消息总线 ====================

    def msg(self, *args: str) -> tuple[bool, str]:
        """向运行中的 Noctalia 发送消息命令。"""
        if self.dry_run:
            return True, f"[演练模拟] noctalia msg {' '.join(args)}"
        if not self.noctalia_bin:
            return False, "未找到 noctalia 可执行文件"
        ok, out = run_capture([self.noctalia_bin, "msg", *args], timeout=8)
        if ok:
            return True, out or "ok"
        return False, out

    def validate(self) -> tuple[bool, str]:
        if not self.noctalia_bin:
            return False, "未找到 noctalia 可执行文件"
        try:
            from nirice.core import run

            result = run([self.noctalia_bin, "config", "validate"], timeout=10)
            output = (result.stdout + result.stderr).strip()
            return result.returncode == 0, output or "配置有效"
        except OSError as exc:
            return False, f"校验失败: {exc}"

    def reload(self) -> tuple[bool, str]:
        return self.msg("config-reload")

    def status(self) -> dict[str, Any]:
        ok, out = self.msg("status")
        if not ok:
            return {}
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            return {}

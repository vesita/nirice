"""终端与 Shell 生态控制器。

职责边界：**配色交给 Noctalia 模板自动渲染，nirice 只负责模板覆盖不到的部分**
（Kitty 的排版/磨砂/Tab/快捷键，以及 Noctalia 不可用时的回退配色）。
"""

from __future__ import annotations

from pathlib import Path

from nirice.core import XDGPaths, pkill, which
from nirice.noctalia import NoctaliaController
from nirice.noctalia.templates import TEMPLATE_FOR_APP
from nirice.terminal import backends
from nirice.terminal.catalog import TERMINAL_PALETTES
from nirice.terminal.kitty import (
    NIRICE_AESTHETIC_REL,
    NIRICE_FALLBACK_THEME_REL,
    render_kitty_aesthetics,
    render_kitty_conf,
    render_kitty_theme,
)
from nirice.terminal.palettes import TerminalPalette
from nirice.terminal.prompt import (
    extract_noctalia_palette_block,
    generate_fastfetch_config,
    generate_starship_config,
)

# 终端/工具 的中文展示名
APP_LABELS = {
    "kitty": "Kitty",
    "alacritty": "Alacritty",
    "ghostty": "Ghostty",
    "foot": "Foot",
    "wezterm": "WezTerm",
    "zellij": "Zellij",
}


class TerminalController:
    """管理终端模拟器与 Shell 提示符的配色、字体与视觉布局。"""

    def __init__(
        self,
        dry_run: bool = False,
        home_dir: Path | None = None,
        noctalia: NoctaliaController | None = None,
    ) -> None:
        self.dry_run = dry_run
        self.paths = XDGPaths.resolve(home_dir)
        self.home = self.paths.home
        self.config_dir = self.paths.config
        self.data_dir = self.paths.data
        self._noctalia = noctalia

    @property
    def noctalia(self) -> NoctaliaController:
        """惰性构造 Noctalia 控制器。"""
        if self._noctalia is None:
            self._noctalia = NoctaliaController(dry_run=self.dry_run, home_dir=self.home)
        return self._noctalia

    # ==================== 调色板 ====================

    def get_palette(self, name: str) -> TerminalPalette | None:
        return TERMINAL_PALETTES.get(name.lower())

    def list_palettes(self) -> dict[str, TerminalPalette]:
        return TERMINAL_PALETTES

    def _resolve_palette(self, value: str | TerminalPalette | None) -> TerminalPalette | None:
        if value is None:
            return None
        if isinstance(value, str):
            return self.get_palette(value)
        return value

    def detect_installed_terminals(self) -> dict[str, bool]:
        """检测系统已安装或已配置的终端与 Shell 工具。"""
        config = self.config_dir
        return {
            "kitty": which("kitty") is not None or (config / "kitty").exists(),
            "alacritty": which("alacritty") is not None or (config / "alacritty").exists(),
            "ghostty": which("ghostty") is not None or (config / "ghostty").exists(),
            "foot": which("foot") is not None or (config / "foot").exists(),
            "wezterm": which("wezterm") is not None or (config / "wezterm").exists(),
            "zellij": which("zellij") is not None or (config / "zellij").exists(),
            "starship": which("starship") is not None or (config / "starship.toml").exists(),
            "fastfetch": which("fastfetch") is not None or (config / "fastfetch").exists(),
        }

    # ==================== Noctalia 模板编排 ====================

    def noctalia_managed_apps(self) -> dict[str, str]:
        """返回「已安装且可交由 Noctalia 自动配色」的软件 -> 模板 id。"""
        if not self.noctalia.is_installed():
            return {}
        available = self.noctalia.available_builtin_templates()
        detected = self.detect_installed_terminals()
        managed: dict[str, str] = {}
        for app, template_id in TEMPLATE_FOR_APP.items():
            if available and template_id not in available:
                continue
            if app in ("niri", "gtk3", "gtk4", "qt") or detected.get(app):
                managed[app] = template_id
        return managed

    def enable_noctalia_templates(self, apps: list[str] | None = None) -> tuple[bool, str]:
        """启用并渲染 Noctalia 模板，让各软件配色自动跟随外壳主题。"""
        managed = self.noctalia_managed_apps()
        if not managed:
            return False, "未检测到可用的 Noctalia 模板（Noctalia 未安装或模板缺失）"
        wanted = list(managed.values()) if apps is None else [managed[a] for a in apps if a in managed]
        if not wanted:
            return False, "指定的软件没有对应的 Noctalia 模板"
        return self.noctalia.enable_templates(sorted(set(wanted)))

    def noctalia_palette_name(self) -> str:
        return self.noctalia.get_theme()[0]

    def _noctalia_covers(self, app: str) -> bool:
        if not self.noctalia.is_installed():
            return False
        template = self.noctalia.template_for_app(app)
        return bool(template) and template in self.noctalia.get_enabled_templates()

    # ==================== Kitty（美学层 + 自动配色）====================

    def apply_kitty(
        self,
        palette: str | TerminalPalette | None = None,
        use_noctalia: bool = True,
    ) -> tuple[bool, str]:
        """写入 Kitty 美学层，配色优先由 Noctalia 自动生成。"""
        pal = self._resolve_palette(palette)
        if palette is not None and pal is None:
            return False, f"未知的调色板 '{palette}'"

        noctalia_ready = use_noctalia and self._noctalia_covers("kitty")

        if self.dry_run:
            mode = "Noctalia 自动配色" if noctalia_ready else "nirice 回退配色"
            return True, f"[演练模拟] 将写入 Kitty 美学层与主配置（{mode}）"

        kitty_dir = self.config_dir / "kitty"
        try:
            kitty_dir.mkdir(parents=True, exist_ok=True)
            (kitty_dir / NIRICE_AESTHETIC_REL).write_text(render_kitty_aesthetics(), encoding="utf-8")
            (kitty_dir / "kitty.conf").write_text(render_kitty_conf(use_noctalia=noctalia_ready), encoding="utf-8")

            if noctalia_ready:
                ok, msg = self.noctalia.apply_templates()
                if not ok:
                    return False, f"已写入美学层，但 Noctalia 渲染配色失败: {msg}"
                detail = "配色由 Noctalia 自动生成"
            else:
                effective = pal or self.get_palette("nord-light") or next(iter(TERMINAL_PALETTES.values()))
                (kitty_dir / NIRICE_FALLBACK_THEME_REL).write_text(render_kitty_theme(effective), encoding="utf-8")
                detail = f"配色使用 nirice 调色板 '{effective.name}'"
        except OSError as exc:
            return False, f"写入 Kitty 配置失败: {exc}"

        pkill("-USR1", "kitty")
        return True, f"Kitty 美学层已更新，{detail}。"

    # ==================== 其余终端 ====================

    def _apply_backend(self, app: str, palette: str | TerminalPalette) -> tuple[bool, str]:
        if self._noctalia_covers(app):
            ok, msg = self.noctalia.apply_templates()
            label = APP_LABELS.get(app, app)
            return ok, f"{label} 配色已由 Noctalia 模板刷新" if ok else msg

        pal = self._resolve_palette(palette)
        if pal is None:
            return False, f"未知的调色板 '{palette}'"
        return backends.BACKENDS[app](self.config_dir, pal, self.dry_run)

    def apply_alacritty(self, palette: str | TerminalPalette) -> tuple[bool, str]:
        return self._apply_backend("alacritty", palette)

    def apply_ghostty(self, palette: str | TerminalPalette) -> tuple[bool, str]:
        return self._apply_backend("ghostty", palette)

    def apply_foot(self, palette: str | TerminalPalette) -> tuple[bool, str]:
        return self._apply_backend("foot", palette)

    def apply_wezterm(self, palette: str | TerminalPalette) -> tuple[bool, str]:
        return self._apply_backend("wezterm", palette)

    def apply_zellij(self, palette: str | TerminalPalette) -> tuple[bool, str]:
        return self._apply_backend("zellij", palette)

    # ==================== Shell 提示符与看板 ====================

    def apply_starship(self, palette: str | TerminalPalette) -> tuple[bool, str]:
        """写入 Starship 胶囊提示符布局；配色引用 Noctalia 调色板。"""
        pal = self._resolve_palette(palette)
        if pal is None:
            return False, f"未知的调色板 '{palette}'"
        if self.dry_run:
            return True, f"[演练模拟] 将为 Starship 写入布局（调色板: {pal.name}）"

        starship_file = self.config_dir / "starship.toml"
        use_noctalia = self._noctalia_covers("starship")
        try:
            starship_file.parent.mkdir(parents=True, exist_ok=True)
            existing = starship_file.read_text(encoding="utf-8") if starship_file.exists() else ""
            content = generate_starship_config(pal, use_noctalia_palette=use_noctalia)
            if use_noctalia:
                block = extract_noctalia_palette_block(existing)
                if block:
                    content = content.rstrip("\n") + "\n\n" + block + "\n"
            starship_file.write_text(content, encoding="utf-8")
        except OSError as exc:
            return False, f"更新 starship.toml 失败: {exc}"

        source = "Noctalia 调色板" if use_noctalia else f"nirice 调色板 '{pal.name}'"
        return True, f"Starship 提示符布局已写入（配色来源: {source}）。"

    def apply_fastfetch(self, palette: str | TerminalPalette) -> tuple[bool, str]:
        pal = self._resolve_palette(palette)
        if pal is None:
            return False, f"未知的调色板 '{palette}'"
        if self.dry_run:
            return True, f"[演练模拟] 将为 Fastfetch 应用调色板: {pal.name}"

        target = self.config_dir / "fastfetch" / "config.jsonc"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(generate_fastfetch_config(pal), encoding="utf-8")
        except OSError as exc:
            return False, f"更新 Fastfetch 配置失败: {exc}"
        return True, f"Fastfetch 看板已匹配调色板 '{pal.display_name}'。"

    # ==================== 批量应用 ====================

    def apply_all(
        self,
        palette_or_name: str | TerminalPalette = "nord-light",
        terminals: list[str] | None = None,
    ) -> dict[str, tuple[bool, str]]:
        """把配色应用到所有已安装的终端与 Shell 工具。"""
        palette = (
            self._resolve_palette(palette_or_name)
            or self.get_palette("nord-light")
            or next(iter(TERMINAL_PALETTES.values()))
        )
        detected = self.detect_installed_terminals()
        allowed = {t.lower() for t in terminals} if terminals else None

        def wanted(key: str) -> bool:
            return allowed is None or key in allowed

        results: dict[str, tuple[bool, str]] = {}

        if self.noctalia.is_installed():
            results["Noctalia 模板"] = self.enable_noctalia_templates()

        if wanted("kitty") and detected.get("kitty"):
            results["Kitty"] = self.apply_kitty(palette)

        for app in ("alacritty", "ghostty", "foot", "wezterm", "zellij"):
            if wanted(app) and detected.get(app):
                results[APP_LABELS[app]] = self._apply_backend(app, palette)

        if wanted("starship") and detected.get("starship"):
            results["Starship"] = self.apply_starship(palette)
        if wanted("fastfetch") and detected.get("fastfetch"):
            results["Fastfetch"] = self.apply_fastfetch(palette)

        return results

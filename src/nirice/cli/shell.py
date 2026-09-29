"""Noctalia 外壳相关命令：状态、主题、状态栏与模板。"""

from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from nirice.cli.common import FAIL, OK, console
from nirice.noctalia import BAR_POSITIONS, NoctaliaController
from nirice.terminal import TerminalController

app = typer.Typer(help="管理 Noctalia 桌面外壳：状态栏位置、主题配色与模板渲染。")
bar_app = typer.Typer(help="管理 Noctalia 状态栏。")
templates_app = typer.Typer(help="管理 Noctalia 主题模板（自动为各软件生成配色）。")

app.add_typer(bar_app, name="bar")
app.add_typer(templates_app, name="templates")


@app.command("status")
def shell_status() -> None:
    """查看 Noctalia 外壳的主题、状态栏与模板状态。"""
    noctalia = NoctaliaController()
    palette, mode = noctalia.get_theme()
    console.print(
        Panel.fit(
            f"[bold cyan]安装状态:[/] {'已安装' if noctalia.is_installed() else '未安装'}\n"
            f"[bold cyan]运行状态:[/] {'运行中' if noctalia.is_running() else '未运行'}\n"
            f"[bold cyan]主题配色:[/] [yellow]{palette}[/yellow] / {mode}\n"
            f"[bold cyan]状态栏位置:[/] [yellow]{noctalia.get_bar_position()}[/yellow]\n"
            f"[bold cyan]Dock 位置:[/] {noctalia.get_dock_position()}\n"
            f"[bold cyan]已启用模板:[/] {', '.join(noctalia.get_enabled_templates()) or '无'}\n"
            f"[dim]配置文件: {noctalia.settings_path}[/dim]",
            title="Noctalia 外壳状态",
        )
    )


@app.command("reload")
def shell_reload() -> None:
    """让 Noctalia 重新加载配置。"""
    ok, message = NoctaliaController().reload()
    console.print(f"{OK if ok else FAIL} {message}")


@app.command("theme")
def shell_theme(
    palette: str | None = typer.Argument(None, help="内置配色名称，如 Nord / Catppuccin Mocha"),
    mode: str | None = typer.Option(None, "--mode", "-m", help="明暗模式: dark / light"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """设置 Noctalia 主题配色与明暗模式，并重新渲染所有模板。"""
    noctalia = NoctaliaController(dry_run=dry_run)
    if not palette and not mode:
        current_palette, current_mode = noctalia.get_theme()
        console.print(f"当前主题: [yellow]{current_palette}[/yellow] / {current_mode}")
        console.print("[dim]用法: nirice shell theme Nord --mode light[/dim]")
        return

    ok, message = noctalia.set_theme(palette=palette, mode=mode)
    console.print(f"  {OK if ok else FAIL} {message}")
    if not ok or dry_run:
        return
    noctalia.reload()
    templates_ok, templates_msg = noctalia.apply_templates()
    console.print(f"  {OK if templates_ok else FAIL} 已重新渲染模板: {templates_msg}")


@app.command("panel")
def shell_panel(
    panel_id: str = typer.Argument(..., help="面板 ID: launcher / control-center / wallpaper / session / clipboard"),
) -> None:
    """开关指定的 Noctalia 面板。"""
    ok, message = NoctaliaController().toggle_panel(panel_id)
    console.print(f"{OK if ok else FAIL} {message}")


# ==============================================================================
# 状态栏
# ==============================================================================


@bar_app.command("position")
def bar_position(
    position: str | None = typer.Argument(None, help=f"状态栏位置: {' / '.join(BAR_POSITIONS)}"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """查看或设置 Noctalia 状态栏所在的屏幕边缘。"""
    noctalia = NoctaliaController(dry_run=dry_run)
    if not position:
        console.print(f"当前状态栏位置: [bold yellow]{noctalia.get_bar_position()}[/bold yellow]")
        console.print(f"[dim]可选: {' / '.join(BAR_POSITIONS)}[/dim]")
        return

    ok, message = noctalia.set_bar_position(position)
    console.print(f"  {OK if ok else FAIL} {message}")
    if ok and not dry_run:
        reload_ok, reload_msg = noctalia.reload()
        console.print(f"  {OK if reload_ok else FAIL} {reload_msg}")


@bar_app.command("toggle")
def bar_toggle() -> None:
    """显示/隐藏状态栏。"""
    ok, message = NoctaliaController().msg("bar-toggle")
    console.print(f"{OK if ok else FAIL} {message}")


# ==============================================================================
# 主题模板
# ==============================================================================


@templates_app.command("list")
def templates_list() -> None:
    """列出 Noctalia 可用的内置模板与启用状态。"""
    noctalia = NoctaliaController()
    available = noctalia.available_builtin_templates()
    if not available:
        console.print("[yellow]未找到 Noctalia 模板清单（Noctalia 未安装？）[/yellow]")
        return

    enabled = set(noctalia.get_enabled_templates())
    table = Table(title="[bold cyan]🧩 Noctalia 内置模板[/bold cyan]", header_style="bold cyan")
    table.add_column("模板 ID", style="bold yellow", width=16)
    table.add_column("名称", width=20)
    table.add_column("状态", width=12)
    for template_id, name in sorted(available.items()):
        table.add_row(template_id, name, "[green]已启用[/green]" if template_id in enabled else "[dim]未启用[/dim]")
    console.print(table)
    console.print("[dim]模板由 Noctalia 渲染，自动为各软件生成匹配当前主题的配色。[/dim]")


@templates_app.command("enable")
def templates_enable(
    ids: list[str] | None = typer.Argument(None, help="要启用的模板 ID（留空则自动检测已安装软件）"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """启用模板并立即渲染生效。"""
    noctalia = NoctaliaController(dry_run=dry_run)
    if ids:
        target = list(ids)
    else:
        term = TerminalController(dry_run=dry_run, noctalia=noctalia)
        target = sorted(set(term.noctalia_managed_apps().values()))
        if not target:
            console.print("[yellow]未自动检测到可用模板，请显式指定模板 ID。[/yellow]")
            return
        console.print(f"[dim]自动检测到: {', '.join(target)}[/dim]")

    ok, message = noctalia.enable_templates(target)
    console.print(f"{OK if ok else FAIL} {message}")


@templates_app.command("apply")
def templates_apply() -> None:
    """按当前主题重新渲染所有已启用模板。"""
    ok, message = NoctaliaController().apply_templates()
    console.print(f"{OK if ok else FAIL} {message}")

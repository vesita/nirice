"""终端与 Shell 提示符相关命令。"""

from __future__ import annotations

from collections.abc import Callable

import typer
from rich.table import Table

from nirice.cli.common import FAIL, OK, console, print_results
from nirice.terminal import TERMINAL_PALETTES, TerminalController

app = typer.Typer(help="管理终端与 Shell 提示符：配色由 Noctalia 自动渲染，nirice 负责美学层。")


@app.command("list")
def terminal_list() -> None:
    """列出可用的终端调色板（仅在 Noctalia 不可用时作为回退）。"""
    table = Table(title="[bold cyan]终端回退调色板[/bold cyan]", header_style="bold cyan")
    table.add_column("名称", style="bold yellow", width=18)
    table.add_column("模式", width=10)
    table.add_column("背景", style="dim", width=10)
    table.add_column("前景", style="dim", width=10)
    table.add_column("说明", style="white")
    for key, palette in TERMINAL_PALETTES.items():
        table.add_row(
            key,
            "[blue]暗色[/blue]" if palette.is_dark else "[yellow]浅色[/yellow]",
            palette.background,
            palette.foreground,
            palette.display_name,
        )
    console.print(table)


@app.command("set-kitty")
def terminal_set_kitty(
    palette: str | None = typer.Argument(None, help="回退调色板名称（仅当 Noctalia 不可用时使用）"),
    no_noctalia: bool = typer.Option(False, "--no-noctalia", help="强制使用 nirice 自带调色板"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """写入 Kitty 美学层；配色默认由 Noctalia 自动生成。"""
    ok, message = TerminalController(dry_run=dry_run).apply_kitty(palette, use_noctalia=not no_noctalia)
    console.print(f"{OK if ok else FAIL} {message}")


@app.command("apply")
def terminal_apply(
    palette: str = typer.Argument("nord-light", help="回退调色板名称"),
    terminals: str | None = typer.Option(None, "--terminals", "-t", help="逗号分隔的目标终端"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """把配色应用到所有终端：优先启用 Noctalia 模板，再用 nirice 补齐。"""
    ctl = TerminalController(dry_run=dry_run)
    target = [t.strip().lower() for t in terminals.split(",")] if terminals else None
    console.print(f"[bold cyan]正在同步终端与 Shell 生态[/bold cyan] [dim](回退调色板: {palette})[/dim]")
    print_results(ctl.apply_all(palette, terminals=target))


@app.command("export-palette")
def terminal_export_palette(palette_name: str = typer.Argument(..., help="调色板名称")) -> None:
    """查看指定调色板的 16 色 ANSI 色卡。"""
    palette = TerminalController().get_palette(palette_name)
    if not palette:
        console.print(f"{FAIL} 未找到调色板 '{palette_name}'")
        raise typer.Exit(code=1)

    table = Table(title=f"[bold cyan]调色板: {palette.display_name} ({palette.name})[/bold cyan]")
    table.add_column("槽位", style="bold white", width=18)
    table.add_column("HEX", style="yellow", width=12)
    table.add_column("预览", width=16)
    items = [
        ("Background", palette.background),
        ("Foreground", palette.foreground),
        ("Cursor", palette.cursor),
        ("Selection", palette.selection_bg),
        *[(f"Color {i}", c) for i, c in enumerate(palette.to_ansi_list())],
    ]
    for name, value in items:
        table.add_row(name, value, f"[{value}]██████████[/{value}]")
    console.print(table)


# ==============================================================================
# 各终端的 set-* 命令（用工厂生成，避免大量重复样板）
# ==============================================================================


def _make_setter(method_name: str, label: str) -> Callable[..., None]:
    def command(
        palette: str | None = typer.Argument(None, help="回退调色板名称"),
        dry_run: bool = typer.Option(False, "--dry-run", "-n"),
    ) -> None:
        ctl = TerminalController(dry_run=dry_run)
        name = palette or "nord-light"
        if ctl.get_palette(name) is None:
            console.print(f"{FAIL} 未知调色板 '{name}'")
            raise typer.Exit(code=1)
        ok, message = getattr(ctl, method_name)(name)
        console.print(f"{OK if ok else FAIL} {message}")

    command.__name__ = method_name.replace("apply_", "set_")
    command.__doc__ = f"应用 {label} 配色（优先由 Noctalia 模板接管）。"
    return command


for _app_name, _method, _label in (
    ("alacritty", "apply_alacritty", "Alacritty"),
    ("ghostty", "apply_ghostty", "Ghostty"),
    ("foot", "apply_foot", "Foot"),
    ("wezterm", "apply_wezterm", "WezTerm"),
    ("zellij", "apply_zellij", "Zellij"),
    ("starship", "apply_starship", "Starship 提示符布局"),
    ("fastfetch", "apply_fastfetch", "Fastfetch 看板"),
):
    app.command(f"set-{_app_name}")(_make_setter(_method, _label))

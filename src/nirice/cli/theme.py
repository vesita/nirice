"""整合式 Rice 方案命令。"""

from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from nirice.cli.common import FAIL, OK, console, print_results
from nirice.niri import ANIMATION_PRESETS, NiriController
from nirice.noctalia import NoctaliaController
from nirice.terminal import TerminalController
from nirice.theme import RICE_PRESETS

app = typer.Typer(help="整合式 Rice 方案：一键切换 Niri 动效 + 外壳主题 + 终端配色。")


@app.command("list")
def theme_list() -> None:
    """列出整合式 Rice 方案。"""
    table = Table(title="[bold cyan]整合式 Rice 方案[/bold cyan]", header_style="bold magenta")
    table.add_column("名称", style="bold yellow", width=18)
    table.add_column("Noctalia 配色", style="cyan", width=18)
    table.add_column("模式", width=8)
    table.add_column("Niri 动效", style="blue", width=10)
    table.add_column("说明", style="white")
    for key, preset in RICE_PRESETS.items():
        table.add_row(
            key,
            preset.noctalia_palette or "-",
            preset.noctalia_mode or "-",
            preset.animation_preset,
            preset.description,
        )
    console.print(table)


@app.command("apply")
def theme_apply(
    preset_name: str = typer.Argument("nord-light", help="Rice 方案名称"),
    no_terminal: bool = typer.Option(False, "--no-terminal", help="跳过终端与 Shell 配色"),
    no_niri: bool = typer.Option(False, "--no-niri", help="跳过 Niri 动效写入"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """一键应用整合式 Rice 方案。"""
    preset = RICE_PRESETS.get(preset_name.lower())
    if not preset:
        console.print(f"{FAIL} 未知方案 '{preset_name}'，运行 'nirice theme list' 查看。")
        raise typer.Exit(code=1)

    noctalia = NoctaliaController(dry_run=dry_run)
    niri = NiriController(dry_run=dry_run)
    term = TerminalController(dry_run=dry_run, noctalia=noctalia)

    console.print(
        Panel.fit(
            f"[bold cyan]正在应用 Rice 方案：[/bold cyan] [bold yellow]{preset.name}[/bold yellow]\n"
            f"[dim]{preset.description}[/dim]\n\n"
            f"• Noctalia 配色: [green]{preset.noctalia_palette or '保持当前'}[/green]\n"
            f"• 明暗模式: [green]{preset.noctalia_mode or '保持当前'}[/green]\n"
            f"• Niri 动效: [blue]{preset.animation_preset}[/blue]\n"
            f"• 终端回退调色板: [cyan]{preset.terminal_palette or '无'}[/cyan]",
            title="Rice 方案详情",
        )
    )

    if preset.noctalia_palette or preset.noctalia_mode:
        ok, message = noctalia.set_theme(palette=preset.noctalia_palette, mode=preset.noctalia_mode)
        console.print(f"  {OK if ok else FAIL} [bold]外壳主题:[/bold] {message}")
        if not dry_run:
            noctalia.reload()
            templates_ok, templates_msg = noctalia.apply_templates()
            console.print(f"  {OK if templates_ok else FAIL} [bold]模板渲染:[/bold] {templates_msg}")

    if not no_niri:
        animation = ANIMATION_PRESETS.get(preset.animation_preset)
        if animation:
            result = niri.write_fragment("animation.kdl", animation.animations_kdl)
            console.print(
                f"  {OK if result.ok else FAIL} [bold]Niri 动效:[/bold] {result.describe()} ({preset.animation_preset})"
            )

    if not no_terminal:
        console.print("\n  [bold cyan]💻 终端与 Shell:[/bold cyan]")
        print_results(term.apply_all(preset.terminal_palette or "nord-light"))

    if preset.notes:
        console.print("\n[bold]方案要点：[/bold]")
        for note in preset.notes:
            console.print(f"  • {note}")

    console.print(f"\n{OK} [bold green]Rice 方案应用完成！[/bold green]")

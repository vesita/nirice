"""KDE → Niri 迁移命令。"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.panel import Panel
from rich.table import Table

from nirice.cli.common import FAIL, OK, console, print_results
from nirice.niri import NiriController
from nirice.noctalia import NoctaliaController
from nirice.system import DependencyHelper, MigrationPlanner
from nirice.terminal import TerminalController

app = typer.Typer(help="KDE → Niri 迁移：检测残留、补齐缺失组件、生成可执行计划。")


def _render_plan(plan) -> None:
    for phase, steps in plan.grouped().items():
        table = Table(title=f"[bold cyan]{phase}[/bold cyan]", header_style="bold blue")
        table.add_column("", width=3)
        table.add_column("步骤", style="bold white", width=28)
        table.add_column("说明", style="dim")
        table.add_column("命令", style="yellow")
        for step in steps:
            icon = OK if step.done else ("[bold red]![/bold red]" if step.essential else "[dim]·[/dim]")
            table.add_row(icon, step.title, step.detail, step.command or "-")
        console.print(table)
        console.print()


@app.command("plan")
def migrate_plan() -> None:
    """检测 KDE 残留与 Niri 组件缺口，输出迁移计划。"""
    planner = MigrationPlanner()
    plan = planner.build_plan()

    console.print(
        Panel.fit(
            f"[bold cyan]当前会话:[/] {planner.current_session()}\n"
            f"[bold cyan]残留 KDE 软件包:[/] {len(plan.detected_kde_packages)} 个\n"
            f"[bold cyan]残留 KDE 配置项:[/] {len(plan.detected_kde_configs)} 个\n"
            f"[bold cyan]缺失必需组件:[/] {', '.join(plan.missing_niri_packages) or '无'}\n"
            f"[bold cyan]门户路由配置:[/] {'已就绪' if not plan.missing_portal_conf else '缺失'}",
            title="KDE → Niri 迁移检测",
        )
    )
    console.print()
    _render_plan(plan)

    if plan.detected_kde_configs:
        console.print("[bold]检测到的 KDE 残留配置：[/bold]")
        for item in plan.detected_kde_configs:
            console.print(f"  [dim]•[/dim] {item}")
        console.print()

    console.print(
        f"[bold yellow]待处理必需项: {len(plan.pending_essential)}[/bold yellow]"
        "  ·  运行 [bold green]nirice migrate apply[/bold green] 自动完成可自动化部分。"
    )


@app.command("apply")
def migrate_apply(
    skip_install: bool = typer.Option(False, "--skip-install", help="跳过依赖安装"),
    clean_configs: bool = typer.Option(False, "--clean-configs", help="归档 KDE 残留配置（可逆）"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """执行迁移计划中可自动化的部分（依赖 → 配置 → 模板 → 校验）。"""
    planner = MigrationPlanner()
    helper = DependencyHelper()

    if not skip_install:
        missing = helper.missing_packages(essential_only=False)
        if missing:
            console.print(f"[bold cyan]安装缺失依赖: {', '.join(missing)}[/bold cyan]")
            ok, message = helper.install_packages(missing)
            console.print(f"  {OK if ok else FAIL} {message}")
        else:
            console.print(f"{OK} 依赖已就绪")

    niri = NiriController(dry_run=dry_run)
    console.print("[bold cyan]写入 Niri 配置...[/bold cyan]")
    for result in niri.apply_all():
        console.print(f"  {OK if result.ok else FAIL} {result.name}: {result.describe()}")

    noctalia = NoctaliaController(dry_run=dry_run)
    if noctalia.is_installed():
        console.print("[bold cyan]配置 Noctalia 外壳...[/bold cyan]")
        for ok, message in (
            noctalia.set_bar_position("left"),
            noctalia.set_theme(palette="Nord", mode="light"),
        ):
            console.print(f"  {OK if ok else FAIL} {message}")
        term = TerminalController(dry_run=dry_run, noctalia=noctalia)
        ok, message = term.enable_noctalia_templates()
        console.print(f"  {OK if ok else FAIL} {message}")

    console.print("[bold cyan]配置 Kitty...[/bold cyan]")
    term = TerminalController(dry_run=dry_run, noctalia=noctalia)
    ok, message = term.apply_kitty(use_noctalia=noctalia.is_installed())
    console.print(f"  {OK if ok else FAIL} {message}")

    if clean_configs:
        console.print("[bold cyan]归档 KDE 残留配置...[/bold cyan]")
        print_results(planner.clean_kde_configs(dry_run=dry_run))

    if not dry_run:
        ok, message = niri.validate()
        console.print(f"\n{OK if ok else FAIL} {message}")

    console.print(f"\n{OK} [bold green]迁移自动化部分完成。[/bold green]")
    console.print("[dim]卸载 KDE 软件包属于不可逆操作，请按 `nirice migrate plan` 输出的命令自行执行。[/dim]")


@app.command("clean-configs")
def migrate_clean_configs(dry_run: bool = typer.Option(False, "--dry-run", "-n")) -> None:
    """把 KDE 残留配置归档到 ~/.cache/nirice/kde-leftovers/（不删除，可找回）。"""
    results = MigrationPlanner().clean_kde_configs(dry_run=dry_run)
    if not results:
        console.print("[green]未发现 KDE 残留配置。[/green]")
        return
    print_results(results)


@app.command("report")
def migrate_report(
    output: Path = typer.Option(Path("MIGRATION.md"), "--output", "-o", help="报告输出路径"),
) -> None:
    """导出 KDE → Niri 迁移报告（Markdown）。"""
    planner = MigrationPlanner()
    plan = planner.build_plan()

    lines = [
        "# KDE → Niri 迁移报告",
        "",
        f"- 当前会话: `{planner.current_session()}`",
        f"- 残留 KDE 软件包: {len(plan.detected_kde_packages)} 个",
        f"- 残留 KDE 配置: {len(plan.detected_kde_configs)} 个",
        f"- 缺失必需组件: {', '.join(plan.missing_niri_packages) or '无'}",
        f"- 门户路由配置: {'已就绪' if not plan.missing_portal_conf else '缺失'}",
        "",
    ]
    for phase, steps in plan.grouped().items():
        lines += [f"## {phase}", "", "| 状态 | 步骤 | 说明 | 命令 |", "| --- | --- | --- | --- |"]
        for step in steps:
            mark = "✅" if step.done else ("❗" if step.essential else "⬜")
            lines.append(f"| {mark} | {step.title} | {step.detail} | `{step.command or '-'}` |")
        lines.append("")

    if plan.detected_kde_configs:
        lines += ["## 检测到的 KDE 残留配置", ""]
        lines += [f"- `{item}`" for item in plan.detected_kde_configs]
        lines.append("")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(f"{OK} 迁移报告已写入 [bold cyan]{output}[/bold cyan]")

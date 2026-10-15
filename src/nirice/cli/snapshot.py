"""配置快照命令：打包、查看与还原。"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.panel import Panel
from rich.table import Table

from nirice.cli.common import FAIL, OK, console
from nirice.snapshot import SnapshotManager

app = typer.Typer(help="配置打包导出、跨机器无损还原与依赖自愈。")


@app.command("save")
def snapshot_save(
    name: str | None = typer.Option(None, "--name", "-m", help="快照名称"),
    output: Path | None = typer.Option(None, "--output", "-o", help="输出路径 (.pmz)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """把 Niri / Noctalia / 终端配置打包为便携快照。"""
    out_file = SnapshotManager(dry_run=dry_run).create_snapshot(output_path=output, name=name)
    if dry_run:
        console.print(f"{OK} 干跑：未写入任何文件；本应生成: [bold cyan]{out_file}[/bold cyan]")
    else:
        console.print(f"{OK} 快照打包成功: [bold cyan]{out_file}[/bold cyan]")


@app.command("info")
def snapshot_info(archive: Path = typer.Argument(..., help=".pmz 快照路径")) -> None:
    """查看快照元数据与包含的文件清单。"""
    try:
        data = SnapshotManager().inspect_snapshot(archive)
    except Exception as exc:  # noqa: BLE001 - 面向用户的诊断输出
        console.print(f"{FAIL} 读取快照失败: {exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        Panel.fit(
            f"[bold cyan]名称:[/] {data.get('name', '未知')}\n"
            f"[bold cyan]打包时间:[/] {data.get('created_at', '未知')}\n"
            f"[bold cyan]生成工具:[/] {data.get('generator', '未知')}\n"
            f"[bold cyan]范围:[/] {data.get('scope', '-')}\n"
            f"[bold cyan]包含目标数:[/] {len(data.get('files', []))}",
            title=f"快照: {archive.name}",
        )
    )
    files = data.get("files", [])
    if files:
        table = Table(title="包含的配置目标", header_style="bold blue")
        table.add_column("路径", style="dim")
        for item in files:
            table.add_row(item)
        console.print(table)


@app.command("load")
@app.command("restore", hidden=True)
def snapshot_load(
    archive: Path = typer.Argument(..., help=".pmz 快照路径"),
    no_backup: bool = typer.Option(False, "--no-backup", help="跳过还原前的自动备份"),
    install_deps: bool = typer.Option(False, "--install-deps", "-i", help="自动安装缺失的必需依赖"),
    no_hooks: bool = typer.Option(False, "--no-hooks", help="跳过 Shell 提示符挂钩注入"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """把快照还原到当前机器，并热重载 Niri / Noctalia / Kitty。"""
    try:
        restored = SnapshotManager(dry_run=dry_run).restore_snapshot(
            archive,
            create_backup=not no_backup,
            install_deps=install_deps,
            wire_shell_hooks=not no_hooks,
        )
    except Exception as exc:  # noqa: BLE001
        console.print(f"{FAIL} 还原失败: {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"{OK} 已还原 [bold]{len(restored)}[/bold] 个配置目标。")
    # 只说「请求」：缺失的组件会被静默跳过，不能替它们宣称已经重载过
    console.print(f"{OK} 已对可用的组件请求热重载 Niri / Noctalia / Kitty。")

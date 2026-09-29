"""Niri 合成器相关命令。"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.panel import Panel
from rich.table import Table

from nirice.cli.common import FAIL, OK, console
from nirice.niri import ANIMATION_PRESETS, NiriController
from nirice.niri.catalog import MANAGED_FRAGMENTS

app = typer.Typer(help="管理 Niri 合成器配置：快捷键、动效、布局、校验与热重载。")

HIGHLIGHTS = [
    ("Mod + T / Return", "打开终端 (kitty)"),
    ("Mod + ← → ↑ ↓", "在列/窗口之间聚焦导航"),
    ("Mod + Ctrl + ← → ↑ ↓", "移动列/窗口"),
    ("Mod + R / Mod + F", "最大化当前列（占满整列）"),
    ("Mod + Shift + R", "在预设列宽间循环 (1/3 → 1/2 → 2/3)"),
    ("Mod + C", "当前列居中"),
    ("Mod + Alt + ← / →", "吸附到最左 / 最右（50% 宽 + 移动）"),
    ("Mod + Alt + ↑", "当前列居中"),
    ("Mod + Alt + ↓", "扩展到可用宽度"),
    ("Mod + Shift + F", "真全屏"),
    ("Mod + V", "切换浮动窗口"),
    ("Mod + 1..9 / Mod + Ctrl + 1..9", "切换工作区 / 把列移到工作区"),
    ("Mod + D / Space", "Noctalia 应用启动器"),
    ("Mod + S / Mod + Shift + S", "控制中心 / 系统设置"),
    ("Mod + Ctrl + V", "剪贴板历史"),
    ("Mod + Escape", "紧急解除快捷键抑制"),
]


def _apply_and_reload(ctl: NiriController) -> None:
    ok, message = ctl.validate()
    if not ok:
        console.print(f"\n{FAIL} [bold red]配置校验失败，未热重载：[/bold red]\n{message}")
        raise typer.Exit(code=1)
    console.print(f"\n{OK} {message}")
    reload_ok, reload_msg = ctl.reload()
    console.print(f"{OK if reload_ok else FAIL} {reload_msg}")


@app.command("apply")
def niri_apply(
    animation: str | None = typer.Option(None, "--animation", "-a", help="同时应用指定动效方案"),
    no_keybinds: bool = typer.Option(False, "--no-keybinds", help="保留本地 keybinds.kdl，不覆盖快捷键"),
    no_backup: bool = typer.Option(False, "--no-backup", help="覆盖前不备份原文件"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="演练模拟，不写入文件"),
) -> None:
    """把 nirice 管理的 Niri 分片配置写入 ~/.config/niri/。"""
    ctl = NiriController(dry_run=dry_run)
    fragments = dict(MANAGED_FRAGMENTS)

    if animation:
        preset = ANIMATION_PRESETS.get(animation.lower())
        if not preset:
            console.print(f"{FAIL} 未知动效方案 '{animation}'，可用: {', '.join(ANIMATION_PRESETS)}")
            raise typer.Exit(code=1)
        fragments["animation.kdl"] = preset.animations_kdl

    results = ctl.apply_all(fragments, skip=["keybinds.kdl"] if no_keybinds else None, backup=not no_backup)

    console.print(
        Panel.fit(
            "[bold cyan]正在写入 Niri 受管配置[/bold cyan]\n"
            f"[dim]目标目录: {ctl.niri_dir}[/dim]\n"
            f"[dim]快捷键: {'保留本地文件' if no_keybinds else '使用 nirice 预设'}[/dim]",
            title="nirice niri apply",
        )
    )
    for result in results:
        console.print(f"  {OK if result.ok else FAIL} [bold]{result.name}[/bold]: {result.describe()}")

    if dry_run:
        console.print("\n[yellow]演练模拟结束，未写入任何文件。[/yellow]")
        return
    _apply_and_reload(ctl)


@app.command("check")
def niri_check() -> None:
    """校验 Niri 配置文件语法（niri validate）。"""
    ok, message = NiriController().validate()
    console.print(f"{OK if ok else FAIL} {message}")
    if not ok:
        raise typer.Exit(code=1)


@app.command("reload")
def niri_reload() -> None:
    """热重载 Niri 配置（无需注销）。"""
    ok, message = NiriController().reload()
    console.print(f"{OK if ok else FAIL} {message}")
    if not ok:
        raise typer.Exit(code=1)


@app.command("diff")
def niri_diff() -> None:
    """对比磁盘现状与 nirice 预设。"""
    ctl = NiriController()
    labels = {"same": "[green]一致[/green]", "changed": "[yellow]已本地修改[/yellow]", "missing": "[red]缺失[/red]"}

    table = Table(title="[bold cyan]Niri 配置片段对比[/bold cyan]", header_style="bold blue")
    table.add_column("片段", style="bold white", width=20)
    table.add_column("状态", width=20)
    table.add_column("路径", style="dim")
    for name, state in ctl.diff_fragments().items():
        table.add_row(name, labels.get(state, state), str(ctl.fragment_path(name)))
    console.print(table)


@app.command("keybinds")
def niri_keybinds(
    dump: Path | None = typer.Option(None, "--dump", "-o", help="把快捷键配置导出到指定路径"),
) -> None:
    """查看 nirice 预设的 Niri 快捷键设计。"""
    ctl = NiriController()
    content = ctl.read_fragment("keybinds.kdl") or MANAGED_FRAGMENTS["keybinds.kdl"]

    if dump:
        dump.parent.mkdir(parents=True, exist_ok=True)
        dump.write_text(content, encoding="utf-8")
        console.print(f"{OK} 已导出到 [bold cyan]{dump}[/bold cyan]")
        return

    table = Table(title="[bold cyan]⌨️  nirice Niri 快捷键设计[/bold cyan]", header_style="bold blue")
    table.add_column("快捷键", style="bold yellow", width=24)
    table.add_column("动作", style="white")
    for key, action in HIGHLIGHTS:
        table.add_row(key, action)
    console.print(table)
    console.print("[dim]加 --dump 可导出完整 KDL 后自行微调。[/dim]")


@app.command("animations")
def niri_animations() -> None:
    """列出可用的 Niri 动效方案。"""
    table = Table(title="[bold cyan]🎞️  Niri 动效方案[/bold cyan]", header_style="bold blue")
    table.add_column("名称", style="bold yellow", width=12)
    table.add_column("说明", style="white")
    for key, preset in ANIMATION_PRESETS.items():
        table.add_row(key, preset.description)
    console.print(table)


@app.command("animation")
def niri_set_animation(
    preset_name: str = typer.Argument(..., help="动效方案名称 (arctic/snappy/silky/instant)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """单独应用一个 Niri 动效方案。"""
    preset = ANIMATION_PRESETS.get(preset_name.lower())
    if not preset:
        console.print(f"{FAIL} 未知动效方案 '{preset_name}'，可用: {', '.join(ANIMATION_PRESETS)}")
        raise typer.Exit(code=1)

    ctl = NiriController(dry_run=dry_run)
    result = ctl.write_fragment("animation.kdl", preset.animations_kdl)
    console.print(f"  {OK if result.ok else FAIL} animation.kdl: {result.describe()}")
    if dry_run or not result.ok:
        return
    _apply_and_reload(ctl)


@app.command("outputs")
def niri_outputs() -> None:
    """列出当前显示器与分辨率。"""
    ctl = NiriController()
    outputs = ctl.get_outputs()
    if not outputs:
        console.print("[yellow]未检测到运行中的 Niri 实例。[/yellow]")
        return

    table = Table(title="[bold cyan]🖥️  Niri 显示器输出[/bold cyan]", header_style="bold blue")
    table.add_column("名称", style="bold yellow")
    table.add_column("型号", style="dim")
    table.add_column("当前分辨率")
    table.add_column("缩放 / 变换")
    for name, info in outputs.items():
        logical = info.get("logical") or {}
        modes = info.get("modes") or []
        index = info.get("current_mode")
        mode = ""
        if modes and isinstance(index, int) and 0 <= index < len(modes):
            entry = modes[index]
            mode = f"{entry.get('width')}x{entry.get('height')}@{entry.get('refresh_rate', 0) / 1000:.3f}"
        table.add_row(
            name,
            f"{info.get('make', '')} {info.get('model', '')}".strip() or "-",
            mode or "-",
            f"{logical.get('scale', '-')} / {logical.get('transform', '-')}",
        )
    console.print(table)


@app.command("workspaces")
def niri_workspaces() -> None:
    """列出当前工作区状态。"""
    workspaces = NiriController().get_workspaces()
    if not workspaces:
        console.print("[yellow]未检测到运行中的 Niri 实例。[/yellow]")
        return

    table = Table(title="[bold cyan]🗂️  Niri 工作区[/bold cyan]", header_style="bold blue")
    table.add_column("ID", style="dim", width=6)
    table.add_column("序号", width=6)
    table.add_column("名称", style="bold white")
    table.add_column("显示器", style="dim")
    table.add_column("聚焦", width=6)
    for ws in workspaces:
        table.add_row(
            str(ws.get("id", "-")),
            str(ws.get("idx", "-")),
            ws.get("name") or f"#{ws.get('idx', '-')}",
            ws.get("output", "-"),
            "[green]●[/green]" if ws.get("is_focused") else "",
        )
    console.print(table)

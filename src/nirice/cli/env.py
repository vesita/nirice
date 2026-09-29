"""环境相关命令：状态总览、健康诊断与依赖安装。"""

from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from nirice.cli.app import app
from nirice.cli.common import FAIL, OK, console, print_results
from nirice.inspector import DesktopInspector
from nirice.system import DependencyHelper


@app.command("status")
def status() -> None:
    """查看 Niri 合成器、Noctalia 外壳、状态栏与终端集成的当前状态。"""
    report = DesktopInspector().inspect()

    t_desk = Table(title="[bold cyan]🪟 Niri 合成器与 Noctalia 外壳[/bold cyan]", header_style="bold magenta")
    t_desk.add_column("项目", style="dim", width=24)
    t_desk.add_column("状态", style="bold green")
    t_desk.add_row("会话类型", report.session_type)
    t_desk.add_row(
        "Niri 合成器",
        f"{report.compositor_version} "
        + ("[green](运行中)[/green]" if report.compositor_running else "[yellow](未运行)[/yellow]"),
    )
    t_desk.add_row(
        "Noctalia 外壳",
        f"{report.shell_version} "
        + ("[green](运行中)[/green]" if report.shell_running else "[yellow](未运行)[/yellow]"),
    )
    t_desk.add_row("状态栏位置", f"[bold yellow]{report.bar_position}[/bold yellow]")
    t_desk.add_row("主题配色", f"{report.theme_palette} / {report.theme_mode}")
    t_desk.add_row("已启用模板", ", ".join(report.enabled_templates) or "[dim]无[/dim]")

    t_niri = Table(title="[bold cyan]⌨️  Niri 受管配置片段[/bold cyan]", header_style="bold blue")
    t_niri.add_column("片段文件", style="dim", width=20)
    t_niri.add_column("与 nirice 预设对比", width=22)
    labels = {"same": "[green]一致[/green]", "changed": "[yellow]已本地修改[/yellow]", "missing": "[red]缺失[/red]"}
    for name, state in report.niri_fragments.items():
        t_niri.add_row(name, labels.get(state, state))
    t_niri.add_row("快捷键绑定数", str(report.keybind_count))

    t_term = Table(title="[bold cyan]💻 终端与字体[/bold cyan]", header_style="bold cyan")
    t_term.add_column("组件", style="dim", width=24)
    t_term.add_column("状态")
    t_term.add_row("已安装终端", ", ".join(report.installed_terminals) or "[dim]无[/dim]")
    t_term.add_row(
        "Kitty 配色来源",
        "[green]Noctalia 自动生成[/green]"
        if report.kitty_managed_by_noctalia
        else "[yellow]nirice 回退调色板[/yellow]",
    )
    t_term.add_row(
        "Starship 提示符", "[green]已安装[/green]" if report.starship_installed else "[yellow]未安装[/yellow]"
    )
    t_term.add_row("Fastfetch", "[green]已安装[/green]" if report.fastfetch_installed else "[yellow]未安装[/yellow]")
    t_term.add_row("Nerd Font", f"[{'green' if report.font_ready else 'red'}]{report.font_detail}[/]")

    console.print(t_desk)
    console.print()
    console.print(t_niri)
    console.print()
    console.print(t_term)


@app.command("doctor")
def doctor() -> None:
    """诊断 Niri 生态依赖、Nerd Font 与 Shell 提示符挂钩健康状态。"""
    doc = DependencyHelper().doctor()

    table = Table(title="[bold cyan]🏥 Niri 生态依赖健康状态[/bold cyan]", header_style="bold green")
    table.add_column("组件", style="bold white", width=24)
    table.add_column("分类", style="dim", width=14)
    table.add_column("重要性", width=10)
    table.add_column("状态", width=14)
    table.add_column("安装指令", style="yellow")
    for pkg in doc.packages:
        table.add_row(
            pkg.name,
            pkg.category,
            "[bold red]必需[/bold red]" if pkg.essential else "[dim]可选[/dim]",
            f"{OK} 已安装" if pkg.installed else f"{FAIL} 缺失",
            "[dim]已就绪[/dim]" if pkg.installed else f"[bold yellow]{pkg.install_command}[/bold yellow]",
        )
    console.print(table)

    t_hooks = Table(title="[bold cyan]🐚 Shell 提示符挂钩状态[/bold cyan]", header_style="bold blue")
    t_hooks.add_column("Shell", style="bold white", width=10)
    t_hooks.add_column("配置文件", style="dim", width=38)
    t_hooks.add_column("状态", width=16)
    for hook in doc.hooks:
        t_hooks.add_row(hook.shell, str(hook.rc_file), f"{OK} 已集成" if hook.hooked else "[yellow]未配置[/yellow]")
    console.print(t_hooks)

    font_color = "green" if doc.fonts_ready else "red"
    console.print(
        Panel.fit(
            f"[bold cyan]包管理器:[/] {doc.pkg_manager}   [bold cyan]AUR 助手:[/] {doc.aur_helper or '无'}\n"
            f"[bold cyan]Nerd Font:[/] [{font_color}]{doc.font_details}[/{font_color}]\n"
            f"[bold yellow]提示:[/] 运行 [bold green]nirice install --all[/bold green] 自动补齐缺失依赖。",
            title="诊断总览",
        )
    )


@app.command("install")
def install(
    all_deps: bool = typer.Option(False, "--all", "-a", help="安装全部缺失依赖（含可选推荐项）"),
    hooks_only: bool = typer.Option(False, "--hooks", help="只注入 Starship Shell 挂钩"),
) -> None:
    """通过系统包管理器补齐 Niri 生态依赖，并配置 Shell 提示符挂钩。"""
    helper = DependencyHelper()

    if hooks_only:
        console.print("[bold cyan]正在向 fish/zsh/bash 注入 Starship 挂钩...[/bold cyan]")
        print_results(helper.inject_shell_hooks(["fish", "zsh", "bash"]))
        return

    missing = helper.missing_packages(essential_only=not all_deps)
    if missing:
        console.print(f"[bold cyan]正在安装缺失依赖: {', '.join(missing)}[/bold cyan]")
        ok, message = helper.install_packages(missing)
        console.print(f"  {OK if ok else FAIL} {message}")
    else:
        console.print(f"{OK} [green]所有必需依赖均已就绪！[/green]")

    console.print("[bold cyan]正在校验 Shell 提示符挂钩...[/bold cyan]")
    print_results(helper.inject_shell_hooks(["fish", "zsh", "bash"]))
    console.print(f"\n{OK} [bold green]Niri 生态环境配置完成！[/bold green]")


@app.command("check-deps", hidden=True)
def check_deps() -> None:
    """别名命令，等同 doctor。"""
    doctor()

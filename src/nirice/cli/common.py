"""CLI 共享工具：控制台、状态标记与结果渲染。"""

from __future__ import annotations

from rich.console import Console

console = Console()
OK = "[bold green]✓[/bold green]"
FAIL = "[bold red]✗[/bold red]"


def print_results(results: dict[str, tuple[bool, str]] | list[tuple[str, bool, str]]) -> None:
    """统一渲染 {名称: (是否成功, 消息)} 或 [(名称, 是否成功, 消息)]。"""
    if isinstance(results, dict):
        for name, (ok, message) in results.items():
            console.print(f"  {OK if ok else FAIL} [bold]{name}[/bold]: {message}")
        return
    for name, ok, message in results:
        console.print(f"  {OK if ok else FAIL} [bold]{name}[/bold]: {message}")

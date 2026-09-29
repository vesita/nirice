"""nirice 命令行入口：组装根应用并注册各领域子命令。"""

from __future__ import annotations

# 导入顺序即命令注册顺序；这些模块在 import 时完成 @app.command / add_typer 注册。
from nirice.cli import env as _env  # noqa: E402,F401
from nirice.cli import migrate as _migrate  # noqa: E402,F401
from nirice.cli import niri as _niri  # noqa: E402,F401
from nirice.cli import shell as _shell  # noqa: E402,F401
from nirice.cli import snapshot as _snapshot  # noqa: E402,F401
from nirice.cli import terminal as _terminal  # noqa: E402,F401
from nirice.cli import theme as _theme  # noqa: E402,F401
from nirice.cli.app import app

app.add_typer(_niri.app, name="niri")
app.add_typer(_shell.app, name="shell")
app.add_typer(_terminal.app, name="terminal")
app.add_typer(_theme.app, name="theme")
app.add_typer(_snapshot.app, name="snapshot")
app.add_typer(_migrate.app, name="migrate")


def main() -> None:
    """控制台脚本入口。"""
    app()


__all__ = ["app", "main"]

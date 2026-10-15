"""nirice 根 CLI 应用对象。

单独成模块是为了让各子命令模块可以安全地 import 它而不产生循环依赖：
`nirice.cli.__init__` 负责按顺序导入各模块以完成命令注册。
"""

from __future__ import annotations

import typer

app = typer.Typer(
    name="nirice",
    help="Niri + Noctalia Wayland 桌面美化、终端联动与跨机器迁移工具箱。",
    add_completion=False,
)

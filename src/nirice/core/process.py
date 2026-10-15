"""子进程调用的统一封装：超时、静默失败与输出归一化。"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

Command = Sequence[str | Path]


def which(name: str) -> str | None:
    """包装 shutil.which，便于测试替换。"""
    return shutil.which(name)


def run(
    cmd: Command,
    *,
    timeout: int = 10,
    check: bool = False,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    """执行命令并永远返回 CompletedProcess（不抛 CalledProcessError）。"""
    return subprocess.run(
        [str(part) for part in cmd],
        capture_output=capture,
        text=True,
        timeout=timeout,
        check=check,
    )


def run_capture(cmd: Command, *, timeout: int = 10) -> tuple[bool, str]:
    """执行命令并返回 (是否成功, 合并后的输出)。"""
    try:
        result = run(cmd, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return False, str(exc)
    output = (result.stdout or result.stderr or "").strip()
    return result.returncode == 0, output


def run_quiet(cmd: Command, *, timeout: int = 10) -> bool:
    """只关心成败的命令执行。"""
    ok, _ = run_capture(cmd, timeout=timeout)
    return ok


def pkill(signal: str, process: str) -> bool:
    """向进程发送信号（用于 Kitty 配置热重载等）。"""
    if not which("pkill"):
        return False
    return run_quiet(["pkill", signal, process])

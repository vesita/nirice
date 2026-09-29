"""TOML 设置文件的「外科手术式」编辑工具。

Noctalia 的 `settings.toml` 由它自己维护，内含大量嵌套表与未知键。
用 TOML 库整体重写会破坏格式并可能丢失新版本才有的字段，
因此这里只做「定位小节 + 增删改目标键」的文本级操作。
"""

from __future__ import annotations

import re
from typing import Any


def format_value(value: Any) -> str:
    """把 Python 值渲染为 TOML 字面量。"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def find_section(lines: list[str], section: str) -> tuple[int, int] | None:
    """定位 `[section]` 的行区间 [start, end)，end 为下一个表头之前。"""
    header = f"[{section}]"
    for index, line in enumerate(lines):
        if line.strip() == header:
            end = index + 1
            while end < len(lines) and not lines[end].lstrip().startswith("["):
                end += 1
            return index, end
    return None


def get_key(text: str, section: str, key: str) -> str | None:
    """读取指定小节中某个键的原始字面量（不含键名与等号）。"""
    lines = text.splitlines()
    found = find_section(lines, section)
    if not found:
        return None
    start, end = found
    for index in range(start + 1, end):
        match = re.match(rf"^{re.escape(key)}\s*=\s*(.+)$", lines[index].strip())
        if match:
            return match.group(1).strip()
    return None


def set_key(text: str, section: str, key: str, value: Any) -> str:
    """在指定小节中写入/替换一个键，小节不存在时追加到文件末尾。"""
    raw = format_value(value)
    lines = text.splitlines()
    found = find_section(lines, section)

    if found:
        start, end = found
        for index in range(start + 1, end):
            if re.match(rf"^{re.escape(key)}\s*=", lines[index].strip()):
                lines[index] = f"{key} = {raw}"
                return "\n".join(lines) + "\n"
        lines.insert(start + 1, f"{key} = {raw}")
        return "\n".join(lines) + "\n"

    base = text.rstrip("\n")
    prefix = f"{base}\n\n" if base else ""
    return f"{prefix}[{section}]\n{key} = {raw}\n"

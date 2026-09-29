"""Niri 生态的声明式依赖清单与探测探针。"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from nirice.core import which


@dataclass
class PackageDef:
    """一个软件包的声明式定义（含多个探测探针，任一命中即视为已安装）。"""

    name: str
    category: str
    description: str
    probes: tuple[Callable[[], bool], ...]
    pacman_name: str | None = None
    essential: bool = False

    def installed(self) -> bool:
        return any(probe() for probe in self.probes)

    @property
    def install_name(self) -> str:
        return self.pacman_name or self.name


def has_bin(*names: str) -> Callable[[], bool]:
    return lambda: any(which(name) is not None for name in names)


def has_path(*paths: str) -> Callable[[], bool]:
    return lambda: any(Path(p).exists() for p in paths)


def has_pacman_pkg(name: str) -> Callable[[], bool]:
    def check() -> bool:
        if not shutil.which("pacman"):
            return False
        result = subprocess.run(["pacman", "-Qq", name], capture_output=True, text=True, check=False)
        return result.returncode == 0

    return check


def _has_nerd_font() -> bool:
    """探测 Nerd Font：优先 fc-list，其次本地/系统字体目录。"""
    if shutil.which("fc-list"):
        try:
            result = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, check=False)
            output = result.stdout.lower()
            if "meslolgs nerd font" in output or "nerd font" in output:
                return True
        except OSError:
            pass
    for base in (Path.home() / ".local/share/fonts", Path("/usr/share/fonts"), Path("/usr/local/share/fonts")):
        if not base.exists():
            continue
        try:
            for entry in base.rglob("*"):
                if "meslo" in entry.name.lower() or "nerd" in entry.name.lower():
                    return True
        except OSError:
            continue
    return False


def package_defs() -> list[PackageDef]:
    """返回 Niri 生态的完整依赖清单。"""
    return [
        # ── 1. 合成器与外壳 ──
        PackageDef("niri", "合成器", "可滚动平铺的现代 Wayland 合成器", (has_bin("niri"),), "niri", essential=True),
        PackageDef(
            "noctalia",
            "桌面外壳",
            "状态栏 / 启动器 / 通知 / OSD 一体的 Quickshell 外壳",
            (has_bin("noctalia"),),
            "noctalia",
            essential=True,
        ),
        PackageDef(
            "cachyos-niri-noctalia",
            "CachyOS 集成",
            "CachyOS 提供的 Niri+Noctalia 默认配置与 dconf 主题",
            (has_pacman_pkg("cachyos-niri-noctalia"), has_path("/etc/skel/.config/niri/config.kdl")),
            "cachyos-niri-noctalia",
            essential=True,
        ),
        # ── 2. 会话与门户 ──
        PackageDef(
            "xdg-desktop-portal",
            "桌面门户",
            "沙盒应用与桌面集成的门户守护",
            (has_bin("xdg-desktop-portal"), has_path("/usr/lib/xdg-desktop-portal")),
            "xdg-desktop-portal",
            essential=True,
        ),
        PackageDef(
            "xdg-desktop-portal-gtk",
            "桌面门户",
            "GTK 门户后端（文件选择器等）",
            (has_path("/usr/lib/xdg-desktop-portal-gtk"),),
            "xdg-desktop-portal-gtk",
            essential=True,
        ),
        PackageDef(
            "xdg-desktop-portal-gnome",
            "桌面门户",
            "GNOME 门户后端（屏幕共享、远程桌面）",
            (has_path("/usr/lib/xdg-desktop-portal-gnome"),),
            "xdg-desktop-portal-gnome",
            essential=False,
        ),
        PackageDef(
            "xwayland-satellite",
            "X11 兼容",
            "让 X11 应用在 niri 下可用的根less Xwayland",
            (has_bin("xwayland-satellite"),),
            "xwayland-satellite",
            essential=False,
        ),
        PackageDef(
            "gnome-keyring",
            "密钥环",
            "保存 Wi-Fi / 应用密码的 Secret Service",
            (has_bin("gnome-keyring-daemon"),),
            "gnome-keyring",
            essential=True,
        ),
        # ── 3. 外观与字体 ──
        PackageDef(
            "adw-gtk-theme",
            "GTK 主题",
            "让 GTK3 应用使用 libadwaita 观感",
            (has_path("/usr/share/themes/adw-gtk3"),),
            "adw-gtk-theme",
            essential=False,
        ),
        PackageDef(
            "capitaine-cursors",
            "鼠标指针",
            "niri 默认配置引用的指针主题",
            (has_path("/usr/share/icons/capitaine-cursors", "/usr/share/icons/Capitaine-cursors"),),
            "capitaine-cursors",
            essential=False,
        ),
        PackageDef(
            "noto-fonts",
            "字体",
            "基础无衬线字体",
            (has_path("/usr/share/fonts/noto"), has_pacman_pkg("noto-fonts")),
            "noto-fonts",
            essential=False,
        ),
        PackageDef(
            "noto-fonts-cjk",
            "字体",
            "中日韩字形（避免字距异常）",
            (has_path("/usr/share/fonts/noto-cjk"), has_pacman_pkg("noto-fonts-cjk")),
            "noto-fonts-cjk",
            essential=False,
        ),
        PackageDef(
            "noto-fonts-emoji",
            "字体",
            "彩色 Emoji 字体",
            (has_path("/usr/share/fonts/noto-emoji"), has_pacman_pkg("noto-fonts-emoji")),
            "noto-fonts-emoji",
            essential=False,
        ),
        PackageDef(
            "ttf-meslo-nerd",
            "Nerd Font",
            "MesloLGS Nerd Font：Kitty 与 Starship 图标字体",
            (has_pacman_pkg("ttf-meslo-nerd"), _has_nerd_font),
            "ttf-meslo-nerd",
            essential=True,
        ),
        # ── 4. 终端与 Shell ──
        PackageDef(
            "kitty",
            "终端模拟器",
            "GPU 加速终端，支持真彩色、分屏与透明度",
            (has_bin("kitty"),),
            "kitty",
            essential=True,
        ),
        PackageDef("fish", "Shell", "开箱即用的现代交互式 Shell", (has_bin("fish"),), "fish", essential=False),
        PackageDef(
            "starship", "Shell 提示符", "跨 Shell 现代化提示符", (has_bin("starship"),), "starship", essential=False
        ),
        PackageDef("fastfetch", "系统看板", "极速系统信息展示", (has_bin("fastfetch"),), "fastfetch", essential=False),
        PackageDef("eza", "CLI 工具", "ls 现代化替代（图标 + Git 状态）", (has_bin("eza"),), "eza", essential=False),
        PackageDef("bat", "CLI 工具", "cat 现代化替代（语法高亮）", (has_bin("bat"),), "bat", essential=False),
        PackageDef("zoxide", "CLI 工具", "智能目录跳转", (has_bin("zoxide"),), "zoxide", essential=False),
        # ── 5. Wayland 常用工具 ──
        PackageDef(
            "wl-clipboard",
            "Wayland 工具",
            "命令行剪贴板读写（剪贴板面板依赖）",
            (has_bin("wl-copy", "wl-paste"),),
            "wl-clipboard",
            essential=True,
        ),
        PackageDef(
            "brightnessctl", "硬件控制", "屏幕亮度调节", (has_bin("brightnessctl"),), "brightnessctl", essential=False
        ),
        PackageDef("playerctl", "媒体控制", "MPRIS 播放器控制", (has_bin("playerctl"),), "playerctl", essential=False),
        PackageDef(
            "networkmanager",
            "系统服务",
            "网络管理（状态栏 Wi-Fi/有线）",
            (has_bin("nmcli"),),
            "networkmanager",
            essential=False,
        ),
        PackageDef("bluez", "系统服务", "蓝牙协议栈", (has_bin("bluetoothctl"),), "bluez", essential=False),
        PackageDef("upower", "系统服务", "电池与电源管理", (has_bin("upower"),), "upower", essential=False),
    ]

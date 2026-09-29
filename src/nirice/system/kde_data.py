"""KDE 残留的检测清单（仅用于识别与提示，永不自动卸载）。"""

from __future__ import annotations

# 典型 KDE Plasma 软件包
KDE_PACKAGES = [
    "plasma-desktop",
    "plasma-workspace",
    "plasma-nm",
    "plasma-pa",
    "plasma-integration",
    "kwin",
    "kwin-x11",
    "kdecoration",
    "kdeplasma-addons",
    "kde-gtk-config",
    "bluedevil",
    "powerdevil",
    "kscreen",
    "konsole",
    "dolphin",
    "kate",
    "ark",
    "gwenview",
    "sddm-kcm",
    "breeze",
    "breeze-gtk",
    "kwallet",
    "kwallet-pam",
    "polkit-kde-agent",
    "xdg-desktop-portal-kde",
]

# KDE 会持续写入、在 niri 会话里毫无用处的用户配置
KDE_CONFIG_FILES = [
    "kdeglobals",
    "kwinrc",
    "kwinrulesrc",
    "kglobalshortcutsrc",
    "kcminputrc",
    "kcmfonts",
    "plasmarc",
    "plasmashellrc",
    "ksplashrc",
    "klauncherrc",
    "kded5rc",
    "kded6rc",
    "kwalletrc",
    "konsolerc",
    "plasma-org.kde.plasma.desktop-appletsrc",
    "plasma-org.kde.plasma.desktop-appletsrc.lock",
    "kactivitiesrc",
    "ktimezonedrc",
    "kio_httprc",
]

# KDE 的用户级数据目录
KDE_DATA_DIRS = [
    "plasma",
    "kwin",
    "kxmlgui5",
    "knotifications5",
    "kded5",
    "konsole",
    "dolphin",
    "kate",
    "aurorae",
]

# 自动启动项中命中这些关键字即视为 KDE 残留
KDE_AUTOSTART_TAGS = ("kde", "plasma", "kwin", "kdeconnect", "kded")

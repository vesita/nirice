"""Niri 受管配置片段模板（cfg/*.kdl 与主入口 config.kdl）。"""

# ==============================================================================
# 3. 其余受管片段
# ==============================================================================

AUTOSTART_KDL = """// ────────────── 开机自启动（由 nirice 管理）──────────────
// https://github.com/YaLTeR/niri/wiki/Configuration:-Miscellaneous#spawn-sh-at-startup

spawn-at-startup "noctalia"
"""

INPUT_KDL = """// ────────────── 输入设备（由 nirice 管理）──────────────
// https://github.com/YaLTeR/niri/wiki/Configuration:-Input

input {
    keyboard {
        xkb {
            // 如需强制键盘布局，取消注释并修改
            // layout "us"
        }
        numlock
    }

    touchpad {
        tap
        natural-scroll
    }

    mouse {
        // 如需关闭鼠标加速，取消注释
        // accel-profile "flat"
        // accel-speed 0.0
    }

    focus-follows-mouse
    workspace-auto-back-and-forth
}
"""

LAYOUT_KDL = """// ────────────── 布局（由 nirice 管理）──────────────
// https://github.com/YaLTeR/niri/wiki/Configuration:-Layout

layout {
    gaps 16
    center-focused-column "never"

    // 保持透明以便 Noctalia 绘制壁纸
    background-color "transparent"

    preset-column-widths {
        proportion 0.33333
        proportion 0.5
        proportion 0.66667
    }

    preset-window-heights {
        proportion 0.33333
        proportion 0.5
        proportion 0.66667
    }

    default-column-width { proportion 0.5; }

    struts {}
}
"""

MISC_KDL = """// ────────────── 杂项（由 nirice 管理）──────────────
// https://github.com/YaLTeR/niri/wiki/Configuration:-Miscellaneous

prefer-no-csd
screenshot-path null

environment {
    ELECTRON_OZONE_PLATFORM_HINT "auto"
    QT_QPA_PLATFORM "wayland"
    QT_QPA_PLATFORMTHEME "gtk3"
    QT_WAYLAND_DISABLE_WINDOWDECORATION "1"
    XDG_CURRENT_DESKTOP "niri"
    XDG_SESSION_TYPE "wayland"
}

cursor {
    xcursor-theme "capitaine-cursors"
    xcursor-size 24
}

blur {
    passes 2
    offset 3.0
    noise 0.03
    saturation 1.0
}

debug {
    // 允许 Noctalia 触发通知动作与窗口激活
    honor-xdg-activation-with-invalid-serial
}

hotkey-overlay {
    skip-at-startup
}
"""

RULES_KDL = """// ────────────── 窗口与图层规则（由 nirice 管理）──────────────
// https://github.com/YaLTeR/niri/wiki/Configuration:-Window-Rules

window-rule {
    geometry-corner-radius 20
    clip-to-geometry true
}

window-rule {
    background-effect {
        blur true
        xray false
    }
}

// Noctalia 设置窗口
window-rule {
    match app-id="dev.noctalia.Noctalia"
    open-floating true
    default-column-width { fixed 1080; }
    default-window-height { fixed 920; }
}

// Steam 覆盖层与提示
window-rule {
    match app-id="steam"
    exclude title=r#"^[Ss]team$"#
    open-floating true
}

window-rule {
    match app-id="steam" title=r#"^notificationtoasts_\\d+_desktop$"#
    default-floating-position x=10 y=10 relative-to="bottom-right"
    open-focused false
}

layer-rule {
    match namespace="^noctalia-wallpaper"
    place-within-backdrop true
}

layer-rule {
    match namespace="^noctalia-(bar-[^\\"]+|notification|dock|panel|attached-panel|osd)$"
    background-effect {
        xray false
    }
}
"""

CONFIG_KDL = """// ────────────── Niri 主配置（由 nirice 管理）──────────────
// https://github.com/YaLTeR/niri/wiki/Configuration:-Introduction
//
// noctalia.kdl 由 Noctalia 自动生成（焦点环/边框/标签指示器配色），
// 请不要删除下面这行 include，否则外壳配色将无法联动到合成器。

include "./cfg/animation.kdl"
include "./cfg/autostart.kdl"
include "./cfg/keybinds.kdl"
include "./cfg/input.kdl"
include "./cfg/display.kdl"
include "./cfg/layout.kdl"
include "./cfg/rules.kdl"
include "./cfg/misc.kdl"

include "noctalia.kdl"
"""

# display.kdl 与具体硬件绑定，nirice 默认只在文件缺失时生成，不覆盖用户配置。
DISPLAY_KDL = """// ────────────── 显示器输出（用户自有，nirice 不覆盖）──────────────
// 运行 `niri msg outputs` 获取正确的显示器名称，然后取消注释并修改。
// https://github.com/YaLTeR/niri/wiki/Configuration:-Outputs

// output "eDP-1" {
//     mode "1920x1080@60.000"
//     scale 1.25
//     transform "normal"
// }
"""

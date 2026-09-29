"""Niri 快捷键（binds 块）预设。

niri 的 hotkey overlay **没有本地化**：文案硬编码在二进制里，没有翻译文件，
设置 LANG 也无效。因此这里给每一条绑定都显式加上 `hotkey-overlay-title`，
让 Mod+/ 弹出的快捷键总览完全显示中文。

设计取舍：

- 只保留单 Mod 可达的高频动作，**同一动作不留别名**。
- 方向键负责跨列 / 跨工作区导航，K / J 负责列内窗口导航。二者不可互相替代：
  `focus-window-up/down` 没有方向键版本，删掉 K / J 就再也无法在列内切窗口。
- 长尾动作一律移除：缩放 ±10%、居中、侧边吸附、数字工作区、鼠标滚轮、
  反向循环列宽、关闭显示器、壁纸选择器。这些由 `Mod+R` 循环列宽、
  `Mod+Tab` 总览和 Noctalia 面板覆盖。
"""

from __future__ import annotations

# 说明：niri 一个快捷键只允许一个动作；多步操作需用 spawn-sh 串联 `niri msg action`。
# 注意：修饰键顺序无意义 —— Mod+Ctrl+Shift+X 与 Mod+Shift+Ctrl+X 是同一个键，
#       新增绑定后务必运行 `nirice niri check`，niri validate 会直接报出重复绑定。
KEYBINDS_KDL = """// ────────────── Niri 快捷键（由 nirice 管理）──────────────
// 参考：https://github.com/YaLTeR/niri/wiki/Configuration:-Key-Bindings
// 手工修改本文件会被 `nirice niri apply` 覆盖；请改 nirice 预设或使用 --no-keybinds。
//
// 每条绑定都带 hotkey-overlay-title，因此 Mod+/ 弹出的快捷键总览是全中文的。
//
// 导航分工（不要合并）：
//   Mod+← / →   跨列        Mod+↑ / ↓   跨工作区
//   Mod+K / J   列内上下窗口（无方向键等价物）

binds {
    // ─── 快捷键总览与应急逃生 ───
    Mod+Slash                     hotkey-overlay-title="查看全部快捷键" { show-hotkey-overlay; }
    Mod+Escape                    allow-inhibiting=false hotkey-overlay-title="解除快捷键抑制（应急）" { toggle-keyboard-shortcuts-inhibit; }

    // ─── 窗口操作 ───
    Mod+Q                         hotkey-overlay-title="关闭窗口" { close-window; }
    Mod+Shift+V                   hotkey-overlay-title="在浮动与平铺之间切换" { toggle-window-floating; }

    // ─── 应用启动 ───
    Mod+T                         repeat=false hotkey-overlay-title="终端：kitty" { spawn "kitty"; }
    Mod+D                         repeat=false hotkey-overlay-title="应用启动器" { spawn-sh "noctalia msg panel-toggle launcher"; }
    Mod+B                         repeat=false hotkey-overlay-title="浏览器：Firefox" { spawn "firefox"; }
    Mod+E                         repeat=false hotkey-overlay-title="文件管理器：Nautilus" { spawn "nautilus"; }

    // ─── Noctalia 外壳 ───
    Mod+V                         repeat=false hotkey-overlay-title="剪贴板历史" { spawn-sh "noctalia msg panel-toggle clipboard"; }
    Mod+S                         repeat=false hotkey-overlay-title="控制中心" { spawn-sh "noctalia msg panel-toggle control-center"; }
    Mod+Shift+S                   repeat=false hotkey-overlay-title="系统设置" { spawn-sh "noctalia msg settings-toggle"; }
    Mod+Shift+Q                   repeat=false hotkey-overlay-title="会话菜单（关机 / 重启）" { spawn-sh "noctalia msg panel-toggle session"; }
    Mod+Alt+L                     repeat=false hotkey-overlay-title="锁定屏幕" { spawn-sh "noctalia msg session lock"; }

    // ─── 导航：跨列与跨工作区 ───
    Mod+Left                      hotkey-overlay-title="聚焦左侧一列" { focus-column-left; }
    Mod+Right                     hotkey-overlay-title="聚焦右侧一列" { focus-column-right; }
    Mod+Up                        hotkey-overlay-title="上一个工作区" { focus-workspace-up; }
    Mod+Down                      hotkey-overlay-title="下一个工作区" { focus-workspace-down; }
    Mod+G                         hotkey-overlay-title="回到上一个聚焦的窗口" { focus-window-previous; }

    // ─── 导航：列内上下窗口 ───
    // 不要用 focus-window-up-or-column-left —— 列内没有上层窗口时它会自动
    // 掉到相邻列，导致"上下"和"左右"表现一样。
    Mod+K                         hotkey-overlay-title="列内上一个窗口" { focus-window-up; }
    Mod+J                         hotkey-overlay-title="列内下一个窗口" { focus-window-down; }

    // ─── 移动列与窗口 ───
    Mod+Ctrl+Left                 hotkey-overlay-title="整列左移" { move-column-left; }
    Mod+Ctrl+Right                hotkey-overlay-title="整列右移" { move-column-right; }
    Mod+Ctrl+Up                   hotkey-overlay-title="整列移到上一个工作区" { move-column-to-workspace-up; }
    Mod+Ctrl+Down                 hotkey-overlay-title="整列移到下一个工作区" { move-column-to-workspace-down; }
    Mod+Ctrl+K                    hotkey-overlay-title="列内窗口上移" { move-window-up; }
    Mod+Ctrl+J                    hotkey-overlay-title="列内窗口下移" { move-window-down; }

    // ─── 布局 ───
    // Mod+R 在预设列宽之间循环：1/3 → 1/2 → 2/3
    Mod+R                         hotkey-overlay-title="改变窗口大小（循环预设列宽）" { switch-preset-column-width; }
    Mod+Shift+F                   hotkey-overlay-title="真全屏" { fullscreen-window; }
    Mod+W                         hotkey-overlay-title="切换标签式列显示" { toggle-column-tabbed-display; }

    // ─── 总览 ───
    Mod+Tab                       repeat=false hotkey-overlay-title="总览 Overview（所有工作区）" { toggle-overview; }

    // ─── 截图 ───
    Print                         hotkey-overlay-title="截图（交互式选区）" { screenshot; }
    Ctrl+Print                    hotkey-overlay-title="截取整个屏幕" { screenshot-screen; }
    Alt+Print                     hotkey-overlay-title="截取当前窗口" { screenshot-window; }

    // ─── 媒体与亮度（XF86 功能键，不占用组合键）───
    // 播放键用 toggle：笔记本通常只有一个播放/暂停键，同时发 XF86AudioPlay。
    XF86AudioRaiseVolume          allow-when-locked=true hotkey-overlay-title="音量增大" { spawn-sh "noctalia msg volume-up"; }
    XF86AudioLowerVolume          allow-when-locked=true hotkey-overlay-title="音量减小" { spawn-sh "noctalia msg volume-down"; }
    XF86AudioMute                 allow-when-locked=true hotkey-overlay-title="静音开关" { spawn-sh "noctalia msg volume-mute"; }
    XF86AudioMicMute              allow-when-locked=true hotkey-overlay-title="麦克风静音开关" { spawn-sh "noctalia msg mic-mute"; }
    XF86AudioPlay                 allow-when-locked=true hotkey-overlay-title="播放 / 暂停" { spawn-sh "noctalia msg media toggle"; }
    XF86AudioNext                 allow-when-locked=true hotkey-overlay-title="下一首" { spawn-sh "noctalia msg media next"; }
    XF86AudioPrev                 allow-when-locked=true hotkey-overlay-title="上一首" { spawn-sh "noctalia msg media previous"; }
    XF86MonBrightnessUp           allow-when-locked=true hotkey-overlay-title="屏幕亮度增大" { spawn-sh "noctalia msg brightness-up"; }
    XF86MonBrightnessDown         allow-when-locked=true hotkey-overlay-title="屏幕亮度减小" { spawn-sh "noctalia msg brightness-down"; }

    // ─── 退出 ───
    Ctrl+Alt+Delete               hotkey-overlay-title="退出 niri" { quit; }
}
"""

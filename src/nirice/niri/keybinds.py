"""Niri 快捷键（binds 块）预设。

niri 的 hotkey overlay **没有本地化**：文案硬编码在二进制里，没有翻译文件，
设置 LANG 也无效。因此这里给每一条绑定都显式加上 `hotkey-overlay-title`，
让 Mod+/ 弹出的快捷键总览完全显示中文。
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

binds {
    // ─── 快捷键总览与紧急逃生 ───
    Mod+Slash                     hotkey-overlay-title="查看全部快捷键" { show-hotkey-overlay; }
    Mod+Shift+Escape              hotkey-overlay-title="查看全部快捷键（备用）" { show-hotkey-overlay; }
    Mod+Escape                    allow-inhibiting=false hotkey-overlay-title="解除快捷键抑制（应急）" { toggle-keyboard-shortcuts-inhibit; }

    // ─── 窗口操作 ───
    Mod+Q                         hotkey-overlay-title="关闭窗口" { close-window; }

    // ─── 应用启动 ───
    Mod+T                         repeat=false hotkey-overlay-title="终端：kitty" { spawn "kitty"; }
    Mod+Return                    repeat=false hotkey-overlay-title="终端：kitty" { spawn "kitty"; }
    Mod+Shift+T                   repeat=false hotkey-overlay-title="终端：alacritty" { spawn "alacritty"; }
    Mod+B                         repeat=false hotkey-overlay-title="浏览器：Firefox" { spawn "firefox"; }
    Mod+E                         repeat=false hotkey-overlay-title="文件管理器：Nautilus" { spawn "nautilus"; }

    // ─── Noctalia 外壳 ───
    Mod+D                         repeat=false hotkey-overlay-title="应用启动器" { spawn-sh "noctalia msg panel-toggle launcher"; }
    Mod+Space                     repeat=false hotkey-overlay-title="应用启动器" { spawn-sh "noctalia msg panel-toggle launcher"; }
    Mod+S                         repeat=false hotkey-overlay-title="控制中心" { spawn-sh "noctalia msg panel-toggle control-center"; }
    Mod+Shift+S                   repeat=false hotkey-overlay-title="系统设置" { spawn-sh "noctalia msg settings-toggle"; }
    Mod+Shift+Return              repeat=false hotkey-overlay-title="壁纸选择器" { spawn-sh "noctalia msg panel-toggle wallpaper"; }
    Mod+Shift+Q                   repeat=false hotkey-overlay-title="会话菜单（关机 / 重启）" { spawn-sh "noctalia msg panel-toggle session"; }
    Mod+Alt+L                     repeat=false hotkey-overlay-title="锁定屏幕" { spawn-sh "noctalia msg session lock"; }
    Mod+Ctrl+V                    repeat=false hotkey-overlay-title="剪贴板历史" { spawn-sh "noctalia msg panel-toggle clipboard"; }
    Mod+Ctrl+N                    repeat=false hotkey-overlay-title="切换免打扰模式" { spawn-sh "noctalia msg notification-dnd-toggle"; }
    Mod+Grave                     repeat=false hotkey-overlay-title="窗口切换器" { spawn-sh "noctalia msg window-switcher"; }

    // ─── 媒体与亮度 ───
    XF86AudioRaiseVolume          allow-when-locked=true hotkey-overlay-title="音量增大" { spawn-sh "noctalia msg volume-up"; }
    XF86AudioLowerVolume          allow-when-locked=true hotkey-overlay-title="音量减小" { spawn-sh "noctalia msg volume-down"; }
    XF86AudioMute                 allow-when-locked=true hotkey-overlay-title="静音开关" { spawn-sh "noctalia msg volume-mute"; }
    XF86AudioMicMute              allow-when-locked=true hotkey-overlay-title="麦克风静音开关" { spawn-sh "noctalia msg mic-mute"; }
    XF86AudioNext                 allow-when-locked=true hotkey-overlay-title="下一首" { spawn-sh "noctalia msg media next"; }
    XF86AudioPrev                 allow-when-locked=true hotkey-overlay-title="上一首" { spawn-sh "noctalia msg media previous"; }
    XF86AudioPlay                 allow-when-locked=true hotkey-overlay-title="播放" { spawn-sh "noctalia msg media play"; }
    XF86AudioPause                allow-when-locked=true hotkey-overlay-title="暂停" { spawn-sh "noctalia msg media stop"; }
    XF86MonBrightnessUp           allow-when-locked=true hotkey-overlay-title="屏幕亮度增大" { spawn-sh "noctalia msg brightness-up"; }
    XF86MonBrightnessDown         allow-when-locked=true hotkey-overlay-title="屏幕亮度减小" { spawn-sh "noctalia msg brightness-down"; }
    XF86KbdBrightnessUp           allow-when-locked=true hotkey-overlay-title="键盘背光增大" { spawn-sh "noctalia msg keyboard-backlight-up"; }
    XF86KbdBrightnessDown         allow-when-locked=true hotkey-overlay-title="键盘背光减小" { spawn-sh "noctalia msg keyboard-backlight-down"; }

    // ─── 横向导航：列 ───
    Mod+Left                      hotkey-overlay-title="聚焦左侧一列" { focus-column-left; }
    Mod+H                         hotkey-overlay-title="聚焦左侧一列" { focus-column-left; }
    Mod+Right                     hotkey-overlay-title="聚焦右侧一列" { focus-column-right; }
    Mod+L                         hotkey-overlay-title="聚焦右侧一列" { focus-column-right; }
    Mod+Home                      hotkey-overlay-title="跳到第一列" { focus-column-first; }
    Mod+End                       hotkey-overlay-title="跳到最后一列" { focus-column-last; }
    Mod+G                         hotkey-overlay-title="回到上一个聚焦的窗口" { focus-window-previous; }

    // ─── 上下切页：工作区（Mod+上下，与旧的 Mod+Tab 语义一致）───
    // 方向对应关系：上/下 = 上/下一个工作区，左/右 = 上/下一列。
    Mod+Up                        hotkey-overlay-title="上一个工作区" { focus-workspace-up; }
    Mod+Down                      hotkey-overlay-title="下一个工作区" { focus-workspace-down; }
    Mod+Page_Up                   hotkey-overlay-title="上一个工作区" { focus-workspace-up; }
    Mod+Page_Down                 hotkey-overlay-title="下一个工作区" { focus-workspace-down; }
    Mod+Shift+Tab                 hotkey-overlay-title="回到上一个工作区" { focus-workspace-previous; }

    // ─── 列内上下窗口：Mod+K / Mod+J ───
    // 不要用 focus-window-up-or-column-left —— 列内没有上层窗口时它会自动
    // 掉到相邻列，导致"上下"和"左右"表现一样。
    Mod+K                         hotkey-overlay-title="列内上一个窗口" { focus-window-up; }
    Mod+J                         hotkey-overlay-title="列内下一个窗口" { focus-window-down; }

    // ─── 移动列与窗口 ───
    Mod+Ctrl+Left                 hotkey-overlay-title="整列左移" { move-column-left; }
    Mod+Ctrl+H                    hotkey-overlay-title="整列左移" { move-column-left; }
    Mod+Ctrl+Right                hotkey-overlay-title="整列右移" { move-column-right; }
    Mod+Ctrl+L                    hotkey-overlay-title="整列右移" { move-column-right; }
    Mod+Ctrl+Up                   hotkey-overlay-title="整列移到上一个工作区" { move-column-to-workspace-up; }
    Mod+Ctrl+Down                 hotkey-overlay-title="整列移到下一个工作区" { move-column-to-workspace-down; }
    Mod+Ctrl+Page_Up              hotkey-overlay-title="整列移到上一个工作区" { move-column-to-workspace-up; }
    Mod+Ctrl+Page_Down            hotkey-overlay-title="整列移到下一个工作区" { move-column-to-workspace-down; }
    Mod+Ctrl+K                    hotkey-overlay-title="列内窗口上移" { move-window-up; }
    Mod+Ctrl+J                    hotkey-overlay-title="列内窗口下移" { move-window-down; }
    Mod+Ctrl+Home                 hotkey-overlay-title="整列移到最左" { move-column-to-first; }
    Mod+Ctrl+End                  hotkey-overlay-title="整列移到最右" { move-column-to-last; }
    Mod+Ctrl+Shift+H              hotkey-overlay-title="与右邻窗口交换位置" { swap-window-right; }

    // ─── 多显示器 ───
    Mod+Shift+Left                hotkey-overlay-title="聚焦左侧显示器" { focus-monitor-left; }
    Mod+Shift+Right               hotkey-overlay-title="聚焦右侧显示器" { focus-monitor-right; }
    Mod+Shift+Ctrl+Left           hotkey-overlay-title="整列移到左侧显示器" { move-column-to-monitor-left; }
    Mod+Shift+Ctrl+Right          hotkey-overlay-title="整列移到右侧显示器" { move-column-to-monitor-right; }
    Mod+Shift+Ctrl+Up             hotkey-overlay-title="整列移到上方显示器" { move-column-to-monitor-up; }
    Mod+Shift+Ctrl+Down           hotkey-overlay-title="整列移到下方显示器" { move-column-to-monitor-down; }

    // ─── 布局：窗口尺寸 ───
    // Mod+R 在预设列宽之间循环：1/3 → 1/2 → 2/3
    Mod+R                         hotkey-overlay-title="改变窗口大小（循环预设列宽）" { switch-preset-column-width; }
    Mod+Shift+R                   hotkey-overlay-title="反向循环预设列宽" { switch-preset-column-width-back; }
    Mod+Minus                     hotkey-overlay-title="列宽减小 10%" { set-column-width "-10%"; }
    Mod+Equal                     hotkey-overlay-title="列宽增大 10%" { set-column-width "+10%"; }
    Mod+Shift+Minus               hotkey-overlay-title="窗口高度减小 10%" { set-window-height "-10%"; }
    Mod+Shift+Equal               hotkey-overlay-title="窗口高度增大 10%" { set-window-height "+10%"; }
    Mod+Ctrl+Shift+R              hotkey-overlay-title="循环预设窗口高度" { switch-preset-window-height; }
    Mod+Ctrl+R                    hotkey-overlay-title="重置窗口高度" { reset-window-height; }

    // ─── 布局：最大化与全屏 ───
    Mod+F                         hotkey-overlay-title="最大化当前列" { maximize-column; }
    Mod+Shift+F                   hotkey-overlay-title="真全屏" { fullscreen-window; }
    Mod+Shift+D                   hotkey-overlay-title="窗口化全屏（保留边框）" { toggle-windowed-fullscreen; }
    Mod+M                         hotkey-overlay-title="最大化到屏幕边缘" { maximize-window-to-edges; }
    Mod+Shift+M                   hotkey-overlay-title="扩展到可用宽度" { expand-column-to-available-width; }

    // ─── 布局：居中与侧边对齐 ───
    // niri 是滚动平铺模型，"对齐侧边" = 先设宽 50% 再移动到条带最左/最右
    Mod+C                         hotkey-overlay-title="当前列居中" { center-column; }
    Mod+Shift+C                   hotkey-overlay-title="所有可见列居中" { center-visible-columns; }
    Mod+Alt+Up                    hotkey-overlay-title="当前列居中" { center-column; }
    Mod+Alt+Down                  hotkey-overlay-title="扩展到可用宽度" { expand-column-to-available-width; }
    Mod+Alt+Left                  repeat=false hotkey-overlay-title="吸附到左半屏（50% 宽 + 移到最左）" { spawn-sh "niri msg action set-column-width 50% && niri msg action move-column-to-first"; }
    Mod+Alt+Right                 repeat=false hotkey-overlay-title="吸附到右半屏（50% 宽 + 移到最右）" { spawn-sh "niri msg action set-column-width 50% && niri msg action move-column-to-last"; }

    // ─── 列组合与标签 ───
    Mod+BracketLeft               hotkey-overlay-title="把左邻窗口吞进本列" { consume-or-expel-window-left; }
    Mod+BracketRight              hotkey-overlay-title="把右邻窗口吞进本列" { consume-or-expel-window-right; }
    Mod+Comma                     hotkey-overlay-title="把窗口并入当前列" { consume-window-into-column; }
    Mod+Period                    hotkey-overlay-title="把窗口移出当前列" { expel-window-from-column; }
    Mod+W                         hotkey-overlay-title="切换标签式列显示" { toggle-column-tabbed-display; }

    // ─── 浮动窗口 ───
    Mod+V                         hotkey-overlay-title="在浮动与平铺之间切换" { toggle-window-floating; }
    Mod+Shift+V                   hotkey-overlay-title="在浮动与平铺之间切换焦点" { switch-focus-between-floating-and-tiling; }

    // ─── 工作区：滚轮与数字键 ───
    Mod+WheelScrollDown           cooldown-ms=150 hotkey-overlay-title="下一个工作区" { focus-workspace-down; }
    Mod+WheelScrollUp             cooldown-ms=150 hotkey-overlay-title="上一个工作区" { focus-workspace-up; }
    Mod+Ctrl+WheelScrollDown      cooldown-ms=150 hotkey-overlay-title="整列移到下一个工作区" { move-column-to-workspace-down; }
    Mod+Ctrl+WheelScrollUp        cooldown-ms=150 hotkey-overlay-title="整列移到上一个工作区" { move-column-to-workspace-up; }
    Mod+WheelScrollRight          hotkey-overlay-title="聚焦右侧一列" { focus-column-right; }
    Mod+WheelScrollLeft           hotkey-overlay-title="聚焦左侧一列" { focus-column-left; }
    Mod+Ctrl+WheelScrollRight     hotkey-overlay-title="整列右移" { move-column-right; }
    Mod+Ctrl+WheelScrollLeft      hotkey-overlay-title="整列左移" { move-column-left; }
    Mod+Shift+WheelScrollDown     hotkey-overlay-title="聚焦右侧一列" { focus-column-right; }
    Mod+Shift+WheelScrollUp       hotkey-overlay-title="聚焦左侧一列" { focus-column-left; }

    Mod+1                         hotkey-overlay-title="切换到工作区 1" { focus-workspace 1; }
    Mod+2                         hotkey-overlay-title="切换到工作区 2" { focus-workspace 2; }
    Mod+3                         hotkey-overlay-title="切换到工作区 3" { focus-workspace 3; }
    Mod+4                         hotkey-overlay-title="切换到工作区 4" { focus-workspace 4; }
    Mod+5                         hotkey-overlay-title="切换到工作区 5" { focus-workspace 5; }
    Mod+6                         hotkey-overlay-title="切换到工作区 6" { focus-workspace 6; }
    Mod+7                         hotkey-overlay-title="切换到工作区 7" { focus-workspace 7; }
    Mod+8                         hotkey-overlay-title="切换到工作区 8" { focus-workspace 8; }
    Mod+9                         hotkey-overlay-title="切换到工作区 9" { focus-workspace 9; }
    Mod+Ctrl+1                    hotkey-overlay-title="整列移到工作区 1" { move-column-to-workspace 1; }
    Mod+Ctrl+2                    hotkey-overlay-title="整列移到工作区 2" { move-column-to-workspace 2; }
    Mod+Ctrl+3                    hotkey-overlay-title="整列移到工作区 3" { move-column-to-workspace 3; }
    Mod+Ctrl+4                    hotkey-overlay-title="整列移到工作区 4" { move-column-to-workspace 4; }
    Mod+Ctrl+5                    hotkey-overlay-title="整列移到工作区 5" { move-column-to-workspace 5; }
    Mod+Ctrl+6                    hotkey-overlay-title="整列移到工作区 6" { move-column-to-workspace 6; }
    Mod+Ctrl+7                    hotkey-overlay-title="整列移到工作区 7" { move-column-to-workspace 7; }
    Mod+Ctrl+8                    hotkey-overlay-title="整列移到工作区 8" { move-column-to-workspace 8; }
    Mod+Ctrl+9                    hotkey-overlay-title="整列移到工作区 9" { move-column-to-workspace 9; }

    // ─── 截图 ───
    Print                         hotkey-overlay-title="截图（交互式选区）" { screenshot; }
    Ctrl+Print                    hotkey-overlay-title="截取整个屏幕" { screenshot-screen; }
    Alt+Print                     hotkey-overlay-title="截取当前窗口" { screenshot-window; }
    Mod+Shift+1                   hotkey-overlay-title="截图（交互式选区）" { screenshot; }
    Mod+Shift+2                   hotkey-overlay-title="截取整个屏幕" { screenshot-screen; }
    Mod+Shift+3                   hotkey-overlay-title="截取当前窗口" { screenshot-window; }

    // ─── 总览与电源 ───
    // 总览原本在 Mod+O，已按要求挪到 Mod+Tab；Mod+O 不再绑定。
    Mod+Tab                       repeat=false hotkey-overlay-title="总览 Overview（所有工作区）" { toggle-overview; }
    Mod+Shift+P                   hotkey-overlay-title="关闭显示器" { power-off-monitors; }
    Ctrl+Alt+Delete               hotkey-overlay-title="退出 niri" { quit; }
}
"""

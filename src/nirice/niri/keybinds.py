"""Niri 快捷键（binds 块）预设。"""

from __future__ import annotations

# 说明：niri 一个快捷键只允许一个动作；多步操作需用 spawn-sh 串联 `niri msg action`。
# 注意：修饰键顺序无意义 —— Mod+Ctrl+Shift+X 与 Mod+Shift+Ctrl+X 是同一个键，
#       新增绑定后务必运行 `nirice niri check`，niri validate 会直接报出重复绑定。
KEYBINDS_KDL = """// ────────────── Niri 快捷键（由 nirice 管理）──────────────
// 参考：https://github.com/YaLTeR/niri/wiki/Configuration:-Key-Bindings
// 手工修改本文件会被 `nirice niri apply` 覆盖；请改 nirice 预设或使用 --no-keybinds。

binds {
    // ─── 快捷键总览与紧急逃生 ───
    // 随时按 Mod+/ 查看 niri 的全部快捷键提示；Mod+Shift+Esc 为备用入口
    Mod+Slash                     { show-hotkey-overlay; }
    Mod+Shift+Escape              { show-hotkey-overlay; }
    Mod+Escape                    allow-inhibiting=false { toggle-keyboard-shortcuts-inhibit; }

    // ─── 窗口操作 ───
    Mod+Q                         { close-window; }

    // ─── 应用启动 ───
    Mod+T                         repeat=false hotkey-overlay-title="终端: kitty" { spawn "kitty"; }
    Mod+Return                    repeat=false hotkey-overlay-title="终端: kitty" { spawn "kitty"; }
    Mod+Shift+T                   repeat=false hotkey-overlay-title="终端: alacritty" { spawn "alacritty"; }
    Mod+B                         repeat=false hotkey-overlay-title="浏览器: Firefox" { spawn "firefox"; }
    Mod+E                         repeat=false hotkey-overlay-title="文件: Nautilus" { spawn "nautilus"; }

    // ─── Noctalia 外壳 ───
    Mod+D                         repeat=false hotkey-overlay-title="应用启动器" { spawn-sh "noctalia msg panel-toggle launcher"; }
    Mod+Space                     repeat=false hotkey-overlay-title="应用启动器" { spawn-sh "noctalia msg panel-toggle launcher"; }
    Mod+S                         repeat=false hotkey-overlay-title="控制中心" { spawn-sh "noctalia msg panel-toggle control-center"; }
    Mod+Shift+S                   repeat=false hotkey-overlay-title="系统设置" { spawn-sh "noctalia msg settings-toggle"; }
    Mod+Shift+Return              repeat=false hotkey-overlay-title="壁纸选择器" { spawn-sh "noctalia msg panel-toggle wallpaper"; }
    Mod+Shift+Q                   repeat=false hotkey-overlay-title="会话菜单" { spawn-sh "noctalia msg panel-toggle session"; }
    Mod+Alt+L                     repeat=false hotkey-overlay-title="锁屏" { spawn-sh "noctalia msg session lock"; }
    Mod+Ctrl+V                    repeat=false hotkey-overlay-title="剪贴板历史" { spawn-sh "noctalia msg panel-toggle clipboard"; }
    Mod+Ctrl+N                    repeat=false hotkey-overlay-title="免打扰开关" { spawn-sh "noctalia msg notification-dnd-toggle"; }
    Mod+Grave                     repeat=false hotkey-overlay-title="窗口切换器" { spawn-sh "noctalia msg window-switcher"; }

    // ─── 媒体与亮度 ───
    XF86AudioRaiseVolume          allow-when-locked=true { spawn-sh "noctalia msg volume-up"; }
    XF86AudioLowerVolume          allow-when-locked=true { spawn-sh "noctalia msg volume-down"; }
    XF86AudioMute                 allow-when-locked=true { spawn-sh "noctalia msg volume-mute"; }
    XF86AudioMicMute              allow-when-locked=true { spawn-sh "noctalia msg mic-mute"; }
    XF86AudioNext                 allow-when-locked=true { spawn-sh "noctalia msg media next"; }
    XF86AudioPrev                 allow-when-locked=true { spawn-sh "noctalia msg media previous"; }
    XF86AudioPlay                 allow-when-locked=true { spawn-sh "noctalia msg media play"; }
    XF86AudioPause                allow-when-locked=true { spawn-sh "noctalia msg media stop"; }
    XF86MonBrightnessUp           allow-when-locked=true { spawn-sh "noctalia msg brightness-up"; }
    XF86MonBrightnessDown         allow-when-locked=true { spawn-sh "noctalia msg brightness-down"; }
    XF86KbdBrightnessUp           allow-when-locked=true { spawn-sh "noctalia msg keyboard-backlight-up"; }
    XF86KbdBrightnessDown         allow-when-locked=true { spawn-sh "noctalia msg keyboard-backlight-down"; }

    // ─── 横向导航：列 ───
    Mod+Left                      { focus-column-left; }
    Mod+H                         { focus-column-left; }
    Mod+Right                     { focus-column-right; }
    Mod+L                         { focus-column-right; }
    Mod+Home                      { focus-column-first; }
    Mod+End                       { focus-column-last; }
    Mod+G                         { focus-window-previous; }

    // ─── 上下切页：工作区（Mod+上下，与旧的 Mod+Tab 语义一致）───
    // 方向对应关系：上/下 = 上/下一个工作区，左/右 = 上/下一列。
    Mod+Up                        { focus-workspace-up; }
    Mod+Down                      { focus-workspace-down; }
    Mod+Page_Up                   { focus-workspace-up; }
    Mod+Page_Down                 { focus-workspace-down; }
    Mod+Shift+Tab                 { focus-workspace-previous; }

    // ─── 列内上下窗口：Mod+K / Mod+J ───
    // 不要用 focus-window-up-or-column-left —— 列内没有上层窗口时它会自动
    // 掉到相邻列，导致"上下"和"左右"表现一样。
    Mod+K                         { focus-window-up; }
    Mod+J                         { focus-window-down; }

    // ─── 移动列与窗口 ───
    Mod+Ctrl+Left                 { move-column-left; }
    Mod+Ctrl+H                    { move-column-left; }
    Mod+Ctrl+Right                { move-column-right; }
    Mod+Ctrl+L                    { move-column-right; }
    Mod+Ctrl+Up                   { move-window-up; }
    Mod+Ctrl+Down                 { move-window-down; }
    Mod+Ctrl+K                    { move-window-up; }
    Mod+Ctrl+J                    { move-window-down; }
    Mod+Ctrl+Home                 { move-column-to-first; }
    Mod+Ctrl+End                  { move-column-to-last; }
    Mod+Ctrl+Shift+H              { swap-window-right; }

    // ─── 把整列送到别的工作区 ───
    Mod+Ctrl+Page_Up              { move-column-to-workspace-up; }
    Mod+Ctrl+Page_Down            { move-column-to-workspace-down; }

    // ─── 多显示器 ───
    Mod+Shift+Left                { focus-monitor-left; }
    Mod+Shift+Right               { focus-monitor-right; }
    Mod+Shift+Ctrl+Left           { move-column-to-monitor-left; }
    Mod+Shift+Ctrl+Right          { move-column-to-monitor-right; }
    Mod+Shift+Ctrl+Up             { move-column-to-monitor-up; }
    Mod+Shift+Ctrl+Down           { move-column-to-monitor-down; }

    // ─── 布局：窗口尺寸 ───
    // Mod+R 在预设列宽之间循环：1/3 → 1/2 → 2/3
    Mod+R                         { switch-preset-column-width; }
    Mod+Shift+R                   { switch-preset-column-width-back; }
    Mod+Minus                     { set-column-width "-10%"; }
    Mod+Equal                     { set-column-width "+10%"; }
    Mod+Shift+Minus               { set-window-height "-10%"; }
    Mod+Shift+Equal               { set-window-height "+10%"; }
    Mod+Ctrl+Shift+R              { switch-preset-window-height; }
    Mod+Ctrl+R                    { reset-window-height; }

    // ─── 布局：最大化与全屏 ───
    Mod+F                         { maximize-column; }
    Mod+Shift+F                   { fullscreen-window; }
    Mod+Shift+D                   { toggle-windowed-fullscreen; }
    Mod+M                         { maximize-window-to-edges; }
    Mod+Shift+M                   { expand-column-to-available-width; }

    // ─── 布局：居中与侧边对齐 ───
    // niri 是滚动平铺模型，"对齐侧边" = 先设宽 50% 再移动到条带最左/最右
    Mod+C                         { center-column; }
    Mod+Shift+C                   { center-visible-columns; }
    Mod+Alt+Up                    { center-column; }
    Mod+Alt+Down                  { expand-column-to-available-width; }
    Mod+Alt+Left                  repeat=false hotkey-overlay-title="吸附到左半屏（50% 宽 + 移到最左）" { spawn-sh "niri msg action set-column-width 50% && niri msg action move-column-to-first"; }
    Mod+Alt+Right                 repeat=false hotkey-overlay-title="吸附到右半屏（50% 宽 + 移到最右）" { spawn-sh "niri msg action set-column-width 50% && niri msg action move-column-to-last"; }

    // ─── 列组合与标签 ───
    Mod+BracketLeft               { consume-or-expel-window-left; }
    Mod+BracketRight              { consume-or-expel-window-right; }
    Mod+Comma                     { consume-window-into-column; }
    Mod+Period                    { expel-window-from-column; }
    Mod+W                         { toggle-column-tabbed-display; }

    // ─── 浮动窗口 ───
    Mod+V                         { toggle-window-floating; }
    Mod+Shift+V                   { switch-focus-between-floating-and-tiling; }

    // ─── 工作区：滚轮与数字键 ───
    Mod+WheelScrollDown           cooldown-ms=150 { focus-workspace-down; }
    Mod+WheelScrollUp             cooldown-ms=150 { focus-workspace-up; }
    Mod+Ctrl+WheelScrollDown      cooldown-ms=150 { move-column-to-workspace-down; }
    Mod+Ctrl+WheelScrollUp        cooldown-ms=150 { move-column-to-workspace-up; }
    Mod+WheelScrollRight          { focus-column-right; }
    Mod+WheelScrollLeft           { focus-column-left; }
    Mod+Ctrl+WheelScrollRight     { move-column-right; }
    Mod+Ctrl+WheelScrollLeft      { move-column-left; }
    Mod+Shift+WheelScrollDown     { focus-column-right; }
    Mod+Shift+WheelScrollUp       { focus-column-left; }

    Mod+1                         { focus-workspace 1; }
    Mod+2                         { focus-workspace 2; }
    Mod+3                         { focus-workspace 3; }
    Mod+4                         { focus-workspace 4; }
    Mod+5                         { focus-workspace 5; }
    Mod+6                         { focus-workspace 6; }
    Mod+7                         { focus-workspace 7; }
    Mod+8                         { focus-workspace 8; }
    Mod+9                         { focus-workspace 9; }
    Mod+Ctrl+1                    { move-column-to-workspace 1; }
    Mod+Ctrl+2                    { move-column-to-workspace 2; }
    Mod+Ctrl+3                    { move-column-to-workspace 3; }
    Mod+Ctrl+4                    { move-column-to-workspace 4; }
    Mod+Ctrl+5                    { move-column-to-workspace 5; }
    Mod+Ctrl+6                    { move-column-to-workspace 6; }
    Mod+Ctrl+7                    { move-column-to-workspace 7; }
    Mod+Ctrl+8                    { move-column-to-workspace 8; }
    Mod+Ctrl+9                    { move-column-to-workspace 9; }

    // ─── 截图 ───
    Print                         { screenshot; }
    Ctrl+Print                    { screenshot-screen; }
    Alt+Print                     { screenshot-window; }
    Mod+Shift+1                   { screenshot; }
    Mod+Shift+2                   { screenshot-screen; }
    Mod+Shift+3                   { screenshot-window; }

    // ─── 总览与电源 ───
    // 总览原本在 Mod+O，已按要求挪到 Mod+Tab；Mod+O 不再绑定。
    Mod+Tab                       repeat=false { toggle-overview; }
    Mod+Shift+P                   { power-off-monitors; }
    Ctrl+Alt+Delete               { quit; }
}
"""

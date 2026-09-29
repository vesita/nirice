"""Niri 快捷键（binds 块）预设。"""

# ==============================================================================
# 2. 快捷键（binds 代码块）
# ==============================================================================

KEYBINDS_KDL = """// ────────────── Niri 快捷键（由 nirice 管理）──────────────
// 参考：https://github.com/YaLTeR/niri/wiki/Configuration:-Key-Bindings
// 手工修改本文件会被 `nirice niri apply` 覆盖；请改 nirice 预设或使用 --no-keybinds。

binds {
    // ─── 紧急逃生（全屏应用卡住快捷键时使用）───
    Mod+Escape                    allow-inhibiting=false { toggle-keyboard-shortcuts-inhibit; }
    Mod+Shift+Escape              { show-hotkey-overlay; }

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

    // ─── 窗口聚焦导航（Mod + 方向键 / HJKL）───
    Mod+Left                      { focus-column-left; }
    Mod+H                         { focus-column-left; }
    Mod+Right                     { focus-column-right; }
    Mod+L                         { focus-column-right; }
    Mod+Up                        { focus-window-up-or-column-left; }
    Mod+K                         { focus-window-up-or-column-left; }
    Mod+Down                      { focus-window-down-or-column-right; }
    Mod+J                         { focus-window-down-or-column-right; }

    Mod+Home                      { focus-column-first; }
    Mod+End                       { focus-column-last; }

    Mod+Shift+H                   { focus-window-previous; }

    // ─── 窗口/列移动 ───
    Mod+Ctrl+Left                 { move-column-left; }
    Mod+Ctrl+H                    { move-column-left; }
    Mod+Ctrl+Right                { move-column-right; }
    Mod+Ctrl+L                    { move-column-right; }
    Mod+Ctrl+Up                   { move-window-up; }
    Mod+Ctrl+K                    { move-window-up; }
    Mod+Ctrl+Down                 { move-window-down; }
    Mod+Ctrl+J                    { move-window-down; }
    Mod+Ctrl+Home                 { move-column-to-first; }
    Mod+Ctrl+End                  { move-column-to-last; }
    Mod+Ctrl+Shift+H              { swap-window-right; }

    // ─── 多显示器 ───
    Mod+Shift+Left                { focus-monitor-left; }
    Mod+Shift+Right               { focus-monitor-right; }
    Mod+Shift+Up                  { focus-monitor-up; }
    Mod+Shift+Down                { focus-monitor-down; }
    Mod+Shift+Ctrl+Left           { move-column-to-monitor-left; }
    Mod+Shift+Ctrl+Right          { move-column-to-monitor-right; }
    Mod+Shift+Ctrl+Up             { move-column-to-monitor-up; }
    Mod+Shift+Ctrl+Down           { move-column-to-monitor-down; }

    // ─── 布局：最大化 / 全屏 ───
    // Mod+R = 占据整列（等价于旧配置里的 Mod+F 档位）
    Mod+R                         { maximize-column; }
    Mod+F                         { maximize-column; }
    Mod+Shift+F                   { fullscreen-window; }
    Mod+M                         { maximize-window-to-edges; }
    Mod+Shift+M                   { expand-column-to-available-width; }

    // ─── 布局：列宽 / 窗高 ───
    // Mod+Shift+R 在预设宽度间循环：1/3 → 1/2 → 2/3
    Mod+Shift+R                   { switch-preset-column-width; }
    Mod+Ctrl+R                    { switch-preset-column-width-back; }
    Mod+Minus                     { set-column-width "-10%"; }
    Mod+Equal                     { set-column-width "+10%"; }
    Mod+Shift+Minus               { set-window-height "-10%"; }
    Mod+Shift+Equal               { set-window-height "+10%"; }
    Mod+Ctrl+Shift+Up             { switch-preset-window-height; }
    Mod+Ctrl+Shift+Down           { reset-window-height; }

    // ─── 布局：居中与侧边对齐 ───
    // niri 是滚动平铺模型，"对齐侧边" = 先设宽 50% 再移动到条带最左/最右
    Mod+C                         { center-column; }
    Mod+Shift+C                   { center-visible-columns; }
    Mod+Alt+Up                    { center-column; }
    Mod+Alt+Left                  { spawn-sh "niri msg action set-column-width 50% && niri msg action move-column-to-first"; }
    Mod+Alt+Right                 { spawn-sh "niri msg action set-column-width 50% && niri msg action move-column-to-last"; }
    Mod+Alt+Down                  { expand-column-to-available-width; }

    // ─── 列组合 ───
    Mod+BracketLeft               { consume-or-expel-window-left; }
    Mod+BracketRight              { consume-or-expel-window-right; }
    Mod+Comma                     { consume-window-into-column; }
    Mod+Period                    { expel-window-from-column; }
    Mod+W                         { toggle-column-tabbed-display; }

    // ─── 浮动窗口 ───
    Mod+V                         { toggle-window-floating; }
    Mod+Shift+V                   { switch-focus-between-floating-and-tiling; }

    // ─── 工作区切换 ───
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
    Mod+Tab                       { focus-workspace-previous; }

    // ─── 截图 ───
    Print                         { screenshot; }
    Ctrl+Print                    { screenshot-screen; }
    Alt+Print                     { screenshot-window; }
    Mod+Shift+1                   { screenshot; }
    Mod+Shift+2                   { screenshot-screen; }
    Mod+Shift+3                   { screenshot-window; }

    // ─── 总览与电源 ───
    Mod+O                         repeat=false { toggle-overview; }
    Mod+Shift+P                   { power-off-monitors; }
    Ctrl+Alt+Delete               { quit; }
}
"""

"""Niri 快捷键（binds 块）预设。

niri 的 hotkey overlay **没有本地化**：文案硬编码在二进制里，没有翻译文件，
设置 LANG 也无效。因此这里给每一条绑定都显式加上 `hotkey-overlay-title`，
让 Mod+/ 弹出的快捷键总览完全显示中文。

设计取舍：

- **只绑单修饰键组合**：`Mod+X` 或 `Ctrl+X`。两个及以上修饰键
  （Mod+Shift / Mod+Ctrl / Mod+Alt / Ctrl+Alt）一律不绑。
- **同一动作不留别名**。
- 方向键负责跨列 / 跨工作区导航，K / J 负责列内窗口导航。二者不可互相替代：
  `focus-window-up/down` 没有方向键版本，删掉 K / J 就再也无法在列内切窗口。
- 长尾动作一律移除：缩放 ±10%、数字工作区、鼠标滚轮、反向循环列宽、
  关闭显示器、壁纸选择器。
- 对齐到边界用 `move-column-to-first/last`：niri 是滚动平铺模型，把列移到
  最左 / 最右位置即视觉上的贴边，无需改列宽。
- 硬件功能键（音量 / 亮度 / 媒体）保留绑定，但用 `hotkey-overlay-title=null`
  从 Mod+/ 总览里隐去，让总览只呈现 Mod 组合键。`null` 是 niri 的显式隐藏写法，
  与「不绑定」是两回事：功能照常可用，只是不列进总览。
"""

from __future__ import annotations

# 说明：niri 一个快捷键只允许一个动作；多步操作需用 spawn-sh 串联 `niri msg action`。
# 注意：修饰键顺序无意义 —— Mod+Ctrl+X 与 Ctrl+Mod+X 是同一个键，
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
    Mod+Escape                    allow-inhibiting=false hotkey-overlay-title="应急：恢复快捷键响应" { toggle-keyboard-shortcuts-inhibit; }

    // ─── 窗口操作 ───
    Mod+Q                         hotkey-overlay-title="关闭窗口" { close-window; }
    Mod+P                         hotkey-overlay-title="浮动 / 平铺切换" { toggle-window-floating; }

    // ─── 应用启动 ───
    Mod+T                         repeat=false hotkey-overlay-title="打开终端" { spawn "kitty"; }
    Mod+D                         repeat=false hotkey-overlay-title="打开应用启动器" { spawn-sh "noctalia msg panel-toggle launcher"; }
    Mod+B                         repeat=false hotkey-overlay-title="打开浏览器" { spawn "firefox"; }
    Mod+E                         repeat=false hotkey-overlay-title="打开文件管理器" { spawn "nautilus"; }

    // ─── Noctalia 外壳 ───
    Mod+V                         repeat=false hotkey-overlay-title="剪贴板历史" { spawn-sh "noctalia msg panel-toggle clipboard"; }
    Mod+S                         repeat=false hotkey-overlay-title="控制中心" { spawn-sh "noctalia msg panel-toggle control-center"; }
    Mod+I                         repeat=false hotkey-overlay-title="系统设置" { spawn-sh "noctalia msg settings-toggle"; }
    Mod+O                         repeat=false hotkey-overlay-title="电源与会话" { spawn-sh "noctalia msg panel-toggle session"; }

    // ─── 导航：跨列与跨工作区 ───
    Mod+Left                      hotkey-overlay-title="聚焦左列" { focus-column-left; }
    Mod+Right                     hotkey-overlay-title="聚焦右列" { focus-column-right; }
    Mod+Up                        hotkey-overlay-title="上一个工作区" { focus-workspace-up; }
    Mod+Down                      hotkey-overlay-title="下一个工作区" { focus-workspace-down; }
    Mod+G                         hotkey-overlay-title="聚焦上一个窗口" { focus-window-previous; }

    // ─── 导航：列内上下窗口 ───
    // 不要用 focus-window-up-or-column-left —— 列内没有上层窗口时它会自动
    // 掉到相邻列，导致"上下"和"左右"表现一样。
    Mod+K                         hotkey-overlay-title="同列上一个窗口" { focus-window-up; }
    Mod+J                         hotkey-overlay-title="同列下一个窗口" { focus-window-down; }

    // ─── 布局：最大化与对齐 ───
    Mod+R                         hotkey-overlay-title="最大化 / 还原当前列" { maximize-column; }
    Mod+C                         hotkey-overlay-title="当前列居中" { center-column; }
    Mod+Z                         hotkey-overlay-title="当前列靠左" { move-column-to-first; }
    Mod+X                         hotkey-overlay-title="当前列靠右" { move-column-to-last; }
    Mod+W                         hotkey-overlay-title="标签式分组" { toggle-column-tabbed-display; }

    // ─── 总览 ───
    Mod+Tab                       repeat=false hotkey-overlay-title="工作区总览" { toggle-overview; }

    // ─── 截图 ───
    Print                         hotkey-overlay-title="区域截图" { screenshot; }
    Ctrl+Print                    hotkey-overlay-title=null { screenshot-screen; }
    Alt+Print                     hotkey-overlay-title=null { screenshot-window; }

    // ─── 媒体与亮度（XF86 硬件键）───
    // 这些是键盘上的硬件功能键：照常生效，但用 hotkey-overlay-title=null 从
    // Mod+/ 总览里隐去 —— 总览只留 Mod 组合键，硬件键本来就无需提示。
    // 播放键用 toggle：笔记本通常只有一个播放/暂停键，同时发 XF86AudioPlay。
    XF86AudioRaiseVolume          allow-when-locked=true hotkey-overlay-title=null { spawn-sh "noctalia msg volume-up"; }
    XF86AudioLowerVolume          allow-when-locked=true hotkey-overlay-title=null { spawn-sh "noctalia msg volume-down"; }
    XF86AudioMute                 allow-when-locked=true hotkey-overlay-title=null { spawn-sh "noctalia msg volume-mute"; }
    XF86AudioMicMute              allow-when-locked=true hotkey-overlay-title=null { spawn-sh "noctalia msg mic-mute"; }
    XF86AudioPlay                 allow-when-locked=true hotkey-overlay-title=null { spawn-sh "noctalia msg media toggle"; }
    XF86AudioNext                 allow-when-locked=true hotkey-overlay-title=null { spawn-sh "noctalia msg media next"; }
    XF86AudioPrev                 allow-when-locked=true hotkey-overlay-title=null { spawn-sh "noctalia msg media previous"; }
    XF86MonBrightnessUp           allow-when-locked=true hotkey-overlay-title=null { spawn-sh "noctalia msg brightness-up"; }
    XF86MonBrightnessDown         allow-when-locked=true hotkey-overlay-title=null { spawn-sh "noctalia msg brightness-down"; }
}
"""

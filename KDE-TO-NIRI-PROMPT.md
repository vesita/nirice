# 提示词：在 CachyOS 上彻底移除 KDE，改造为原生 Niri + Noctalia 桌面

> 用法：把下面「=== 提示词开始 ===」到「=== 提示词结束 ===」之间的全部内容，原样粘贴给运行在**目标机器**上的 AI Agent（或你自己按步骤执行）。

---

=== 提示词开始 ===

## 0. 你的角色与任务

你是一名 Linux 桌面环境迁移工程师。你正在一台 **CachyOS（Arch 系）** 机器上工作。

**背景**：这台机器原生安装的是 **KDE Plasma 6**，用户中途改装了 **niri**，因此系统同时存在两类问题：

1. **KDE 残留**：Plasma/KWin/KDE 应用、`xdg-desktop-portal-kde`、`pam_kwallet5` 钩子、一堆 `~/.config/kde*` 配置仍在，会和 niri 抢门户、抢环境变量、拖慢登录。
2. **niri 栈不完整**：因为不是走 CachyOS 的 niri 安装流程，缺少装机时本应自动补齐的组件（门户后端、密钥环、指针主题、dconf 主题、Noctalia 外壳等），导致截图/文件选择器/密码保存/状态栏等功能残缺。

**你的最终目标**：把系统改造成一台**干净的原生 niri + Noctalia 桌面**，KDE 被彻底移除，且所有组件都按 CachyOS niri 版的标准配置正确。

---

## 1. 铁律（违反任何一条都算任务失败）

1. **先立后破，绝不先删 KDE。**
   必须先把 niri 原生栈装好并确认能从显示管理器正常登录，**才允许**开始卸载 KDE。任何时刻都不能让这台机器失去可用的图形登录能力。
2. **禁止重启、注销、关机。**
   不要执行 `reboot` / `systemctl reboot` / `loginctl terminate-session` / 注销当前会话。你做完所有改动后，把「请手动重启并在 SDDM 选择 niri 会话」交给用户。
3. **破坏性操作前必须备份。**
   修改 `/etc/pam.d/*`、`/etc/sddm.conf*`、`/etc/environment`、任何 `~/.config` 前，先复制一份到 `/root/backup-kde-to-niri-<日期>/` 或 `~/.cache/kde-to-niri-backup-<日期>/`。
4. **不要猜包名。**
   任何卸载/安装前，先用 `pacman -Qq`、`pacman -Qi`、`pacman -Ql`、`pacman -Rns --print` 核实真实包名与依赖关系。Arch 的包名不在本提示词里的，一律先查证。
5. **优先使用软件自带的自动化能力。**
   尤其是**配色**：不要手写十六进制色值到各软件的配置里。niri / kitty / starship / GTK / Qt 的配色应当由 **Noctalia 的主题模板**统一渲染，这样换主题/换壁纸时全生态自动联动，不会出现「一半新配色一半旧配色」的不完整状态。
6. **保留显示管理器 SDDM。**
   SDDM 不属于 KDE 专属组件，是 niri 会话的登录入口。只需要把它主题从 KDE 主题改掉、清掉 PAM 里的 kwallet 钩子即可，**不要卸载 sddm**。
7. **每一步都要验证。**
   每个阶段结束都跑一次该阶段的验证命令。验证失败就停下来报告，不要继续往下做。

---

## 2. 阶段 0：侦察，先摸清现状

先收集信息，不要做任何修改：

```bash
# 发行版与内核
cat /etc/os-release; uname -r

# 当前会话与桌面
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE"; echo "XDG_CURRENT_DESKTOP=$XDG_CURRENT_DESKTOP"

# 已安装的 KDE / Plasma / KWin 组件
pacman -Qq | grep -iE 'plasma|kwin|kde|kwallet|breeze|sddm|kactivity|kglobalaccel' | sort

# 已安装的门户后端（关键！）
pacman -Qq | grep -iE 'xdg-desktop-portal'

# 显示管理器
systemctl status display-manager --no-pager | head -5
ls /usr/share/wayland-sessions/ /usr/share/xsessions/ 2>/dev/null

# niri / noctalia 是否已装
command -v niri noctalia; niri --version 2>/dev/null

# 用户配置文件残留
ls -1 ~/.config | grep -iE 'kde|kwin|plasma|kwallet|ksplash|kglobal|kcminput|dolphin|konsole|kate'

# PAM 里的 kwallet / keyring 钩子（卸载 KDE 后最容易导致登录异常的地方）
grep -nE 'kwallet|keyring' /etc/pam.d/sddm /etc/pam.d/system-login 2>/dev/null

# 是否存在 CachyOS 的 niri 套件
pacman -Qi cachyos-niri-noctalia 2>/dev/null || echo "cachyos-niri-noctalia 未安装"
```

把结果整理成一份现状清单后再进入阶段 1。

---

## 3. 阶段 1：安装原生 niri 栈（先立）

### 3.1 安装 CachyOS 官方 niri 套件

CachyOS 把 niri 版的默认配置打包在 **`cachyos-niri-noctalia`** 里（描述：*CachyOS Niri (+Noctalia) settings*）。装上它，就一次性补齐了装机时本应自动到位的组件：

```bash
sudo pacman -S --needed cachyos-niri-noctalia
```

该包的依赖就是「CachyOS niri 版标准组件清单」，请以实际输出为准核对，至少应包含：

| 类别 | 包 | 作用 |
| --- | --- | --- |
| 合成器 | `niri` | 滚动平铺 Wayland 合成器 |
| 桌面外壳 | `noctalia` | 状态栏/启动器/通知/OSD/锁屏一体 |
| GTK 主题 | `adw-gtk-theme` | 让 GTK3 应用有 libadwaita 观感 |
| 指针主题 | `capitaine-cursors` | niri 默认配置引用的光标主题 |
| 密钥环 | `gnome-keyring` | Secret Service（保存 Wi-Fi/应用密码） |
| 门户 | `xdg-desktop-portal-gtk` | 文件选择器等 GTK 后端 |
| 门户 | `xdg-desktop-portal-gnome` | 屏幕共享/远程桌面后端 |
| X11 兼容 | `xwayland-satellite` | 让 X11 应用在 niri 下可用 |
| 剪贴板 | `wl-clipboard` | Noctalia 剪贴板面板依赖 |
| 字体 | `noto-fonts`、`noto-fonts-emoji` | 基础字体与彩色 Emoji |
| 终端配置 | `cachyos-alacritty-config` | CachyOS 默认终端配置 |

如果 `cachyos-niri-noctalia` 在你的仓库里找不到，改为**逐项手动安装**上表所有包。

### 3.2 让 dconf 主题生效

该包会安装 `/etc/dconf/db/local.d/00-cachyos.conf` 与 `/etc/dconf/profile/user`，内容是：

```ini
[org/gnome/desktop/interface]
color-scheme='prefer-dark'
gtk-theme='adw-gtk3-dark'
cursor-theme='capitaine-cursors'
```

执行：

```bash
sudo dconf update
```

### 3.3 把 skel 配置铺给已有用户

包里的配置放在 `/etc/skel/.config/`，只对**新建用户**生效。当前用户需要手动复制过去，**注意不要覆盖用户已经改过的文件**（用 `-n` 不覆盖）：

```bash
mkdir -p ~/.config
cp -rn /etc/skel/.config/niri     ~/.config/ 2>/dev/null
cp -rn /etc/skel/.config/noctalia ~/.config/ 2>/dev/null
```

复制后确认目录结构：

```bash
find ~/.config/niri -maxdepth 2 -type f | sort
```

标准结构应为：

```
~/.config/niri/config.kdl          # 主入口，只放 include
~/.config/niri/cfg/animation.kdl
~/.config/niri/cfg/autostart.kdl
~/.config/niri/cfg/display.kdl
~/.config/niri/cfg/input.kdl
~/.config/niri/cfg/keybinds.kdl
~/.config/niri/cfg/layout.kdl
~/.config/niri/cfg/misc.kdl
~/.config/niri/cfg/rules.kdl
```

### 3.4 补齐门户路由，并**抢占** KDE 门户

确认 niri 的门户路由文件存在，内容应为：

```bash
cat /usr/share/xdg-desktop-portal/niri-portals.conf
```

期望内容：

```ini
[preferred]
default=gnome;gtk;
org.freedesktop.impl.portal.Access=gtk;
org.freedesktop.impl.portal.Notification=gtk;
org.freedesktop.impl.portal.Secret=gnome-keyring;
```

**这一步极其关键**：如果系统里装着 `xdg-desktop-portal-kde`，它会注册 KDE 后端，在 niri 会话下抢走门户请求，导致**截图、文件选择器、屏幕共享、密码保存全部失效**。必须卸载它：

```bash
sudo pacman -Rns xdg-desktop-portal-kde
```

### 3.5 验证阶段 1

```bash
# niri 配置语法正确
niri validate

# 会话入口存在（SDDM 里能选到 niri）
ls -l /usr/share/wayland-sessions/niri.desktop

# 门户后端就位且没有 KDE 后端
pacman -Qq | grep xdg-desktop-portal
ls /usr/lib/xdg-desktop-portal* 2>/dev/null

# 密钥环、X11 桥、剪贴板就位
command -v gnome-keyring-daemon xwayland-satellite wl-copy
```

> **检查点**：以上全部通过后，才允许进入阶段 5 卸载 KDE。在此之前不要碰 KDE 软件包。

---

## 4. 阶段 2：配置 niri

### 4.1 配置文件组织

`~/.config/niri/config.kdl` 只做 include，**必须包含 Noctalia 自动生成的配色文件**：

```kdl
include "./cfg/animation.kdl"
include "./cfg/autostart.kdl"
include "./cfg/keybinds.kdl"
include "./cfg/input.kdl"
include "./cfg/display.kdl"
include "./cfg/layout.kdl"
include "./cfg/rules.kdl"
include "./cfg/misc.kdl"

include "noctalia.kdl"
```

> `noctalia.kdl` 由 Noctalia 的 `niri` 模板自动生成（焦点环/边框/标签指示器配色）。**不要手写这份文件，也不要删掉这行 include**，否则外壳配色无法联动到合成器。

### 4.2 显示器

`display.kdl` 与硬件绑定。**不要照搬别人的配置**，先查询本机实际输出：

```bash
niri msg outputs          # 需要 niri 正在运行
# 或查看当前（KDE 会话下可能拿不到）：
ls /sys/class/drm/
```

确认输出名（如 `eDP-1` / `DP-1`）、分辨率与缩放后再写：

```kdl
output "eDP-1" {
    mode "1920x1080@60.000"
    scale 1.25
    transform "normal"
}
```

若不确定，**先把 output 块整段注释掉**，让 niri 用默认值，之后再调。

### 4.3 快捷键（按用户明确需求设计）

**关键限制**：niri **一个快捷键只允许一个动作**。多步骤操作必须通过 `spawn-sh` 调用 `niri msg action` 串联，例如侧边吸附：

```kdl
Mod+Alt+Left  { spawn-sh "niri msg action set-column-width 50% && niri msg action move-column-to-first"; }
```

用户明确要求：

| 需求 | 绑定 |
| --- | --- |
| 用 `Mod+T` 唤起终端（保留旧习惯） | `Mod+T` → `spawn "kitty"`（`Mod+Return` 可同时保留） |
| 用 `Mod+上下左右` 在窗口间导航 | `Mod+←→↑↓` → `focus-column-*` / `focus-window-*` |
| `Mod+R` 让窗口占满整列（即原来的 `Mod+F` 语义） | `Mod+R` → `maximize-column` |
| 窗口居中的快捷键 | `Mod+C` → `center-column` |
| 窗口对齐左/右侧的快捷键 | `Mod+Alt+←` → 50% 宽 + `move-column-to-first`；`Mod+Alt+→` → 50% 宽 + `move-column-to-last` |

参考实现（可直接采用，再按喜好微调）：

```kdl
binds {
    // 紧急逃生：全屏应用卡住快捷键时恢复控制
    Mod+Escape allow-inhibiting=false { toggle-keyboard-shortcuts-inhibit; }

    // 应用
    Mod+T      repeat=false { spawn "kitty"; }
    Mod+Return repeat=false { spawn "kitty"; }
    Mod+B      repeat=false { spawn "firefox"; }
    Mod+E      repeat=false { spawn "nautilus"; }

    // Noctalia 外壳
    Mod+D          repeat=false { spawn-sh "noctalia msg panel-toggle launcher"; }
    Mod+Space      repeat=false { spawn-sh "noctalia msg panel-toggle launcher"; }
    Mod+S          repeat=false { spawn-sh "noctalia msg panel-toggle control-center"; }
    Mod+Shift+S    repeat=false { spawn-sh "noctalia msg settings-toggle"; }
    Mod+Shift+Q    repeat=false { spawn-sh "noctalia msg panel-toggle session"; }
    Mod+Alt+L      repeat=false { spawn-sh "noctalia msg session lock"; }
    Mod+Ctrl+V     repeat=false { spawn-sh "noctalia msg panel-toggle clipboard"; }

    // 窗口导航（方向键 + HJKL）
    Mod+Left  { focus-column-left; }
    Mod+H     { focus-column-left; }
    Mod+Right { focus-column-right; }
    Mod+L     { focus-column-right; }
    Mod+Up    { focus-window-up-or-column-left; }
    Mod+K     { focus-window-up-or-column-left; }
    Mod+Down  { focus-window-down-or-column-right; }
    Mod+J     { focus-window-down-or-column-right; }

    // 移动窗口/列
    Mod+Ctrl+Left  { move-column-left; }
    Mod+Ctrl+Right { move-column-right; }
    Mod+Ctrl+Up    { move-window-up; }
    Mod+Ctrl+Down  { move-window-down; }

    // 最大化 / 全屏
    Mod+R     { maximize-column; }
    Mod+F     { maximize-column; }
    Mod+Shift+F { fullscreen-window; }
    Mod+M     { maximize-window-to-edges; }

    // 列宽循环（1/3 → 1/2 → 2/3）
    Mod+Shift+R { switch-preset-column-width; }
    Mod+Ctrl+R  { switch-preset-column-width-back; }
    Mod+Minus   { set-column-width "-10%"; }
    Mod+Equal   { set-column-width "+10%"; }

    // 居中与侧边对齐
    Mod+C         { center-column; }
    Mod+Shift+C   { center-visible-columns; }
    Mod+Alt+Up    { center-column; }
    Mod+Alt+Left  { spawn-sh "niri msg action set-column-width 50% && niri msg action move-column-to-first"; }
    Mod+Alt+Right { spawn-sh "niri msg action set-column-width 50% && niri msg action move-column-to-last"; }
    Mod+Alt+Down  { expand-column-to-available-width; }

    // 浮动 / 标签列
    Mod+V       { toggle-window-floating; }
    Mod+Shift+V { switch-focus-between-floating-and-tiling; }
    Mod+W       { toggle-column-tabbed-display; }

    // 工作区
    Mod+1..9        → { focus-workspace N; }
    Mod+Ctrl+1..9   → { move-column-to-workspace N; }
    Mod+Tab         { focus-workspace-previous; }
    Mod+WheelScrollDown cooldown-ms=150 { focus-workspace-down; }
    Mod+WheelScrollUp   cooldown-ms=150 { focus-workspace-up; }

    // 截图
    Print        { screenshot; }
    Ctrl+Print   { screenshot-screen; }
    Alt+Print    { screenshot-window; }

    // 总览 / 电源
    Mod+O       repeat=false { toggle-overview; }
    Mod+Shift+P { power-off-monitors; }
    Ctrl+Alt+Delete { quit; }
}
```

> 注意：上面 `Mod+1..9` 是简写，实际要逐条写出 1 到 9（niri 不支持区间语法）。

### 4.4 其他片段要点

- `autostart.kdl`：**必须有** `spawn-at-startup "noctalia"`，否则登录后没有状态栏。
- `misc.kdl`：保持 `prefer-no-csd`、`screenshot-path null`（让 Noctalia 接管截图）、`cursor { xcursor-theme "capitaine-cursors"; xcursor-size 24; }`，以及 `debug { honor-xdg-activation-with-invalid-serial }`（Noctalia 通知动作与窗口激活需要）。
- `layout.kdl`：`background-color "transparent"`（必须，否则挡住 Noctalia 壁纸）、`gaps 16`、`preset-column-widths { proportion 0.33333; proportion 0.5; proportion 0.66667; }`。
- `rules.kdl`：给所有窗口加 `geometry-corner-radius 20` + `clip-to-geometry true` + `background-effect { blur true }`，并保留 Noctalia 的 layer-rule。
- `blur` 放在 `misc.kdl` 里（Niri 合成器负责模糊；kitty 的 `background_blur` 只在 macOS 生效，Linux 上不要依赖它）。

### 4.5 校验并热重载

```bash
niri validate
niri msg action load-config-file     # niri 正在运行时
```

**必须每一项都通过**，否则不要继续。

---

## 5. 阶段 3：配置 Noctalia 外壳

Noctalia 是配色的**唯一事实来源**。它的配置分两层：

- `~/.config/noctalia/*.toml` —— 基础配置
- `~/.local/state/noctalia/settings.toml` —— 设置界面的覆盖层（**状态栏位置、主题、模板开关都在这里**）

### 5.1 状态栏移到左侧

往 `~/.local/state/noctalia/settings.toml` 追加：

```toml
[bar]
position = "left"
```

合法值为 `top` / `bottom` / `left` / `right`。改完执行：

```bash
noctalia config validate
noctalia msg config-reload
```

### 5.2 设定主题

```toml
[theme]
builtin = "Nord"
mode = "light"
```

也可以走官方命令：

```bash
noctalia msg color-scheme-set builtin Nord
noctalia msg theme-mode-set light
```

### 5.3 启用主题模板（**这是"自动配色"的核心**）

Noctalia 自带模板系统，能把当前配色渲染进各软件的配置文件。检查可用模板：

```bash
ls /usr/share/noctalia/assets/templates/
# 官方内置：alacritty btop cava emacs foot ghostty gtk3 gtk4 helix hyprland kde
#           kitty labwc mango niri qt scroll starship sway umbriel wezterm
```

启用需要的模板（**只启用本机确实安装了的软件**），写进 `settings.toml`：

```toml
[theme.templates]
builtin_ids = ["niri", "kitty", "starship", "alacritty", "gtk3", "gtk4"]
```

然后让 Noctalia 渲染并落盘：

```bash
noctalia msg config-reload
noctalia msg templates-apply
```

**渲染结果（用于验证）**：

| 模板 | 落盘位置 |
| --- | --- |
| `niri` | `~/.config/niri/noctalia.kdl` + 在 `config.kdl` 末尾追加 `include "noctalia.kdl"` |
| `kitty` | `~/.config/kitty/themes/noctalia.conf` + 在 `kitty.conf` 追加 `include themes/noctalia.conf` |
| `starship` | `~/.config/starship.toml` 内的 `# >>> NOCTALIA STARSHIP PALETTE >>>` 标记块 |
| `alacritty` | `~/.config/alacritty/themes/noctalia.toml` + 在配置里加 `import` |
| `gtk3`/`gtk4` | `~/.config/gtk-3.0/noctalia.css`、`~/.config/gtk-4.0/noctalia.css` + `gtk.css` 里 `@import` |

> `kde` 模板**不要启用**（KDE 正在被移除）。

### 5.4 验证阶段 3

```bash
noctalia config validate
noctalia msg status
noctalia msg color-scheme-get      # 应输出: builtin Nord
noctalia msg theme-mode-get        # 应输出: light
echo '--- niri 是否被注入 include ---'; grep -n noctalia ~/.config/niri/config.kdl
echo '--- kitty 是否被注入 include ---'; grep -n noctalia ~/.config/kitty/kitty.conf
```

---

## 6. 阶段 4：终端（Kitty）

### 6.1 配色：交给 Noctalia，不要手写

`kitty.conf` 里只需保留 Noctalia 注入的 include：

```
include themes/noctalia.conf
```

### 6.2 美学：字体/磨砂/Tab 单独写

配色由模板管，**排版与交互**才需要手写。建议把美学部分单独放在 `~/.config/kitty/nirice.conf`，并在 `kitty.conf` 里 include，避免和 Noctalia 的 include 打架。

**字体是本机最容易踩的坑**：`monospace` 别名在 CachyOS 上会解析到 `Noto Sans Mono CJK`，导致 ASCII 字符被按 CJK 全角宽度渲染，出现**双倍字距的稀疏感**。必须显式指定 Nerd Font：

```conf
# 主字体：显式 Nerd Font，规避 monospace → CJK 的宽度问题
font_family      MesloLGS Nerd Font
bold_font        auto
italic_font      auto
bold_italic_font auto
# CJK 只作为缺失字形的回退，不影响 ASCII 宽度
font_family      Noto Sans Mono CJK SC
font_size        11.5

# Nerd Font 图标锁定主字体
symbol_map U+E000-U+F8FF,U+F0000-U+FFFFD,U+100000-U+10FFFD MesloLGS Nerd Font

# 磨砂玻璃：透明度归 kitty，模糊归 niri
background_opacity 0.78
dynamic_background_opacity yes
window_padding_width 8
hide_window_decorations yes
confirm_os_window_close 0
remember_window_size yes

# 光标
cursor_shape beam
cursor_blink_interval 0.5

# 顶部圆角药丸 Tab
tab_bar_edge top
tab_bar_style powerline
tab_powerline_style round
tab_bar_min_tabs 1
tab_bar_margin_width 6.0
tab_bar_margin_height 6.0 0.0
tab_title_template " {index}: {title} "
active_tab_font_style bold
inactive_tab_font_style normal

# 让 nirice/脚本能热重载（SIGUSR1）
allow_remote_control socket-only

# 快捷键
map ctrl+shift+t new_tab
map ctrl+shift+w close_tab
map ctrl+shift+right next_tab
map ctrl+shift+left previous_tab
map ctrl+shift+enter new_window_with_cwd
map ctrl+shift+h neighboring_window left
map ctrl+shift+l neighboring_window right
map ctrl+shift+u set_background_opacity +0.05
map ctrl+shift+o set_background_opacity -0.05
map ctrl+shift+delete set_background_opacity default
```

字体确认：

```bash
fc-match "MesloLGS Nerd Font"     # 应解析到 MesloLGSNerdFont-*.ttf
fc-match monospace                # 会解析到 CJK 字体，这正是不能用它的原因
```

若缺少 Meslo 字体：`sudo pacman -S ttf-meslo-nerd`。

### 6.3 验证

```bash
kitty --debug-config 2>&1 | head -20      # 输出错误会直接报出来
pkill -USR1 kitty                         # 让运行中的 kitty 重载配置
```

---

## 7. 阶段 5：彻底移除 KDE（**先破后立之后才做**）

> **前提**：阶段 1~4 全部验证通过，且你已确认 niri 会话能从 SDDM 登录。

### 7.1 卸载顺序

**顺序很重要**，从「会抢功能的外围」到「核心组件」：

```bash
# 1) 先移除门户后端，避免它继续劫持 niri 下的门户请求
sudo pacman -Rns xdg-desktop-portal-kde

# 2) 移除 KDE 的 polkit 代理（Noctalia 自带 polkit agent：config.toml 里 polkit_agent = true）
sudo pacman -Rns polkit-kde-agent

# 3) 移除 KWallet（改用 gnome-keyring 提供 Secret Service）
sudo pacman -Rns kwallet kwallet-pam kwalletmanager

# 4) 移除 Plasma 桌面组与 KWin
pacman -Qgq plasma                 # 先看这个组里到底有哪些包
sudo pacman -Rns kwin plasma-desktop plasma-workspace plasma-integration
```

### 7.2 卸载前必须做依赖体检

**不要直接 `pacman -Rns` 一大串包**。先用 `--print` 预览，确认不会连带删掉你还需要的组件（尤其是 GTK/Qt 应用、字体、SDL 等共享依赖）：

```bash
sudo pacman -Rns --print <包名列表>
```

把输出的 "removing" 列表看一遍，出现以下类别要格外警惕，必要时改用 `pacman -R`（只删包、保留依赖）：

- `qt6-*` / `qt5-*`（其他 Qt 应用要用）
- `gtk3` / `gtk4` / `glib2`
- `pipewire` / `wireplumber` / `networkmanager` / `bluez` / `upower`
- 任何 GTK/Qt 应用、截图/录屏工具

### 7.3 清理 PAM 的 kwallet 钩子（**最容易导致登录异常的一步**）

```bash
sudo cp /etc/pam.d/sddm /root/backup-kde-to-niri-$(date +%F)/ 2>/dev/null || sudo mkdir -p /root/backup-kde-to-niri-$(date +%F) && sudo cp /etc/pam.d/sddm /root/backup-kde-to-niri-$(date +%F)/
sudo grep -nE 'kwallet' /etc/pam.d/sddm
```

把 `/etc/pam.d/sddm` 中包含 `pam_kwallet5.so` 的行**整行删除**（通常是这两行）：

```
-auth       optional    pam_kwallet5.so
-session    optional    pam_kwallet5.so         auto_start
```

保留 `pam_gnome_keyring.so` 的行不动（这正是自动解锁密钥环所需要的）。

同样检查 `/etc/pam.d/system-login` 与 `/etc/pam.d/login` 是否有 kwallet 行，有则一并清掉。

### 7.4 处理 SDDM 主题

卸载 `breeze` 等 KDE 主题包后，如果 SDDM 当前主题指向被删掉的 KDE 主题，登录界面会变成空白/报错。

```bash
ls /usr/share/sddm/themes/
grep -rn "Current" /etc/sddm.conf /etc/sddm.conf.d/ 2>/dev/null
```

把 `/etc/sddm.conf.d/*.conf` 里的主题改成仍然存在的主题，例如：

```ini
[Theme]
Current=elarun
```

### 7.5 清理环境变量与自启动

```bash
# KDE 写进环境变量的东西（XDG_CURRENT_DESKTOP 等）
grep -rnE 'KDE|PLASMA' /etc/environment /etc/profile.d/ ~/.config/environment.d/ 2>/dev/null

# KDE 残留的用户自启动项
ls -l ~/.config/autostart/
# 删除/归档指向 kde/plasma/kwin/kdeconnect/kded 的 .desktop

# KDE 的用户级 systemd 单元残留
systemctl --user list-unit-files | grep -iE 'plasma|kwin|kde|kwallet'
```

### 7.6 归档用户配置（不要直接删）

```bash
mkdir -p ~/.cache/kde-leftovers
for f in kdeglobals kwinrc kwinrulesrc kglobalshortcutsrc kcminputrc \
         plasmarc plasmashellrc ksplashrc kded5rc kded6rc kwalletrc konsolerc \
         plasma-org.kde.plasma.desktop-appletsrc; do
  [ -e ~/.config/$f ] && mv ~/.config/$f ~/.cache/kde-leftovers/ && echo "已归档 $f"
done
```

（KDE 会持续往这些文件写东西；在 niri 会话里它们毫无用处，但保留归档以便随时找回配置。）

### 7.7 可选：移除 KDE 应用

按需移除，不要无脑全删：

```bash
sudo pacman -Rns dolphin konsole kate ark gwenview spectacle ksysguard \
                 plasma-nm plasma-pa bluedevil powerdevil kscreen
```

移除 `plasma-nm`/`plasma-pa`/`bluedevil`/`powerdevil` 前，**确认替代品在位**：

| 被移除的 KDE 组件 | 替代方案 |
| --- | --- |
| `plasma-nm`（网络托盘） | `networkmanager` + Noctalia 的网络小组件 |
| `plasma-pa`（音量） | `pipewire` + `wireplumber` |
| `bluedevil`（蓝牙） | `bluez` + Noctalia 蓝牙小组件 |
| `powerdevil`（电源） | `upower` + Noctalia 电源管理 |
| `kscreen`（显示设置） | niri 的 `display.kdl` + `niri msg outputs` |

注意：**保留 `sddm`**。它不是 KDE 专属组件，且是 niri 的登录入口。

---

## 8. 阶段 6：最终验证清单

逐条执行并确认结果：

```bash
# —— niri ——
niri validate                                   # 配置语法正确
niri msg version                                # 正在运行
grep -n 'noctalia' ~/.config/niri/config.kdl     # 已注入 noctalia 配色 include
niri msg outputs                                # 显示器识别正常

# —— Noctalia ——
noctalia config validate                         # 配置合法
noctalia msg status                              # 外壳运行中
noctalia msg color-scheme-get                    # builtin <配色名>
noctalia msg theme-mode-get                      # dark / light
grep -A2 '^\[bar\]' ~/.local/state/noctalia/settings.toml   # position = "left"

# —— 模板渲染产物 ——
ls ~/.config/kitty/themes/noctalia.conf
ls ~/.config/niri/noctalia.kdl
head -3 ~/.config/starship.toml

# —— 门户（niri 下必须由 gtk/gnome 提供，不能有 kde）——
cat /usr/share/xdg-desktop-portal/niri-portals.conf
pacman -Qq | grep xdg-desktop-portal             # 不应出现 -kde
systemctl --user status xdg-desktop-portal --no-pager | head -5

# —— 密钥环 ——
command -v gnome-keyring-daemon
grep -c 'pam_gnome_keyring' /etc/pam.d/sddm       # 应 > 0
grep -c 'pam_kwallet' /etc/pam.d/sddm             # 应为 0

# —— X11 兼容 ——
command -v xwayland-satellite

# —— 字体 ——
fc-match "MesloLGS Nerd Font"
fc-list | grep -ci 'nerd font'                    # 应 > 0

# —— KDE 残留（应基本清空）——
pacman -Qq | grep -iE 'plasma|kwin|kwallet' || echo "无 KDE 核心残留"
ls ~/.config | grep -iE 'kde|kwin|plasma' || echo "无 KDE 配置残留"
```

### 人工验收（提示用户执行）

1. **重启**机器（由用户手动执行）。
2. 在 SDDM 登录界面，会话类型选择 **Niri**。
3. 登录后确认：
   - 状态栏出现在**屏幕左侧**（不是顶部）
   - `Mod+T` 打开 kitty，且字体字距正常、背景半透明磨砂
   - `Mod+方向键` 在窗口间导航
   - `Mod+R` 让窗口占满整列
   - `Mod+C` 居中，`Mod+Alt+←/→` 吸附左右半屏
   - 截图、文件选择器（打开/保存对话框）、剪贴板历史、Wi-Fi/蓝牙/音量小组件均可用

---

## 9. 回滚方案

出现问题时：

1. **图形界面进不去** → `Ctrl+Alt+F3` 切到 TTY 登录。
2. **回滚配置** → 从 `/root/backup-kde-to-niri-<日期>/` 和 `~/.cache/kde-to-niri-backup-<日期>/` 还原。
3. **快速装回 KDE** →
   ```bash
   sudo pacman -S plasma-meta kde-applications-meta sddm
   ```
   （KDE 的用户配置已归档在 `~/.cache/kde-leftovers/`，复制回 `~/.config/` 即可恢复）
4. **重装 niri 栈** → `sudo pacman -S --needed cachyos-niri-noctalia`

---

## 10. 关键事实速查

**CachyOS niri 版标准组件清单**（`cachyos-niri-noctalia` 的依赖）：
`adw-gtk-theme`、`cachyos-alacritty-config`、`capitaine-cursors`、`gnome-keyring`、`niri`、`noctalia`、`noto-fonts`、`noto-fonts-emoji`、`wl-clipboard`、`xdg-desktop-portal-gnome`、`xdg-desktop-portal-gtk`、`xwayland-satellite`

**关键路径**：

| 用途 | 路径 |
| --- | --- |
| niri 主配置 | `~/.config/niri/config.kdl` |
| niri 分片 | `~/.config/niri/cfg/*.kdl` |
| Noctalia 自动生成的 niri 配色 | `~/.config/niri/noctalia.kdl` |
| Noctalia 基础配置 | `~/.config/noctalia/*.toml` |
| Noctalia 设置（状态栏/主题/模板） | `~/.local/state/noctalia/settings.toml` |
| Noctalia 模板源 | `/usr/share/noctalia/assets/templates/` |
| niri 门户路由 | `/usr/share/xdg-desktop-portal/niri-portals.conf` |
| CachyOS skel 配置 | `/etc/skel/.config/{niri,noctalia}/` |
| dconf 主题 | `/etc/dconf/db/local.d/00-cachyos.conf` |
| SDDM PAM（kwallet 坑） | `/etc/pam.d/sddm` |

**常用 Noctalia 消息命令**：
`config-reload`、`templates-apply`、`bar-toggle`、`panel-toggle <launcher|control-center|wallpaper|session|clipboard|tray-drawer>`、`settings-toggle`、`session lock`、`color-scheme-set`、`theme-mode-set`、`volume-up/down/mute`、`brightness-up/down`、`notification-dnd-toggle`

**niri 热重载**：`niri msg action load-config-file`
**niri 校验**：`niri validate`

---

## 11. 可选：用 nirice 工具自动化

上面的步骤全部可以手工执行。如果你希望少写重复命令，可以选用配套工具 **nirice**（本提示词所在的仓库，Python + uv）：

```bash
# 安装（需要 uv：https://docs.astral.sh/uv/）
uv tool install git+https://github.com/vesita/nirice
# 或在克隆后的仓库内
uv run nirice --help
```

它与各阶段的对应关系：

| 阶段 | 手工做法 | nirice 命令 |
| --- | --- | --- |
| 侦察 | `pacman -Qq \| grep -i plasma` | `nirice migrate plan` |
| 补齐依赖 | `sudo pacman -S --needed ...` | `nirice install --all` |
| 写 Niri 配置 | 手写 `~/.config/niri/**` | `nirice niri apply` |
| 状态栏左置 | 改 `settings.toml` | `nirice shell bar position left` |
| 启用配色模板 | 改 `[theme.templates]` | `nirice shell templates enable` |
| Kitty 美学层 | 手写 `kitty.conf` | `nirice terminal set-kitty` |
| 归档 KDE 残留 | 手动 mv | `nirice migrate clean-configs` |
| 校验 | `niri validate` | `nirice niri check` |

**注意**：`nirice` 只自动化可逆操作。卸载 KDE 软件包这类不可逆动作，它仍然只输出命令（`nirice migrate plan` 的第 3 阶段），需要你确认后自行执行 —— 与本文档的立场一致。

---

## 12. 交付要求

完成后，向用户汇报：

1. 每个阶段的执行结果与验证证据（命令 + 实际输出摘要）。
2. 仍然存在的 KDE 残留（如果有）及原因。
3. 未自动化、需要用户自行决定的项（例如 KDE 应用是否卸载、显示器缩放参数）。
4. **提醒用户手动重启**，并在 SDDM 选择 **Niri** 会话。

=== 提示词结束 ===

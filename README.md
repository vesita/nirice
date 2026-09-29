# nirice

**nirice** 是面向 **CachyOS / Arch Linux + Niri (Wayland) + Noctalia** 的桌面美化（Rice）与配置管理工具箱：Niri 合成器配置、Noctalia 外壳主题联动、终端与 Shell 生态、跨机器迁移，全部收在一条 CLI 里。

> 名字来源于 **niri + rice**。项目早期基于 KDE Plasma，现已**彻底移除全部 KDE / KWin / Plasma 代码**。

---

## 🎯 设计原则

**能交给软件自动完成的，绝不手写。**

这是整个项目最重要的约束，具体表现为：

| 领域 | 谁负责 | 为什么 |
| --- | --- | --- |
| kitty / starship / niri / GTK / Qt 的**配色** | **Noctalia 官方主题模板** | 换主题/换壁纸时全生态自动联动，不会出现「一半新配色一半旧配色」 |
| kitty 的**排版 / 磨砂 / Tab / 快捷键** | nirice | 模板只负责颜色，美学层需要显式管理 |
| Niri 的**快捷键 / 动效 / 布局 / 规则** | nirice | 属于用户意图，不应被主题系统覆盖 |
| 显示器输出 `display.kdl` | **用户自己** | 与硬件绑定，nirice 只在文件缺失时生成，绝不覆盖 |
| Noctalia 状态栏位置 / 主题 / 模板开关 | nirice 写入 `settings.toml`，Noctalia 生效 | 走官方配置层，不做逆向修改 |

---

## 🌟 核心能力

1. **🪟 Niri 合成器全托管（`nirice niri`）**
   分片式配置（`config.kdl` + `cfg/*.kdl`）统一生成与校验、热重载、显示器/工作区实时查询、动效方案切换、快捷键导出与微调。

2. **🧩 Noctalia 外壳联动（`nirice shell`）**
   状态栏位置切换、内置配色与明暗模式、面板开关，以及**主题模板编排** —— 一条命令让 kitty / starship / niri / GTK3 / GTK4 / alacritty 的配色随外壳主题自动渲染。

3. **💻 终端与 Shell 生态（`nirice terminal`）**
   Kitty 美学层（MesloLGS Nerd Font + 0.78 磨砂透明 + 圆角药丸 Tab + 分屏快捷键）、Starship 胶囊提示符布局、Fastfetch 看板；Alacritty / Ghostty / Foot / WezTerm / Zellij 优先交给 Noctalia 模板，Noctalia 缺席时自动回退到内置调色板（18 套，含 Nord / Catppuccin / Tokyo Night / Dracula / Gruvbox / Solarized）。

4. **📦 跨机器打包与还原（`nirice snapshot`）**
   把 Niri 分片、Noctalia 设置（含状态栏位置与模板开关）、终端与 Shell 配置打成单一 `.pmz`，在新机器上 `--install-deps` 一键补齐依赖并还原，随后自动热重载 Niri / Noctalia / Kitty。

5. **🚚 KDE → Niri 迁移（`nirice migrate`）**
   检测 KDE 残留软件包与配置、找出缺失的 Niri 生态组件（门户后端、密钥环、指针主题、dconf 主题…），生成分阶段可执行计划。**卸载 KDE 属于不可逆操作，nirice 只输出命令，绝不自动执行。**

6. **🏥 健康诊断（`nirice doctor` / `nirice status`）**
   依赖审计、Nerd Font 检测、Shell 挂钩状态，以及 Niri / Noctalia / 终端的一体化状态看板。

---

## 🚀 快速开始

项目使用 [uv](https://docs.astral.sh/uv/) 管理：

```bash
git clone <repo> && cd nirice
uv sync                      # 创建 .venv 并安装依赖

uv run nirice --help
uv run nirice status         # 桌面状态总览
uv run nirice doctor         # 依赖与字体健康诊断
uv run nirice install --all  # 自动补齐缺失依赖
```

也可以直接安装为全局命令：`uv tool install .`

---

## 📖 常用命令

### 全局状态与诊断
```bash
uv run nirice status          # Niri / Noctalia / 终端状态看板
uv run nirice doctor          # 依赖、字体与 Shell 挂钩诊断
uv run nirice install --all   # 安装全部缺失依赖并配置 Shell 挂钩
uv run nirice install --hooks # 只注入 Starship 提示符挂钩
```

### Niri 合成器
```bash
uv run nirice niri diff                       # 对比磁盘现状与预设，看哪些片段被本地改过
uv run nirice niri apply                      # 写入全部受管配置片段并热重载
uv run nirice niri apply --no-keybinds        # 保留你自己的 keybinds.kdl
uv run nirice niri apply --animation snappy   # 同时切换动效方案
uv run nirice niri animations                 # 列出动效方案（arctic / snappy / silky / instant）
uv run nirice niri keybinds --dump ./my.kdl   # 导出快捷键配置自行微调
uv run nirice niri check                      # niri validate 语法校验
uv run nirice niri outputs                    # 显示器与分辨率
uv run nirice niri workspaces                 # 工作区状态
```

### Noctalia 外壳
```bash
uv run nirice shell status                    # 外壳状态
uv run nirice shell bar position left         # 把状态栏移到左侧（top/bottom/left/right）
uv run nirice shell theme Nord --mode light   # 切换配色与明暗模式
uv run nirice shell templates list            # 列出可用模板与启用状态
uv run nirice shell templates enable          # 自动检测已安装软件并启用模板
uv run nirice shell templates apply           # 按当前主题重新渲染全部模板
```

### 终端
```bash
uv run nirice terminal list                   # 列出内置回退调色板
uv run nirice terminal set-kitty              # 写入 Kitty 美学层（配色由 Noctalia 提供）
uv run nirice terminal set-kitty nord-light --no-noctalia   # 强制使用内置调色板
uv run nirice terminal apply nord-light       # 全终端同步
uv run nirice terminal export-palette dracula # 查看 16 色 ANSI 色卡
```

### 整合式 Rice 方案
```bash
uv run nirice theme list                      # 列出方案
uv run nirice theme apply nord-light          # 一键：外壳主题 + 模板渲染 + Niri 动效 + 终端
```

### 迁移
```bash
uv run nirice migrate plan                    # 检测 KDE 残留与 Niri 组件缺口
uv run nirice migrate apply                   # 执行可自动化部分（依赖→配置→模板→校验）
uv run nirice migrate clean-configs           # 归档 KDE 残留配置（可逆，不删除）
uv run nirice migrate report -o MIGRATION.md  # 导出迁移报告
```

> 面向「原生 KDE 中途转 Niri」机器的完整操作指引见 [KDE-TO-NIRI-PROMPT.md](KDE-TO-NIRI-PROMPT.md)。

### 快照
```bash
uv run nirice snapshot save --name my-rice
uv run nirice snapshot info snapshots/my-rice.pmz
uv run nirice snapshot load snapshots/my-rice.pmz --install-deps
```

---

## ⌨️ 默认快捷键设计

| 快捷键 | 动作 |
| --- | --- |
| `Mod+T` / `Mod+Return` | 打开终端 (kitty) |
| `Mod+← → ↑ ↓` | 在列 / 窗口之间聚焦导航 |
| `Mod+Ctrl+← → ↑ ↓` | 移动列 / 窗口 |
| `Mod+R` / `Mod+F` | 最大化当前列（占满整列） |
| `Mod+Shift+R` | 在预设列宽间循环（1/3 → 1/2 → 2/3） |
| `Mod+C` | 当前列居中 |
| `Mod+Alt+← / →` | 吸附到最左 / 最右（50% 宽 + 移动） |
| `Mod+Alt+↑` | 当前列居中 |
| `Mod+Alt+↓` | 扩展到可用宽度 |
| `Mod+Shift+F` | 真全屏 |
| `Mod+V` | 切换浮动窗口 |
| `Mod+1..9` / `Mod+Ctrl+1..9` | 切换工作区 / 把列移到工作区 |
| `Mod+D` / `Mod+Space` | Noctalia 应用启动器 |
| `Mod+S` / `Mod+Shift+S` | 控制中心 / 系统设置 |
| `Mod+Ctrl+V` | 剪贴板历史 |
| `Mod+Escape` | 紧急解除快捷键抑制 |

> **注意**：Niri 一个快捷键只允许一个动作。像「吸附左半屏」这种多步操作，实现上通过 `spawn-sh "niri msg action ... && niri msg action ..."` 串联两次官方 CLI 调用。

### Kitty 快捷键
`Ctrl+Shift+T` 新建 Tab、`Ctrl+Shift+W` 关闭、`Ctrl+Shift+←/→` 切换 Tab、`Ctrl+Shift+Enter` 分屏、`Ctrl+Shift+H/J/K/L` 分屏导航、`Ctrl+Shift+U/O` 实时调透明度、`Ctrl+Shift+Delete` 恢复默认。

---

## 📁 目录结构

```
src/nirice/
├── cli/                    # 命令行界面（按领域拆分，单文件均 < 250 行）
│   ├── app.py              #   根 Typer 应用
│   ├── env.py              #   status / doctor / install
│   ├── niri.py             #   niri 子命令
│   ├── shell.py            #   shell / bar / templates 子命令
│   ├── terminal.py         #   terminal 子命令
│   ├── theme.py            #   theme 子命令
│   ├── snapshot.py         #   snapshot 子命令
│   └── migrate.py          #   migrate 子命令
├── core/                   # 基础设施
│   ├── paths.py            #   XDG 目录统一解析
│   ├── process.py          #   子进程封装
│   └── toml_edit.py        #   TOML 外科手术式编辑
├── niri/                   # Niri 合成器
│   ├── animations.py       #   动效方案
│   ├── keybinds.py         #   快捷键预设
│   ├── fragments.py        #   其余受管片段
│   ├── catalog.py          #   受管片段聚合清单
│   └── controller.py       #   写入 / 校验 / 热重载 / 实时查询
├── noctalia/               # Noctalia 外壳
│   ├── templates.py        #   面板 ID、模板映射、产物路径
│   └── controller.py       #   settings.toml 编辑与模板编排
├── terminal/               # 终端与 Shell
│   ├── palettes.py         #   TerminalPalette 数据结构与色彩工具
│   ├── palettes_light.py   #   浅色调色板
│   ├── palettes_dark.py    #   暗色调色板
│   ├── catalog.py          #   调色板注册表
│   ├── kitty.py            #   Kitty 美学层与回退配色渲染
│   ├── backends.py         #   Alacritty / Ghostty / Foot / WezTerm / Zellij
│   ├── prompt.py           #   Starship 提示符与 Fastfetch 生成
│   └── controller.py       #   编排与模板委派
├── system/                 # 系统层
│   ├── packages.py         #   声明式依赖清单与探针
│   ├── installer.py        #   依赖审计与包安装
│   ├── kde_data.py         #   KDE 残留检测清单
│   └── migrate.py          #   迁移规划器
├── theme/rice.py           # 整合式 Rice 方案
├── inspector.py            # 桌面状态诊断
├── models.py               # 跨领域数据模型
└── snapshot.py             # 快照打包与还原
```

---

## 🧪 开发

```bash
uv sync                  # 安装依赖（含 dev）
uv run pytest            # 运行测试（59 项）
uv run ruff check .      # 静态检查
uv run ruff format .     # 代码格式化
```

测试通过 `tests/conftest.py` 的 `xdg` 夹具把 `HOME` 与全部 `XDG_*` 目录重定向到临时路径，
并通过 `binary=""` 注入「未安装 niri/noctalia」的控制器，因此**不会触碰真实桌面配置**。

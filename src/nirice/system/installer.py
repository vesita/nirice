"""依赖审计、系统包管理器安装与 Shell 提示符挂钩注入。"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from nirice.core import XDGPaths, which
from nirice.system.packages import PackageDef, package_defs


@dataclass
class PackageStatus:
    name: str
    category: str
    description: str
    installed: bool
    install_command: str
    essential: bool = False


@dataclass
class ShellHookStatus:
    shell: str
    rc_file: Path
    hooked: bool
    hook_code: str


@dataclass
class DoctorReport:
    packages: list[PackageStatus] = field(default_factory=list)
    hooks: list[ShellHookStatus] = field(default_factory=list)
    fonts_ready: bool = False
    font_details: str = ""
    pkg_manager: str = "pacman"
    has_aur_helper: bool = False
    aur_helper: str = ""


class DependencyHelper:
    """Niri 生态依赖检测、包管理器安装与 Shell 挂钩注入。"""

    def __init__(self, home_dir: Path | None = None) -> None:
        self.paths = XDGPaths.resolve(home_dir)
        self.home = self.paths.home
        self.config_dir = self.paths.config
        self.data_dir = self.paths.data
        self.fonts_dir = self.data_dir / "fonts"

    # ==================== 包管理器 ====================

    def detect_package_manager(self) -> tuple[str, str, bool]:
        """返回 (包管理器, AUR 助手, 是否有 AUR 助手)。"""
        aur_helper = ""
        has_aur = False
        for helper in ("paru", "yay"):
            if which(helper):
                aur_helper = helper
                has_aur = True
                break
        for manager in ("pacman", "dnf", "apt", "zypper"):
            if which(manager):
                return manager, aur_helper, has_aur
        return "未知", aur_helper, has_aur

    def installer_command(self) -> str:
        """用于展示的安装命令前缀。"""
        manager, aur_helper, has_aur = self.detect_package_manager()
        if has_aur:
            return aur_helper
        if manager == "pacman":
            return "sudo pacman -S"
        if manager == "未知":
            return "# 手动安装"
        return f"sudo {manager} install"

    # ==================== 字体与 Shell ====================

    def check_font_installed(self) -> tuple[bool, str]:
        """检查是否具备 Nerd Font（Powerline 图标与胶囊提示符依赖）。"""
        if which("fc-list"):
            try:
                result = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, check=False)
                output = result.stdout.lower()
                if "meslolgs nerd font" in output:
                    return True, "MesloLGS Nerd Font (已安装并生效)"
                if "nerd font" in output:
                    return True, "已检测到通用 Nerd Font 图标字体"
            except OSError:
                pass

        if self.fonts_dir.exists():
            for entry in self.fonts_dir.glob("*"):
                if "meslo" in entry.name.lower() or "nerd" in entry.name.lower():
                    return True, f"已找到本地字体: {entry.name}"

        for base in (Path("/usr/share/fonts"), Path("/usr/local/share/fonts")):
            if not base.exists():
                continue
            try:
                for entry in base.rglob("*"):
                    if "meslo" in entry.name.lower():
                        return True, f"已找到系统全局字体: {entry.name}"
            except OSError:
                continue

        return False, "缺少 Nerd Font（工作目录胶囊与 Git 图标需要 MesloLGS NF）"

    def check_shell_hooks(self) -> list[ShellHookStatus]:
        """检查 fish/zsh/bash 是否已注入 Starship 提示符。"""
        fish_config = self.config_dir / "fish" / "config.fish"
        fish_confd = self.config_dir / "fish" / "conf.d" / "starship.fish"
        fish_hooked = any(
            candidate.exists() and "starship init fish" in candidate.read_text(encoding="utf-8", errors="ignore")
            for candidate in (fish_confd, fish_config)
        )

        zshrc = self.home / ".zshrc"
        zsh_hooked = zshrc.exists() and "starship init zsh" in zshrc.read_text(encoding="utf-8", errors="ignore")

        bashrc = self.home / ".bashrc"
        bash_hooked = bashrc.exists() and "starship init bash" in bashrc.read_text(encoding="utf-8", errors="ignore")

        return [
            ShellHookStatus("fish", fish_config, fish_hooked, "starship init fish | source"),
            ShellHookStatus("zsh", zshrc, zsh_hooked, 'eval "$(starship init zsh)"'),
            ShellHookStatus("bash", bashrc, bash_hooked, 'eval "$(starship init bash)"'),
        ]

    # ==================== 依赖清单与审计 ====================

    def package_defs(self) -> list[PackageDef]:
        return package_defs()

    def check_all(self) -> list[PackageStatus]:
        """执行全量依赖审计。"""
        installer = self.installer_command()
        return [
            PackageStatus(
                name=definition.name,
                category=definition.category,
                description=definition.description,
                installed=definition.installed(),
                install_command=f"{installer} {definition.install_name}",
                essential=definition.essential,
            )
            for definition in self.package_defs()
        ]

    def doctor(self) -> DoctorReport:
        manager, aur_helper, has_aur = self.detect_package_manager()
        font_ok, font_msg = self.check_font_installed()
        return DoctorReport(
            packages=self.check_all(),
            hooks=self.check_shell_hooks(),
            fonts_ready=font_ok,
            font_details=font_msg,
            pkg_manager=manager,
            has_aur_helper=has_aur,
            aur_helper=aur_helper,
        )

    def missing_packages(self, essential_only: bool = False) -> list[str]:
        """返回缺失的软件包名列表。"""
        missing: list[str] = []
        for definition in self.package_defs():
            if definition.installed():
                continue
            if essential_only and not definition.essential:
                continue
            missing.append(definition.install_name)
        return missing

    def install_packages(self, package_names: list[str]) -> tuple[bool, str]:
        """调用系统包管理器安装指定包。"""
        if not package_names:
            return True, "无需安装任何软件包"

        manager, aur_helper, has_aur = self.detect_package_manager()
        if has_aur and aur_helper:
            cmd = [aur_helper, "-S", "--needed", "--noconfirm", *package_names]
        elif manager == "pacman":
            cmd = ["sudo", "pacman", "-S", "--needed", "--noconfirm", *package_names]
        elif manager == "dnf":
            cmd = ["sudo", "dnf", "install", "-y", *package_names]
        elif manager == "apt":
            cmd = ["sudo", "apt-get", "install", "-y", *package_names]
        elif manager == "zypper":
            cmd = ["sudo", "zypper", "install", "-y", *package_names]
        else:
            return False, f"当前系统包管理器不支持自动安装 ({manager})，请手动安装: {' '.join(package_names)}"

        try:
            result = subprocess.run(cmd, check=False)
        except OSError as exc:
            return False, f"执行安装命令异常: {exc}"
        if result.returncode == 0:
            return True, f"已成功安装: {' '.join(package_names)}"
        return False, f"包管理器执行退出，返回码: {result.returncode}"

    # ==================== Shell 挂钩注入 ====================

    FISH_SNIPPET = (
        "\n# >>> nirice starship prompt integration >>>\n"
        "if type -q starship\n"
        "    starship init fish | source\n"
        "end\n"
        "# <<< nirice starship prompt integration <<<\n"
    )
    POSIX_SNIPPET = (
        "\n# >>> nirice starship prompt integration >>>\n"
        "if command -v starship >/dev/null 2>&1; then\n"
        '    eval "$(starship init {shell})"\n'
        "fi\n"
        "# <<< nirice starship prompt integration <<<\n"
    )

    def inject_shell_hooks(self, shells: list[str] | None = None) -> list[tuple[str, bool, str]]:
        """在 fish/zsh/bash 中注入 Starship 挂钩（幂等）。"""
        results: list[tuple[str, bool, str]] = []
        for shell in shells or ["fish", "zsh", "bash"]:
            if shell == "fish":
                results.append(
                    self._inject(
                        self.config_dir / "fish" / "config.fish", "starship init fish", self.FISH_SNIPPET, "fish"
                    )
                )
            elif shell in ("zsh", "bash"):
                snippet = self.POSIX_SNIPPET.format(shell=shell)
                results.append(self._inject(self.home / f".{shell}rc", f"starship init {shell}", snippet, shell))
        return results

    @staticmethod
    def _inject(rc_file: Path, marker: str, snippet: str, shell: str) -> tuple[str, bool, str]:
        try:
            if not rc_file.exists():
                rc_file.parent.mkdir(parents=True, exist_ok=True)
                rc_file.write_text(snippet, encoding="utf-8")
                return shell, True, f"已创建 {rc_file} 并写入 Starship 集成"
            content = rc_file.read_text(encoding="utf-8", errors="ignore")
            if marker in content:
                return shell, True, f"{rc_file} 中已包含 Starship 配置"
            rc_file.write_text(content.rstrip() + "\n" + snippet, encoding="utf-8")
            return shell, True, f"已在 {rc_file} 中注入 Starship 挂钩"
        except OSError as exc:
            return shell, False, f"写入 {rc_file} 失败: {exc}"

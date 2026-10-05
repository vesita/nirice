"""快照引擎测试：Niri / Noctalia / 终端配置的打包与还原。"""

from __future__ import annotations

import io
import tarfile
from pathlib import Path

from nirice.snapshot import TRACKED_TARGETS, SnapshotManager


def _write_tar(archive: Path, entries: dict[str, bytes]) -> Path:
    """按给定成员名手工造一个快照，用于验证还原侧的防御。"""
    with tarfile.open(archive, "w:gz") as tar:
        for name, payload in entries.items():
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
    return archive


def _seed(xdg: dict[str, Path]) -> None:
    (xdg["config"] / "niri" / "cfg").mkdir(parents=True, exist_ok=True)
    (xdg["config"] / "niri" / "config.kdl").write_text('include "./cfg/keybinds.kdl"\n', encoding="utf-8")
    (xdg["config"] / "niri" / "cfg" / "keybinds.kdl").write_text("binds {\n}\n", encoding="utf-8")

    (xdg["config"] / "kitty").mkdir(parents=True, exist_ok=True)
    (xdg["config"] / "kitty" / "kitty.conf").write_text("include nirice.conf\n", encoding="utf-8")

    (xdg["state"] / "noctalia").mkdir(parents=True, exist_ok=True)
    (xdg["state"] / "noctalia" / "settings.toml").write_text(
        '[bar]\nposition = "left"\n\n[theme]\nbuiltin = "Nord"\nmode = "light"\n', encoding="utf-8"
    )

    (xdg["config"] / "starship.toml").write_text('palette = "noctalia"\n', encoding="utf-8")


def test_tracked_targets_are_niri_centric() -> None:
    joined = " ".join(f"{cat}/{rel}" for cat, rel in TRACKED_TARGETS)
    assert "niri" in joined
    assert "noctalia/settings.toml" in joined
    assert "kitty" in joined
    # KDE 相关目标必须已全部移除
    for legacy in ("kwinrc", "kdeglobals", "plasmarc", "color-schemes", "waybar"):
        assert legacy not in joined


def test_snapshot_roundtrip(xdg: dict[str, Path], tmp_path: Path) -> None:
    _seed(xdg)
    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])

    archive = manager.create_snapshot(output_path=tmp_path / "rice.pmz", name="unit-test")
    assert archive.exists()

    info = manager.inspect_snapshot(archive)
    assert info["name"] == "unit-test"
    files = info["files"]
    assert any("niri/config.kdl" in f for f in files)
    assert any("noctalia/settings.toml" in f for f in files)
    assert any("kitty" in f for f in files)


def test_dry_run_creates_nothing(xdg: dict[str, Path], tmp_path: Path, monkeypatch) -> None:
    _seed(xdg)
    manager = SnapshotManager(dry_run=True, home_dir=xdg["home"])

    out = tmp_path / "nested" / "rice.pmz"
    result = manager.create_snapshot(output_path=out, name="dry-run")
    assert result == out
    assert not out.exists()
    assert not out.parent.exists()

    # 默认输出路径同样不得创建 Path.cwd()/snapshots
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    default_out = manager.create_snapshot(name="dry-run-cwd")
    assert default_out == workdir / "snapshots" / "dry-run-cwd.pmz"
    assert not default_out.exists()
    assert not (workdir / "snapshots").exists()


def test_snapshot_excludes_backup_junk(xdg: dict[str, Path], tmp_path: Path) -> None:
    _seed(xdg)
    fcitx5 = xdg["config"] / "fcitx5"
    fcitx5.mkdir(parents=True, exist_ok=True)
    (fcitx5 / "theme.conf").write_text("keep me\n", encoding="utf-8")
    (fcitx5 / "theme.conf.bak").write_text("drop me\n", encoding="utf-8")
    (fcitx5 / "old.bak").mkdir()
    (fcitx5 / "old.bak" / "inner.conf").write_text("drop me too\n", encoding="utf-8")

    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])
    archive = manager.create_snapshot(output_path=tmp_path / "rice.pmz", name="exclude-test")

    files = manager.inspect_snapshot(archive)["files"]
    assert "config/fcitx5/theme.conf" in files
    assert not any(".bak" in f for f in files)


def test_restore_into_fresh_home(xdg: dict[str, Path], tmp_path: Path) -> None:
    _seed(xdg)
    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])
    archive = manager.create_snapshot(output_path=tmp_path / "rice.pmz", name="restore-test")

    # 抹掉所有受管文件，模拟一台新机器
    for target in (xdg["config"] / "niri", xdg["config"] / "kitty", xdg["state"] / "noctalia"):
        for path in sorted(target.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()

    restored = manager.restore_snapshot(archive, create_backup=False, wire_shell_hooks=False)
    assert restored

    assert (xdg["config"] / "niri" / "config.kdl").exists()
    assert (xdg["config"] / "kitty" / "kitty.conf").exists()
    settings = (xdg["state"] / "noctalia" / "settings.toml").read_text(encoding="utf-8")
    assert 'position = "left"' in settings


def test_restore_creates_backup_by_default(xdg: dict[str, Path], tmp_path: Path) -> None:
    _seed(xdg)
    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])
    archive = manager.create_snapshot(output_path=tmp_path / "rice.pmz", name="backup-test")

    manager.restore_snapshot(archive, create_backup=True, wire_shell_hooks=False)
    assert list(manager.backup_dir.rglob("config.kdl")), "还原前应创建安全备份"


def test_inspect_missing_snapshot_raises(xdg: dict[str, Path], tmp_path: Path) -> None:
    import pytest

    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])
    with pytest.raises(FileNotFoundError):
        manager.inspect_snapshot(tmp_path / "does-not-exist.pmz")


def test_snapshot_excludes_privacy_files(xdg: dict[str, Path], tmp_path: Path) -> None:
    """受管目录里混进的密钥/凭据/历史不得进包。"""
    _seed(xdg)
    scripts = xdg["config"] / "niri" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "id_ed25519").write_text("PRIVATE KEY\n", encoding="utf-8")
    kitty = xdg["config"] / "kitty"
    (kitty / ".netrc").write_text("machine x password y\n", encoding="utf-8")
    (kitty / "api.token").write_text("tok\n", encoding="utf-8")
    conf_d = xdg["config"] / "fish" / "conf.d"
    conf_d.mkdir(parents=True, exist_ok=True)
    (conf_d / "credentials").write_text("user=root\n", encoding="utf-8")

    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])
    archive = manager.create_snapshot(output_path=tmp_path / "privacy.pmz", name="privacy")
    files = manager.inspect_snapshot(archive)["files"]

    assert "config/kitty/kitty.conf" in files
    assert "config/niri/config.kdl" in files
    for leaked in ("id_ed25519", ".netrc", "api.token", "credentials"):
        assert not any(leaked in name for name in files), leaked


def test_snapshot_metadata_has_no_machine_identity(xdg: dict[str, Path], tmp_path: Path) -> None:
    """快照会被跨机器拷贝与分享，元数据不记录来源主机名。"""
    _seed(xdg)
    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])
    archive = manager.create_snapshot(output_path=tmp_path / "meta.pmz", name="meta")

    info = manager.inspect_snapshot(archive)
    assert "hostname" not in info
    assert info["generator"].startswith("nirice ")


def test_restore_rejects_path_traversal(xdg: dict[str, Path], tmp_path: Path) -> None:
    """绝对路径与 `..` 成员必须被拒绝，合法成员照常还原。"""
    archive = _write_tar(
        tmp_path / "evil.pmz",
        {
            "config/../pwned.txt": b"pwn",
            "config/niri/../../pwned2.txt": b"pwn",
            "/tmp/pwned3.txt": b"pwn",
            "config/niri/ok.kdl": b"binds {\n}\n",
        },
    )
    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])
    restored = manager.restore_snapshot(archive, create_backup=False, wire_shell_hooks=False)

    assert (xdg["config"] / "niri" / "ok.kdl").exists()
    assert not (xdg["config"].parent / "pwned.txt").exists()
    assert not (xdg["home"] / "pwned2.txt").exists()
    assert not Path("/tmp/pwned3.txt").exists()
    assert all("pwned" not in item for item in restored)


def test_restore_filters_privacy_files(xdg: dict[str, Path], tmp_path: Path) -> None:
    """来历不明的快照不得把凭据写到本机。"""
    archive = _write_tar(
        tmp_path / "incoming.pmz",
        {
            "config/kitty/kitty.conf": b"ok\n",
            "config/kitty/.netrc": b"secret\n",
            "config/niri/scripts/id_ed25519": b"key\n",
        },
    )
    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])
    manager.restore_snapshot(archive, create_backup=False, wire_shell_hooks=False)

    assert (xdg["config"] / "kitty" / "kitty.conf").read_text(encoding="utf-8") == "ok\n"
    assert not (xdg["config"] / "kitty" / ".netrc").exists()
    assert not (xdg["config"] / "niri" / "scripts" / "id_ed25519").exists()


def test_restore_symlink_must_stay_inside_root(xdg: dict[str, Path], tmp_path: Path) -> None:
    """指向 XDG 根之外（含绝对路径）的符号链接不建，根内的照常建。"""
    archive = tmp_path / "links.pmz"
    with tarfile.open(archive, "w:gz") as tar:
        for name, linkname in (
            ("config/niri/evil", "/etc"),
            ("config/niri/up", "../../.."),
            ("config/niri/good", "config.kdl"),
        ):
            info = tarfile.TarInfo(name)
            info.type = tarfile.SYMTYPE
            info.linkname = linkname
            tar.addfile(info)

    manager = SnapshotManager(dry_run=False, home_dir=xdg["home"])
    manager.restore_snapshot(archive, create_backup=False, wire_shell_hooks=False)

    assert not (xdg["config"] / "niri" / "evil").exists()
    assert not (xdg["config"] / "niri" / "up").exists()
    good = xdg["config"] / "niri" / "good"
    assert good.is_symlink() and good.readlink() == Path("config.kdl")

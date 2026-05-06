import pytest
from unittest.mock import MagicMock
from pathlib import Path

from ibridgesgui.mainmenu.config_manager import ConfigManager


@pytest.fixture
def fake_config():
    return {
        "cached_passwords": {
            "/tmp/env1.json": "pw1"
        },
        "tabs": ["Home", "Data"],
        "last_upload_path": "/tmp/upload",
        "last_download_path": "/tmp/download",
    }


@pytest.fixture
def patched_config(monkeypatch, fake_config):
    """Patch all config.py functions used by ConfigManager."""

    # Patch _get_config to return fake config
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager._get_config",
        lambda: fake_config.copy()
    )

    # Patch _save_config to capture writes
    saved = {}
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager._save_config",
        lambda cfg: saved.update(cfg)
    )

    # Patch last env
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.get_last_ienv_name",
        lambda: "alias1 - /tmp/env1.json"
    )
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.set_last_ienv",
        lambda alias, path: saved.update({"last_env": f"{alias} - {path}"})
    )

    # Patch log level
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.get_log_level",
        lambda: "INFO"
    )
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.set_log_level",
        lambda level: saved.update({"log_level": level})
    )

    # Patch upload/download paths
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.config_get_last_upload_path",
        lambda: Path("/tmp/upload")
    )
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.config_set_last_upload_path",
        lambda p: saved.update({"upload_path": str(p)})
    )

    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.config_get_last_download_path",
        lambda: Path("/tmp/download")
    )
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.config_set_last_download_path",
        lambda p: saved.update({"download_path": str(p)})
    )

    # Patch prev settings
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.get_prev_settings",
        lambda: {"prev": True}
    )

    return saved


@pytest.fixture
def manager(patched_config):
    return ConfigManager()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_save_current_settings(manager, patched_config):
    manager.save_current_settings(Path("/tmp/env1.json"))
    assert "last_env" not in patched_config  # save_current_settings does not set last_env
    assert manager._config is not None


def test_get_last_env(manager):
    assert manager.get_last_env() == "alias1 - /tmp/env1.json"


def test_set_last_ienv(manager, patched_config):
    manager.set_last_ienv("aliasX", "/tmp/envX.json")
    assert patched_config["last_env"] == "aliasX - /tmp/envX.json"


def test_get_log_level(manager):
    assert manager.get_log_level() == "INFO"


def test_set_log_level(manager, patched_config):
    manager.set_log_level("DEBUG")
    assert patched_config["log_level"] == "DEBUG"


def test_load_tabs(manager):
    assert manager.load_tabs() == ["Home", "Data"]


def test_save_tabs(manager, patched_config):
    manager.save_tabs(["A", "B"])
    assert patched_config["tabs"] == ["A", "B"]


def test_upload_paths(manager, patched_config):
    assert manager.get_last_upload_path() == Path("/tmp/upload")

    manager.set_last_upload_path(Path("/new/upload"))
    assert patched_config["upload_path"] == "/new/upload"


def test_download_paths(manager, patched_config):
    assert manager.get_last_download_path() == Path("/tmp/download")

    manager.set_last_download_path(Path("/new/download"))
    assert patched_config["download_path"] == "/new/download"


def test_get_prev_settings(manager):
    assert manager.get_prev_settings() == {"prev": True}


def test_reload(manager):
    old = manager._config
    manager._config = {}
    manager.reload()
    assert manager._config == old


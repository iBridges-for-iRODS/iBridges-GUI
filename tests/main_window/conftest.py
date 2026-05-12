import pytest
from pathlib import Path


@pytest.fixture
def fake_config():
    return {
        "gui_last_env": "alias1 - /tmp/env1.json",
        "log_level": "INFO",
        "tabs": ["Home", "Data"],
        "last_upload_path": "/tmp/upload",
        "last_download_path": "/tmp/download",
        "prev_settings": {"prev": True},
    }


@pytest.fixture
def patched_config(monkeypatch, fake_config):
    saved = {}

    # --- Patch _get_config in BOTH modules ---
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager._get_config",
        lambda: fake_config.copy()
    )
    monkeypatch.setattr(
        "ibridgesgui.config._get_config",
        lambda: fake_config.copy()
    )

    # --- Patch get_last_ienv_name to return ONLY alias ---
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.get_last_ienv_name",
        lambda: fake_config["gui_last_env"].split(" - ", 1)[0]
    )
    monkeypatch.setattr(
        "ibridgesgui.config.get_last_ienv_name",
        lambda: fake_config["gui_last_env"].split(" - ", 1)[0]
    )

    # --- Patch set_last_ienv to update gui_last_env ---
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.set_last_ienv",
        lambda alias, path: saved.update({"gui_last_env": f"{alias} - {path}"})
    )
    monkeypatch.setattr(
        "ibridgesgui.config.set_last_ienv",
        lambda alias, path: saved.update({"gui_last_env": f"{alias} - {path}"})
    )

    # --- Patch log level ---
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.get_log_level",
        lambda: fake_config["log_level"]
    )
    monkeypatch.setattr(
        "ibridgesgui.config.get_log_level",
        lambda: fake_config["log_level"]
    )

    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.set_log_level",
        lambda level: saved.update({"log_level": level})
    )
    monkeypatch.setattr(
        "ibridgesgui.config.set_log_level",
        lambda level: saved.update({"log_level": level})
    )

    # --- Upload path ---
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.config_get_last_upload_path",
        lambda: Path(fake_config["last_upload_path"])
    )
    monkeypatch.setattr(
        "ibridgesgui.config.config_get_last_upload_path",
        lambda: Path(fake_config["last_upload_path"])
    )

    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.config_set_last_upload_path",
        lambda p: saved.update({"last_upload_path": str(p)})
    )
    monkeypatch.setattr(
        "ibridgesgui.config.config_set_last_upload_path",
        lambda p: saved.update({"last_upload_path": str(p)})
    )

    # --- Download path ---
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.config_get_last_download_path",
        lambda: Path(fake_config["last_download_path"])
    )
    monkeypatch.setattr(
        "ibridgesgui.config.config_get_last_download_path",
        lambda: Path(fake_config["last_download_path"])
    )

    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.config_set_last_download_path",
        lambda p: saved.update({"last_download_path": str(p)})
    )
    monkeypatch.setattr(
        "ibridgesgui.config.config_set_last_download_path",
        lambda p: saved.update({"last_download_path": str(p)})
    )

    # --- prev settings ---
    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager.get_prev_settings",
        lambda: fake_config["prev_settings"]
    )
    monkeypatch.setattr(
        "ibridgesgui.config.get_prev_settings",
        lambda: fake_config["prev_settings"]
    )

    monkeypatch.setattr(
        "ibridgesgui.mainmenu.config_manager._save_config",
        lambda cfg: saved.update(cfg)
    )
    monkeypatch.setattr(
        "ibridgesgui.config._save_config",
        lambda cfg: saved.update(cfg)
    )


    return saved


@pytest.fixture
def manager(patched_config):
    # Import AFTER monkeypatching
    from ibridgesgui.mainmenu.config_manager import ConfigManager
    return ConfigManager()


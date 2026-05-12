import pytest
from unittest.mock import MagicMock
from pathlib import Path


def test_get_last_env(manager):
    print("Get last env info:", manager.get_last_env())
    assert manager.get_last_env() == "alias1"


def test_set_last_ienv(manager, patched_config):
    manager.set_last_ienv("aliasX", "/tmp/envX.json")
    assert patched_config["gui_last_env"] == "aliasX - /tmp/envX.json"


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
    assert patched_config["last_upload_path"] == "/new/upload"


def test_download_paths(manager, patched_config):
    assert manager.get_last_download_path() == Path("/tmp/download")

    manager.set_last_download_path(Path("/new/download"))
    assert patched_config["last_download_path"] == "/new/download"


def test_get_prev_settings(manager):
    assert manager.get_prev_settings() == {"prev": True}


def test_reload(manager):
    old = manager._config
    manager._config = {}
    manager.reload()
    assert manager._config == old


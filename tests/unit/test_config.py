# tests/test_config.py

import json
from pathlib import Path
import logging
import pytest
from unittest.mock import MagicMock

import ibridgesgui.config as cfg


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Redirect CONFIG_DIR and CONFIG_FILE to a temporary directory."""
    config_dir = tmp_path / ".ibridges"
    config_dir.mkdir()

    monkeypatch.setattr(cfg, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(cfg, "CONFIG_FILE", config_dir / "ibridges_gui.json")

    return config_dir


@pytest.fixture
def temp_irods_dir(tmp_path, monkeypatch):
    """Redirect ~/.irods to a temporary directory."""
    irods_dir = tmp_path / ".irods"
    irods_dir.mkdir()

    monkeypatch.setattr(cfg, "IRODSA", irods_dir / ".irodsA")
    return irods_dir


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_basic_env(env_file: Path):
    env_file.write_text(json.dumps({
        "irods_host": "host",
        "irods_port": 1247,
        "irods_home": "/home",
        "irods_default_resource": "resc",
    }))


def _write_full_env(env_file: Path):
    env_file.write_text(json.dumps({
        "irods_host": "host",
        "irods_port": 1247,
        "irods_zone_name": "zone",
        "irods_user_name": "user",
        "irods_home": "/zone/home/user",
        "irods_default_resource": "resc",
    }))


class DummySession:
    """Minimal fake iBridges Session for is_session_from_config tests."""
    def __init__(self, host, port, zone, username, home, default_resc, env_file=None):
        self.host = host
        self.port = port
        self.zone = zone
        self.username = username
        self.home = home
        self.default_resc = default_resc

        class DummyIRODSSession:
            def __init__(self, env_file):
                self.env_file = env_file

        self.irods_session = DummyIRODSSession(env_file)


# ---------------------------------------------------------------------------
# Tests: config loading
# ---------------------------------------------------------------------------

def test_get_config_file_not_found(temp_config_dir):
    assert cfg._get_config() is None


def test_load_config_valid(temp_config_dir):
    (temp_config_dir / "ibridges_gui.json").write_text('{"tabs": ["Browser"]}')
    assert cfg._get_config()["tabs"] == ["Browser"]


def test_get_config_empty_file(temp_config_dir):
    cfg.CONFIG_FILE.write_text("")
    assert cfg._get_config() is None


def test_get_config_json_decode_error(temp_config_dir):
    cfg.CONFIG_FILE.write_text("{not valid json")
    with pytest.raises(SystemExit):
        cfg._get_config()


# ---------------------------------------------------------------------------
# Tests: saving config
# ---------------------------------------------------------------------------

def test_save_config_creates_file(temp_config_dir):
    cfg._save_config({"x": 1})
    assert cfg.CONFIG_FILE.exists()


def test_save_and_load_config(temp_config_dir):
    cfg._save_config({"a": 1})
    assert cfg._get_config() == {"a": 1}


# ---------------------------------------------------------------------------
# Tests: last ienv helpers
# ---------------------------------------------------------------------------

def test_get_last_ienv_path(temp_config_dir):
    cfg._save_config({"gui_last_env": "alias - /tmp/env.json"})
    assert cfg.get_last_ienv_path() == "/tmp/env.json"


def test_set_last_ienv(temp_config_dir):
    cfg.set_last_ienv("alias", "/tmp/env.json")
    assert cfg._get_config()["gui_last_env"] == "alias - /tmp/env.json"


# ---------------------------------------------------------------------------
# Tests: save_current_settings
# ---------------------------------------------------------------------------

def test_save_current_settings(temp_config_dir, temp_irods_dir, monkeypatch):
    cfg.IRODSA.write_text("mypw")

    fake_conf = MagicMock()
    fake_conf.get_entry.side_effect = KeyError
    fake_conf.servers = {}

    monkeypatch.setattr(cfg, "IbridgesConf", lambda _: fake_conf)

    cfg.save_current_settings(Path("/tmp/env.json"))

    assert fake_conf.servers["/tmp/env.json"]["irodsa_backup"] == "mypw"
    fake_conf.save.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: is_session_from_config
# ---------------------------------------------------------------------------

def test_is_session_from_config_env_file_match(temp_config_dir, tmp_path):
    env_file = tmp_path / "env.json"
    _write_full_env(env_file)

    cfg.set_last_ienv("alias", env_file)

    session = DummySession(
        host="host",
        port=1247,
        zone="zone",
        username="user",
        home="/zone/home/user",
        default_resc="resc",
        env_file=str(env_file),
    )

    assert cfg.is_session_from_config(session) is True


def test_is_session_from_config_env_file_mismatch(temp_config_dir, tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text("{}")

    cfg.set_last_ienv("alias", env_file)

    session = DummySession(
        host="host",
        port=1247,
        zone="zone",
        username="user",
        home="/zone/home/user",
        default_resc="resc",
        env_file=str(tmp_path / "other.json"),
    )

    assert cfg.is_session_from_config(session) is False


def test_is_session_from_config_legacy_match(temp_config_dir, tmp_path):
    env_file = tmp_path / "env.json"
    _write_full_env(env_file)

    cfg.set_last_ienv("alias", env_file)

    session = DummySession(
        host="host",
        port=1247,
        zone="zone",
        username="user",
        home="/zone/home/user",
        default_resc="resc",
        env_file=None,
    )

    assert cfg.is_session_from_config(session) is True


def test_is_session_from_config_no_last_env(temp_config_dir):
    session = MagicMock()
    assert cfg.is_session_from_config(session) is False


def test_is_session_from_config_env_read_error(temp_config_dir, tmp_path, monkeypatch):
    env_file = tmp_path / "env.json"
    cfg.set_last_ienv("alias", env_file)

    def fake_read_json(path):
        if path == env_file:
            raise RuntimeError("boom")
        return {}

    monkeypatch.setattr(cfg, "_read_json", fake_read_json)
    assert cfg.is_session_from_config(MagicMock()) is False


# ---------------------------------------------------------------------------
# Tests: check_irods_config
# ---------------------------------------------------------------------------

def test_check_irods_config_file_not_found(tmp_path):
    msg = cfg.check_irods_config(tmp_path / "missing.json", include_network=False)
    assert "not found" in msg


def test_check_irods_config_malformed_file(tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text("{not-json}")
    msg = cfg.check_irods_config(env_file, include_network=False)
    assert "not well formatted" in msg


def test_check_irods_config_missing_required_field(tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({"irods_port": 1247}))
    msg = cfg.check_irods_config(env_file, include_network=False)
    assert '"irods_host" is missing' in msg


def test_check_irods_config_port_not_int(tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({
        "irods_host": "host",
        "irods_port": "1247",
        "irods_home": "/home",
        "irods_default_resource": "resc",
    }))
    msg = cfg.check_irods_config(env_file, include_network=False)
    assert "must be a number" in msg


def test_check_irods_config_skip_network(tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({
        "irods_host": "host",
        "irods_port": 1247,
        "irods_home": "/home",
        "irods_default_resource": "resc",
    }))
    assert cfg.check_irods_config(env_file, include_network=False) == "All checks passed successfully."


def test_check_irods_config_network_unreachable(tmp_path, monkeypatch):
    env_file = tmp_path / "env.json"
    _write_basic_env(env_file)

    monkeypatch.setattr(cfg.Session, "network_check", lambda *_: False)
    msg = cfg.check_irods_config(env_file, include_network=True)
    assert "Unable to connect" in msg


def test_check_irods_config_network_success(tmp_path, monkeypatch):
    env_file = tmp_path / "env.json"
    _write_basic_env(env_file)

    monkeypatch.setattr(cfg.Session, "network_check", lambda *_: True)

    class FakeSess:
        server_version = "4.3.0"
        def __init__(self, **kwargs):
            pass

    monkeypatch.setattr(cfg, "iRODSSession", FakeSess)
    assert cfg.check_irods_config(env_file, include_network=True) == "All checks passed successfully."


def test_check_irods_config_network_error(tmp_path, monkeypatch):
    env_file = tmp_path / "env.json"
    _write_basic_env(env_file)

    monkeypatch.setattr(cfg.Session, "network_check", lambda *_: True)
    monkeypatch.setattr(cfg, "iRODSSession", lambda **_: (_ for _ in ()).throw(AttributeError("boom")))

    msg = cfg.check_irods_config(env_file, include_network=True)
    assert "invalid or incomplete" in msg or "Unknown problem" in msg


# ---------------------------------------------------------------------------
# Tests: upload/download paths
# ---------------------------------------------------------------------------

def test_upload_path(temp_config_dir):
    p = Path("/tmp/upload")
    cfg.config_set_last_upload_path(p)
    assert cfg.config_get_last_upload_path() == p


def test_download_path(temp_config_dir):
    p = Path("/tmp/download")
    cfg.config_set_last_download_path(p)
    assert cfg.config_get_last_download_path() == p


def test_upload_path_default_home(temp_config_dir, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    assert cfg.config_get_last_upload_path() == Path.home()


def test_download_path_default_home(temp_config_dir, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    assert cfg.config_get_last_download_path() == Path.home()


# ---------------------------------------------------------------------------
# Tests: previous settings
# ---------------------------------------------------------------------------

def test_get_prev_settings_default_empty(temp_config_dir):
    cfg._save_config({})
    assert cfg.get_prev_settings() == {}


def test_get_prev_settings_from_config(temp_config_dir):
    cfg._save_config({"settings": {"env1": {"x": 1}}})
    assert cfg.get_prev_settings() == {"env1": {"x": 1}}


def test_save_current_settings_removes_legacy_settings(temp_config_dir, temp_irods_dir, monkeypatch):
    cfg.IRODSA.write_text("mypw")

    fake_conf = MagicMock()
    fake_conf.get_entry.side_effect = KeyError
    fake_conf.servers = {}
    monkeypatch.setattr(cfg, "IbridgesConf", lambda _: fake_conf)

    env_path = Path("/tmp/env.json")

    cfg._save_config({"settings": {str(env_path): {"irodsa_backup": "old"}}})
    cfg.save_current_settings(env_path)

    conf = cfg._get_config()
    assert "settings" not in conf or str(env_path) not in conf.get("settings", {})


# ---------------------------------------------------------------------------
# Tests: logging
# ---------------------------------------------------------------------------

def test_ensure_log_config_location(temp_config_dir):
    cfg.ensure_log_config_location()
    assert cfg.CONFIG_DIR.exists()
    assert cfg.CONFIG_DIR == temp_config_dir


def test_ensure_irods_location(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg.ensure_irods_location()
    assert (tmp_path / ".irods").exists()


def test_init_logger_creates_logfile(temp_config_dir, monkeypatch):
    monkeypatch.setattr(cfg, "CONFIG_DIR", temp_config_dir)
    monkeypatch.setattr(cfg, "version", lambda _: "1.0.0")

    logger = cfg.init_logger("testapp", "debug")
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG

    logfile = temp_config_dir / "testapp.log"
    assert logfile.exists()
    assert "Starting iBridges-GUI 1.0.0" in logfile.read_text(encoding="utf-8")


def test_get_and_set_log_level(temp_config_dir):
    assert cfg.get_log_level() is None
    cfg.set_log_level("debug")
    assert cfg.get_log_level() == "debug"


# ---------------------------------------------------------------------------
# Tests: saving iRODS config
# ---------------------------------------------------------------------------

def test_save_irods_config_invalid_suffix(tmp_path):
    with pytest.raises(ValueError):
        cfg.save_irods_config(tmp_path / "env.txt", {})


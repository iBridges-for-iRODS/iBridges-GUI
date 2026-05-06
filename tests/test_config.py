import json
from pathlib import Path
import pytest

import ibridgesgui.config as cfg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class DummySession:
    """A minimal fake iBridges Session object."""
    def __init__(self, host, port, zone, username, home, default_resc, env_file=None):
        self.host = host
        self.port = port
        self.zone = zone
        self.username = username
        self.home = home
        self.default_resc = default_resc

        # Underlying python-irodsclient session
        class DummyIRODSSession:
            def __init__(self, env_file):
                self.env_file = env_file

        self.irods_session = DummyIRODSSession(env_file)


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
# Tests: config read/write
# ---------------------------------------------------------------------------

def test_save_and_load_config(temp_config_dir):
    cfg._save_config({"a": 1})
    assert cfg._get_config() == {"a": 1}


def test_get_last_ienv_path(temp_config_dir):
    cfg._save_config({"gui_last_env": "alias - /tmp/env.json"})
    assert cfg.get_last_ienv_path() == "/tmp/env.json"


def test_set_last_ienv(temp_config_dir):
    cfg.set_last_ienv("alias - /tmp/env.json")
    assert cfg._get_config()["gui_last_env"] == "alias - /tmp/env.json"


# ---------------------------------------------------------------------------
# Tests: upload/download paths
# ---------------------------------------------------------------------------

def test_upload_path(temp_config_dir):
    p = Path("/tmp/upload")
    cfg.config_set_last_upload_path(p)
    assert cfg.config_get_last_upload_path() == str(p)


def test_download_path(temp_config_dir):
    p = Path("/tmp/download")
    cfg.config_set_last_download_path(p)
    assert cfg.config_get_last_download_path() == str(p)


# ---------------------------------------------------------------------------
# Tests: is_session_from_config
# ---------------------------------------------------------------------------

def test_is_session_from_config_env_file_match(temp_config_dir, tmp_path):
    # Create fake env file
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({
        "irods_host": "host",
        "irods_port": 1247,
        "irods_zone_name": "zone",
        "irods_user_name": "user",
        "irods_home": "/zone/home/user",
        "irods_default_resource": "resc"
    }))

    # Save last used env
    cfg.set_last_ienv(f"alias - {env_file}")

    # Session with matching env_file
    session = DummySession(
        host="host",
        port=1247,
        zone="zone",
        username="user",
        home="/zone/home/user",
        default_resc="resc",
        env_file=str(env_file)
    )

    assert cfg.is_session_from_config(session) is True


def test_is_session_from_config_env_file_mismatch(temp_config_dir, tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text("{}")

    cfg.set_last_ienv(f"alias - {env_file}")

    session = DummySession(
        host="host",
        port=1247,
        zone="zone",
        username="user",
        home="/zone/home/user",
        default_resc="resc",
        env_file=str(tmp_path / "other.json")
    )

    assert cfg.is_session_from_config(session) is False


def test_is_session_from_config_legacy_match(temp_config_dir, tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({
        "irods_host": "host",
        "irods_port": 1247,
        "irods_zone_name": "zone",
        "irods_user_name": "user",
        "irods_home": "/zone/home/user",
        "irods_default_resource": "resc"
    }))

    cfg.set_last_ienv(f"alias - {env_file}")

    # Session WITHOUT env_file → triggers legacy comparison
    session = DummySession(
        host="host",
        port=1247,
        zone="zone",
        username="user",
        home="/zone/home/user",
        default_resc="resc",
        env_file=None
    )

    assert cfg.is_session_from_config(session) is True


def test_is_session_from_config_legacy_mismatch(temp_config_dir, tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({
        "irods_host": "host",
        "irods_port": 1247,
        "irods_zone_name": "zone",
        "irods_user_name": "user",
        "irods_home": "/zone/home/user",
        "irods_default_resource": "resc"
    }))

    cfg.set_last_ienv(f"alias - {env_file}")

    session = DummySession(
        host="wrong",
        port=1247,
        zone="zone",
        username="user",
        home="/zone/home/user",
        default_resc="resc",
        env_file=None
    )

    assert cfg.is_session_from_config(session) is False


# ---------------------------------------------------------------------------
# Tests: check_irods_config (non-network)
# ---------------------------------------------------------------------------

def test_check_irods_config_missing_key(tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({"irods_host": "host"}))

    msg = cfg.check_irods_config(env_file, include_network=False)
    assert "irods_port" in msg


def test_check_irods_config_port_not_int(tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({
        "irods_host": "host",
        "irods_port": "1247",
        "irods_home": "/home",
        "irods_default_resource": "resc"
    }))

    msg = cfg.check_irods_config(env_file, include_network=False)
    assert "must be a number" in msg


def test_check_irods_config_success_no_network(tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({
        "irods_host": "host",
        "irods_port": 1247,
        "irods_home": "/home",
        "irods_default_resource": "resc"
    }))

    msg = cfg.check_irods_config(env_file, include_network=False)
    assert msg == "All checks passed successfully."


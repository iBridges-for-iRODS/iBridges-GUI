import pytest
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Unified Fake iRODS Session
# ---------------------------------------------------------------------------

class FakeIrodsSession:
    def __init__(self):
        # The real session object
        class Inner:
            pass

        self.irods_session = Inner()
        self.irods_session.data_objects = type("X", (), {"exists": lambda self, p: False})()
        self.irods_session.collections = type("Y", (), {"exists": lambda self, p: False})()

        # Required by IrodsPath.absolute()
        self.zone = "tempZone"
        self.home = "/tempZone/home"
        self.cwd = "/tempZone/home/testuser"


# ---------------------------------------------------------------------------
# Fake IrodsPath
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_irods_path():
    """Return a fresh FakeIrodsPath object each time (not a factory)."""

    class FakeObj:
        def __init__(self, name):
            self.name = name

    class FakeCollection:
        def __init__(self):
            self.subcollections = [FakeObj("sub1"), FakeObj("sub2")]
            self.data_objects = [FakeObj("file1"), FakeObj("file2")]

    class FakeIrodsPath:
        def __init__(self, name="test_item"):
            self.name = name
            self.session = FakeIrodsSession()
            self.collection = FakeCollection()

        def collection_exists(self):
            return True

    # IMPORTANT: return a *new instance* each time
    return FakeIrodsPath()


# ---------------------------------------------------------------------------
# Patch config + environment paths
# ---------------------------------------------------------------------------

@pytest.fixture
def patch_config(monkeypatch, tmp_path):
    env_dir = tmp_path / "ienv"
    env_dir.mkdir()

    env_file = env_dir / "test_env.json"
    data = {
        "host": "localhost",
        "port": 1247,
        "zone": "tempZone",
        "username": "alice",
        "password": "secret",
    }
    env_file.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.check_config.get_last_ienv_path",
        lambda: env_dir,
        raising=False,
    )

    written = {}

    def fake_write(path, text):
        written["path"] = path
        written["text"] = text

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.check_config.write_config",
        fake_write,
        raising=False,
    )

    return {"dir": env_dir, "file": env_file, "written": written}


@pytest.fixture(autouse=True)
def patch_env_path(monkeypatch, tmp_path):
    """Patch config lookups so CI does not crash."""
    fake_config = {"last_download_path": str(tmp_path)}

    monkeypatch.setattr(
        "ibridgesgui.config._get_config",
        lambda: fake_config,
        raising=False,
    )

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.get_last_ienv_path",
        lambda: str(tmp_path),
        raising=False,
    )

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.get_last_ienv_path",
        lambda: str(tmp_path),
        raising=False,
    )

    return fake_config


# ---------------------------------------------------------------------------
# Logger + dummy ops
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_logger():
    class FakeLogger:
        def info(self, *args, **kwargs): pass
        def warning(self, *args, **kwargs): pass
        def error(self, *args, **kwargs): pass
    return FakeLogger()


@pytest.fixture
def dummy_ops():
    class DummyOps:
        def __init__(self):
            self.download = ["file1"]
            self.meta_download = []
    return DummyOps()


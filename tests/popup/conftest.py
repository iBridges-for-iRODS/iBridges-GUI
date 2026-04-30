import pytest
from pathlib import Path


# ---------------------------------------------------------------------------
# Fake iRODS session + path objects
# ---------------------------------------------------------------------------

class FakeDataObjects:
    """Minimal stub for session.irods_session.data_objects."""
    def exists(self, path: str) -> bool:
        return False

class FakeCollections:
    def exists(self, path):
        return False


class FakeSession:
    """
    Combined fake session object that satisfies all requirements of IrodsPath.
    Provides:
      - irods_session.data_objects.exists()
      - irods_session.collections.exists()
      - cwd, home, zone
    """

    class _DataObjects:
        def exists(self, path):
            return False

    class _Collections:
        def exists(self, path):
            return False

    class _IrodsSession:
        pass

    _IrodsSession.data_objects = _DataObjects()
    _IrodsSession.collections = _Collections()

    irods_session = _IrodsSession()

    # Required by IrodsPath.absolute()
    cwd = "/"
    home = "/"
    zone = "tempZone"


@pytest.fixture
def fake_irods_path():
    class FakeIrodsPath:
        def __init__(self, name="test_item"):
            self.name = name
            self.session = FakeSession()
            self.collection = self
            self.subcollections = []
            self.data_objects = []

        def collection_exists(self):
            return True

    return FakeIrodsPath()

# ---------------------------------------------------------------------------
# Patch environment path lookups
# ---------------------------------------------------------------------------

@pytest.fixture
def patch_env_path(monkeypatch):
    """Patch get_last_ienv_path() to avoid touching real config."""
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.get_last_ienv_path",
        lambda: str(Path.cwd()),
        raising=False,
    )
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.get_last_ienv_path",
        lambda: str(Path.cwd()),
        raising=False,
    )


# ---------------------------------------------------------------------------
# Dummy ops object for dry-run upload/download
# ---------------------------------------------------------------------------

@pytest.fixture
def dummy_ops():
    class DummyOps:
        upload = True
        download = True
        meta_download = False
    return DummyOps()


# tests/conftest.py

import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication
from ibridges import IrodsPath


# ---------------------------------------------------------
# Ensure a QApplication exists (required for pytest-qt)
# ---------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Ensure a single QApplication instance for all GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# ---------------------------------------------------------
# Minimal fake iBridges session for IrodsPath
# ---------------------------------------------------------
class _FakeCollections:
    def exists(self, path: str) -> bool:
        return True


class _FakeIrodsSession:
    def __init__(self):
        self.collections = _FakeCollections()


class _FakeSessionWrapper:
    """Matches the structure expected by IrodsPath."""
    def __init__(self):
        self.irods_session = _FakeIrodsSession()


def _make_irods_path(path: str) -> IrodsPath:
    """Create an IrodsPath with a minimal fake session."""
    return IrodsPath(_FakeSessionWrapper(), path)


@pytest.fixture
def make_irods_path():
    """Factory fixture to create fake IrodsPath objects."""
    return _make_irods_path


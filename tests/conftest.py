# tests/conftest.py

import pytest
from unittest.mock import MagicMock
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication
from ibridges import IrodsPath

# ---------------------------------------------------------
# Ensure a QApplication exists (required for pytest-qt)
# ---------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class DummyCollections:
    def exists(self, path: str) -> bool:
        return True   # pretend all collections exist


class DummyIrodsSession:
    def __init__(self):
        self.collections = DummyCollections()


class DummySession:
    def __init__(self):
        self.irods_session = DummyIrodsSession()


def make_path(path: str) -> IrodsPath:
    return IrodsPath(DummySession(), path)


@pytest.fixture
def make_irods_path():
    return make_path


# tests/conftest.py

import pytest
from unittest.mock import MagicMock
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication

# ---------------------------------------------------------
# Ensure a QApplication exists (required for pytest-qt)
# ---------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

# ---------------------------------------------------------
# Your existing fake_view fixture
# ---------------------------------------------------------
@pytest.fixture
def fake_view(qtbot):
    """Creates a minimal fake view with the widgets the controller expects."""

    class FakeView(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            self.local_fs_tree = MagicMock()
            self.irods_tree = MagicMock()
            self.local_to_irods_button = MagicMock()
            self.irods_to_local_button = MagicMock()
            self.create_coll_button = MagicMock()
            self.create_dir_button = MagicMock()
            self.sync_button = MagicMock()
            self.error_label = MagicMock()
            self.progress_bar = MagicMock()
            self.diff_table = MagicMock()

    view = FakeView()
    qtbot.addWidget(view)
    return view


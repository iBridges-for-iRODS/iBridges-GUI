# tests/sync/conftest.py
import pytest
from unittest.mock import MagicMock
from PySide6 import QtWidgets
from ibridges import IrodsPath

# -----------------------------
# Fake view matching real Sync
# -----------------------------
@pytest.fixture
def fake_view(qtbot):
    class FakeView(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()

            # widgets the controller expects
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
            self._setCursor_called = False

        def setCursor(self, cursor):
            self._cursor = cursor
            self._setCursor_called = True

        def assert_cursor_called(self):
            assert getattr(self, "_setCursor_called", False)


        # ---- view helper methods ----
        def clear_error(self):
            self.error_label.clear()

        def show_error(self, text):
            self.error_label.setText(text)

        def set_ui_busy(self, busy):
            self.local_to_irods_button.setEnabled(not busy)
            self.irods_to_local_button.setEnabled(not busy)
            self.create_coll_button.setEnabled(not busy)
            self.create_dir_button.setEnabled(not busy)
            self.sync_button.setEnabled(not busy)
        
            # simulate real cursor behavior
            if busy:
                self.setCursor("wait")
            else:
                self.setCursor("arrow")
         
        def set_progress(self, value):
            self.progress_bar.setValue(value)

        def update_progress(self, value):
            self.set_progress(value)

        def hide_sync_button(self):
            self.sync_button.hide()

        def show_sync_button(self):
            self.sync_button.show()

        def clear_diff_table(self):
            self.diff_table.setRowCount(0)

        def display_diff_rows(self, rows):
            self._rows = rows

    view = FakeView()
    qtbot.addWidget(view)
    return view

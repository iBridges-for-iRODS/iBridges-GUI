"""Sync widget."""
# sync.py
import sys

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui, populate_table
from ibridgesgui.ui_files.tabSync import Ui_tabSync

from .sync_controller import SyncController


class Sync(QtWidgets.QWidget, Ui_tabSync):
    """Sync view for iRODS session (UI only, logic in SyncController)."""

    def __init__(self, session, app_name: str):
        """Init."""
        super().__init__()

        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabSync.ui", self)

        # Create controller
        self.controller = SyncController(self, session, app_name)


    # -------------------------
    # UI helper methods
    # -------------------------

    def set_busy_cursor(self):
        """Set cursor to busy."""
        self.setCursor(QCursor(Qt.WaitCursor))

    def set_normal_cursor(self):
        """Set cursor to normal."""
        self.setCursor(QCursor(Qt.ArrowCursor))

    def set_buttons_enabled(self, enabled: bool):
        """Enable or disable buttons."""
        self.local_to_irods_button.setEnabled(enabled)
        self.irods_to_local_button.setEnabled(enabled)
        self.create_coll_button.setEnabled(enabled)
        self.create_dir_button.setEnabled(enabled)
        self.sync_button.setEnabled(enabled)

    def show_sync_button(self):
        """Show sync button."""
        self.sync_button.show()

    def hide_sync_button(self):
        """Hide sync button."""
        self.sync_button.hide()

    def show_error(self, text: str):
        """Set the text in the error label."""
        self.error_label.setText(text)

    def set_ui_busy(self, busy: bool):
        """Enable/disable all buttons."""
        self.local_to_irods_button.setEnabled(not busy)
        self.irods_to_local_button.setEnabled(not busy)
        self.create_coll_button.setEnabled(not busy)
        self.create_dir_button.setEnabled(not busy)
        self.sync_button.setEnabled(not busy)

        # Cursor
        if busy:
            self.setCursor(QCursor(Qt.WaitCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))


    def clear_error(self):
        """Clear error label."""
        self.error_label.clear()

    def update_progress(self, percent: int):
        """Update progress bar."""
        self.progress_bar.setValue(percent)

    def display_diff_rows(self, rows):
        """Display result from sync diff."""
        populate_table(self.diff_table, len(rows), rows)

    def clear_diff_table(self):
        """Clear table with sync diff results."""
        self.diff_table.setRowCount(0)

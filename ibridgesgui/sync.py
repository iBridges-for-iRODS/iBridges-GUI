"""Sync widget."""

import sys

from PySide6 import QtWidgets

from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.ui_files.tabSync import Ui_tabSync

from .sync_controller import SyncController


class Sync(QtWidgets.QWidget, Ui_tabSync):
    """Sync view for iRODS session (UI only, logic in SyncController)."""

    def __init__(self, session, app_name: str):
        """Init."""
        super().__init__()

        # Load UI (same pattern as Browser)
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabSync.ui", self)

        # Create controller and initialize logic
        self.controller = SyncController(self, session, app_name)

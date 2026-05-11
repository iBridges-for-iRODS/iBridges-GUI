"""Dialog for creating a new local directory."""

from __future__ import annotations

import os
from pathlib import Path

from PySide6 import QtCore, QtWidgets

from ibridgesgui.popup_widgets.base import UiDialogMixin
from ibridgesgui.ui_files.createCollection import Ui_createCollection


class CreateDirectory(UiDialogMixin, QtWidgets.QDialog, Ui_createCollection):
    """Popup dialog to create a new local directory."""

    ui_filename = "createCollection.ui"

    def __init__(self, parent: Path) -> None:
        """Init."""
        super().__init__()
        self._init_ui()

        self.parent = parent

        self.setWindowTitle("Create Directory")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.label.setText(f"{self.parent}{os.sep}")

        self.buttonBox.accepted.connect(self.accept)

    def accept(self) -> None:  # type: ignore[override]
        """Create the directory if it does not already exist."""
        name = self.coll_path_input.text().strip()
        if not name:
            return

        new_dir = self.parent / name
        try:
            os.makedirs(new_dir)
            self.done(1)
        except FileExistsError:
            self.error_label.setText("ERROR: Folder already exists.")
        except Exception as err:  # noqa: BLE001
            self.error_label.setText(str(getattr(err, "message", err)))

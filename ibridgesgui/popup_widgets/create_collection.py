"""Dialog for creating a new iRODS collection."""

from __future__ import annotations

from ibridges import IrodsPath
from PySide6 import QtCore, QtWidgets

from ibridgesgui.popup_widgets.base import UiDialogMixin
from ibridgesgui.ui_files.createCollection import Ui_createCollection


class CreateCollection(UiDialogMixin, QtWidgets.QDialog, Ui_createCollection):
    """Popup dialog to create a new iRODS collection."""

    ui_filename = "createCollection.ui"

    def __init__(self, parent: IrodsPath, logger) -> None:
        """Init."""
        super().__init__()
        self._init_ui()

        self.logger = logger
        self.parent = parent

        self.setWindowTitle("Create iRODS collection")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.label.setText(f"{self.parent}/")

        self.buttonBox.accepted.connect(self.accept)

    def accept(self) -> None:  # type: ignore[override]
        """Create the collection if it does not already exist."""
        name = self.coll_path_input.text().strip()
        if not name:
            return

        new_path = IrodsPath(self.parent.session, self.parent, name)
        if new_path.exists():
            self.error_label.setText(f"{new_path} already exists.")
            return

        try:
            new_path.create_collection()
            self.logger.info("Created collection %s", new_path)
            self.done(0)
        except Exception as err:  # noqa: BLE001
            self.error_label.setText(f"Could not create {new_path}: {err}")

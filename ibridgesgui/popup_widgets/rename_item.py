"""Dialog for renaming or moving an iRODS item."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from ibridges import IrodsPath
from ibridgesgui.popup_widgets.base import UiDialogMixin
from ibridgesgui.ui_files.renameItem import Ui_renameItem


class Rename(UiDialogMixin, QtWidgets.QDialog, Ui_renameItem):
    """Popup dialog to rename or move an iRODS path."""

    ui_filename = "renameItem.ui"

    def __init__(self, irods_path: IrodsPath, logger) -> None:
        """Init."""
        super().__init__()
        self._init_ui()

        self.logger = logger
        self.irods_path = irods_path

        self.setWindowTitle("Rename / Move iRODS item")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.item_path_label.setText(str(irods_path))
        self.item_path_input.setText(str(irods_path))

        self.buttonBox.accepted.connect(self.accept)

    def accept(self) -> None:  # type: ignore[override]
        """Rename or move the item."""
        new_text = self.item_path_input.text().strip()
        if not new_text:
            return

        new_path = IrodsPath(self.irods_path.session, new_text)
        if new_path.exists():
            self.error_label.setText(f"{new_path} already exists.")
            return

        try:
            new_irods_path = self.irods_path.rename(new_path)
            self.logger.info("Rename/Move %s --> %s", self.irods_path, new_irods_path)
            self.done(0)
        except Exception as err:  # noqa: BLE001
            self.error_label.setText(f"Could not create {new_path}: {err}")

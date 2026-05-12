"""Base classes shared by popup dialogs."""

from __future__ import annotations

import sys

from PySide6 import QtCore, QtGui, QtWidgets

from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui


class UiDialogMixin:    # pylint: disable=too-few-public-methods
    """Mixin that loads a Qt Designer UI file or compiled UI class."""

    ui_filename: str

    def _init_ui(self) -> None:
        """Load UI from compiled Python or from .ui file."""
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)  # type: ignore[misc]
        else:
            load_ui(UI_FILE_DIR / self.ui_filename, self)

        # Ensure all dialogs have wrapped error labels
        if hasattr(self, "error_label"):
            self.error_label.setWordWrap(True)


class TransferDialogBase(QtWidgets.QDialog):
    """Base class for dialogs that run long‑running transfers."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """Init."""
        super().__init__(parent)
        self.active_transfer = False

    # pylint: disable=invalid-name
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # noqa: N802
        """Block closing if a transfer is active."""
        thread = getattr(self, "transfer_thread", None)

        if thread and thread.isRunning():
            event.ignore()
            return

        self.active_transfer = False
        super().closeEvent(event)

    def set_wait_cursor(self) -> None:
        """Switch to a wait cursor during long operations."""
        self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    def set_arrow_cursor(self) -> None:
        """Restore the normal cursor."""
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def force_unlock(self) -> None:
        """Force the dialog out of active-transfer mode."""
        self.active_transfer = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

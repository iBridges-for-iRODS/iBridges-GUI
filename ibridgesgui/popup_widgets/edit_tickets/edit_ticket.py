"""Dialog to edit a tickets. """

import json
from pathlib import Path

from PySide6 import QtCore, QtWidgets
from ibridges import IrodsPath
from ibridges.tickets import TicketAccess
from ibridgesgui.popup_widgets.base import UiDialogMixin
from ibridgesgui.ui_files.ticketEditor import Ui_ticketEditor

class TicketEditor(UiDialogMixin, QtWidgets.QDialog, Ui_ticketEditor):
    """Popup dialog to supply a ticket."""

    ui_filename = "ticketEditor.ui"

    def __init__(self, session, logger) -> None:
        """Init."""
        super().__init__()
        self._init_ui()

        self.logger = logger
        self.session = session

        self.setWindowTitle("Edit Tickets")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.close_button.clicked.connect(self.close)



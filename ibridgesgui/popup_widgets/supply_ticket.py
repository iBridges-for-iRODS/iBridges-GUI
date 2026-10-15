"""Dialog to supply a ticket."""

from PySide6 import QtCore, QtWidgets

from ibridges import IrodsPath
from ibridges.tickets import TicketAccess
from ibridgesgui.popup_widgets.base import UiDialogMixin
from ibridgesgui.ui_files.ticketSupply import Ui_ticketSupply


class SupplyTicket(UiDialogMixin, QtWidgets.QDialog, Ui_ticketSupply):
    """Popup dialog to supply a ticket."""

    ui_filename = "ticketSupply.ui"

    def __init__(self, session_manager, logger) -> None:
        """Init."""
        super().__init__()
        self._init_ui()

        self.logger = logger
        self.session_manager = session_manager
        self._busy = False

        self.setWindowTitle("Supply Ticket")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def accept(self) -> None:
        """Add ticket to session."""
        self.error_label.clear()
        if self.irods_path.text().strip() == "":
            self.error_label.setText("Please provide an irods path.")
            return
        if self.ticket_string.text().strip() == "":
            self.error_label.setText("Please provide a ticket.")
            return

        ipath = IrodsPath(self.session_manager.session, self.irods_path.text())
        ta = TicketAccess(self.session_manager.session, self.ticket_string.text(), ipath)
        try:
            ta = TicketAccess(
                self.session_manager.session, self.ticket_string.text(), irods_path=ipath
            )
            if ipath.collection_exists():
                self.session_manager.session.home = str(ipath)
                self.session_manager.session_changed.emit(self.session_manager.session)
                self.logger.info("Supplied ticket %s with path %s", ta.ticket_str, str(ipath))
                self.done(0)
            elif ipath.dataobject_exists():
                self.session_manager.session.home = str(ipath.parent)
                self.session_manager.session_changed.emit(self.session_manager.session)
                self.logger.info("Supplied ticket %s with path %s", ta.ticket_str, str(ipath))
                self.done(0)
            else:
                raise ValueError(
                    f"Ticket {ta.ticket_str} and path {ipath} do not match, "
                    "or the path does not exist."
                )
        except ValueError as err:
            self.error_label.setText(f"{err}")
        # except Exception as err: # noqa: BLE001
        #    self.error_label.setText(f"{err}")

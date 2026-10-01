"""Dialog to create and delete tickets."""

from datetime import datetime

from PySide6 import QtCore, QtWidgets

from ibridges import IrodsPath
from ibridges.tickets import TicketData, Tickets
from ibridgesgui.irods_tree_model import IrodsTreeModel
from ibridgesgui.popup_widgets.base import UiDialogMixin
from ibridgesgui.ui_files.ticketEditor import Ui_ticketEditor


class TicketEditor(UiDialogMixin, QtWidgets.QDialog, Ui_ticketEditor):
    """Popup dialog to create and delete tickets."""

    ui_filename = "ticketEditor.ui"

    def __init__(self, session, logger) -> None:
        """Init."""
        super().__init__()
        self._init_ui()

        self.logger = logger
        self.session = session
        self.tickets = Tickets(self.session)
        self.irods_model = None

        self.setWindowTitle("Manage Tickets")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self._init_ticket_table()
        self._init_irods_tree()
        self._refresh_ticket_table()

        self.expiry_calendar.setDisabled(self.expiry_checkbox.isChecked())
        self.expiry_checkbox.toggled.connect(self.expiry_calendar.setDisabled)
        self.create_ticket_button.clicked.connect(self.create_ticket)
        self.close_button.clicked.connect(self.close)

    def _init_irods_tree(self) -> None:
        root = self._irods_root()
        self.irods_model = IrodsTreeModel(self.irods_tree_view, root)
        self.irods_tree_view.setModel(self.irods_model)
        self.irods_tree_view.expanded.connect(self.irods_model.refresh_subtree)
        self.irods_tree_view.setHeaderHidden(True)
        self.irods_model.init_tree()

        for col in (1, 2, 3, 4, 5):
            self.irods_tree_view.setColumnHidden(col, True)

        self._expand_to_home()

    def _irods_root(self):
        lowest = IrodsPath(self.session).absolute()
        while lowest.parent.exists() and str(lowest) != "/":
            lowest = lowest.parent
        return lowest

    def _expand_to_home(self) -> None:
        home_path = IrodsPath(self.session, self.session.home)
        index = self._expand_path(home_path)
        if index.isValid():
            self.irods_tree_view.setCurrentIndex(index)

    def _expand_index(self, index) -> None:
        self.irods_tree_view.expand(index)
        self.irods_model.refresh_subtree(index)

    def _expand_path(self, irods_path: IrodsPath):
        """Expand the tree down to irods_path, return the index of the deepest node found."""
        index = self.irods_model.index(0, 0)
        if not index.isValid():
            return QtCore.QModelIndex()

        self._expand_index(index)
        QtWidgets.QApplication.processEvents()

        parent_index = index
        current_path = ""
        for part in str(irods_path).strip("/").split("/"):
            current_path += "/" + part
            idx = self.irods_model.index_from_irods_path(IrodsPath(self.session, current_path))
            if not idx.isValid():
                return parent_index
            self._expand_index(idx)
            parent_index = idx

        return parent_index

    def _init_ticket_table(self) -> None:
        header = self.ticket_table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.ticket_table.setColumnWidth(3, 40)

    def _refresh_ticket_table(self) -> None:
        """Fetch the tickets from the server and fill the table."""
        self.ticket_table.setRowCount(0)
        for tick in self.tickets.fetch_tickets():
            self._add_row(tick)
        self.ticket_table.resizeColumnsToContents()

    def _add_row(self, tick: TicketData) -> None:
        row = self.ticket_table.rowCount()
        self.ticket_table.insertRow(row)

        path = str(tick.path)
        path_item = QtWidgets.QTableWidgetItem(path)
        path_item.setToolTip(path)
        expires = str(tick.expiration_date) if tick.expiration_date else "never"

        self.ticket_table.setItem(row, 0, QtWidgets.QTableWidgetItem(tick.name))
        self.ticket_table.setItem(row, 1, path_item)
        self.ticket_table.setItem(row, 2, QtWidgets.QTableWidgetItem(expires))

        # The button knows the ticket name, not its row: rows shift when tickets are deleted.
        btn = QtWidgets.QPushButton("❌")
        btn.clicked.connect(lambda _, name=tick.name: self.delete_ticket(name))
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(btn)
        layout.setContentsMargins(0, 0, 0, 0)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.ticket_table.setCellWidget(row, 3, container)

    def delete_ticket(self, ticket_name: str) -> None:
        """Delete a ticket by its name."""
        self.error_label.clear()
        try:
            self.tickets.delete_ticket(ticket_name)
            self.logger.info("Deleted ticket %s", ticket_name)
            self._refresh_ticket_table()
        except Exception as err:  # noqa: BLE001
            self.error_label.setText(str(err))
            self.logger.error("DELETE TICKET ERROR: %s", err)

    def create_ticket(self) -> None:
        """Get information from widget and create ticket."""
        self.error_label.clear()

        irods_sel = self.irods_tree_view.selectedIndexes()
        if not irods_sel:
            self.error_label.setText("Please select an iRODS path.")
            return
        irods_path = self.irods_model.irods_path_from_tree_index(irods_sel[0])
        if not irods_path.exists():
            self.error_label.setText(
                "Tree path not found in session, session and widget do not match."
            )
            return

        expiry_date = None if self.expiry_checkbox.isChecked() else self._selected_expiry()
        access_mode = "write" if self.write_button.isChecked() else "read"

        try:
            ticket, _ = self.tickets.create_ticket(irods_path, access_mode, expiry_date)
            self.logger.info("Create ticket  %s --> %s, mode %s", ticket, irods_path, access_mode)
            self._refresh_ticket_table()
        except Exception as err:  # noqa: BLE001
            self.error_label.setText(str(err))
            self.logger.error("CREATE TICKET ERROR: %s", err)

    def _selected_expiry(self) -> datetime:
        q_date = self.expiry_calendar.selectedDate()
        return datetime(q_date.year(), q_date.month(), q_date.day())

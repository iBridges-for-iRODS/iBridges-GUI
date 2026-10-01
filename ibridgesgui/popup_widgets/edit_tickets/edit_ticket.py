"""Dialog to edit a tickets. """

import json
from pathlib import Path
from datetime import datetime

from PySide6 import QtCore, QtWidgets
from ibridges import IrodsPath
from ibridges.tickets import Tickets

from ibridgesgui.popup_widgets.base import UiDialogMixin
from ibridgesgui.ui_files.ticketEditor import Ui_ticketEditor
from ibridgesgui.irods_tree_model import IrodsTreeModel

class TicketEditor(UiDialogMixin, QtWidgets.QDialog, Ui_ticketEditor):
    """Popup dialog to supply a ticket."""

    ui_filename = "ticketEditor.ui"

    def __init__(self, session, logger) -> None:
        """Init."""
        super().__init__()
        self._init_ui()

        self.setWindowTitle("Edit Tickets")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.ticket_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ticket_table.horizontalHeader().setSectionResizeMode(
            3,
            QtWidgets.QHeaderView.ResizeMode.Fixed
        )
        self.ticket_table.setColumnWidth(3, 40)

        self.logger = logger
        self.session = session
        self.tickets = Tickets(self.session)
        self.existing_tickets = self.tickets.fetch_tickets()

        self.irods_model = None

        self.create_ticket_button.clicked.connect(self.create_ticket)
        self.close_button.clicked.connect(self.close)

        self._init_irods_tree()
        self._update_tickets_table()

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

    def _expand_to_home(self):
        home_path = IrodsPath(self.session, self.session.home)
        index = self._expand_path(home_path)
        if index.isValid():
            self.irods_tree_view.setCurrentIndex(index)

    def _expand_path(self, irods_path: IrodsPath):
        parts = irods_path._path.parts[1:]
        current_path = "/" + irods_path._path.parts[0]

        index = self.irods_model.index(0, 0)
        if not index.isValid():
            return QtCore.QModelIndex()

        self.irods_tree_view.expand(index)
        self.irods_model.refresh_subtree(index)
        QtWidgets.QApplication.processEvents()

        parent_index = index

        for part in parts:
            if not part:
                continue

            current_path = current_path.rstrip("/") + "/" + part
            target = IrodsPath(self.session, current_path)

            idx = self.irods_model.index_from_irods_path(target)
            if not idx.isValid():
                return parent_index

            self.irods_tree_view.expand(idx)
            self.irods_model.refresh_subtree(idx)

            parent_index = idx

        return parent_index

    def _update_tickets_table(self) -> None:
        self.ticket_table.clearContents()
        self.ticket_table.setRowCount(0)
        for t in self.existing_tickets:
            self._add_row(t.name, str(t.path), t.expiration_date)
        self.ticket_table.resizeColumnsToContents()

    def _add_row(self, name: str, path: str, exp_date: datetime):
        row = self.ticket_table.rowCount()
        self.ticket_table.insertRow(row)
        self.ticket_table.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
        item = QtWidgets.QTableWidgetItem(path)
        item.setToolTip(path)
        self.ticket_table.setItem(row, 1, item)
        self.ticket_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(exp_date)))

        btn = QtWidgets.QPushButton("❌")
        btn.row = row  # type: ignore[attr-defined]
        btn.clicked.connect(lambda _, b=btn: self.delete_ticket(b.row))
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(btn)
        layout.setContentsMargins(0, 0, 0, 0)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.ticket_table.setCellWidget(row, 3, container)

    def delete_ticket(self, row) -> None:
        self.error_label.clear()
        item = self.ticket_table.item(row, 0)
        ticket = item.text() if item is not None else ""
        item = self.ticket_table.item(row, 1)
        path = item.text() if item is not None else ""
        try:
            self.tickets.delete_ticket(ticket)
            self.logger.info("Deleted ticket %s --> %s", ticket, path)
            self.existing_tickets = self.tickets.fetch_tickets()
            self._update_tickets_table()
        except Exception as err:
            self.error_label("%s", err)
            self.logger.error("DELETE TICKET ERROR: %s", err)
        return

    def create_ticket(self) -> None:
        """Get information from widget and create ticket."""
        q_date = self.expiry_calendar.selectedDate()
        expiry_date = datetime(q_date.year(), q_date.month(), q_date.day())

        do_not_expire = self.expiry_checkbox.isChecked()
        if do_not_expire:
            expiry_date = None
        access_mode = "write" if self.write_button.isChecked() else "read"

        irods_sel = self.irods_tree_view.selectedIndexes()
        if not irods_sel:
            self.error_label("Please select an iRODS Path.")
            return None
        irods_path = self.irods_model.irods_path_from_tree_index(irods_sel[0])
        if not irods_path.exists():
            self.error_label("Tree path not found in session, session and widget do not match.")
        try:
            ticket, _ = self.tickets.create_ticket(irods_path, access_mode, expiry_date)
            self.logger.info("Create ticket  %s --> %s, mode %s", ticket, irods_path, access_mode)
            self.existing_tickets = self.tickets.fetch_tickets()
            self._update_tickets_table()
        except Exception as err:
            self.error_label("%s", err)
            self.logger.error("CREATE TICKET ERROR: %s", err)
        return None

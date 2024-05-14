"""Provide the GUI with iRODS information."""
import sys

import PyQt6
import PyQt6.QtWidgets
import PyQt6.uic
from ibridges.resources import Resources

from ibridgesgui.config import CONFIG_DIR
from ibridgesgui.gui_utils import UI_FILE_DIR, populate_table, populate_textfield
from ibridgesgui.ui_files.tabInfo import Ui_tabInfo


class Info(PyQt6.QtWidgets.QWidget, Ui_tabInfo):
    """Set iRODS information in the GUI."""

    def __init__(self, session):
        """Initialise the tab."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi(UI_FILE_DIR / "tabInfo.ui", self)
        self.session = session

        self.refreshButton.clicked.connect(self.refresh_info)
        self.refresh_info()

    def refresh_info(self):
        """Find and set the information of the connected iRODS system."""
        self.rescTable.setRowCount(0)
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.WaitCursor))
        # irods Zone
        self.zoneLabel.setText(self.session.zone)
        # irods user
        self.userLabel.setText(self.session.username)
        # irods user type and groups
        user_type, user_groups = self.session.get_user_info()
        self.typeLabel.setText(user_type)
        populate_textfield(self.groupsBrowser, user_groups)
        # ibridges log location
        self.log_loc.setText(str(CONFIG_DIR))
        # default resource
        self.rescLabel.setText(self.session.default_resc)
        # irods server and version
        self.serverLabel.setText(self.session.host)
        self.versionLabel.setText(
            ".".join((str(num) for num in self.session.server_version)))
        # irods resources
        resc_info = Resources(self.session).root_resources
        populate_table(self.rescTable, len(resc_info[0]), resc_info)
        self.rescTable.resizeColumnsToContents()
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))

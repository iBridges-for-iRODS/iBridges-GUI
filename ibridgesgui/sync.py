"""Sync tab."""
import logging
import sys
from pathlib import Path

import PyQt6.uic
from ibridges import IrodsPath, get_collection, get_dataobject
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox

from ibridgesgui.gui_utils import (
    UI_FILE_DIR,
    populate_table,
)
from ibridgesgui.threads import DownloadThread, SearchThread
from ibridgesgui.ui_files.tabSync import Ui_tabSync

class Sync(PyQt6.QtWidgets.QWidget, Ui_tabSync):
    """SYnc view."""
    def __init__(self, session, app_name):
        """Initialise data synchronisation between iRODS and local.

        Parameters
        ----------
        session : ibridges.Session
            The iRODS session object
        app_name : str
            The name of the app and corresponding logger
        """
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi(UI_FILE_DIR / "tabSync.ui", self)

        self.logger = logging.getLogger(app_name)
        self.session = session
        self.sync_thread = None



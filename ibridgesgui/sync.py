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
from ibridgesgui.irodsTreeView import IrodsModel

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
        self.local_to_irods_button.setToolTip("Local to iRODS")
        self.irods_to_local_button.setToolTip("iRODS to Local")
        self._init_local_fs_tree()

    def _init_local_fs_tree(self):
        """Create local FS tree."""
        self.local_fs_model = QtGui.QFileSystemModel(self.local_fs_tree)
        self.local_fs_tree.setModel(self.local_fs_model)
        home_location = QtCore.QStandardPaths.standardLocations(
                        QtCore.QStandardPaths.StandardLocation.HomeLocation)[0]
        index = self.local_fs_model.setRootPath(home_location)
        self.local_fs_tree.setCurrentIndex(index)

        # hide too much information
        self.local_fs_tree.setColumnHidden(1, True)
        self.local_fs_tree.setColumnHidden(2, True)
        self.local_fs_tree.setColumnHidden(3, True)

    def _init_irods_tree(self):
        self.irods_model = IrodsModel(self.irods_tree)
        self.irods_tree.setModel(self.irods_model)
        self.irods_tree.expanded.connect(self.irods_model.refresh_subtree)
        self.irods_model.init_tree()

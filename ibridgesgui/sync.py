"""Sync tab."""
import logging
import sys

import PyQt6.uic
from ibridges import IrodsPath
from PyQt6 import QtCore, QtGui

from ibridgesgui.gui_utils import (
    UI_FILE_DIR,
)
from ibridgesgui.irods_tree_model import IrodsTreeModel
from ibridgesgui.ui_files.tabSync import Ui_tabSync


class Sync(PyQt6.QtWidgets.QWidget, Ui_tabSync):
    """Sync view."""

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
        self._init_irods_tree()

    def _init_local_fs_tree(self):
        """Create local FS tree."""
        self.local_fs_model = QtGui.QFileSystemModel(self.local_fs_tree)
        self.local_fs_tree.setModel(self.local_fs_model)
        home_location = QtCore.QStandardPaths.standardLocations(
                        QtCore.QStandardPaths.StandardLocation.HomeLocation)[0]
        index = self.local_fs_model.setRootPath(home_location)
        self.local_fs_tree.setCurrentIndex(index)

        # hide unnecessary information
        self.local_fs_tree.setColumnHidden(1, True)
        self.local_fs_tree.setColumnHidden(2, True)
        self.local_fs_tree.setColumnHidden(3, True)

    def _init_irods_tree(self):
        root = self.irods_root(IrodsPath(self.session, "~"))
        self.irods_model = IrodsTreeModel(self.irods_tree, root)
        self.irods_tree.setModel(self.irods_model)
        self.irods_tree.expanded.connect(self.irods_model.refresh_subtree)
        self.irods_model.init_tree()

        # hide unnecessary information
        self.irods_tree.setColumnHidden(1, True)
        self.irods_tree.setColumnHidden(2, True)
        self.irods_tree.setColumnHidden(3, True)
        self.irods_tree.setColumnHidden(4, True)
        self.irods_tree.setColumnHidden(5, True)

    def irods_root(self, irods_path):
        """Retrieve lowest visible level in the iRODS tree for the user."""
        lowest = IrodsPath(irods_path.session, irods_path.absolute_path())
        while lowest.parent.exists():
            lowest = IrodsPath(irods_path.session, lowest.parent)
        return lowest

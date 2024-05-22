"""Sync tab."""
import logging
import sys
from pathlib import Path

import PyQt6.uic
from ibridges import IrodsPath
from PyQt6 import QtCore, QtGui

from ibridgesgui.gui_utils import UI_FILE_DIR
from ibridgesgui.irods_tree_model import IrodsTreeModel
from ibridgesgui.ui_files.tabSync import Ui_tabSync
from ibridgesgui.popup_widgets import CreateCollection, CreateDirectory

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
        self.create_coll_button.clicked.connect(self.create_collection)
        self.create_dir_button.clicked.connect(self.create_dir)
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

    def create_collection(self):
        """Create a new collection in current collection."""
        self.error_label.clear()
        indexes = self.irods_tree.selectedIndexes()
        if len(indexes) == 0:
            self.error_label.setText("Please select a parent colection.")
            return

        parent = self.irods_model.irods_path_from_tree_index(indexes[0])
        if parent.collection_exists():
            coll_widget = CreateCollection(parent, self.logger)
            coll_widget.exec()
            self.irods_model.refresh_subtree(indexes[0])
        else:
            self.error_label.setText("Please select a parent collection, not a data object.")

    def create_dir(self):
        """Create a directory/folder on the local filesystem."""
        self.error_label.clear()
        indexes = self.local_fs_tree.selectedIndexes()
        if len(indexes) == 0:
            self.error_label.setText('Please select a parent directory.')
            return

        parent = self.local_fs_model.filePath(indexes[0])
        if Path(parent).is_dir():
            dir_widget = CreateDirectory(parent)
            dir_widget.exec()
        else:
            self.error_label.setText('Please select a parent directory, not a file.')

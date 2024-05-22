"""Sync tab."""
import logging
import sys
from pathlib import Path

import PyQt6.uic
from ibridges import IrodsPath
from PyQt6 import QtCore, QtGui

from ibridgesgui.gui_utils import UI_FILE_DIR
from ibridgesgui.irods_tree_model import IrodsTreeModel
from ibridgesgui.popup_widgets import CreateCollection, CreateDirectory
from ibridgesgui.threads import SyncThread
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
        self.sync_source = "" #irods or local
        self.refresh_irods_index = None
        self.local_to_irods_button.setToolTip("Local to iRODS")
        self.local_to_irods_button.clicked.connect(self.local_to_irods)
        self.irods_to_local_button.setToolTip("iRODS to Local")
        self.irods_to_local_button.clicked.connect(self.irods_to_local)
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
            self.error_label.setText("Please select a parent directory.")
            return

        parent = self.local_fs_model.filePath(indexes[0])
        if Path(parent).is_dir():
            dir_widget = CreateDirectory(parent)
            dir_widget.exec()
        else:
            self.error_label.setText("Please select a parent directory, not a file.")

    def prep_sync(self, dry_run = True):
        """Prepare and call the sync thread."""
        paths = self._gather_info_for_transfer()
        if paths is None:
            return
        local_path, irods_path, _, _ = paths

        if self.sync_source == "local":
            if not dry_run:
                # updating data in iRODS --> save index to update tree
                _, _, _, self.refresh_irods_index = paths
            self.logger.info("Starting sync from %s to %s.", str(local_path), str(irods_path))
            self.status_browser.append(
                f"Starting sync from {str(local_path)} to {str(irods_path)}.")
            self._start_sync(self.session, self.logger, local_path, irods_path,
                                dry_run=dry_run)
        else:
            self.logger.info("Starting sync from %s to %s.", str(local_path), str(irods_path))
            self.status_browser.append(
                f"Starting sync from {str(local_path)} to {str(irods_path)}.")
            self._start_sync(self.session, self.logger, irods_path, local_path,
                                dry_run=dry_run)

    def local_to_irods(self):
        """Start sync from local to irods."""
        self.sync_source = "local"
        self.prep_sync()

    def irods_to_local(self):
        """Start sync from irods to local."""
        self.sync_source = "irods"
        self.prep_sync()

    def _gather_info_for_transfer(self):
        self.error_label.clear()
        self.status_browser.clear()
        # Retrieve local fs path
        fs_selection = self.local_fs_tree.selectedIndexes()
        if len(fs_selection) == 0:
            self.error_label.setText("Please select a directory.")
            return None
        fs_index = fs_selection[0]
        local_path = Path(self.local_fs_model.filePath(fs_index))
        if local_path.is_file():
            self.error_label.setText("Please select a directory, not a file.")
            return None

        # Retrieve irods path
        irods_selection = self.irods_tree.selectedIndexes()
        if len(irods_selection) == 0:
            self.error_label.setText("Please select a collection.")
            return None
        irods_index = irods_selection[0]
        irods_path = self.irods_model.irods_path_from_tree_index(irods_index)
        if irods_path.dataobject_exists():
            self.error_label.setText("Please select a collection, not a data object.")
            return None

        return local_path, irods_path, fs_index, irods_index

    def _enable_buttons(self, enable):
        self.local_to_irods_button.setEnabled(enable)
        self.irods_to_local_button.setEnabled(enable)
        self.create_coll_button.setEnabled(enable)
        self.create_dir_button.setEnabled(enable)

    def _start_sync(self, session, logger, source, target, dry_run):
        self.error_label.clear()
        self.status_browser.clear()
        self._enable_buttons(False)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))

        if dry_run:
            self.error_label.setText("Calculating differences ....")
        else:
            self.error_label.setText(f"Synchronising from {source} to {target} ....")
            print(f"Synchronising from {source} to {target} ....")
        self.sync_thread = SyncThread(session, logger, source, target, dry_run)
        self.sync_thread.succeeded.connect(self._sync_end)
        self.sync_thread.finished.connect(self._finish_sync)
        self.sync_thread.start()

    def _finish_sync(self):
        self._enable_buttons(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        if self.sync_thread:
            del self.sync_thread

    def _sync_end(self, thread_output: dict):
        if thread_output["error"] != "":
            self.error_label.setText(thread_output["error"])
            self.sync_source = ""
            self.refresh_irods_index = None
        elif "result" in thread_output:
            self.error_label.clear()
            self.status_browser.append("Sync preview")
            info = ''
            for key in thread_output["result"]:
                info += "\n".join([str(i) for i in thread_output["result"][key]])
            if info == '':
                info = "Data is already synchronised."
                self.sync_source = ""
                self.refresh_irods_index = None
            self.status_browser.append(info)
        else:
            self.error_label.setText("Synchronisation finished successfully.")
            self.sync_source = ""
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        if self.refresh_irods_index is not None:
            self.irods_model.refresh_subtree(self.refresh_irods_index)

        # real sync if necessary
        if self.sync_source != "":
            msg = "Do you want to synchronise the data?"
            reply = PyQt6.QtWidgets.QMessageBox.question(
                self, "Message", msg,
                PyQt6.QtWidgets.QMessageBox.StandardButton.Yes,
                PyQt6.QtWidgets.QMessageBox.StandardButton.No)
            if reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
                self.prep_sync(dry_run=False)

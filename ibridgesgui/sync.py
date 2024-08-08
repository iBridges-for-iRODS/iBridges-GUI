"""Sync tab."""

import logging
import sys
from pathlib import Path

import PyQt6.uic
from ibridges import IrodsPath
from PyQt6 import QtCore, QtGui

from ibridgesgui.gui_utils import UI_FILE_DIR, populate_table, prep_session_for_copy
from ibridgesgui.irods_tree_model import IrodsTreeModel
from ibridgesgui.popup_widgets import CreateCollection, CreateDirectory
from ibridgesgui.threads import SyncThread, TransferDataThread
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

        # globals for starting diff and sync
        self.sync_diff_thread = None
        self.sync_data_thread = None
        self.sync_source = ""  # irods or local
        self.refresh_irods_index = None
        self.diffs = None  # output of dry_run

        # widget memeber and their functionlity
        self.local_to_irods_button.setToolTip("Local to iRODS")
        self.local_to_irods_button.clicked.connect(self.local_to_irods)
        self.irods_to_local_button.setToolTip("iRODS to Local")
        self.irods_to_local_button.clicked.connect(self.irods_to_local)
        self.create_coll_button.clicked.connect(self.create_collection)
        self.create_dir_button.clicked.connect(self.create_dir)
        self.sync_button.hide()
        self.sync_button.clicked.connect(self._start_data_sync)
        self._init_local_fs_tree()
        self._init_irods_tree()

    def _init_local_fs_tree(self):
        """Create local FS tree."""
        self.local_fs_model = QtGui.QFileSystemModel(self.local_fs_tree)
        self.local_fs_tree.setModel(self.local_fs_model)
        home_location = QtCore.QStandardPaths.standardLocations(
            QtCore.QStandardPaths.StandardLocation.HomeLocation
        )[0]
        index = self.local_fs_model.setRootPath(home_location)
        self.local_fs_tree.setCurrentIndex(index)

        # hide unnecessary information
        self.local_fs_tree.setColumnHidden(1, True)
        self.local_fs_tree.setColumnHidden(2, True)
        self.local_fs_tree.setColumnHidden(3, True)

    def _init_irods_tree(self):
        root = self.irods_root()
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

    def irods_root(self):
        """Retrieve lowest visible level in the iRODS tree for the user."""
        lowest = IrodsPath(self.session).absolute()
        while lowest.parent.exists() and str(lowest) != "/":
            lowest = lowest.parent
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

    def sync_diff(self):
        """Prepare and call the sync thread to calculate diffs."""
        paths = self._gather_info_for_transfer()
        if paths is None:
            return
        local_path, irods_path, _, _ = paths

        # User info
        self.error_label.setText("Calculating difference ...")
        if self.sync_source == "local":
            self.logger.info(
                "Calculating difference from %s to %s", str(local_path), str(irods_path)
            )
        else:
            self.logger.info(
                "Calculating difference from %s to %s", str(irods_path), str(local_path)
            )

        # start sync thread
        if self.sync_source == "local":
            self._start_sync_diff(local_path, irods_path)
        else:
            self._start_sync_diff(irods_path, local_path)

    def local_to_irods(self):
        """Start sync from local to irods."""
        self.sync_source = "local"
        self.sync_diff()

    def irods_to_local(self):
        """Start sync from irods to local."""
        self.sync_source = "irods"
        self.sync_diff()

    def _gather_info_for_transfer(self):
        self.error_label.clear()
        self.diff_table.setRowCount(0)
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
        self.refresh_irods_index = irods_index
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

    def _start_data_sync(self):
        self._enable_buttons(False)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        self.error_label.setText("Synchronising data ....")

        env_path = prep_session_for_copy(self.session, self.error_label)
        if env_path is None:
            return
        try:
            self.sync_data_thread = TransferDataThread(
                env_path, self.logger, self.diffs, overwrite=True
            )
        except Exception as err:
            self.error_label.setText(
                    f"Could not instantiate a new session from{env_path}: {err}"
            )
            return

        self.sync_data_thread.current_progress.connect(self._sync_data_status)
        self.sync_data_thread.succeeded.connect(self._sync_data_end)
        self.sync_data_thread.finished.connect(self._finish_sync_data)
        self.sync_data_thread.start()

    def _start_sync_diff(self, source, target):
        self.sync_button.hide()
        self.error_label.clear()
        self.diff_table.setRowCount(0)
        self._enable_buttons(False)
        self.progress_bar.setValue(0)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))

        self.error_label.setText("Calculating differences ....")

        # check if session comes from env file in ibridges config
        env_path = prep_session_for_copy(self.session, self.error_label)
        if env_path is None:
            return
        try:
            self.sync_diff_thread = SyncThread(env_path, self.logger, source, target, dry_run=True)
        except Exception:
            self.error_label.setText(
                f"Could not instantiate a new session from{env_path}.Check configuration."
            )

            return
        self.sync_diff_thread.succeeded.connect(self._sync_diff_end)
        self.sync_diff_thread.finished.connect(self._finish_sync_diff)
        self.sync_diff_thread.start()

    def _finish_sync_diff(self):
        self._enable_buttons(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        if self.sync_diff_thread:
            del self.sync_diff_thread

    def _finish_sync_data(self):
        self._enable_buttons(True)
        self.sync_button.hide()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        if self.sync_data_thread:
            del self.sync_data_thread

    def _sync_data_end(self, thread_output: dict):
        if thread_output["error"] != "":
            self.error_label.setText(thread_output["error"])
            self.sync_source = ""
            self.refresh_irods_index = None
            return
        self.error_label.clear()

        if self.refresh_irods_index is not None:
            self.irods_model.refresh_subtree(self.refresh_irods_index)
        self.error_label.setText("Data synchronisation complete.")

    def _sync_data_status(self, state):
        up_size, transferred_size, obj_count, num_objs, obj_failed = state
        self.progress_bar.setValue(int(transferred_size*100/up_size))
        text = f"{obj_count} of {num_objs} files; failed: {obj_failed}."
        self.error_label.setText(text)

    def _sync_diff_end(self, thread_output: dict):
        if thread_output["error"] != "":
            self.error_label.setText(thread_output["error"])
            self.sync_source = ""
            self.refresh_irods_index = None
            return

        self.error_label.clear()

        table_data = [
            (source, dest, source.size if isinstance(source, IrodsPath) else source.stat().st_size)
            for source, dest in thread_output["result"].upload + thread_output["result"].download
        ]
        populate_table(self.diff_table, len(table_data), table_data)
        if len(table_data) == 0:
            self.error_label.setText("Data is already synchronised.")
            self.sync_source = ""
            self.refresh_irods_index = None
        else:
            self.diffs = thread_output["result"]
            self.sync_button.show()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

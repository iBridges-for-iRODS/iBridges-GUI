"""GUI logic for sync tab."""
from pathlib import Path

from ibridges import IrodsPath
from PySide6 import QtCore, QtWidgets

from ibridgesgui.gui_utils import get_last_ienv_path, prep_session_for_copy
from ibridgesgui.irods_tree_model import IrodsTreeModel
from ibridgesgui.popup_widgets import CreateCollection, CreateDirectory
from ibridgesgui.threads import SyncThread, TransferDataThread

from .sync_model import SyncModel


class SyncController:
    """Controller for the Sync tab."""

    def __init__(self, view, session, app_name):
        """Init."""
        self.view = view
        self.session = session
        self.logger = __import__("logging").getLogger(app_name)

        self.model = SyncModel()

        self.sync_diff_thread = None
        self.sync_data_thread = None

        self._last_update = 0

        self.local_fs_model = None
        self.irods_model = None
        self.init_sync()


    # ----------------------------------------------------------------------
    # Initialization
    # ----------------------------------------------------------------------

    def init_sync(self):
        """Init GUI elements."""
        self._init_local_fs_tree()
        self._init_irods_tree()
        self._connect_signals()

        self.view.sync_button.hide()
        self.view.local_to_irods_button.setToolTip("Local to iRODS")
        self.view.irods_to_local_button.setToolTip("iRODS to Local")

    # ----------------------------------------------------------------------
    # Tree initialization
    # ----------------------------------------------------------------------

    def _init_local_fs_tree(self):
        self.local_fs_model = QtWidgets.QFileSystemModel(self.view.local_fs_tree)
        self.view.local_fs_tree.setModel(self.local_fs_model)

        home = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.HomeLocation)
        index = self.local_fs_model.setRootPath(home)
        self.view.local_fs_tree.setCurrentIndex(index)

        for col in (1, 2, 3):
            self.view.local_fs_tree.setColumnHidden(col, True)

    def _init_irods_tree(self):
        root = self._irods_root()
        self.irods_model = IrodsTreeModel(self.view.irods_tree, root)
        self.view.irods_tree.setModel(self.irods_model)
        self.view.irods_tree.expanded.connect(self.irods_model.refresh_subtree)
        self.irods_model.init_tree()

        for col in (1, 2, 3, 4, 5):
            self.view.irods_tree.setColumnHidden(col, True)

        self._expand_to_home()

    def _irods_root(self):
        lowest = IrodsPath(self.session).absolute()
        while lowest.parent.exists() and str(lowest) != "/":
            lowest = lowest.parent
        return lowest

    # ----------------------------------------------------------------------
    # Expand tree to home
    # ----------------------------------------------------------------------

    def _expand_to_home(self):
        home_path = IrodsPath(self.session, self.session.home)
        index = self._expand_path(home_path)
        if index.isValid():
            self.view.irods_tree.setCurrentIndex(index)

    # ----------------------------------------------------------------------
    # Signal wiring
    # ----------------------------------------------------------------------

    def _connect_signals(self):
        self.view.local_to_irods_button.clicked.connect(self.local_to_irods)
        self.view.irods_to_local_button.clicked.connect(self.irods_to_local)
        self.view.create_coll_button.clicked.connect(self.create_collection)
        self.view.create_dir_button.clicked.connect(self.create_dir)
        self.view.sync_button.clicked.connect(self._start_data_sync)

    # ----------------------------------------------------------------------
    # UI actions
    # ----------------------------------------------------------------------

    def create_collection(self):
        """Call widget to create collection."""
        self.view.clear_error()
        indexes = self.view.irods_tree.selectedIndexes()
        if not indexes:
            self.view.show_error("Please select a parent collection.")
            return

        parent = self.irods_model.irods_path_from_tree_index(indexes[0])
        if parent.collection_exists():
            dlg = CreateCollection(parent, self.logger)
            dlg.exec()
            self.irods_model.refresh_subtree(indexes[0])
        else:
            self.view.show_error("Please select a collection, not a data object.")

    def create_dir(self):
        """Call widget to create directory."""
        self.view.clear_error()
        indexes = self.view.local_fs_tree.selectedIndexes()
        if not indexes:
            self.view.show_error("Please select a parent directory.")
            return

        parent = Path(self.local_fs_model.filePath(indexes[0]))
        if parent.is_dir():
            dlg = CreateDirectory(parent)
            dlg.exec()
        else:
            self.view.show_error("Please select a directory, not a file.")

    # ----------------------------------------------------------------------
    # Sync direction
    # ----------------------------------------------------------------------

    def local_to_irods(self):
        """Set sync direction from local to irods."""
        self.model.sync_source = "local"
        self._sync_diff()

    def irods_to_local(self):
        """Set sync direction from irods to local."""
        self.model.sync_source = "irods"
        self._sync_diff()

    # ----------------------------------------------------------------------
    # Diff calculation
    # ----------------------------------------------------------------------

    def _sync_diff(self):
        info = self._gather_paths()
        if info is None:
            return

        local_path, irods_path, _, irods_index = info
        self.model.refresh_irods_index = irods_index

        source, target = (
            (local_path, irods_path)
            if self.model.sync_source == "local"
            else (irods_path, local_path)
        )

        self._start_sync_diff(source, target)


    def _gather_paths(self):
        self.view.clear_error()
        self.view.clear_diff_table()

        # Local
        fs_sel = self.view.local_fs_tree.selectedIndexes()
        if not fs_sel:
            self.view.show_error("Please select a directory.")
            return None

        local_path = Path(self.local_fs_model.filePath(fs_sel[0]))
        if local_path.is_file():
            self.view.show_error("Please select a directory, not a file.")
            return None

        # iRODS
        irods_sel = self.view.irods_tree.selectedIndexes()
        if not irods_sel:
            self.view.show_error("Please select a collection.")
            return None

        irods_path = self.irods_model.irods_path_from_tree_index(irods_sel[0])
        if irods_path.dataobject_exists():
            self.view.show_error("Please select a collection, not a data object.")
            return None

        self.model.set_paths(local_path, irods_path, irods_sel[0])
        return local_path, irods_path, fs_sel[0], irods_sel[0]


    def _start_sync_diff(self, source, target):
        self.view.hide_sync_button()
        self.view.clear_error()
        self.view.clear_diff_table()
        self.view.update_progress(0)

        self.view.set_ui_busy(True)
        self.view.show_error("Calculating differences...")

        env_path = prep_session_for_copy(self.session, self.view.error_label)
        if env_path is None:
            self._finish_sync_diff()
            return

        self.sync_diff_thread = SyncThread(env_path, self.logger, source, target, dry_run=True)
        self.sync_diff_thread.result.connect(self._sync_diff_end)
        self.sync_diff_thread.finished.connect(self._finish_sync_diff)
        self.sync_diff_thread.start()


    def _sync_diff_end(self, output):
        self.view.clear_error()
        if output["error"]:
            self.view.show_error(output["error"])
            self.model.clear()
            return

        self.model.diffs = output["result"]

        rows = [
            (src, dst, src.size if isinstance(src, IrodsPath) else src.stat().st_size)
            for src, dst in self.model.diffs.upload + self.model.diffs.download
        ]

        self.view.display_diff_rows(rows)

        if not rows:
            self.view.show_error("Nothing to synchronise — everything is already up to date.")
            self.model.clear()
        else:
            self.view.show_sync_button()


    def _finish_sync_diff(self):
        self.view.set_ui_busy(False)
        self.sync_diff_thread = None

    # ----------------------------------------------------------------------
    # Data sync
    # ----------------------------------------------------------------------

    def _start_data_sync(self):
        self.view.set_ui_busy(True)
        self.view.show_error("Synchronising data...")

        env_path = Path(get_last_ienv_path())
        if not env_path.exists():
            self.view.show_error("Could not find iRODS environment file.")
            self._finish_sync_data()
            return

        self.sync_data_thread = TransferDataThread(
            env_path, self.logger, self.model.diffs, overwrite=True
        )

        self.sync_data_thread.current_progress.connect(self._sync_data_status)
        self.sync_data_thread.result.connect(self._sync_data_end)
        self.sync_data_thread.finished.connect(self._finish_sync_data)
        self.sync_data_thread.start()

    @QtCore.Slot(list)
    def _sync_data_status(self, state):
        now = QtCore.QTime.currentTime().msecsSinceStartOfDay()
        if now - self._last_update < 100:
            return
        self._last_update = now

        up_size, transferred, count, total, failed, _ = state
        percent = int(transferred * 100 / up_size) if up_size else 0

        self.view.update_progress(percent)
        self.view.show_error(f"{count} of {total} files; failed: {failed}.")

    def _sync_data_end(self, output):
        if output["error"]:
            self.view.show_error(output["error"])
            self.model.clear()
            return

        # Check if there was actually anything to sync
        if self.model.diffs and not self.model.diffs.upload and not self.model.diffs.download:
            self.view.show_error("Nothing to synchronise.")
        else:
            if self.model.refresh_irods_index is not None:
                self.irods_model.refresh_subtree(self.model.refresh_irods_index)
            self.view.show_error("Data synchronisation complete.")

        self.model.clear()

    def _finish_sync_data(self):
        self.view.sync_button.hide()
        self.view.set_ui_busy(False)
        self.sync_data_thread = None

    # ----------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------

    # pylint: disable=W0212
    def _expand_path(self, irods_path: IrodsPath):
        parts = irods_path._path.parts[1:]
        current_path = "/" + irods_path._path.parts[0]

        index = self.irods_model.index(0, 0)
        if not index.isValid():
            return QtCore.QModelIndex()

        self.view.irods_tree.expand(index)
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

            self.view.irods_tree.expand(idx)
            self.irods_model.refresh_subtree(idx)

            parent_index = idx

        return parent_index

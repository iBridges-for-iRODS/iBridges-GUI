"""Search tab."""

import logging
import sys
from pathlib import Path

import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets
from ibridges import IrodsPath, download
from ibridges.search import MetaSearch

from ibridgesgui.config import get_last_ienv_path, is_session_from_config
from ibridgesgui.gui_utils import UI_FILE_DIR, append_table, combine_operations, load_ui
from ibridgesgui.threads import SearchThread, TransferDataThread
from ibridgesgui.ui_files.tabSearch import Ui_tabSearch


class Search(PySide6.QtWidgets.QWidget, Ui_tabSearch):
    """Search view."""

    def __init__(self, session, app_name, browser):
        """Initialize an iRODS search view.

        This tab is linked to the browser tab. When double-clicking one of
        the results the path will be loaded into the browser of the browser tab.

        Parameters
        ----------
        session : ibridges.Session
            The iRODS session object
        app_name : str
            The name of the app and corresponding logger
        browser : PyQt6.QtWidgets.QWidget
            The browser widget

        """
        super().__init__()
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabSearch.ui", self)

        self.logger = logging.getLogger(app_name)
        self.session = session
        self.results = None
        self.current_batch_num = 0  # number of batches of 50; loading results
        self.browser = browser
        self.search_thread = None
        self.download_thread = None

        self.hide_result_elements()
        self.load_more_button.clicked.connect(self.next_batch)
        self.search_button.clicked.connect(self.search)
        self.clear_button.clicked.connect(self.hide_result_elements)
        self.download_button.clicked.connect(self.download)
        self.select_all_box.clicked.connect(self.select_all)

        # group textfields for gathering key, value, unit
        self.meta_fields = [
            (self.key1, self.val1, self.units1),
            (self.key2, self.val2, self.units2),
            (self.key3, self.val3, self.units3),
            (self.key4, self.val4, self.units4),
        ]
        self.search_path_field.setText(self.session.home)
        self.search_table.doubleClicked.connect(self.send_to_browser)

    def hide_result_elements(self):
        """Hide the GUI elemnts that show and manipulate search results."""
        self.error_label.clear()
        self.search_table.hide()
        self.download_button.hide()
        self.select_all_box.hide()
        self.load_more_button.hide()
        self.clear_button.hide()
        self.search_table.setRowCount(0)

    def show_result_elements(self):
        """Show the GUI elemnts that show and manipulate search results."""
        self.search_table.show()
        self.select_all_box.show()
        self.download_button.show()
        self.clear_button.show()

    def search(self):
        """Validate search parameters and start search."""
        self.hide_result_elements()
        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.WaitCursor))
        self.error_label.clear()
        self.current_batch_num = 0
        self.results = None
        case_sensitive = self.case_sensitive_box.isChecked()

        msg, search_path, path_pattern, meta_searches, checksum = self._validate_search_params()
        self.logger.debug(
            "Search parameters %s, %s, %s, %s, %s, %s",
            msg,
            str(search_path),
            path_pattern,
            str(meta_searches),
            checksum,
            str(case_sensitive),
        )
        if msg is not None:
            self.error_label.setText(msg)
            self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))
            return

        self._start_search(search_path, path_pattern, meta_searches, checksum, case_sensitive)

    def next_batch(self):
        """Load next batch of results."""
        self.load_results(batch_size=25)

    def load_results(self, batch_size=25):
        """Load seach results into the table view."""
        self.error_label.clear()
        table_data = []  # (Path, Name, Size, Checksum, created, modified)
        start = self.current_batch_num * batch_size
        end = min((self.current_batch_num + 1) * 25, len(self.results))
        for ipath in self.results[start:end]:
            ipath = IrodsPath(self.session, str(ipath))
            if ipath.dataobject_exists():
                table_data.append(
                    (
                        "-d",
                        str(ipath),
                        ipath.size,
                        ipath.dataobject.create_time.strftime("%d-%m-%Y"),
                        ipath.dataobject.modify_time.strftime("%d-%m-%Y"),
                    )
                )
            else:
                table_data.append(
                    (
                        "-C",
                        str(ipath),
                        "",
                        ipath.collection.create_time.strftime("%d-%m-%Y"),
                        ipath.collection.modify_time.strftime("%d-%m-%Y"),
                    )
                )
        self.current_batch_num = self.current_batch_num + 1
        append_table(self.search_table, self.search_table.rowCount(), table_data)

        if len(self.results) > batch_size * self.current_batch_num:
            self.load_more_button.show()
            self.load_more_button.setText(f"Load next {batch_size} of {len(self.results)} results.")
        else:
            self.load_more_button.hide()

    def select_all(self):
        """Download all search results."""
        if self.select_all_box.isChecked():
            for row in range(self.search_table.rowCount()):
                cur_sel_rows = [idx.row() for idx in self.search_table.selectedIndexes()]
                if row not in cur_sel_rows:
                    self.search_table.selectRow(row)
        else:
            self.search_table.clearSelection()

    def download(self):
        """Determine iRODS paths, select destination and start download."""
        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.WaitCursor))
        self.error_label.clear()
        irods_paths = self._retrieve_selected_paths()
        print(irods_paths)
        if len(irods_paths) == 0:
            self.error_label.setText("No data selected.")
            self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))
        select_dir = Path(
            PySide6.QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Directory", dir=str(Path("~").expanduser())
            )
        )
        if str(select_dir) == "" or str(select_dir) == ".":
            self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        info = f"Download to: {select_dir}\n"

        data_exists = [(ipath, select_dir.joinpath(ipath.name).exists()) for ipath in irods_paths]
        overwrite = False

        if any(exists for _, exists in data_exists):
            button_reply = PySide6.QtWidgets.QMessageBox.question(
                self,
                "Message Box",
                info + f"Some data already exists in {select_dir}." + "\nOverwrite data?",
            )
        else:
            button_reply = PySide6.QtWidgets.QMessageBox.question(self, "Message Box", info)

        if button_reply == PySide6.QtWidgets.QMessageBox.StandardButton.Yes:
            overwrite = True
            self._start_download(irods_paths, select_dir, overwrite)
        else:
            self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))
            return

    def send_to_browser(self):
        """Set browser input_path to collection or parent of object."""
        row = self.search_table.currentIndex().row()
        irods_path = IrodsPath(self.session, self.search_table.item(row, 1).text())
        if irods_path.collection_exists():
            self.browser.input_path.setText(str(irods_path))
            self.error_label.setText(f"Browser tab switched to {irods_path}")
        else:
            self.browser.input_path.setText(str(irods_path.parent))
            self.error_label.setText(f"Browser tab switched to {irods_path.parent}")
        self.browser.load_browser_table()

    def _validate_search_params(self) -> tuple[IrodsPath, str, dict, str, str]:
        meta_searches = []
        meta_triples = [(k.text(), v.text(), u.text()) for k, v, u in self.meta_fields]
        for key, value, units in meta_triples:
            if key != "" or value != "" or units != "":
                if key == "":
                    key = "%"
                if value == "":
                    value = "%"
                if units == "":
                    units = "%"
                meta_searches.append(MetaSearch(key, value, units))

        search_path = IrodsPath(self.session, self.search_path_field.text())
        path_pattern = (
            self.path_pattern_field.text() if self.path_pattern_field.text() != "" else None
        )
        checksum = self.checksum_field.text() if self.checksum_field.text() != "" else None
        if not search_path.collection_exists():
            msg = f"Search in {str(search_path)}: Collection dos not exist."
            return msg, search_path, path_pattern, meta_searches, checksum
        if len(meta_searches) == 0 and path_pattern is None and checksum is None:
            msg = "Please provide some search criteria."
            return msg, search_path, path_pattern, meta_searches, checksum
        return None, search_path, path_pattern, meta_searches, checksum

    def _retrieve_selected_paths(self) -> list[IrodsPath]:
        """Retrieve paths from all selected rows in search results table."""
        irods_paths = []
        rows = set(idx.row() for idx in self.search_table.selectedIndexes())
        for row in rows:
            irods_paths.append(IrodsPath(self.session, self.search_table.item(row, 1).text()))
        return irods_paths

    def _start_download(self, irods_paths, folder, overwrite):
        self.download_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.select_all_box.setEnabled(False)
        self.search_button.setEnabled(False)
        # check if session comes from env file in ibridges config
        if is_session_from_config(self.session):
            env_path = Path("~").expanduser().joinpath(".irods", get_last_ienv_path())
        else:
            text = "No download possible: The ibridges config changed during the session."
            text += " Please reset or restart the session."
            self.error_label.setText(text)
            return

        # get diff dictionary
        single_ops = []
        for ipath in irods_paths:
            single_ops.append(download(self.session, ipath, folder, overwrite=True, dry_run=True))
        ops = combine_operations(single_ops)

        self.error_label.setText(f"Downloading to {folder} ....")
        try:
            self.download_thread = TransferDataThread(
                env_path, self.logger, ops, overwrite=overwrite
            )
        except Exception as err:
            self.error_label.setText(
                f"Could not instantiate a new session from {env_path}: {repr(err)}."
            )
            self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        self.download_thread.result.connect(self._download_fetch_result)
        self.download_thread.finished.connect(self._finish_download)
        self.download_thread.current_progress.connect(self._download_status)
        self.download_thread.start()

    def _finish_download(self):
        self.download_button.setEnabled(True)
        self.select_all_box.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))
        del self.download_thread

    def _download_status(self, state):
        _, _, obj_count, num_objs, obj_failed = state
        text = f"{obj_count} of {num_objs} files; failed: {obj_failed}."
        self.error_label.setText(text)

    def _download_fetch_result(self, thread: dict):
        if thread["error"] == "":
            self.error_label.setText("Download finished.")
        else:
            self.error_label.setText("Errors occurred during download. Consult the logs.")
        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))

    def _start_search(self, search_path, path_pattern, meta_searches, checksum, case_sensitive):
        self.search_button.setEnabled(False)
        # check if session comes from env file in ibridges config
        if is_session_from_config(self.session):
            env_path = Path("~").expanduser().joinpath(".irods", get_last_ienv_path())
        else:
            text = "No search possible: The ibridges config changed during the session."
            text += " Please reset or restart the session."
            self.error_label.setText(text)
            return
        self.error_label.setText("Searching ...")
        try:
            self.search_thread = SearchThread(
                self.logger,
                env_path,
                search_path,
                path_pattern,
                meta_searches,
                checksum,
                case_sensitive,
            )
        except Exception:
            self.error_label.setText(
                "Could not instantiate a new session from{env_path}.Check configuration"
            )
            return
        self.search_thread.result.connect(self._fetch_results)
        self.search_thread.finished.connect(self._finish_search)
        self.search_thread.start()

    def _finish_search(self):
        self.search_button.setEnabled(True)
        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))
        del self.search_thread

    def _fetch_results(self, thread: dict):
        if "error" in thread:
            self.error_label.setText(thread["error"])
        elif len(thread["results"]) == 0:
            self.error_label.setText("No objects or collections found.")
        else:
            self.show_result_elements()
            self.results = thread["results"]
            self.load_results()

        self.setCursor(PySide6.QtGui.QCursor(PySide6.QtCore.Qt.CursorShape.ArrowCursor))

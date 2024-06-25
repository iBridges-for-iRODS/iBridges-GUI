"""Search tab."""

import logging
import sys
from pathlib import Path

import PyQt6.uic
from ibridges import IrodsPath
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox

from ibridgesgui.config import get_last_ienv_path, is_session_from_config
from ibridgesgui.gui_utils import UI_FILE_DIR, combine_diffs, populate_table
from ibridgesgui.threads import SearchThread, TransferDataThread
from ibridgesgui.ui_files.tabSearch import Ui_tabSearch


class Search(PyQt6.QtWidgets.QWidget, Ui_tabSearch):
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
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi(UI_FILE_DIR / "tabSearch.ui", self)

        self.logger = logging.getLogger(app_name)
        self.session = session
        self.browser = browser
        self.search_thread = None
        self.download_thread = None

        self.hide_result_elements()
        self.search_button.clicked.connect(self.search)
        self.clear_button.clicked.connect(self.hide_result_elements)
        self.download_button.clicked.connect(self.download)

        # group textfields for gathering key, value, unit
        self.keys = [self.key1, self.key2, self.key3, self.key4]
        self.vals = [self.val1, self.val2, self.val3, self.val4]

        self.search_table.doubleClicked.connect(self.send_to_browser)

    def hide_result_elements(self):
        """Hide the GUI elemnts that show and manipulate search results."""
        self.error_label.clear()
        self.search_table.hide()
        self.download_button.hide()
        self.clear_button.hide()
        self.info_label.hide()
        self.search_table.setRowCount(0)

    def show_result_elements(self):
        """Show the GUI elemnts that show and manipulate search results."""
        self.search_table.show()
        self.download_button.show()
        self.clear_button.show()
        self.info_label.show()

    def search(self):
        """Validate search parameters and start search."""
        self.hide_result_elements()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        self.error_label.clear()

        msg, key_vals, path, checksum = self._validate_search_params()
        if msg is not None:
            self.error_label.setText(msg)
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            return

        if key_vals is None and path is None and checksum is None:
            self.error_label.setText("No search critera given.")
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            return

        self._start_search(key_vals, path, checksum)

    def load_results(self, results):
        """Load seach results into the table view."""
        self.error_label.clear()
        table_data = []  # (Path, Name, Size, Checksum, created, modified)
        for result in results:
            if "DATA_NAME" in result:
                obj = IrodsPath(self.session, result["COLL_NAME"], result["DATA_NAME"]).dataobject

                table_data.append(
                    (
                        "-d",
                        obj.path,
                        obj.size,
                        obj.create_time.strftime("%d-%m-%Y"),
                        obj.modify_time.strftime("%d-%m-%Y"),
                    )
                )
            else:
                coll = IrodsPath(self.session, result["COLL_NAME"]).collection
                table_data.append(
                    (
                        "-C",
                        coll.path,
                        "",
                        coll.create_time.strftime("%d-%m-%Y"),
                        coll.modify_time.strftime("%d-%m-%Y"),
                    )
                )
            populate_table(self.search_table, len(table_data), table_data)

    def download(self):
        """Determine iRODS paths, select destination and start download."""
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        self.error_label.clear()
        irods_paths = self._retrieve_selected_paths()
        if len(irods_paths) == 0:
            self.error_label.setText("No data selected.")
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            return
        select_dir = Path(
            QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Directory", directory=str(Path("~").expanduser())
            )
        )
        if str(select_dir) == "" or str(select_dir) == ".":
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            return
        info = f"Download to: {select_dir}\n"

        data_exists = [(ipath, select_dir.joinpath(ipath.name).exists()) for ipath in irods_paths]
        overwrite = False

        if any(exists for _, exists in data_exists):
            button_reply = QMessageBox.question(
                self,
                "Message Box",
                info + f"Some data already exists in {select_dir}." + "\nOverwrite data?",
            )
        else:
            button_reply = QMessageBox.question(self, "Message Box", info)

        if button_reply == QMessageBox.StandardButton.Yes:
            overwrite = True
            self._start_download(irods_paths, select_dir, overwrite)
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            return

    def send_to_browser(self):
        """Set browser path_input to collection or parent of object."""
        row = self.search_table.currentIndex().row()
        irods_path = IrodsPath(self.session, self.search_table.item(row, 1).text())
        if irods_path.collection_exists():
            self.browser.path_input.setText(str(irods_path))
            self.error_label.setText(f"Browser tab switched to {irods_path}")
        else:
            self.browser.path_input.setText(str(irods_path.parent))
            self.error_label.setText(f"Browser tab switched to {irods_path.parent}")
        self.browser.load_browser_table()

    def _validate_search_params(self) -> tuple[str, dict, str, str]:
        # All metadata values need a specific key
        if any(key.text() == "" and val.text() != "" for key, val in zip(self.keys, self.vals)):
            return "There are metadata values without keys. Stop search.", None, None, None
        if all(key.text() == "" for key in self.keys):
            key_vals = None
        else:
            # Replace empty values with the wild card, turn into search key_vals
            key_vals = {
                key.text(): "%" if val.text() == "" else val.text()
                for key, val in zip(self.keys, self.vals)
            }
            if "" in key_vals:
                del key_vals[""]

        path = self.path_field.text() if self.path_field.text() != "" else None
        checksum = self.checksum_field.text() if self.checksum_field.text() != "" else None
        return None, key_vals, path, checksum

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
        diffs = combine_diffs(self.session, irods_paths, folder)

        self.error_label.setText(f"Downloading to {folder} ....")
        try:
            self.download_thread = TransferDataThread(
                env_path, self.logger, diffs, overwrite=overwrite
            )
        except Exception:
            self.error_label.setText(
                "Could not instantiate a new session from{env_path}.Check configuration"
            )
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            return
        self.download_thread.succeeded.connect(self._download_end)
        self.download_thread.finished.connect(self._finish_download)
        self.download_thread.current_progress.connect(self._download_status)
        self.download_thread.start()

    def _finish_download(self):
        self.download_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        del self.download_thread

    def _download_status(self, state):
        self.error_label.setText(state)

    def _download_end(self, thread_output: dict):
        if thread_output["error"] == "":
            self.error_label.setText("Download finished.")
        else:
            self.error_label.setText("Errors occurred during download. Consult the logs.")
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

    def _start_search(self, key_vals, path, checksum):
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
            self.search_thread = SearchThread(self.logger, env_path, path, checksum, key_vals)
        except Exception:
            self.error_label.setText(
                "Could not instantiate a new session from{env_path}.Check configuration"
            )
            return
        self.search_thread.succeeded.connect(self._fetch_results)
        self.search_thread.finished.connect(self._finish_search)
        self.search_thread.start()

    def _finish_search(self):
        self.search_button.setEnabled(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        del self.search_thread

    def _fetch_results(self, therad_output: dict):
        if "error" in therad_output:
            self.error_label.setText(therad_output["error"])
        elif len(therad_output["results"]) == 0:
            self.error_label.setText("No objects or collections found.")
        else:
            self.show_result_elements()
            self.load_results(therad_output["results"])
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

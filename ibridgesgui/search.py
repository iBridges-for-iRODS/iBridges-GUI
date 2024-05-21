"""Search tab."""
import logging
import sys
from pathlib import Path

import PyQt6.uic
from ibridges import IrodsPath, download, get_collection, get_dataobject, search_data
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox

from ibridgesgui.gui_utils import (
    UI_FILE_DIR,
    populate_table,
)
from ibridgesgui.ui_files.tabSearch import Ui_tabSearch


class Search(PyQt6.QtWidgets.QWidget, Ui_tabSearch):
    """Search view."""

    def __init__(self, session, app_name, browser):
        """Initialize an iRODS search view.

        This tab is linked to the browser tab. When double-clicking one of
        the results the path will be loaded into the broswer of the browser tab.

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

        self.hide_result_elements()
        self.searchButton.clicked.connect(self.search)
        self.clearButton.clicked.connect(self.clear)
        self.downloadButton.clicked.connect(self.download)

        #group textfields for gathering key, value, unit
        self.keys = [self.key1, self.key2, self.key3, self.key4]
        self.vals = [self.val1, self.val2, self.val3, self.val4]

        self.searchResTable.doubleClicked.connect(self.send_to_browser)

    def hide_result_elements(self):
        """Hide the GUI elemnts that show and manipulate search results."""
        self.searchResTable.hide()
        self.downloadButton.hide()
        self.clearButton.hide()
        self.info_label.hide()
        self.searchResTable.setRowCount(0)

    def show_result_elements(self):
        """Show the GUI elemnts that show and manipulate search results."""
        self.searchResTable.show()
        self.downloadButton.show()
        self.clearButton.show()
        self.info_label.show()

    def clear(self):
        """Crea search results and hide elements."""
        self.errorLabel.clear()
        self.hide_result_elements()

    def search(self):
        """Validate search parameters and search."""
        self.hide_result_elements()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        self.errorLabel.clear()

        # All metadata values need a specific key
        if any([key.text() == "" and val.text() != "" for key, val in zip(self.keys, self.vals)]):
            self.errorLabel.setText("There are metadata values without keys. Stop search.")
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            return

        if all([key.text() == "" for key in self.keys]):
            key_vals = None
        else:
            # Replace empty values with the wild card, turn into search key_vals
            key_vals = dict(zip([key.text() for key in self.keys],
                                [ "%" if val.text() == "" else val.text() for  val in self.vals]))
            del key_vals['']
        path = self.path_field.text() if self.path_field.text() != "" else None
        checksum = self.checksum_field.text() if self.checksum_field.text() != "" else None

        if key_vals is None and path is None and checksum is None:
            self.errorLabel.setText("No search critera given.")
        else:
            results = search_data(self.session, path=path, checksum=checksum, key_vals=key_vals)
            if len(results) == 0:
                self.errorLabel.setText("No objects or collections found.")
            else:
                self.show_result_elements()
                self.load_results(results)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

    def load_results(self, results):
        """Load seach results into the table view."""
        table_data = [] # (Path, Name, Size, Checksum, created, modified)
        for result in results:
            if "DATA_NAME" in result:
                obj = get_dataobject(self.session, result["COLL_NAME"]+"/"+result["DATA_NAME"])
                table_data.append(('-d', obj.path, obj.size,
                                  obj.create_time.strftime("%d-%m-%Y"),
                                  obj.modify_time.strftime("%d-%m-%Y")))
            else:
                coll = get_collection(self.session, result["COLL_NAME"])
                table_data.append(('-C', coll.path, "",
                                  coll.create_time.strftime("%d-%m-%Y"),
                                  coll.modify_time.strftime("%d-%m-%Y")))
            populate_table(self.searchResTable, len(table_data), table_data)

    def download(self):
        """Download selected data."""
        info = ""

        # Get multiple paths from table
        irods_paths = []
        for idx in self.searchResTable.selectedIndexes():
            irods_paths.append(IrodsPath(
                                    self.session,
                                    self.searchResTable.item(idx.row(), 1).text()))

        select_dir = Path(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Direcectory"))
        if select_dir == "":
            return
        else:
            info = f"Download to: {select_dir}\n"

        data_exists = [(ipath, select_dir.joinpath(ipath.name).exists()) for ipath in irods_paths]
        overwrite = False

        if any(exists for _, exists in data_exists):
            button_reply = QMessageBox.question(self, "Message Box",
                                               info+f"Some data already exists in {select_dir}."+\
                                               "\nOverwrite data?")
        else:
            button_reply = QMessageBox.question(self, "Message Box", info)

        if button_reply == QMessageBox.StandardButton.Yes:
            overwrite = True
            for ipath in irods_paths:
                if ipath.exists():
                    download(self.session, ipath, select_dir, overwrite=overwrite)
                    self.logger.info("Downloading %s to %s, overwrite %s",
                                str(ipath), select_dir, overwrite)
                else:
                    self.errorLabel.setText(f"Download failed. {str(ipath)} does not exist.")
                    self.logger.info("Download failed: %s does nor exist", str(ipath))
        self.errorLabel.setText(f"Download finished, check {select_dir}")

    def send_to_browser(self):
        """Set browser inputPath to collection or parent of object."""
        row = self.searchResTable.currentIndex().row()
        irods_path = IrodsPath(self.session, self.searchResTable.item(row, 1).text())
        if irods_path.collection_exists():
            self.browser.inputPath.setText(str(irods_path))
            self.errorLabel.setText(f"Browser tab switched to {irods_path}")
        else:
            self.browser.inputPath.setText(str(irods_path.parent))
            self.errorLabel.setText(f"Browser tab switched to {irods_path.parent}")
        self.browser.load_browser_table()

"""Search tab."""
import logging
import sys
from pathlib import Path

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialog, QMessageBox
import PyQt6.uic
from ibridges import IrodsPath, download, get_collection, get_dataobject, upload
from ibridges.data_operations import obj_replicas
from ibridges.meta import MetaData
from ibridges.permissions import Permissions
from ibridges import search_data

from ibridgesgui.gui_utils import (
    UI_FILE_DIR,
    get_coll_dict,
    get_downloads_dir,
    get_irods_item,
    populate_table,
    populate_textfield,
)

from ibridgesgui.ui_files.tabSearch import Ui_tabSearch


class Search(PyQt6.QtWidgets.QWidget, Ui_tabSearch):
    """Search view"""

    def __init__(self, session, app_name):
        """Initialize an iRODS search view."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi(UI_FILE_DIR / "tabSearch.ui", self)
        
        self.logger = logging.getLogger(app_name)
        self.session = session
        
        self.hide_result_elements()
        self.searchButton.clicked.connect(self.search)
        self.clearButton.clicked.connect(self.clear)
        
        #group textfields for gathering key, value, unit
        self.keys = [self.key1, self.key2, self.key3, self.key4]
        self.vals = [self.val1, self.val2, self.val3, self.val4]

        self.searchResTable.doubleClicked.connect(self.fill_info)

    def hide_result_elements(self):
        """Hide the GUI elemnts that show and manipulate search results."""
        self.searchResTable.hide()
        self.viewTabs.hide()
        self.downloadButton.hide()
        self.clearButton.hide()

        self.searchResTable.setRowCount(0)
        self.replicaTable.setRowCount(0)
        self.aclTable.setRowCount(0)
        self.metadataTable.setRowCount(0)

    def show_result_elements(self):
        self.viewTabs.setCurrentIndex(0)
        self.searchResTable.show()
        self.viewTabs.show()
        self.downloadButton.show()
        self.clearButton.show()

    def clear(self):
        self.errorLabel.clear()
        self.hide_result_elements()

    def search(self):
        self.hide_result_elements()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        self.errorLabel.clear()
        
        if self._check_search_params():
            # search parameters
            if not all(key == '' for key in self.keys):
                key_vals = dict(zip([key.text() for key in self.keys],
                                    [val.text() for val in self.vals]))
            else:
                key_vals = None

            path = self.path_field.text() if self.path_field.text() is not None else None
            checksum = self.checksum_field.text() if self.checksum_field.text() is not None \
                                                  else None
            print(key_vals)
            print(path)
            print(checksum)

            results = search_data(self.session, path=path, checksum=None, key_vals=None)
            print(results)
            if len(results) == 0:
                self.errorLabel.setText("No objects or collections found.")
            else: 
                self.show_result_elements()
                self.load_results(results)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

    def load_results(self, results):
        table_data = [] # (Path, Name, Size, Checksum, created, modified)
        for result in results:
            if "DATA_NAME" in result:
                obj = get_dataobject(self.session, result["COLL_NAME"]+"/"+result["DATA_NAME"])
                table_data.append((result["COLL_NAME"], result["DATA_NAME"],
                                  obj.create_time.strftime("%d-%m-%Y"),
                                  obj.modify_time.strftime("%d-%m-%Y")))
            else:
                coll_path = IrodsPath(self.session, result["COLL_NAME"])
                coll = get_collection(self.session, result["COLL_NAME"])
                table_data.append((str(coll_path.parent), coll_path.name, "",
                                  coll.create_time.strftime("%d-%m-%Y"),
                                  coll.modify_time.strftime("%d-%m-%Y")))
            populate_table(self.searchResTable, len(table_data), table_data)

    def fill_info(self):
        print("not implemented")

    def _check_search_params(self):
        for key, val in zip([key.text() for key in self.keys], [val.text() for val in self.vals]):
            if key == "" and val != "":
                self.errorLabel.setText("There are metadata values without key. Stop search.")
                return False
        return True

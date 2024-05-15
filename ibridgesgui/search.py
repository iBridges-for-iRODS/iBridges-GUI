"""Search tab."""
import logging
import sys
from pathlib import Path

import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic
from ibridges import IrodsPath, download, get_collection, get_dataobject, upload
from ibridges.data_operations import obj_replicas
from ibridges.meta import MetaData
from ibridges.permissions import Permissions

from ibridgesgui.gui_utils import (
    UI_FILE_DIR,
    get_coll_dict,
    get_downloads_dir,
    get_irods_item,
    populate_table,
    populate_textfield,
)

#from ibridgesgui.ui_files.tabSearch import Ui_tabSearch


#class Search(PyQt6.QtWidgets.QWidget, Ui_tabSearch):
class Search(PyQt6.QtWidgets.QWidget):
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


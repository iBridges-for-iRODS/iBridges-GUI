"""Pop-up widget definitions."""
import os
import sys

from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi
from PyQt6 import QtCore

import irods
from ibridges import IrodsPath

from gui.ui_files.createCollection import Ui_createCollection

class CreateCollection(QDialog, Ui_createCollection):
    """Popup window to create a new collection"""
    def __init__(self, parent):
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            loadUi("gui/ui_files/createCollection.ui", self)

        self.setWindowTitle("Create iRODS collection")
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.parent = parent
        self.label.setText(str(self.parent) + "/")
        self.buttonBox.accepted.connect(self.accept)

    def accept(self):
        """Create"""
        if self.collPathLine.text() != "":
            new_coll_path = IrodsPath(self.parent.session, self.parent,
                                    self.collPathLine.text())
            if new_coll_path.exists():
                self.errorLabel.setText(f'{new_coll_path} already exists.')
            else:
                try:
                    IrodsPath.create_collection(new_coll_path.session, new_coll_path)
                    self.done(0)
                except irods.exception.CAT_NO_ACCESS_PERMISSION:
                    self.errorLabel.setText(f'No access rights to {new_coll_path.parent}.'+\
                                            f' Cannot create {self.collPathLine.text()}.')
                except Exception as error:
                    self.errorLabel.setText(repr(error))

class CreateDirectory(QDialog, Ui_createCollection):
    """Popup window to create a new directory"""
    def __init__(self, parent):
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            loadUi("gui/ui_files/createCollection.ui", self)
        self.setWindowTitle("Create directory")
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.parent = parent
        self.label.setText(self.parent + os.sep)
        self.buttonBox.accepted.connect(self.accept)

    def accept(self):
        """Create"""
        if self.collPathLine.text() != "":
            new_dir_path = self.parent + os.sep + self.collPathLine.text()
            try:
                os.makedirs(new_dir_path)
                self.done(1)
            except Exception as error:
                if hasattr(error, 'message'):
                    self.errorLabel.setText(error.message)
                else:
                    self.errorLabel.setText("ERROR: insufficient rights.")
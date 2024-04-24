#!/usr/bin/env python3
"""iBridges GUI startup script."""
import os
import sys

import PyQt6.QtWidgets
import PyQt6.uic
import setproctitle

from ibridgesgui import ui_files
from ibridgesgui.browser import Browser
from ibridgesgui.gui_utils import UI_FILE_DIR
from ibridgesgui.info import Info
from ibridgesgui.login import Login

# Global constants
THIS_APPLICATION = 'iBridges-GUI'

# Application globals
app = PyQt6.QtWidgets.QApplication(sys.argv)
widget = PyQt6.QtWidgets.QStackedWidget()

# Work around a PRC XML issue handling special characters
os.environ['PYTHON_IRODSCLIENT_DEFAULT_XML'] = 'QUASI_XML'

class MainMenu(PyQt6.QtWidgets.QMainWindow, ui_files.MainMenu.Ui_MainWindow):
    """GUI Main Menu"""

    def __init__(self, widget):
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi(UI_FILE_DIR/'MainMenu.ui', self)

        self.ui_tabs_lookup = {
            'tabBrowser': self.init_browser_tab,
                #'tabUpDownload': self.setupTabUpDownload,
                #'tabDataBundle': self.setupTabDataBundle,
                #'tabCreateTicket': self.setupTabCreateTicket,
                #'tabELNData': self.setupTabELNData,
                #'tabAmberWorkflow': self.setupTabAmberWorkflow,
            'tabInfo': self.init_info_tab
            #'tabExample': self.setupTabExample,
        }

        self.widget = widget
        self.session = None
        self.session_dict = {}
        self.actionConnect.triggered.connect(self.connect)
        self.actionExit.triggered.connect(self.exit)
        self.actionCloseSession.triggered.connect(self.disconnect)
        self.tabWidget.setCurrentIndex(0)

    def disconnect(self):
        """Close iRODS session"""
        if 'session' in self.session_dict:
            self.session_dict['session'].close()
            self.session_dict.clear()
        self.tabWidget.clear()


    def connect(self):
        """Create iRODS session"""
        # Trick to get the session object from the QDialog
        login_window = Login(self.session_dict)
        login_window.exec()
        if 'session' in self.session_dict:
            self.session = self.session_dict['session']
            try:
                self.setup_tabs()
            except:
                self.session = None
                raise

    def exit(self):
        """Quit program"""
        quit_msg = "Are you sure you want to exit the program?"
        reply = PyQt6.QtWidgets.QMessageBox.question(
            self, 'Message', quit_msg,
            PyQt6.QtWidgets.QMessageBox.StandardButton.Yes,
            PyQt6.QtWidgets.QMessageBox.StandardButton.No)
        if reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
            sys.exit()
        else:
            pass

    def setup_tabs(self):
        """Init tab view"""
        for tab_fun in self.ui_tabs_lookup.values():
            tab_fun()
            #self.ui_tabs_lookup[tab_name]()

    def init_info_tab(self):
        """Create info"""
        self.irods_info = Info(self.session)
        self.tabWidget.addTab(self.irods_info, "Info")

    def init_browser_tab(self):
        """Create browser"""
        self.irods_browser = Browser(self.session)
        self.tabWidget.addTab(self.irods_browser, "Browser")

def main():
    """Main function"""
    # Initialize logger first because Context may want to log as well.
    application_name = THIS_APPLICATION
    setproctitle.setproctitle(application_name)
    main_app = MainMenu(widget)
    main_app.this_application = application_name
    widget.addWidget(main_app)
    widget.show()
    app.exec()


if __name__ == "__main__":
    main()

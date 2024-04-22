#!/usr/bin/env python3
"""iBridges GUI startup script.

"""
import logging
import os
import setproctitle
import sys

import irods.exception
import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic

from gui import ui_files
from gui.IrodsInfo import IrodsInfo
from gui.IrodsLogin import IrodsLogin
from gui.IrodsBrowser import IrodsBrowser
#import irodsConnector
#import utils

# Global constants
THIS_APPLICATION = 'iBridges-GUI'

# Application globals
app = PyQt6.QtWidgets.QApplication(sys.argv)
widget = PyQt6.QtWidgets.QStackedWidget()

# Work around a PRC XML issue handling special characters
os.environ['PYTHON_IRODSCLIENT_DEFAULT_XML'] = 'QUASI_XML'

class MainMenu(PyQt6.QtWidgets.QMainWindow,
               ui_files.MainMenu.Ui_MainWindow):

    def __init__(self, widget):
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi('gui/ui_files/MainMenu.ui', self)

        self.ui_tabs_lookup = {
            'tabBrowser': self.setupTabBrowser,
                #'tabUpDownload': self.setupTabUpDownload,
                #'tabDataBundle': self.setupTabDataBundle,
                #'tabCreateTicket': self.setupTabCreateTicket,
                #'tabELNData': self.setupTabELNData,
                #'tabAmberWorkflow': self.setupTabAmberWorkflow,
            'tabInfo': self.setupTabInfo
            #'tabExample': self.setupTabExample,
        }

        self.widget = widget
        self.session_dict = {}
        self.actionConnect.triggered.connect(self.connectIrods)
        self.actionExit.triggered.connect(self.programExit)
        self.actionCloseSession.triggered.connect(self.closeIrods)
        self.tabWidget.setCurrentIndex(0)

    def closeIrods(self):
        if self.session_dict != {}:
            self.session_dict['session'].close()
        self.tabWidget.clear()


    def connectIrods(self):
        # Trick to get the session object from the QDialog
        login_window = IrodsLogin(self.session_dict)
        login_window.exec()
        try:
            self.session = self.session_dict['session']
            self.setup_tabs()
        except:
            self.session = None
            raise

    def programExit(self):
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
        for uitab in self.ui_tabs_lookup:
            print(uitab)
            self.ui_tabs_lookup[uitab]()

    def setupTabInfo(self):
        self.irodsInfo = IrodsInfo(self.session)
        self.tabWidget.addTab(self.irodsInfo, "Info")

    def setupTabBrowser(self):
        self.irodsBrowser = IrodsBrowser(self.session)
        self.tabWidget.addTab(self.irodsBrowser, "Browser")

def main():
    """Main function

    """
    # Initialize logger first because Context may want to log as well.
    #utils.utils.init_logger(THIS_APPLICATION)
    #utils.utils.set_log_level()
    application_name = THIS_APPLICATION
    setproctitle.setproctitle(application_name)
    login_window = MainMenu(widget)
    login_window.this_application = application_name
    widget.addWidget(login_window)
    widget.show()
    # app.setQuitOnLastWindowClosed(False)
    #app.lastWindowClosed.connect(closeClean)
    app.exec()


if __name__ == "__main__":
    main()

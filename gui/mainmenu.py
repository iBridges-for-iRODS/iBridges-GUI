"""Main menu window definition

"""
import logging
import sys

import PyQt6
import PyQt6.QtWidgets
import PyQt6.uic

import gui
import utils


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, m):
        pass


class mainmenu(PyQt6.QtWidgets.QMainWindow,
               gui.ui_files.MainMenu.Ui_MainWindow):

    def __init__(self, widget):
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi('gui/ui_files/MainMenu.ui', self)

        # stackedWidget
        self.widget = widget
        # Menu actions
        # self.actionConnect.triggered.connect(self.connect)
        self.actionExit.triggered.connect(self.programExit)
        #self.actionCloseSession.triggered.connect(self.newSession)
            #ui_tabs_lookup = {
            #    'tabBrowser': self.setupTabBrowser,
            #    'tabUpDownload': self.setupTabUpDownload,
            #    'tabDataBundle': self.setupTabDataBundle,
            #    'tabCreateTicket': self.setupTabCreateTicket,
            #    'tabELNData': self.setupTabELNData,
            #    'tabAmberWorkflow': self.setupTabAmberWorkflow,
            #    'tabInfo': self.setupTabInfo,
            #    'tabExample': self.setupTabExample,
            #}
        self.tabWidget.setCurrentIndex(0)

    # Connect functions
    def programExit(self):
        quit_msg = "Are you sure you want to exit the program?"
        reply = PyQt6.QtWidgets.QMessageBox.question(
            self, 'Message', quit_msg,
            PyQt6.QtWidgets.QMessageBox.StandardButton.Yes,
            PyQt6.QtWidgets.QMessageBox.StandardButton.No)
        if reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
            # connector must be destroyed directly, not a reference to it.
            if self.conn:
                del self.conn
            elif self.ticketAccessTab and self.ticketAccessTab.conn:
                self.ticketAccessTab.conn.closeSession()
            sys.exit()
        else:
            pass

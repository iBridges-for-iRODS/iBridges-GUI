#!/usr/bin/env python3
"""iBridges GUI startup script."""

import logging
import sys
from pathlib import Path

import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic
import setproctitle

from ibridgesgui.browser import Browser
from ibridgesgui.config import get_log_level, init_logger, set_log_level
from ibridgesgui.info import Info
from ibridgesgui.login import Login
from ibridgesgui.logviewer import LogViewer
from ibridgesgui.popup_widgets import CheckConfig
from ibridgesgui.search import Search
from ibridgesgui.sync import Sync
from ibridgesgui.ui_files.MainMenu import Ui_MainWindow
from ibridgesgui.welcome import Welcome

# Global constants
THIS_APPLICATION = "ibridges-gui"

# Application globals
app = PyQt6.QtWidgets.QApplication(sys.argv)


class MainMenu(PyQt6.QtWidgets.QMainWindow, Ui_MainWindow):
    """Set up the GUI Main Menu."""

    def __init__(self, app_name):
        """Initialise the main window."""
        super().__init__()
        super().setupUi(self)

        app.aboutToQuit.connect(self.close_event)

        self.logger = logging.getLogger(app_name)

        self.irods_path = Path("~", ".irods").expanduser()
        self.app_name = app_name
        self.welcome_tab()
        self.ui_tabs_lookup = {
            "tabBrowser": self.init_browser_tab,
            "tabSync": self.init_sync_tab,
            "tabSearch": self.init_search_tab,
            "tabInfo": self.init_info_tab,
            "tabLog": self.init_log_tab,
        }

        self.session = None
        self.irods_browser = None
        self.session_dict = {}
        self.action_connect.triggered.connect(self.connect)
        self.action_exit.triggered.connect(self.exit)
        self.action_close_session.triggered.connect(self.disconnect)
        self.action_add_configuration.triggered.connect(self.create_env_file)
        self.action_check_configuration.triggered.connect(self.inspect_env_file)
        self.tab_widget.setCurrentIndex(0)

    def disconnect(self):
        """Close iRODS session."""
        self.error_label.clear()
        if "session" in self.session_dict:
            self.logger.info("Disconnecting %s from %s", self.session.username, self.session.host)
            self.session.close()
            self.session = None
            self.session_dict.clear()
        self.tab_widget.clear()
        self.welcome_tab()

    def connect(self):
        """Create iRODS session."""
        self.error_label.clear()
        if self.session:
            self.error_label.setText("Please close session first.")
            return

        login_window = Login(self.session_dict, self.app_name)
        login_window.exec()
        # Trick to get the session object from the QDialog

        if "session" in self.session_dict:
            self.session = self.session_dict["session"]
            try:
                self.setup_tabs()
            except:
                self.session = None
                raise
        else:
            self.logger.exception("No session created. %s", self.session_dict)

    def exit(self):
        """Quit program."""
        quit_msg = "Are you sure you want to exit the program?"
        reply = PyQt6.QtWidgets.QMessageBox.question(
            self,
            "Message",
            quit_msg,
            PyQt6.QtWidgets.QMessageBox.StandardButton.Yes,
            PyQt6.QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
            self.disconnect()
            sys.exit()
        else:
            pass

    def close_event(self):
        """Close program properly if main window is closed."""
        self.disconnect()
        sys.exit()

    def setup_tabs(self):
        """Init tab view."""
        for tab_fun in self.ui_tabs_lookup.values():
            tab_fun()
            # self.ui_tabs_lookup[tab_name]()

    def welcome_tab(self):
        """Create first tab."""
        welcome = Welcome()
        self.tab_widget.addTab(welcome, "iBridges")

    def init_info_tab(self):
        """Create info."""
        irods_info = Info(self.session)
        self.tab_widget.addTab(irods_info, "Info")

    def init_log_tab(self):
        """Create log tab."""
        ibridges_log = LogViewer(self.logger)
        self.tab_widget.addTab(ibridges_log, "Logs")

    def init_browser_tab(self):
        """Create browser."""
        self.irods_browser = Browser(self.session, self.app_name)
        self.tab_widget.addTab(self.irods_browser, "Browser")

    def init_search_tab(self):
        """Create search. Depends on Browser."""
        irods_search = Search(self.session, self.app_name, self.irods_browser)
        self.tab_widget.addTab(irods_search, "Search")

    def init_sync_tab(self):
        """Create sync."""
        irods_sync = Sync(self.session, self.app_name)
        self.tab_widget.addTab(irods_sync, "Synchronise Data")

    def create_env_file(self):
        """Populate drop down menu to create a new environment.json."""
        create_widget = CheckConfig(self.logger, self.irods_path)
        create_widget.exec()

    def inspect_env_file(self):
        """Init drop down menu to inspect an environment.json."""
        create_widget = CheckConfig(self.logger, self.irods_path)
        create_widget.exec()


def main():
    """Call main function."""
    setproctitle.setproctitle(THIS_APPLICATION)

    log_level = get_log_level()
    if log_level is not None:
        init_logger(THIS_APPLICATION, log_level)
    else:
        set_log_level("debug")
        init_logger(THIS_APPLICATION, "debug")
    main_widget = PyQt6.QtWidgets.QStackedWidget()
    main_app = MainMenu(THIS_APPLICATION)
    main_widget.addWidget(main_app)
    main_widget.show()
    app.exec()


if __name__ == "__main__":
    main()

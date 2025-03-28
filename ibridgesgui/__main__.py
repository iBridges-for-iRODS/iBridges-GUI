#!/usr/bin/env python3
"""iBridges GUI startup script."""

import logging
import os
import sys
from pathlib import Path

import PySide6.QtGui
import PySide6.QtUiTools
import PySide6.QtWidgets
import setproctitle

from ibridgesgui.browser import Browser
from ibridgesgui.config import ensure_irods_location, get_log_level, init_logger, set_log_level
from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.info import Info
from ibridgesgui.login import Login
from ibridgesgui.logviewer import LogViewer
from ibridgesgui.popup_widgets import CheckConfig
from ibridgesgui.search import Search
from ibridgesgui.sync import Sync
from ibridgesgui.ui_files.MainMenu import Ui_MainWindow
from ibridgesgui.welcome import Welcome

try:  # Python < 3.10 (backport)
    from importlib_metadata import version  # type: ignore
except ImportError:
    from importlib.metadata import version  # type: ignore [assignment]

# Global constants
THIS_APPLICATION = "ibridges-gui"

# Application globals
app = PySide6.QtWidgets.QApplication(sys.argv)


class MainMenu(PySide6.QtWidgets.QMainWindow, Ui_MainWindow):
    """Set up the GUI Main Menu."""

    def __init__(self, app_name):
        """Initialise the main window."""
        super().__init__()
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "MainMenu.ui", self)

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
        if "session" in self.session_dict:
            self.logger.info("Disconnecting %s from %s", self.session.username, self.session.host)
            self.session.close()
            self.session = None
            self.session_dict.clear()
        self.tab_widget.clear()
        self.welcome_tab()

    def connect(self):
        """Create iRODS session."""
        if self.session:
            PySide6.QtWidgets.QMessageBox.about(self, "Information", "Please close session first.")
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
        reply = PySide6.QtWidgets.QMessageBox.question(
            self,
            "Message",
            quit_msg,
            PySide6.QtWidgets.QMessageBox.StandardButton.Yes,
            PySide6.QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == PySide6.QtWidgets.QMessageBox.StandardButton.Yes:
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
        self.tab_widget.setCurrentIndex(1)

    def welcome_tab(self):
        """Create first tab."""
        try:
            release = version("ibridgesgui")
        except Exception:
            release = ""
        welcome = Welcome()
        self.tab_widget.addTab(welcome, f"iBridges {release}")

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

    # Set the working directory to the directory of the current file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ensure_irods_location()
    main_widget = PySide6.QtWidgets.QStackedWidget()
    main_app = MainMenu(THIS_APPLICATION)
    main_widget.addWidget(main_app)
    main_widget.show()
    app.exec()


if __name__ == "__main__":
    main()

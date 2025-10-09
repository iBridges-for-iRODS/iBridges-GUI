#!/usr/bin/env python3
"""iBridges GUI startup script."""

import logging
import os
import sys
from functools import partial
from pathlib import Path
from typing import Optional

import PySide6.QtGui
import PySide6.QtUiTools
import PySide6.QtWidgets
import setproctitle
from ibridges import Session

from ibridgesgui.browser import Browser
from ibridgesgui.config import (
    config_add_tab,
    config_remove_tab,
    ensure_irods_location,
    get_log_level,
    get_tabs,
    init_logger,
    set_log_level,
)
from ibridgesgui.gui_utils import UI_FILE_DIR, find_tab_provider, get_tab_providers, load_ui
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

    def __init__(self, app_name: str, session: Optional[Session] = None):
        """Initialise the main window."""
        super().__init__()
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "MainMenu.ui", self)

        app.aboutToQuit.connect(self.close_event)
        self.started_with_session = session is not None

        self.logger = logging.getLogger(app_name)
        self.irods_path = Path("~", ".irods").expanduser()
        self.app_name = app_name
        self.welcome_tab()

        # Plugin tabs
        self.prev_tabs = get_tabs()  # previously checked tabs
        self.third_party_tabs = get_tab_providers()
        self.logger.info("Third party tabs: %s", self.third_party_tabs)
        self.logger.info("Tab names: %s", [tab.name for tab in self.third_party_tabs])
        # populate Plugin/Tabs drop down
        for tab in self.third_party_tabs:
            # obj_str = str(tab).split("'")[1]
            action = PySide6.QtGui.QAction(tab.name, self.menuPlugins, checkable=True)
            if tab.name in self.prev_tabs:
                action.setChecked(True)
            action.triggered.connect(partial(self.load_and_unload_tab, widget=action))
            self.menuPlugins.addAction(action)
        # Standard tabs
        self.standard_tabs = ["Browser", "Synchronise Data", "Search", "Info", "Logs"]

        self.ui_tabs_lookup = {
            "Browser": self.init_browser_tab,
            "Synchronise Data": self.init_sync_tab,
            "Search": self.init_search_tab,
            "Info": self.init_info_tab,
            "Logs": self.init_log_tab,
        }
        for tab in self.standard_tabs:
            action = PySide6.QtGui.QAction(tab, self.menuPlugins, checkable=True)
            action.triggered.connect(partial(self.load_and_unload_tab, widget=action))
            self.menuPlugins.addAction(action)
            if tab in self.prev_tabs:
                action.setChecked(True)

        self.session = session
        self.irods_browser = None
        self.session_dict = {}
        self.action_connect.triggered.connect(self.connect)
        self.action_exit.triggered.connect(self.exit)
        self.action_close_session.triggered.connect(self.disconnect)
        self.action_add_configuration.triggered.connect(self.create_env_file)
        self.action_check_configuration.triggered.connect(self.inspect_env_file)

        if session: # login from ibridges shell or by calling main(session) from python
            try:
                self.setup_tabs()
                self.menuPlugins.setEnabled(True)
            except:
                self.session = None
                raise
        else: # show only first page and menu bar
            self.tab_widget.setCurrentIndex(0)

    def checked_tabs(self):
        """Retrieve names of checked third party tabs."""
        selected_tabs = []
        for action in self.menuPlugins.actions():
            if action.isChecked():
                selected_tabs.append(action.text())
        return selected_tabs

    def load_and_unload_tab(self, widget):
        """Load and unload a third party provider tab, triggered by drop down menu."""
        # Check if third party tab
        provider = ""
        try:
            provider = find_tab_provider(self.third_party_tabs, widget.text())
        except ValueError:
            if widget.text() in self.standard_tabs:
                provider = widget.text()
            else:
                self.logger.exception("Cannot find provider for %s", widget.text())
        # Current checked tabs
        current_tabs = {self.tab_widget.tabText(idx): idx for idx in range(self.tab_widget.count())}

        if self.session is not None:
            if widget.isChecked() and widget.text() not in current_tabs:
                # Load widget
                if widget.text() not in current_tabs:
                    if provider == "Browser":
                        self.init_browser_tab()
                    elif provider == "Synchronise Data":
                        self.init_sync_tab()
                    elif provider == "Search":
                        self.init_search_tab()
                    elif provider == "Info":
                        self.init_info_tab()
                    elif provider == "Logs":
                        self.init_log_tab()
                    elif provider in self.third_party_tabs:
                        self.init_third_party_tab(provider)
                    config_add_tab(widget.text())
            else:
                if widget.text() in current_tabs:
                    self.remove_tab(current_tabs[widget.text()])
                    config_remove_tab(provider)

    def disconnect(self):
        """Close iRODS session."""
        if "session" in self.session_dict:
            self.logger.info("Disconnecting %s from %s", self.session.username, self.session.host)
            self.session.close()
            self.session = None
            self.session_dict.clear()
        self.tab_widget.clear()
        self.menuPlugins.setEnabled(False)
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
                self.menuPlugins.setEnabled(True)
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
            self.close_event()
        else:
            pass

    def close_event(self):
        """Close program properly if main window is closed."""
        if self.started_with_session:
            self.close()
        else:
            sys.exit()


    def setup_tabs(self):
        """Init tab view."""
        # init the standard tabs first
        for tab in self.standard_tabs:
            if tab in self.prev_tabs:
                self.ui_tabs_lookup[tab]()
        for third_party_tab in set(self.prev_tabs).difference(self.standard_tabs):
            try:
                provider = find_tab_provider(self.third_party_tabs, third_party_tab)
                self.init_third_party_tab(provider)
            except ValueError:
                self.logger.info("Third party tab %s not known", third_party_tab)

        # When no previous tabs in config initialise the standard tabs
        if len(self.prev_tabs) == 0:
            for action in self.menuPlugins.actions():
                if action.text() in self.standard_tabs:
                    action.setChecked(True)
                    config_add_tab(action.text())
            for tab_fun in self.ui_tabs_lookup.values():
                tab_fun()

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

    def init_third_party_tab(self, tab_class: object):
        """Create third-party tabs."""
        third_party_tab = tab_class(self.session, self.app_name, self.logger)
        self.tab_widget.addTab(third_party_tab, third_party_tab.name)

    def remove_tab(self, tab_idx: int):
        """Remove a third party tab from tab widget."""
        self.tab_widget.removeTab(tab_idx)

    def create_env_file(self):
        """Populate drop down menu to create a new environment.json."""
        create_widget = CheckConfig(self.logger, self.irods_path)
        create_widget.exec()

    def inspect_env_file(self):
        """Init drop down menu to inspect an environment.json."""
        create_widget = CheckConfig(self.logger, self.irods_path)
        create_widget.exec()


def main(session: Optional[Session] = None):
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
    if session:
        main_app = MainMenu(THIS_APPLICATION, session)
    else:
        main_app = MainMenu(THIS_APPLICATION)
    main_widget.addWidget(main_app)
    main_widget.show()
    app.exec()

if __name__ == "__main__":
    main(session=None)

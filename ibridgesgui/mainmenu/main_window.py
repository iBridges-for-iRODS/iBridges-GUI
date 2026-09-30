"""Main window."""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.mainmenu import (
    PluginManager,
    SessionManager,
    TabManager,
)
from ibridgesgui.popup_widgets import CheckConfig, SupplyTicket
from ibridgesgui.ui_files.MainMenu import Ui_MainWindow
from ibridgesgui.welcome import Welcome


IBRIDGES_DOCS_URL = "https://ibridges.readthedocs.io"
GUI_DOCS_URL = "https://ibridges-for-irods.github.io/iBridges-GUI"

class MainWindow(QMainWindow, Ui_MainWindow):
    """Main application window."""

    def __init__(self, app_name: str, session=None, config_manager=None) -> None:
        """Init."""
        super().__init__()
        load_ui(UI_FILE_DIR / "MainMenu.ui", self)

        self.app_name = app_name
        self.logger = logging.getLogger(app_name)

        self.config = config_manager
        self.plugin_manager = PluginManager()
        self.session_manager = SessionManager(self.config, self.logger)
        self.tab_manager = TabManager(self.tab_widget, self.plugin_manager, self.config, self)

        self.session_manager.session_changed.connect(self.on_session_changed)

        self._build_plugin_menu()
        self._show_welcome_tab()

        # Menu actions
        self.action_connect.triggered.connect(self._on_connect)
        self.action_close_session.triggered.connect(self._on_disconnect)
        self.action_exit.triggered.connect(self._on_exit)
        self.action_edit_configuration.triggered.connect(self._on_edit_env)
        self.action_supply_ticket.triggered.connect(self._on_supply_ticket)
        self.action_gui_docs.triggered.connect(self._on_gui_docs)
        self.action_ibridges_docs.triggered.connect(self._on_ibridges_docs)

        if session is not None:
            self.on_session_changed(session)

    def _build_plugin_menu(self) -> None:
        self.plugin_actions = {}

        for provider in self.plugin_manager.list_providers():
            action = QAction(provider.name, self.menuPlugins, checkable=True)
            action.triggered.connect(
                self._make_toggle_handler(provider.name),
            )
            self.menuPlugins.addAction(action)
            self.plugin_actions[provider.name] = action

        for name in self.tab_manager.standard_tabs:
            action = QAction(name, self.menuPlugins, checkable=True)
            action.triggered.connect(self._make_toggle_handler(name))
            self.menuPlugins.addAction(action)
            self.plugin_actions[name] = action

        self.tab_manager.update_plugin_menu()

    def _make_toggle_handler(self, name: str):
        def handler() -> None:
            self._toggle_tab(name)

        return handler

    def _toggle_tab(self, name: str) -> None:
        session = self.session_manager.session
        if session is None:
            QMessageBox.information(self, "No session", "Please connect first.")
            return

        # Decide based on actual tab state, not QAction state
        if name in self.tab_manager.loaded_tabs:
            self.tab_manager.unload_tab(name)
        else:
            self.tab_manager.load_tab(name, session, self.app_name, self.logger)

        self.tab_manager.update_plugin_menu()

    def _open_web_page(self, URL):
        if not QDesktopServices.openUrl(QUrl(URL)):
            self.logger.error("Could not open %s in a web browser.", URL)

    def _on_gui_docs(self) -> None:
        self._open_web_page(GUI_DOCS_URL)
    def _on_ibridges_docs(self) -> None:
        self._open_web_page(IBRIDGES_DOCS_URL)

    def _on_connect(self) -> None:
        if self.session_manager.session is not None:
            QMessageBox.information(self, "Already connected", "You are already logged in.")
            return
        self.session_manager.login(self)

    def _on_disconnect(self) -> None:
        self.session_manager.disconnect()

    def _on_exit(self) -> None:
        #self.close()
        QApplication.quit()

    def _on_edit_env(self) -> None:
        widget = CheckConfig(self.logger, Path("~/.irods").expanduser())
        widget.exec()

    def _on_supply_ticket(self) -> None:
        widget = SupplyTicket(self.session_manager, self.logger)
        widget.exec()


    def on_session_changed(self, session) -> None:
        """Reset when session changes."""
        self.tab_widget.clear()
        self.tab_manager.loaded_tabs.clear()

        if session is None:
            self.menuPlugins.setEnabled(False)
            self.action_supply_ticket.setEnabled(False)
            self.action_delete_ticket.setEnabled(False)
            self.action_create_ticket.setEnabled(False)
            self._show_welcome_tab()
            return

        self.menuPlugins.setEnabled(True)
        self.action_supply_ticket.setEnabled(True)
        if session.irods_session.username != "anonymous":
            self.action_delete_ticket.setEnabled(True)
            self.action_create_ticket.setEnabled(True)
        self.tab_manager.restore_tabs(session, self.app_name, self.logger)

    def _show_welcome_tab(self) -> None:
        welcome = Welcome()
        self.tab_widget.addTab(welcome, "Welcome")

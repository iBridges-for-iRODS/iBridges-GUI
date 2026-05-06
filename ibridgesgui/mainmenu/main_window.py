"""Main window."""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox

from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.mainmenu import (
    PluginManager,
    SessionManager,
    TabManager,
)
from ibridgesgui.popup_widgets import CheckConfig
from ibridgesgui.ui_files.MainMenu import Ui_MainWindow
from ibridgesgui.welcome import Welcome


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
        self.action_add_configuration.triggered.connect(self._on_create_env)
        self.action_check_configuration.triggered.connect(self._on_check_env)

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

    def _on_connect(self) -> None:
        self.session_manager.connect(self)

    def _on_disconnect(self) -> None:
        self.session_manager.disconnect()

    def _on_exit(self) -> None:
        self.close()

    def _on_create_env(self) -> None:
        widget = CheckConfig(self.logger, Path("~/.irods").expanduser())
        widget.exec()

    def _on_check_env(self) -> None:
        widget = CheckConfig(self.logger, Path("~/.irods").expanduser())
        widget.exec()

    def on_session_changed(self, session) -> None:
        """Reset when session changes."""
        self.tab_widget.clear()

        if session is None:
            self.menuPlugins.setEnabled(False)
            self._show_welcome_tab()
            return

        self.menuPlugins.setEnabled(True)
        self.tab_manager.restore_tabs(session, self.app_name, self.logger)

    def _show_welcome_tab(self) -> None:
        welcome = Welcome()
        self.tab_widget.addTab(welcome, "Welcome")

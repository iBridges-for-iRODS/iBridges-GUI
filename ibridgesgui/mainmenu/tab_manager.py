"""Load and unload tabs."""
from __future__ import annotations

from typing import Callable

from ibridgesgui.browser import Browser
from ibridgesgui.info import Info
from ibridgesgui.logviewer import LogViewer
from ibridgesgui.searchtab.search import Search
from ibridgesgui.synctab.sync import Sync


class TabManager:
    """Handles loading, unloading, and restoring tabs."""

    def __init__(self, tab_widget, plugin_manager, config, main_window) -> None:
        """Init."""
        self.tab_widget = tab_widget
        self.plugin_manager = plugin_manager
        self.config = config
        self.main_window = main_window
        self.loaded_tabs: dict[str, object] = {}

        self.standard_tabs: dict[str, Callable] = {
            "Browser": self._create_browser,
            "Synchronise Data": self._create_sync,
            "Search": self._create_search,
            "Info": self._create_info,
            "Logs": self._create_logs,
        }

    # --- Standard tab factories ---
    def _create_browser(self, session, app_name: str, _logger) -> Browser:
        return Browser(session, app_name)

    def _create_sync(self, session, app_name: str, _logger) -> Sync:
        return Sync(session, app_name)

    def _create_search(self, session, app_name: str, _logger) -> Search:
        browser = self.loaded_tabs.get("Browser")
        return Search(session, app_name, browser)

    def _create_info(self, session, _app_name, _logger) -> Info:
        return Info(session)

    def _create_logs(self, _session, _app_name, logger) -> LogViewer:
        return LogViewer(logger)

    def load_tab(self, name: str, session, app_name: str, logger) -> None:
        """Load tab."""
        if name in self.loaded_tabs:
            return

        if name in self.standard_tabs:
            widget = self.standard_tabs[name](session, app_name, logger)
        else:
            provider = self.plugin_manager.get_provider(name)
            widget = provider(session, app_name, logger)

        self.tab_widget.addTab(widget, name)
        self.update_plugin_menu()
        self.loaded_tabs[name] = widget

        self.config.save_tabs(list(self.loaded_tabs.keys()))

    def unload_tab(self, name: str) -> None:
        """Remove tab from app."""
        widget = self.loaded_tabs.get(name)
        if widget is None:
            return

        index = self.tab_widget.indexOf(widget)
        if index >= 0:
            self.tab_widget.removeTab(index)

        del self.loaded_tabs[name]
        self.update_plugin_menu()

        self.config.save_tabs(list(self.loaded_tabs.keys()))

    def restore_tabs(self, session, app_name: str, logger) -> None:
        """Load all tabs from config."""
        saved = self.config.load_tabs()
        if not saved:
            saved = list(self.standard_tabs)

        # Standard tabs in correct order
        ordered_standard = [name for name in self.standard_tabs if name in saved]

        # Third‑party tabs in saved order
        third_party = [name for name in saved if name not in self.standard_tabs]

        for name in ordered_standard + third_party:
            self.load_tab(name, session, app_name, logger)


    def update_plugin_menu(self):
        """Check and uncheck tab names in main menu."""
        for name, action in self.main_window.plugin_actions.items():
            action.blockSignals(True)
            action.setChecked(name in self.loaded_tabs)
            action.blockSignals(False)

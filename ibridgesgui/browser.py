import logging
import sys

import PySide6.QtWidgets
from ibridges import IrodsPath

from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.ui_files.tabBrowser import Ui_tabBrowser
from .browser_controller import BrowserController


class Browser(PySide6.QtWidgets.QWidget, Ui_tabBrowser):
    """Browser view for iRODS session (UI only, logic in BrowserController)."""

    def __init__(self, session, app_name: str):
        super().__init__()

        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabBrowser.ui", self)

        self.controller = BrowserController(self, session, app_name)
        self.controller.init_browser()

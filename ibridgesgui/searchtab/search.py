# search.py
import sys
import PySide6.QtWidgets
from PySide6.QtWidgets import QButtonGroup

from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.ui_files.tabSearch import Ui_tabSearch

from .search_controller import SearchController


class Search(PySide6.QtWidgets.QWidget, Ui_tabSearch):
    """Search view for iRODS session (UI only, logic in SearchController)."""

    def __init__(self, session, app_name: str, browser):
        super().__init__()

        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabSearch.ui", self)

        # Group radio buttons
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.objects_radio)
        self.radio_group.addButton(self.collections_radio)
        self.radio_group.addButton(self.all_radio)
        
        # Create controller (same pattern as Browser)
        self.controller = SearchController(self, session, app_name, browser)
        self.controller.init_search()


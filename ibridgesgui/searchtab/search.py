# search.py
import sys
from PySide6.QtWidgets import QFileDialog, QMessageBox
from pathlib import Path
import PySide6.QtWidgets
from PySide6.QtWidgets import QButtonGroup
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt

from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.ui_files.tabSearch import Ui_tabSearch
from ibridgesgui.gui_utils import append_table

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

    def display_results(self, rows):
        """Replace table contents with new rows."""
        append_table(self.search_table, self.search_table.rowCount(), rows)
    
    def append_results(self, rows):
        """Append rows to the existing table."""
        append_table(self.search_table, self.search_table.rowCount(), rows)

    def hide_result_elements(self):
        """Hide the GUI elements that show and manipulate search results."""
        self.error_label.clear()
        self.search_table.hide()
        self.download_button.hide()
        self.select_all_box.hide()
        self.load_more_button.hide()
        self.clear_button.hide()
        self.search_table.setRowCount(0)
    
    def show_result_elements(self):
        """Show the GUI elements that show and manipulate search results."""
        self.search_table.show()
        self.select_all_box.show()
        self.download_button.show()
        self.clear_button.show()

    def get_selected_paths(self):
        """Return a list of selected iRODS paths from the table."""
        rows = {item.row() for item in self.search_table.selectedItems()}
        selected = []

        for row in rows:
            path_item = self.search_table.item(row, 1)
            if path_item:
                selected.append(path_item.text())
        return selected
    
    
    def ask_download_destination(self, selected_paths):
        """Determine download location and get ok to download."""
        overwrite = True
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select download folder",
            str(Path("~").expanduser()),
            QFileDialog.ShowDirsOnly
        )
   
        if not folder:
            return None, False
    
        folder = Path(folder)
    
        # Check for existing files
        exists = []
        for p in selected_paths:
            exists.append(folder.joinpath(Path(p).name).exists())
    
        if any(exists):
            reply = QMessageBox.question(
                self,
                "Overwrite?",
                f"Some files already exist in:\n{folder}\n\nOverwrite?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return None, False
            overwrite = (reply == QMessageBox.Yes)
        else:
            overwrite = True
    
        return folder, overwrite


    def set_wait_cursor(self):
        self.setCursor(QCursor(Qt.WaitCursor))

    def set_normal_cursor(self):
        self.setCursor(QCursor(Qt.ArrowCursor))


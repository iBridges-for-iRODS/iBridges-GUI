"""Browser widget."""

import sys

import PySide6.QtWidgets

from ibridgesgui.browsertab.browser_controller import BrowserController
from ibridgesgui.gui_utils import UI_FILE_DIR, get_irods_item, load_ui, populate_table
from ibridgesgui.ui_files.tabBrowser import Ui_tabBrowser


class Browser(PySide6.QtWidgets.QWidget, Ui_tabBrowser):
    """Browser view for iRODS session (UI only, logic in BrowserController)."""

    def __init__(self, session, app_name: str):
        """Init."""
        super().__init__()

        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabBrowser.ui", self)

        self.controller = BrowserController(self, session, app_name)
        self.controller.init_browser()

    # --- Rendering helpers moved from controller ---

    def render_metadata(self, data, irods_path):
        """Render metadata table."""
        self.meta_key_field.clear()
        self.meta_value_field.clear()
        self.meta_units_field.clear()
        self.no_meta_label.clear()

        populate_table(self.meta_table, len(data), data)
        if len(data) == 0:
            self.no_meta_label.setText(f"Metadata for {irods_path} is empty.")
        self.meta_table.resizeColumnsToContents()

    def render_acls(self, clean, irods_path):
        """Render ACL table."""
        self.acl_table.setRowCount(0)
        self.acl_user_field.clear()
        self.acl_zone_field.clear()
        self.acl_box.clear()
        self.recursive_box.setEnabled(irods_path.collection_exists())

        obj_acl = ["read", "write", "own", "delete"]
        coll_acl = obj_acl + [
            "Newly added items to collection will inherit permissions",
            "Remove inheritance.",
        ]

        for item in coll_acl if irods_path.collection_exists() else obj_acl:
            self.acl_box.addItem(item)
        self.acl_box.setEnabled(True)

        populate_table(self.acl_table, len(clean), clean)
        self.acl_table.resizeColumnsToContents()

        obj = get_irods_item(irods_path)
        self.owner_label.setText(obj.owner_name)

    def render_replicas(self, rows):
        """Render replicas table."""
        self.replica_table.setRowCount(0)
        if rows:
            populate_table(self.replica_table, len(rows), rows)
        self.replica_table.resizeColumnsToContents()

    def clear_info_tabs(self):
        """Creal all info tabs."""
        self.acl_table.setRowCount(0)
        self.meta_table.setRowCount(0)
        self.replica_table.setRowCount(0)
        self.preview_browser.clear()
        self.no_meta_label.clear()

    def load_metadata_item(self, index):
        """Load selected metadata row into edit fields."""
        row = index.row()
        key = self.meta_table.item(row, 0).text()
        val = self.meta_table.item(row, 1).text()
        units = self.meta_table.item(row, 2).text() if self.meta_table.item(row, 2) else ""
        self.meta_key_field.setText(key)
        self.meta_value_field.setText(val)
        self.meta_units_field.setText(units)

    def load_permission(self, index):
        """Load selected ACL row into edit fields."""
        row = index.row()
        user = self.acl_table.item(row, 0).text()
        zone = self.acl_table.item(row, 1).text()
        acc = self.acl_table.item(row, 2).text()

        self.acl_user_field.setText(user)
        self.acl_zone_field.setText(zone)
        self.acl_box.setCurrentText(acc)
        self.recursive_box.setCurrentText("False")

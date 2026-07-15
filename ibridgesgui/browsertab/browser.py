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

        self.setup_tooltips()
        self.controller = BrowserController(self, session, app_name)
        self.controller.init_browser()

    def setup_tooltips(self):
        """Add tool tips to interactive elements."""
        # --- Navigation ---
        self.input_path.setToolTip("Enter an iRODS path and press Enter to navigate.")
        self.refresh_button.setToolTip("Reload the current collection or data object.")
        self.home_button.setToolTip("Go to your iRODS home collection.")
        self.parent_button.setToolTip("Move to the parent collection of the current path.")

        # --- CRUD operations ---
        self.upload_button.setToolTip("Upload a file or directory to the current iRODS path.")
        self.download_button.setToolTip("Download the selected iRODS item.")
        self.create_coll_button.setToolTip("Create a new collection inside the current path.")
        self.rename_button.setToolTip("Rename the selected iRODS item.")
        self.delete_button.setToolTip("Delete the selected iRODS item.")

        # --- Browser table ---
        self.browser_table.setToolTip(
            "Browse collections and data objects. Double‑click to open an item."
        )

        # --- Info tabs ---
        self.info_tabs.setToolTip(
            "View metadata, ACLs, replicas, or a preview of the selected item."
        )

        # --- Metadata ---
        self.meta_table.setToolTip(
            "Metadata attached to this item. Click a row to load it for editing."
        )
        self.add_meta_button.setToolTip("Add a new metadata attribute to this item.")
        self.update_meta_button.setToolTip("Update the selected metadata attribute.")
        self.delete_meta_button.setToolTip("Delete the selected metadata attribute.")

        # --- ACLs ---
        self.acl_table.setToolTip(
            "Access Control List entries. Click a row to load it for editing."
        )
        self.add_acl_button.setToolTip("Add or update an ACL entry for this item.")

        # --- Replicas ---
        self.replica_table.setToolTip("Replica information for this data object.")

        # --- Preview ---
        self.preview_browser.setToolTip("Preview the selected data object, if supported.")

    # --- Rendering helpers moved from controller ---

    def render_metadata(self, data, irods_path):
        """Render metadata table."""
        self.meta_key_field.clear()
        self.meta_value_field.clear()
        self.meta_units_field.clear()
        self.no_meta_label.clear()

        populate_table(self.meta_table, len(data), data)
        current_tab = self.info_tabs.currentWidget().objectName()
        if current_tab == "metadata" and len(data) == 0:
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

    def on_tab_changed(self):
        """Clear the metadata label when switching tabs."""
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

import logging
from typing import Union

import PySide6.QtCore
import PySide6.QtWidgets
import irods.exception
from ibridges import IrodsPath

from ibridgesgui.gui_utils import populate_table, populate_textfield, get_irods_item
from ibridgesgui.popup_widgets import CreateCollection, DownloadData, Rename, UploadData
from .browser_model import BrowserModel
from .irods_browser_service import IrodsBrowserService


class BrowserController:
    """Orchestrates UI, model and iRODS service for the Browser tab."""

    def __init__(
        self,
        ui: PySide6.QtWidgets.QWidget,
        session,
        app_name: str,
    ):
        self.ui = ui
        self.logger = logging.getLogger(app_name)
        self.service = IrodsBrowserService(session, self.logger)
        home = self.service.home_path()
        self.model = BrowserModel(home)

    # ---------- initialization ----------

    def init_browser(self) -> None:
        """Wire signals and set initial state."""
        self._connect_signals()
        self.set_input_path_to_home()
        self.ui.refresh_button.clicked.connect(self.refresh_browser)
        self.ui.input_path.returnPressed.connect(self.refresh_browser)
        self.ui.home_button.clicked.connect(self.set_input_path_to_home)
        self.ui.parent_button.clicked.connect(self.set_input_path_to_parent)
        self.ui.browser_table.doubleClicked.connect(self.load_path)


    def _connect_signals(self) -> None:
        # navigation
        self.ui.input_path.returnPressed.connect(self.refresh_browser)
        self.ui.refresh_button.clicked.connect(self.refresh_browser)
        self.ui.home_button.clicked.connect(self.set_input_path_to_home)
        self.ui.parent_button.clicked.connect(self.set_input_path_to_parent)

        # main actions
        self.ui.upload_button.clicked.connect(self.upload_data)
        self.ui.download_button.clicked.connect(self.download_data)
        self.ui.create_coll_button.clicked.connect(self.create_collection)
        self.ui.rename_button.clicked.connect(self.rename_item)
        self.ui.delete_button.clicked.connect(self.delete_data)

        # table / info tabs
        self.ui.browser_table.doubleClicked.connect(self.load_path)
        self.ui.browser_table.clicked.connect(self._on_row_clicked)
        self.ui.info_tabs.currentChanged.connect(self.fill_info_tab_content)

        # metadata
        self.ui.meta_table.clicked.connect(self.edit_metadata)
        self.ui.add_meta_button.clicked.connect(self.add_icat_meta)
        self.ui.update_meta_button.clicked.connect(self.update_icat_meta)
        self.ui.delete_meta_button.clicked.connect(self.delete_icat_meta)

        # ACLs
        self.ui.acl_table.clicked.connect(self.edit_permission)
        self.ui.add_acl_button.clicked.connect(self.update_permission)

    # ---------- path / navigation ----------

    def update_input_path(self, irods_path: Union[str, IrodsPath]) -> None:
        self.ui.input_path.setText(str(irods_path))
        self.model.reset_selection_cache()
        self.load_browser_table()

    def set_input_path_to_home(self) -> None:
        self.update_input_path(self.model.current_path)

    def set_input_path_to_parent(self) -> None:
        parent = self.service.parent_path(self.ui.input_path.text())
        self.update_input_path(parent)

    def refresh_browser(self) -> None:
        path = self.service.path_from_text(self.ui.input_path.text())
        self.update_input_path(path)

    def load_path(self) -> None:
        row = self.ui.browser_table.currentRow()
        irods_path = self._get_item_path(row)
        if irods_path is None:
            return
        if irods_path.collection_exists():
            self.update_input_path(irods_path)

    # ---------- CRUD operations ----------

    def create_collection(self) -> None:
        # will be filled with original logic
        pass

    def rename_item(self) -> None:
        # will be filled with original logic
        pass

    def download_data(self) -> None:
        # will be filled with original logic
        pass

    def upload_data(self) -> None:
        # will be filled with original logic
        pass

    def delete_data(self) -> None:
        # will be filled with original logic
        pass

    # ---------- main table ----------


    def load_browser_table(self):
        """Load the main browser table using the service."""
        self.ui.error_label.clear()
        self._clear_info_tabs()
    
        path = self.service.path_from_text(self.ui.input_path.text())
    
        if not path.collection_exists():
            self.ui.browser_table.setRowCount(0)
            self.ui.error_label.setText(f"Collection does not exist: {str(path)}.")
            return
    
        try:
            rows = self.service.list_table_rows(path)
            populate_table(self.ui.browser_table, len(rows), rows)
        except Exception as err:
            self.ui.browser_table.setRowCount(0)
            self.logger.exception("Cannot load browser.")
            self.ui.error_label.setText(
                f"Cannot load browser table for {str(path)}: {err}"
            )

    # ---------- info tabs ----------

    def fill_info_tab_content(self):
        if self._nothing_selected_error():
            return
    
        row = self.ui.browser_table.currentRow()
        irods_path = self._get_item_path(row)
    
        if irods_path is None:
            return
    
        tab_name = self.ui.info_tabs.currentWidget().objectName()
    
        if self.model.needs_tab_update(tab_name, row):
            try:
                if tab_name == "metadata":
                    self._fill_metadata_tab(irods_path)
                elif tab_name == "permissions":
                    self._fill_acls_tab(irods_path)
                elif tab_name == "replicas":
                    self._fill_replicas_tab(irods_path)
                elif tab_name == "preview":
                    self._fill_preview_tab(irods_path)
    
                self.model.mark_tab_updated(tab_name)
    
            except Exception as err:
                self.logger.exception("Error loading %s of %s", tab_name, irods_path)
                self.ui.error_label.setText(
                    f"Error loading {tab_name} of {irods_path}: {repr(err)}"
                )

    def _clear_info_tabs(self) -> None:
        self.ui.acl_table.setRowCount(0)
        self.ui.meta_table.setRowCount(0)
        self.ui.replica_table.setRowCount(0)
        self.ui.preview_browser.clear()
        self.ui.no_meta_label.clear()

    # ---------- preview ----------
    def _fill_preview_tab(self, irods_path):
        """Populate the table in the metadata tab.

        Parameters
        ----------
        irods_path : str
            Full name of iRODS collection or data object selected.

        """
        if irods_path.collection_exists():
            obj = irods_path.collection
            content = ["Collections:", "-----------------"]
            content.extend([sc.name for sc in obj.subcollections])
            content.extend(["\n", "DataObjects:", "-----------------"])
            content.extend([do.name for do in obj.data_objects])
        elif irods_path.dataobject_exists():
            file_type = ""
            obj = irods_path.dataobject
            if "." in irods_path.parts[-1]:
                file_type = irods_path.parts[-1].split(".")[1]
            if file_type in ["txt", "json", "csv"]:
                try:
                    with obj.open("r") as objfd:
                        content = [objfd.read(1024).decode("utf-8")]
                except Exception as error:
                    content = [
                        f"No Preview for: {irods_path}",
                        repr(error),
                        "Storage resource might be down.",
                    ]
            else:
                content = [f"No Preview for: {irods_path}"]
        else:
            content = [f"No Preview for: {irods_path}"]
        populate_textfield(self.ui.preview_browser, content)

    # ---------- metadata ----------

    def update_icat_meta(self) -> None:
        # will call self._metadata_edits("update")
        pass

    def add_icat_meta(self) -> None:
        # will call self._metadata_edits("add")
        pass

    def delete_icat_meta(self) -> None:
        # will call self._metadata_edits("delete")
        pass

    def edit_metadata(self, index: PySide6.QtCore.QModelIndex) -> None:
        # will be filled with original logic
        pass

    def _metadata_edits(self, operation: str) -> None:
        # will be filled with original logic, but using service
        pass

    # ---------- ACLs ----------

    def edit_permission(self, index: PySide6.QtCore.QModelIndex) -> None:
        # will be filled with original logic
        pass

    def update_permission(self) -> None:
        """Apply ACL changes using the service."""
        if self._nothing_selected_error():
            return
    
        row = self.ui.browser_table.currentRow()
        irods_path = self._get_item_path(row)
        if irods_path is None:
            return
    
        user_name = self.ui.acl_user_field.text()
        user_zone = self.ui.acl_zone_field.text()
        acc_name = self.ui.acl_box.currentText()
        recursive = self.ui.recursive_box.currentText() == "True"
    
        # Map UI labels to iRODS ACL keywords
        label_to_acl = {
            "Newly added items to collection will inherit permissions": "inherit",
            "Remove inheritance.": "noinherit",
            "delete": "null",
        }
        acl_value = label_to_acl.get(acc_name, acc_name)
    
        # Validation
        if acl_value in ("inherit", "noinherit") and irods_path.dataobject_exists():
            self.ui.error_label.setText("WARNING: (no)inherit is not applicable to data objects.")
            return
    
        if acl_value not in ("inherit", "noinherit") and user_name == "":
            self.ui.error_label.setText("Please provide a user.")
            return
    
        if acc_name == "":
            self.ui.error_label.setText("Please provide an access level from the menu.")
            return
    
        # Apply ACL
        try:
            self.service.set_acl(
                irods_path,
                user_name=user_name,
                user_zone=user_zone,
                access=acl_value,
                recursive=recursive,
            )
    
            # Logging
            if acl_value == "null":
                self.logger.info(
                    "Delete access (%s, %s, %s, %s) for %s",
                    acl_value, user_name, user_zone, recursive, irods_path
                )
            else:
                self.logger.info(
                    "Add/change access of %s to (%s, %s, %s, %s)",
                    irods_path, acl_value, user_name, user_zone, recursive
                )
    
            # Refresh tab
            self._fill_acls_tab(irods_path)
    
        except (irods.exception.CAT_INVALID_USER, irods.exception.SYS_NOT_ALLOWED):
            self.ui.error_label.setText(f"Cannot update ACLs. {user_name}#{user_zone} not known.")
        except irods.exception.MSI_OPERATION_NOT_ALLOWED:
            self.ui.error_label.setText("iRODS server does not allow editing permissions.")
        except Exception as err:
            self.logger.exception("Permissions error for %s", irods_path)
            self.ui.error_label.setText(f"Error editing permissions: {repr(err)}")
    
    def _fill_acls_tab(self, irods_path):
        """Populate the ACL table and update UI controls."""
        self.ui.acl_table.setRowCount(0)
        self.ui.acl_user_field.clear()
        self.ui.acl_zone_field.clear()
        self.ui.acl_box.clear()
        self.ui.recursive_box.setEnabled(False)
    
        # Determine available ACL options
        obj_acl_items = ["read", "write", "own", "delete"]
        coll_acl_items = obj_acl_items + [
            "Newly added items to collection will inherit permissions",
            "Remove inheritance.",
        ]
    
        if irods_path.collection_exists():
            self.ui.recursive_box.setEnabled(True)
            for item in coll_acl_items:
                self.ui.acl_box.addItem(item)
        elif irods_path.dataobject_exists():
            for item in obj_acl_items:
                self.ui.acl_box.addItem(item)
    
        # Load ACLs from service
        try:
            acl_rows = self.service.get_acls(irods_path)
            populate_table(self.ui.acl_table, len(acl_rows), acl_rows)
            self.ui.acl_table.resizeColumnsToContents()
    
            # Owner label
            obj = get_irods_item(irods_path)
            self.ui.owner_label.setText(f"{obj.owner_name}")
    
        except Exception as err:
            self.logger.exception("Error loading ACLs for %s", irods_path)
            self.ui.error_label.setText(f"Error loading ACLs: {repr(err)}")
    

    # ---------- replicas ---------
    def _fill_replicas_tab(self, irods_path):
        """Populate the replicas tab using the service."""
        self.ui.replica_table.setRowCount(0)
    
        rows = self.service.replicas_for(irods_path)
    
        if rows:
            populate_table(self.ui.replica_table, len(rows), rows)
    
        self.ui.replica_table.resizeColumnsToContents()
    

    # ---------- helpers ----------

    def _on_row_clicked(self) -> None:
        row = self.ui.browser_table.currentRow()
        if row < 0:
            return
        self.model.on_row_clicked(row)
        self.fill_info_tab_content()

    def _get_item_path(self, row: int) -> IrodsPath:
        if row is None or row < 0:
            return None
    
        item = self.ui.browser_table.item(row, 1)
        if item is None:
            return None
    
        item_name = item.text()
        return IrodsPath(
            self.service.session,
            "/",
            *self.ui.input_path.text().split("/"),
            item_name,
        )

    def _nothing_selected_error(self) -> bool:
        self.ui.error_label.clear()
        if self.ui.browser_table.currentRow() == -1:
            self.ui.error_label.setText("Please select an item from the table.")
            return True
        return False


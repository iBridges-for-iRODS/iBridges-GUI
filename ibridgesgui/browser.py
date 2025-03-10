"""Browser tab."""

import logging
import sys
from typing import Union

import irods.exception
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets
from ibridges import IrodsPath
from ibridges.permissions import Permissions
from ibridges.util import obj_replicas

from ibridgesgui.gui_utils import (
    UI_FILE_DIR,
    get_irods_item,
    load_ui,
    populate_table,
    populate_textfield,
)
from ibridgesgui.popup_widgets import CreateCollection, DownloadData, Rename, UploadData
from ibridgesgui.ui_files.tabBrowser import Ui_tabBrowser


class Browser(PySide6.QtWidgets.QWidget, Ui_tabBrowser):
    """Browser view for iRODS session."""

    def __init__(self, session, app_name: str):
        """Initialize an iRODS browser view."""
        super().__init__()
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabBrowser.ui", self)

        self.logger = logging.getLogger(app_name)
        self.session = session
        self.home_coll = IrodsPath(self.session)
        self.last_selected_row = -1
        self.current_selected_row = -1
        self.updated_info_tabs = []
        self.init_browser()

    def init_browser(self):
        """Initialize browser view GUI elements. Define the signals and slots."""
        # First time the browser is loaded set path to home
        self.set_input_path_to_home()

        self.input_path.setToolTip("Navigate to path. Hit ENTER.")

        # Couple main navigation elements to their functions
        self.input_path.returnPressed.connect(self.refresh_browser)
        self.refresh_button.clicked.connect(self.refresh_browser)
        self.refresh_button.setToolTip("Refresh table.")
        self.home_button.clicked.connect(self.set_input_path_to_home)
        self.home_button.setToolTip("Go to home.")
        self.parent_button.clicked.connect(self.set_input_path_to_parent)
        self.parent_button.setToolTip("Go one collection up.")

        # Main manipulation buttons Upload/Download, Create collection
        self.upload_button.clicked.connect(self.upload_data)
        self.upload_button.setToolTip("Upload data.")
        self.download_button.clicked.connect(self.download_data)
        self.download_button.setToolTip("Download item from table.")
        self.create_coll_button.clicked.connect(self.create_collection)
        self.create_coll_button.setToolTip("Add a new empty collection to table.")
        self.rename_button.clicked.connect(self.rename_item)
        self.rename_button.setToolTip("Change the name or the path of item in the table.")
        self.delete_button.clicked.connect(self.delete_data)
        self.delete_button.setToolTip("Delete an item permanently.")

        # Browser table behaviour
        self.browser_table.doubleClicked.connect(self.load_path)
        self.browser_table.clicked.connect(self._update_last_selected_row)
        # Load info tabs when requested
        self.info_tabs.currentChanged.connect(self.fill_info_tab_content)

        # Bottom tab view buttons
        # Manipulate Metadata
        self.meta_table.clicked.connect(self.edit_metadata)
        self.add_meta_button.clicked.connect(self.add_icat_meta)
        self.add_meta_button.setToolTip("Add new metadata item.")
        self.update_meta_button.clicked.connect(self.update_icat_meta)
        self.update_meta_button.setToolTip("Update the metadata item.")
        self.delete_meta_button.clicked.connect(self.delete_icat_meta)
        self.delete_meta_button.setToolTip("Delete the metadata item.")
        # Manilpulate ACLs
        self.acl_table.clicked.connect(self.edit_permission)
        self.add_acl_button.clicked.connect(self.update_permission)

    def update_input_path(self, irods_path: Union[str, IrodsPath]):
        """Set the input path to a new path and loads the table."""
        self.input_path.setText(str(irods_path))
        # reset the params to load info tabs
        self.last_selected_row = -1
        self.current_selected_row = -1
        self.updated_info_tabs = []
        self.load_browser_table()

    def set_input_path_to_home(self):
        """Reset browser table to home."""
        self.update_input_path(self.home_coll)

    def set_input_path_to_parent(self):
        """Set browser path to parent of current collection and update browser table."""
        parent_path = IrodsPath(self.session, self.input_path.text()).parent
        self.update_input_path(parent_path)

    def refresh_browser(self):
        """Reload table and reset the caching for the info tabs."""
        irods_path = IrodsPath(self.session, self.input_path.text())
        self.update_input_path(irods_path)

    def load_path(self):
        """Take path from input_path and loads browser table."""
        irods_path = self._get_item_path(self.browser_table.currentRow())
        if irods_path.collection_exists():
            self.update_input_path(irods_path)

    def create_collection(self):
        """Create a new collection in current collection."""
        self.error_label.clear()
        clean_cur_path = IrodsPath(self.session, "/" + self.input_path.text().strip("/"))
        coll_widget = CreateCollection(clean_cur_path, self.logger)
        coll_widget.exec()
        self.update_input_path(clean_cur_path)

    def rename_item(self):
        """Rename/move a collection or data object."""
        if self._nothing_selected_error():
            return
        item_name = self.browser_table.item(self.browser_table.currentRow(), 1).text()
        current_collection = IrodsPath(self.session, "/" + self.input_path.text().strip("/"))
        irods_path = current_collection.joinpath(item_name)
        rename_widget = Rename(irods_path, self.logger)
        rename_widget.exec()
        self.update_input_path(current_collection)

    def download_data(self):
        """Download collection or data object."""
        if self._nothing_selected_error():
            return
        if self.browser_table.item(self.browser_table.currentRow(), 1) is not None:
            item_name = self.browser_table.item(self.browser_table.currentRow(), 1).text()
            path = IrodsPath(self.session, "/", *self.input_path.text().split("/"), item_name)
            download_dialog = DownloadData(self.logger, self.session, path)
            download_dialog.exec()

    def upload_data(self):
        """Upload files or folders."""
        path = IrodsPath(self.session, "/", *self.input_path.text().split("/"))
        if path.collection_exists():
            upload_dialog = UploadData(self.logger, self.session, path)
            upload_dialog.exec()
            self.refresh_browser()
        else:
            self.error_label.setText(f"{path} is not a collection. Cannot upload data.")

    def delete_data(self):
        """Delete selected data in the delete_browser."""
        if self._nothing_selected_error():
            return

        if self.browser_table.item(self.browser_table.currentRow(), 1) is not None:
            item_name = self.browser_table.item(self.browser_table.currentRow(), 1).text()
            irods_path = IrodsPath(self.session, "/", *self.input_path.text().split("/"), item_name)
            quit_msg = f"Are you sure you want to delete {str(irods_path)}?"
            reply = PySide6.QtWidgets.QMessageBox.critical(
                self,
                "Message",
                quit_msg,
                PySide6.QtWidgets.QMessageBox.StandardButton.Yes,
                PySide6.QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply == PySide6.QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    irods_path.remove()
                    self.logger.info("Delete data %s", str(irods_path))
                    self.refresh_browser()
                except (irods.exception.CAT_NO_ACCESS_PERMISSION, PermissionError):
                    self.error_label.setText(f"No permissions to delete {str(irods_path)}")
                except Exception:
                    self.logger.exception("FAILED: Delete data %s", irods_path)
                    self.error_label.setText(f"FAILED: Delete data {irods_path}. Consult the logs.")

    def load_browser_table(self):
        """Load main browser table."""
        self.error_label.clear()
        self._clear_info_tabs()
        irods_path = IrodsPath(self.session, self.input_path.text())
        if irods_path.collection_exists():
            try:
                coll_data = [
                    (
                        "C-",
                        subcoll.name,
                        "",
                        "",
                        subcoll.create_time.strftime("%d-%m-%Y"),
                        subcoll.modify_time.strftime("%d-%m-%Y %H:%m"),
                    )
                    for subcoll in irods_path.collection.subcollections
                ]
                obj_data = [
                    (
                        max(repl[4] for repl in obj_replicas(obj)),
                        obj.name,
                        str(obj.size),
                        obj.checksum,
                        obj.create_time.strftime("%d-%m-%Y"),
                        obj.modify_time.strftime("%d-%m-%Y %H:%m"),
                    )
                    for obj in irods_path.collection.data_objects
                ]

                populate_table(
                    self.browser_table,
                    len(irods_path.collection.data_objects)
                    + len(irods_path.collection.subcollections),
                    coll_data + obj_data,
                )
            except Exception as err:
                self.browser_table.setRowCount(0)
                self.logger.exception("Cannot load browser.")
                self.error_label.setText(f"Cannot load browser table for {str(irods_path)}: {err}")
        else:
            self.browser_table.setRowCount(0)
            self.error_label.setText(f"Collection does not exist: {str(irods_path)}.")

    def fill_info_tab_content(self):
        """Fill lower tabs with info."""
        if self._nothing_selected_error():
            return
        tab_name = self.info_tabs.currentWidget().objectName()
        irods_path = self._get_item_path(self.browser_table.currentRow())
        if (
            self.last_selected_row != self.browser_table.currentRow()
            or tab_name not in self.updated_info_tabs
        ):
            self.last_selected_row = self.current_selected_row
            try:
                if tab_name == "metadata":
                    self._fill_metadata_tab(irods_path)
                elif tab_name == "permissions":
                    self._fill_acls_tab(irods_path)
                elif tab_name == "replicas":
                    self._fill_replicas_tab(irods_path)
                elif tab_name == "preview":
                    self._fill_preview_tab(irods_path)
                self.updated_info_tabs.append(tab_name)
            except Exception as err:
                self.logger.exception("Error loading %s of %s .", tab_name, irods_path)
                self.error_label.setText(f"Error loading {tab_name} of {irods_path}: {repr(err)}")

    def update_icat_meta(self):
        """Button metadata set."""
        try:
            self._metadata_edits("update")
        except Exception as error:
            self.error_label.setText(repr(error))

    def add_icat_meta(self):
        """Button metadata add."""
        try:
            self._metadata_edits("add")
        except Exception as error:
            self.error_label.setText(repr(error))

    def delete_icat_meta(self):
        """Button metadata delete."""
        try:
            self._metadata_edits("delete")
        except Exception as error:
            self.error_label.setText(repr(error))

    # @PyQt6.QtCore.pyqtSlot(PyQt6.QtCore.QModelIndex)
    def edit_metadata(self, index: PySide6.QtCore.QModelIndex):
        """Load selected metadata info edit fields."""
        self.error_label.clear()
        self.meta_key_field.clear()
        self.meta_value_field.clear()
        self.meta_units_field.clear()
        row = index.row()
        key = self.meta_table.item(row, 0).text()
        value = self.meta_table.item(row, 1).text()
        if self.meta_table.item(row, 2):
            units = self.meta_table.item(row, 2).text()
        else:
            units = ""
        self.meta_key_field.setText(key)
        self.meta_value_field.setText(value)
        self.meta_units_field.setText(units)

    # @PyQt6.QtCore.pyqtSlot(PyQt6.QtCore.QModelIndex)
    def edit_permission(self, index: PySide6.QtCore.QModelIndex):
        """Load selected acl into editing fields."""
        self.error_label.clear()
        self.acl_user_field.clear()
        self.acl_zone_field.clear()
        self.acl_box.setCurrentText("")
        row = index.row()
        user_name = self.acl_table.item(row, 0).text()
        user_zone = self.acl_table.item(row, 1).text()
        acc_name = self.acl_table.item(row, 2).text()
        self.acl_user_field.setText(user_name)
        self.acl_zone_field.setText(user_zone)
        self.acl_box.setCurrentText(acc_name)

    def update_permission(self):
        """Send acls to iRODS server."""
        if self._nothing_selected_error():
            return
        irods_path = self._get_item_path(self.browser_table.currentRow())
        user_name = self.acl_user_field.text()
        user_zone = self.acl_zone_field.text()
        acc_name = self.acl_box.currentText()

        perm_lables_to_acl = {
            "Newly added items to collection will inherit permissions": "inherit",
            "Remove inhertiance.": "noinherit",
            "delete": "null",
        }

        if perm_lables_to_acl.get(acc_name, acc_name) in ("inherit", "noinherit"):
            if irods_path.dataobject_exists():
                self.error_label.setText("WARNING: (no)inherit is not applicable to data objects.")
                return
        elif user_name == "":
            self.error_label.setText("Please provide a user.")
            return
        elif acc_name == "":
            self.error_label.setText("Please provide an access level from the menu.")
            return
        recursive = self.recursive_box.currentText() == "True"
        try:
            perm = Permissions(self.session, get_irods_item(irods_path))
            perm.set(
                perm=perm_lables_to_acl.get(acc_name, acc_name),
                user=user_name,
                zone=user_zone,
                recursive=recursive,
            )
            if perm_lables_to_acl.get(acc_name, acc_name) == "null":
                self.logger.info(
                    "Delete access (%s, %s, %s, %s) for %s",
                    perm_lables_to_acl.get(acc_name, acc_name),
                    user_name,
                    user_zone,
                    str(recursive),
                    str(irods_path),
                )
            else:
                self.logger.info(
                    "Add/change access of %s to (%s, %s, %s, %s)",
                    str(irods_path),
                    perm_lables_to_acl.get(acc_name, acc_name),
                    user_name,
                    user_zone,
                    str(recursive),
                )
            self._fill_acls_tab(irods_path)
        except (irods.exception.CAT_INVALID_USER, irods.exception.SYS_NOT_ALLOWED):
            self.error_label.setText(f"Cannot update ACLs. {user_name}#{user_zone} not known.")
        except irods.exception.MSI_OPERATION_NOT_ALLOWED:
            self.error_label.setText("iRODS server does not allow to edit permissions.")
        except Exception as err:
            self.logger.exception("Permissions error for %s", str(irods_path))
            self.error_label.setText(f"Error edit permissions of {str(irods_path)}: {repr(err)}")

    # Internal functions
    def _clear_info_tabs(self):
        """Clear the tabs view."""
        self.acl_table.setRowCount(0)
        self.meta_table.setRowCount(0)
        self.replica_table.setRowCount(0)
        self.preview_browser.clear()
        self.no_meta_label.clear()

    def _get_item_path(self, row: int):
        item_name = self.browser_table.item(row, 1).text()
        return IrodsPath(self.session, "/", *self.input_path.text().split("/"), item_name)

    def _nothing_selected_error(self):
        self.error_label.clear()
        if self.browser_table.currentRow() == -1:
            self.error_label.setText("Please select an item from the table.")
            return True
        return False

    def _update_last_selected_row(self):
        """On click on a row in the browser table, empty cached information and store indices."""
        self.updated_info_tabs = []
        self.last_selected_row = self.current_selected_row
        self.current_selected_row = self.browser_table.currentRow()
        # fill currently selected tab with info
        self.fill_info_tab_content()

    def _fill_replicas_tab(self, irods_path: Union[IrodsPath, str]):
        """Populate the table in the Replicas tab.

        Parameters
        ----------
        irods_path : str
            Path of iRODS collection or data object selected.

        """
        self.replica_table.setRowCount(0)
        if irods_path.dataobject_exists():
            obj = irods_path.dataobject
            populate_table(self.replica_table, len(obj_replicas(obj)), obj_replicas(obj))
            self.replica_table.setRowCount(len(obj.replicas))
        self.replica_table.resizeColumnsToContents()

    def _fill_acls_tab(self, irods_path: Union[IrodsPath, str]):
        """Populate the table in the ACLs tab.

        Parameters
        ----------
        irods_path : str
            Path of iRODS collection or data object selected.

        """
        self.acl_table.setRowCount(0)
        self.acl_user_field.clear()
        self.acl_zone_field.clear()
        self.acl_box.setEnabled(True)
        self.recursive_box.setEnabled(False)
        self.acl_box.clear()
        obj = None
        obj_acl_box_items = ["read", "write", "own", "delete"]
        coll_acl_box_items = obj_acl_box_items + [
            "Newly added items to collection will inherit permissions",
            "Remove inheritance.",
        ]

        if irods_path.collection_exists():
            obj = irods_path.collection
            inheritance = f"{obj.inheritance}"
            self.recursive_box.setEnabled(True)
            _ = [self.acl_box.addItem(item) for item in coll_acl_box_items]
        elif irods_path.dataobject_exists():
            _ = [self.acl_box.addItem(item) for item in obj_acl_box_items]
            obj = irods_path.dataobject
            self.recursive_box.setEnabled(False)
            inheritance = ""
        if obj is not None:
            acls = Permissions(self.session, obj)
            acl_data = [(p.user_name, p.user_zone, p.access_name, inheritance) for p in acls]
            populate_table(self.acl_table, len(list(acls)), acl_data)
        self.acl_table.resizeColumnsToContents()
        self.owner_label.setText(f"{obj.owner_name}")

    def _fill_metadata_tab(self, irods_path: Union[IrodsPath, str]):
        """Populate the table in the metadata tab.

        Parameters
        ----------
        irods_path : str
            Full name of iRODS collection or data object selected.

        """
        self.meta_key_field.clear()
        self.meta_value_field.clear()
        self.meta_units_field.clear()
        self.no_meta_label.clear()
        if irods_path.exists():
            populate_table(self.meta_table, len(list(irods_path.meta)), irods_path.meta)
        if len(irods_path.meta) == 0:
            self.no_meta_label.setText(f"Metadata for {str(irods_path)} is empty.")
        self.meta_table.resizeColumnsToContents()

    def _fill_preview_tab(self, irods_path: Union[IrodsPath, str]):
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
        populate_textfield(self.preview_browser, content)
        self.preview_browser.verticalScrollBar().setValue(0)

    def _metadata_edits(self, operation: str):
        self.error_label.clear()
        if self._nothing_selected_error():
            return

        irods_path = self._get_item_path(self.browser_table.currentRow())
        new_key = self.meta_key_field.text()
        new_val = self.meta_value_field.text()
        new_units = self.meta_units_field.text()
        irods_path = self._get_item_path(self.browser_table.currentRow())
        if operation == "add":
            irods_path.meta.add(new_key, new_val, new_units)
            self.logger.info(
                "Add metadata (%s, %s, %s) to %s", new_key, new_val, new_units, irods_path
            )
        elif operation == "update":
            row = self.meta_table.currentRow()
            old_key = self.meta_table.item(row, 0).text()
            old_val = self.meta_table.item(row, 1).text()
            old_units = self.meta_table.item(row, 2).text()
            print(old_key, old_val, old_units)
            self.logger.info(
                "Update metadata of %s from (%s, %s, %s) to (%s, %s, %s)",
                irods_path,
                old_key,
                old_val,
                old_units,
                new_key,
                new_val,
                new_units,
            )
            irods_path.meta[old_key, old_val, old_units] = [new_key, new_val, new_units]
        elif operation == "delete":
            irods_path.meta.delete(new_key, new_val, new_units)
            self.logger.info(
                "Delete metadata (%s, %s, %s) from %s", new_key, new_val, new_units, irods_path
            )
        self._fill_metadata_tab(irods_path)

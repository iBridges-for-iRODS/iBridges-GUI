"""Browser tab."""

import logging
import sys
from pathlib import Path

import irods.exception
import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic
from ibridges import IrodsPath, download, upload
from ibridges.meta import MetaData
from ibridges.permissions import Permissions
from ibridges.util import obj_replicas

from ibridgesgui.gui_utils import (
    UI_FILE_DIR,
    get_downloads_dir,
    get_irods_item,
    populate_table,
    populate_textfield,
)
from ibridgesgui.popup_widgets import CreateCollection, Rename
from ibridgesgui.ui_files.tabBrowser import Ui_tabBrowser


class Browser(PyQt6.QtWidgets.QWidget, Ui_tabBrowser):
    """Browser view for iRODS session."""

    def __init__(self, session, app_name):
        """Initialize an iRODS browser view."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi(UI_FILE_DIR / "tabBrowser.ui", self)

        self.logger = logging.getLogger(app_name)
        self.session = session
        self.home_coll = IrodsPath(self.session)
        self.last_selected_row = -1
        self.current_selected_row = -1
        self.updated_info_tabs = []
        self.init_browser()

    def init_browser(self):
        """Initialize browser view GUI elements. Define the signals and slots."""
        # First tim the browser is loaded set path to home
        self.set_input_path_to_home()

        # Couple main navigation elements to their functions
        self.input_path.returnPressed.connect(self.refresh_browser)
        self.refresh_button.clicked.connect(self.refresh_browser)
        self.refresh_button.setToolTip("Refresh browser.")
        self.home_button.clicked.connect(self.set_input_path_to_home)
        self.home_button.setToolTip("Go to home.")
        self.parent_button.clicked.connect(self.set_input_path_to_parent)
        self.parent_button.setToolTip("Go one coll up.")

        # Main manipulation buttons Upload/Download, Create collection
        self.upload_file_button.clicked.connect(self.file_upload)
        self.upload_dir_button.clicked.connect(self.folder_upload)
        self.download_button.clicked.connect(self.download)
        self.create_coll_button.clicked.connect(self.create_collection)
        self.rename_button.clicked.connect(self.rename_item)
        self.delete_button.clicked.connect(self.delete_data)

        # Browser table behaviour
        self.browser_table.doubleClicked.connect(self.load_path)
        self.browser_table.clicked.connect(self._update_last_selected_row)
        # Load info tabs when requested
        self.info_tabs.currentChanged.connect(self.fill_info_tab_content)

        # Bottom tab view buttons
        # Manipulate Metadata
        self.meta_table.clicked.connect(self.edit_metadata)
        self.add_meta_button.clicked.connect(self.add_icat_meta)
        self.update_meta_button.clicked.connect(self.set_icat_meta)
        self.delete_meta_button.clicked.connect(self.delete_icat_meta)
        # Manilpulate ACLs
        self.acl_table.clicked.connect(self.edit_permission)
        self.add_acl_button.clicked.connect(self.update_permission)

    def update_input_path(self, irods_path):
        """Set the input path to a niew path and loads the table."""
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

    def folder_upload(self):
        """Select a folder and upload."""
        self.error_label.clear()
        select_dir = PyQt6.QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        path = self._fs_select(select_dir)
        if path is not None:
            self._upload(path)

    def file_upload(self):
        """Select a file and upload."""
        self.error_label.clear()
        select_file = PyQt6.QtWidgets.QFileDialog.getOpenFileName(self, "Open Filie")
        path = self._fs_select(select_file)
        if path is not None:
            self._upload(path)

    def download(self):
        """Download collection or data object."""
        if self._nothing_selected_error():
            return

        if self.browser_table.item(self.browser_table.currentRow(), 1) is not None:
            item_name = self.browser_table.item(self.browser_table.currentRow(), 1).text()
            path = IrodsPath(self.session, "/", *self.input_path.text().split("/"), item_name)
            overwrite = self.overwrite.isChecked()
            download_dir = get_downloads_dir()
            if overwrite:
                write = "All data will be updated."
            else:
                write = "Only new data will be added."
            info = f"Download data:\n{path}\n\nto\n\n{download_dir}\n\n{write}"

            try:
                if path.exists():
                    button_reply = PyQt6.QtWidgets.QMessageBox.question(self, "", info)
                    if button_reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
                        if Path(download_dir).joinpath(item_name).exists() and not overwrite:
                            raise FileExistsError
                        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.BusyCursor))
                        self.logger.info(
                            "Downloading %s to %s, overwrite %s", path, download_dir, str(overwrite)
                        )
                        download(self.session, path, download_dir, overwrite=overwrite)
                        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
                        self.error_label.setText("Data downloaded to: " + str(download_dir))
                else:
                    self.error_label.setText(f"Data {path.parent} does not exist.")
            except FileExistsError:
                self.error_label.setText(
                    f"Data already exists in {download_dir}."
                    + ' Check "overwrite" to overwrite the data.'
                )
            except Exception as err:
                self.logger.exception("Downloading %s failed: %s", path, err)
                self.error_label.setText(f"Could not download {path}. Consult the logs.")

    def delete_data(self):
        """Delete selected data in the delete_browser."""
        if self._nothing_selected_error():
            return

        if self.browser_table.item(self.browser_table.currentRow(), 1) is not None:
            item_name = self.browser_table.item(self.browser_table.currentRow(), 1).text()
            irods_path = IrodsPath(self.session, "/", *self.input_path.text().split("/"), item_name)
            quit_msg = f"Are you sure you want to delete {str(irods_path)}?"
            reply = PyQt6.QtWidgets.QMessageBox.critical(
                self,
                "Message",
                quit_msg,
                PyQt6.QtWidgets.QMessageBox.StandardButton.Yes,
                PyQt6.QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
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
            and tab_name not in self.updated_info_tabs
        ):
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

    def set_icat_meta(self):
        """Button metadata set."""
        try:
            self._metadata_edits("set")
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
    def edit_metadata(self, index):
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
    def edit_permission(self, index):
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

        if acc_name in ("inherit", "noinherit"):
            if irods_path.dataobject_exists():
                self.error_label.setText("WARNING: (no)inherit is not applicable to data objects.")
                return
        elif user_name == "":
            self.error_label.setText("Please provide a user.")
            return
        elif acc_name == "":
            self.error_label.setText("Please provide an access level from the menu.")
            return
        recursive = self.recurisive_box.currentText() == "True"
        try:
            perm = Permissions(self.session, get_irods_item(irods_path))
            perm.set(perm=acc_name, user=user_name, zone=user_zone, recursive=recursive)
            if acc_name == "null":
                self.logger.info(
                    "Delete access (%s, %s, %s, %s) for %s",
                    acc_name, user_name, user_zone, str(recursive), str(irods_path)
                )
            else:
                self.logger.info(
                    "Add/change access of %s to (%s, %s, %s, %s)",
                    str(irods_path), acc_name, user_name, user_zone, str(recursive)
                )
            self._fill_acls_tab(irods_path)
        except irods.exception.CAT_INVALID_USER:
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

    def _get_item_path(self, row):
        item_name = self.browser_table.item(row, 1).text()
        return IrodsPath(self.session, "/", *self.input_path.text().split("/"), item_name)

    def _nothing_selected_error(self):
        self.error_label.clear()
        if self.browser_table.currentRow() == -1:
            self.error_label.setText("Please select an item from the table.")
            return True
        return False

    def _update_last_selected_row(self):
        self.last_selected_row = self.current_selected_row
        self.current_selected_row = self.browser_table.currentRow()
        # fill currently selected tab with info
        self.fill_info_tab_content()

    def _fill_replicas_tab(self, irods_path):
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

    def _fill_acls_tab(self, irods_path):
        """Populate the table in the ACLs tab.

        Parameters
        ----------
        irods_path : str
            Path of iRODS collection or data object selected.

        """
        self.acl_table.setRowCount(0)
        self.acl_user_field.clear()
        self.acl_zone_field.clear()
        self.acl_box.setCurrentText("")
        obj = None
        if irods_path.collection_exists():
            obj = irods_path.collection
            inheritance = f"{obj.inheritance}"
        elif irods_path.dataobject_exists():
            obj = irods_path.dataobject
            inheritance = ""
        if obj is not None:
            acls = Permissions(self.session, obj)
            acl_data = [(p.user_name, p.user_zone, p.access_name, inheritance) for p in acls]
            populate_table(self.acl_table, len(list(acls)), acl_data)
        self.acl_table.resizeColumnsToContents()
        self.owner_label.setText(f"{obj.owner_name}")

    def _fill_metadata_tab(self, irods_path):
        """Populate the table in the metadata tab.

        Parameters
        ----------
        irods_path : str
            Full name of iRODS collection or data object selected.

        """
        self.meta_key_field.clear()
        self.meta_value_field.clear()
        self.meta_units_field.clear()
        item = None
        if irods_path.collection_exists():
            item = irods_path.collection
        elif irods_path.dataobject_exists():
            item = irods_path.dataobject
        if item is not None:
            meta = MetaData(item)
            populate_table(self.meta_table, len(list(meta)), meta)
        self.meta_table.resizeColumnsToContents()

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
        populate_textfield(self.preview_browser, content)
        self.preview_browser.verticalScrollBar().setValue(0)

    def _metadata_edits(self, operation):
        self.error_label.clear()
        if self._nothing_selected_error():
            return

        irods_path = self._get_item_path(self.browser_table.currentRow())
        new_key = self.meta_key_field.text()
        new_val = self.meta_value_field.text()
        new_units = self.meta_units_field.text()
        if new_key != "" and new_val != "":
            irods_path = self._get_item_path(self.browser_table.currentRow())
            if operation == "add":
                irods_path.meta.add(new_key, new_val, new_units)
                self.logger.info(
                    "Add metadata (%s, %s, %s) to %s", new_key, new_val, new_units, irods_path
                )
            elif operation == "set":
                irods_path.meta.set(new_key, new_val, new_units)
                self.logger.info(
                    "Set all metadata with key %s to (%s, %s, %s) for %s",
                    new_key, new_key, new_val, new_units, irods_path
                )
            elif operation == "delete":
                irods_path.meta.delete(new_key, new_val, new_units)
                self.logger.info(
                    "Delete metadata (%s, %s, %s) from %s",
                    new_key, new_val, new_units, irods_path
                )
            self._fill_metadata_tab(irods_path)

    def _fs_select(self, path_select):
        """Retrieve the path (file or folder) from a QFileDialog.

        Parameters
        ----------
        path_select: PyQt6.QtWidgets.QFileDialog.getExistingDirectory
                     PyQt6.QtWidgets.QFileDialog.getOpenFileName

        """
        yes_button = PyQt6.QtWidgets.QMessageBox.StandardButton.Yes
        if isinstance(path_select, tuple):
            path = path_select[0]
        else:
            path = path_select

        if path != "":
            if self.overwrite.isChecked():
                write = "All data will be updated."
            else:
                write = "Only new data will be added."
            info = f"Upload data:\n{path}\n\nto\n{self.input_path.text()}\n\n{write}"
            reply = PyQt6.QtWidgets.QMessageBox.question(self, "", info)
            if reply == yes_button:
                return Path(path)
        return None

    def _upload(self, source):
        """Upload data to path in input_path."""
        overwrite = self.overwrite.isChecked()
        parent_path = IrodsPath(self.session, "/", *self.input_path.text().split("/"))

        try:
            if parent_path.joinpath(source.name).exists() and not overwrite:
                raise FileExistsError
            self.logger.info(
                "Uploading %s to %s, overwrite %s", source, parent_path, str(overwrite)
            )
            upload(self.session, source, parent_path, overwrite=overwrite)
            self.load_browser_table()
        except FileExistsError:
            self.error_label.setText(
                f"Data already exists in {parent_path}."
                + ' Check "overwrite" to overwrite the data.'
            )
        except irods.exception.CAT_NO_ACCESS_PERMISSION:
            self.error_label.setText(f"No permission to upload data to {parent_path}.")
            self.logger.info(
                "Uploading %s to %s, overwrite %s failed. No permissions.",
                source,
                parent_path,
                str(overwrite),
            )
        except Exception as err:
            self.logger.exception("Failed to upload %s to %s: %s", source, parent_path, err)
            self.error_label.setText(f"Failed to upload {source}. Consult the logs.")

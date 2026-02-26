"""GUI logic for browser."""

import logging

import irods.exception
import PySide6.QtCore
import PySide6.QtWidgets
from ibridges import IrodsPath

from ibridgesgui.gui_utils import get_irods_item, populate_table, populate_textfield
from ibridgesgui.popup_widgets import CreateCollection, DownloadData, Rename, UploadData

from .browser_model import BrowserModel
from .irods_browser_service import IrodsBrowserService


class BrowserController:
    """Orchestrates UI, model and iRODS service for the Browser tab."""

    def __init__(self, ui: PySide6.QtWidgets.QWidget, session, app_name: str):
        """Init."""
        self.ui = ui
        self.logger = logging.getLogger(app_name)
        self.service = IrodsBrowserService(session, self.logger)

        home = self.service.home_path()
        self.model = BrowserModel(home)

    # ----------------------------------------------------------------------
    # Initialization
    # ----------------------------------------------------------------------

    def init_browser(self) -> None:
        """Init buttons and signals."""
        self._connect_signals()
        self._set_path(self.model.current_path)

    def _connect_signals(self) -> None:
        # navigation
        self.ui.input_path.returnPressed.connect(self._refresh_browser)
        self.ui.refresh_button.clicked.connect(self._refresh_browser)
        self.ui.home_button.clicked.connect(lambda: self._set_path(self.service.home_path()))
        self.ui.parent_button.clicked.connect(self._go_to_parent)

        # CRUD
        self.ui.upload_button.clicked.connect(self.upload_data)
        self.ui.download_button.clicked.connect(self.download_data)
        self.ui.create_coll_button.clicked.connect(self.create_collection)
        self.ui.rename_button.clicked.connect(self.rename_item)
        self.ui.delete_button.clicked.connect(self.delete_data)

        # table / info tabs
        self.ui.browser_table.doubleClicked.connect(self._open_selected_path)
        self.ui.browser_table.clicked.connect(self._on_row_clicked)
        self.ui.info_tabs.currentChanged.connect(self._fill_current_info_tab)

        # metadata
        self.ui.meta_table.clicked.connect(self._load_metadata_item)
        self.ui.add_meta_button.clicked.connect(lambda: self._metadata_edits("add"))
        self.ui.update_meta_button.clicked.connect(lambda: self._metadata_edits("update"))
        self.ui.delete_meta_button.clicked.connect(lambda: self._metadata_edits("delete"))

        # ACLs
        self.ui.acl_table.clicked.connect(self._load_permission)
        self.ui.add_acl_button.clicked.connect(self._update_permission)

    # ----------------------------------------------------------------------
    # Path handling
    # ----------------------------------------------------------------------

    def _set_path(self, irods_path: IrodsPath) -> None:
        """Central path setter using the model."""
        self.model.set_path(irods_path)
        self.ui.input_path.setText(str(irods_path))
        self._load_browser_table()

    def _refresh_browser(self) -> None:
        path = self.service.path_from_text(self.ui.input_path.text())
        self._set_path(path)

    def _go_to_parent(self) -> None:
        parent = self.service.parent_path(self.ui.input_path.text())
        self._set_path(parent)

    def _open_selected_path(self) -> None:
        row = self.ui.browser_table.currentRow()
        irods_path = self._item_path(row)
        if irods_path and irods_path.collection_exists():
            self._set_path(irods_path)

    # ----------------------------------------------------------------------
    # CRUD operations
    # ----------------------------------------------------------------------

    def create_collection(self) -> None:
        """Call widget to create new collection."""
        self.ui.error_label.clear()
        path = self.model.current_path
        dialog = CreateCollection(path, self.logger)
        dialog.exec()
        self._set_path(path)

    def rename_item(self) -> None:
        """Call widget to rename item."""
        if not self._validate_selection():
            return
        row = self.ui.browser_table.currentRow()
        irods_path = self._item_path(row)
        dialog = Rename(irods_path, self.logger)
        dialog.exec()
        self._set_path(self.model.current_path)

    def download_data(self) -> None:
        """Call widget to download."""
        if not self._validate_selection():
            return
        row = self.ui.browser_table.currentRow()
        irods_path = self._item_path(row)
        dialog = DownloadData(self.logger, irods_path.session, irods_path)
        dialog.exec()

    def upload_data(self) -> None:
        """Call widget to upload."""
        path = self.model.current_path
        if not path.collection_exists():
            self.ui.error_label.setText(f"{path} is not a collection. Cannot upload data.")
            return
        dialog = UploadData(self.logger, path.session, path)
        dialog.exec()
        self._refresh_browser()

    def delete_data(self) -> None:
        """Confirm delete."""
        if not self._validate_selection():
            return
        row = self.ui.browser_table.currentRow()
        irods_path = self._item_path(row)

        reply = PySide6.QtWidgets.QMessageBox.critical(
            self.ui,
            "Message",
            f"Are you sure you want to delete {irods_path}?",
            PySide6.QtWidgets.QMessageBox.Yes,
            PySide6.QtWidgets.QMessageBox.No,
        )
        if reply != PySide6.QtWidgets.QMessageBox.Yes:
            return

        try:
            irods_path.remove()
            self.logger.info("Deleted %s", irods_path)
            self._refresh_browser()
        except (irods.exception.CAT_NO_ACCESS_PERMISSION, PermissionError):
            self.ui.error_label.setText(f"No permissions to delete {irods_path}")
        except Exception:
            self.logger.exception("FAILED: Delete %s", irods_path)
            self.ui.error_label.setText(f"FAILED: Delete {irods_path}. Consult logs.")

    # ----------------------------------------------------------------------
    # Browser table
    # ----------------------------------------------------------------------

    def _load_browser_table(self) -> None:
        self.ui.error_label.clear()
        self._clear_info_tabs()

        path = self.model.current_path
        if not path.collection_exists():
            self.ui.browser_table.setRowCount(0)
            self.ui.error_label.setText(f"Collection does not exist: {path}")
            return

        try:
            rows = self.service.list_table_rows(path)
            populate_table(self.ui.browser_table, len(rows), rows)
        except Exception as err:
            self.logger.exception("Cannot load browser.")
            self.ui.browser_table.setRowCount(0)
            self.ui.error_label.setText(f"Cannot load browser table for {path}: {err}")

    # ----------------------------------------------------------------------
    # Info tabs (with caching)
    # ----------------------------------------------------------------------

    def _fill_current_info_tab(self) -> None:
        if not self._validate_selection():
            return

        row = self.ui.browser_table.currentRow()
        irods_path = self._item_path(row)
        tab_name = self.ui.info_tabs.currentWidget().objectName()

        if self.model.needs_tab_update(tab_name):
            try:
                self._fill_tab(tab_name, irods_path, row)
                self.model.mark_tab_updated(tab_name)
            except Exception as err:
                self.logger.exception("Error loading %s of %s", tab_name, irods_path)
                self.ui.error_label.setText(f"Error loading {tab_name}: {err!r}")

    def _fill_tab(self, tab_name: str, irods_path: IrodsPath, row: int) -> None:
        if tab_name == "metadata":
            cached = self.model.get_cached_metadata(row)
            if cached is None:
                data = list(irods_path.meta)
                self.model.cache_metadata(row, data)
            else:
                data = cached
            self._render_metadata(data, irods_path)

        elif tab_name == "permissions":
            cached = self.model.get_cached_acls(row)
            if cached is None:
                acls = self.service.get_acls(irods_path)
                clean = [
                    (
                        user,
                        zone,
                        "read"
                        if perm == "read_object"
                        else "write"
                        if perm == "modify_object"
                        else perm,
                        status,
                    )
                    for user, zone, perm, status in acls
                ]
                self.model.cache_acls(row, clean)
            else:
                clean = cached
            self._render_acls(clean, irods_path)

        elif tab_name == "replicas":
            cached = self.model.get_cached_replicas(row)
            if cached is None:
                rows = self.service.replicas_for(irods_path)
                self.model.cache_replicas(row, rows)
            else:
                rows = cached
            self._render_replicas(rows)

        elif tab_name == "preview":
            cached = self.model.get_cached_preview(row)
            if cached is None:
                content = self._compute_preview(irods_path)
                self.model.cache_preview(row, content)
            else:
                content = cached
            populate_textfield(self.ui.preview_browser, content)

    # ----------------------------------------------------------------------
    # Rendering helpers
    # ----------------------------------------------------------------------

    def _render_metadata(self, data, irods_path):
        self.ui.meta_key_field.clear()
        self.ui.meta_value_field.clear()
        self.ui.meta_units_field.clear()
        self.ui.no_meta_label.clear()

        populate_table(self.ui.meta_table, len(data), data)
        if len(data) == 0:
            self.ui.no_meta_label.setText(f"Metadata for {irods_path} is empty.")
        self.ui.meta_table.resizeColumnsToContents()

    def _render_acls(self, clean, irods_path):
        self.ui.acl_table.setRowCount(0)
        self.ui.acl_user_field.clear()
        self.ui.acl_zone_field.clear()
        self.ui.acl_box.clear()
        self.ui.recursive_box.setEnabled(irods_path.collection_exists())

        obj_acl = ["read", "write", "own", "delete"]
        coll_acl = obj_acl + [
            "Newly added items to collection will inherit permissions",
            "Remove inheritance.",
        ]

        for item in coll_acl if irods_path.collection_exists() else obj_acl:
            self.ui.acl_box.addItem(item)
        self.ui.acl_box.setEnabled(True)

        populate_table(self.ui.acl_table, len(clean), clean)
        self.ui.acl_table.resizeColumnsToContents()

        obj = get_irods_item(irods_path)
        self.ui.owner_label.setText(obj.owner_name)

    def _render_replicas(self, rows):
        self.ui.replica_table.setRowCount(0)
        if rows:
            populate_table(self.ui.replica_table, len(rows), rows)
        self.ui.replica_table.resizeColumnsToContents()

    def _compute_preview(self, irods_path):
        if irods_path.collection_exists():
            subcolls, objs = self.service.list_collection(irods_path)
            content = ["Collections:", "-----------------"]
            content.extend([sc.name for sc in subcolls])
            content.extend(["", "DataObjects:", "-----------------"])
            content.extend([do.name for do in objs])
            return content

        if irods_path.dataobject_exists():
            ext = irods_path.name.split(".")[-1] if "." in irods_path.name else ""
            if ext in ("txt", "json", "csv"):
                try:
                    self.service.stream_obj(irods_path)
                    return []
                except Exception as error:
                    return [
                        f"No Preview for: {irods_path}",
                        repr(error),
                        "Storage resource might be down.",
                    ]
            return [f"No Preview for: {irods_path}"]

        return [f"No Preview for: {irods_path}"]

    # ----------------------------------------------------------------------
    # Metadata editing
    # ----------------------------------------------------------------------

    def _load_metadata_item(self, index: PySide6.QtCore.QModelIndex):
        self.ui.error_label.clear()
        row = index.row()
        key = self.ui.meta_table.item(row, 0).text()
        val = self.ui.meta_table.item(row, 1).text()
        units = self.ui.meta_table.item(row, 2).text() if self.ui.meta_table.item(row, 2) else ""
        self.ui.meta_key_field.setText(key)
        self.ui.meta_value_field.setText(val)
        self.ui.meta_units_field.setText(units)

    def _metadata_edits(self, operation: str):
        self.ui.error_label.clear()
        if not self._validate_selection():
            return

        row = self.ui.browser_table.currentRow()
        irods_path = self._item_path(row)

        new_key = self.ui.meta_key_field.text()
        new_val = self.ui.meta_value_field.text()
        new_units = self.ui.meta_units_field.text()

        try:
            if operation == "add":
                self.service.add_metadata(irods_path, new_key, new_val, new_units)
                self.logger.info(
                    "Add metadata (%s, %s, %s) to %s", new_key, new_val, new_units, irods_path
                )
            elif operation == "update":
                mrow = self.ui.meta_table.currentRow()
                old_key = self.ui.meta_table.item(mrow, 0).text()
                old_val = self.ui.meta_table.item(mrow, 1).text()
                old_units = self.ui.meta_table.item(mrow, 2).text()
                self.service.update_metadata(irods_path, old_key, new_key, new_val, new_units)
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
            elif operation == "delete":
                self.service.delete_metadata(irods_path, new_key, new_val, new_units)
                self.logger.info(
                    "Delete metadata (%s, %s, %s) from %s", new_key, new_val, new_units, irods_path
                )

            # invalidate cache for this row
            self.model.metadata_cache.pop(row, None)
            if 'metadata' in self.model.updated_info_tabs:
                self.model.updated_info_tabs.remove('metadata')

            self._fill_current_info_tab()

        except Exception as error:
            self.ui.error_label.setText(repr(error))

    # ----------------------------------------------------------------------
    # ACLs
    # ----------------------------------------------------------------------

    def _load_permission(self, index: PySide6.QtCore.QModelIndex):
        self.ui.error_label.clear()
        row = index.row()
        user = self.ui.acl_table.item(row, 0).text()
        zone = self.ui.acl_table.item(row, 1).text()
        acc = self.ui.acl_table.item(row, 2).text()

        self.ui.acl_user_field.setText(user)
        self.ui.acl_zone_field.setText(zone)
        self.ui.acl_box.setCurrentText(acc)
        self.ui.recursive_box.setCurrentText("False")

    def _update_permission(self) -> None:
        if not self._validate_selection():
            return

        row = self.ui.browser_table.currentRow()
        irods_path = self._item_path(row)

        user = self.ui.acl_user_field.text()
        zone = self.ui.acl_zone_field.text()
        acc_label = self.ui.acl_box.currentText()
        recursive = self.ui.recursive_box.currentText() == "True"

        label_to_acl = {
            "Newly added items to collection will inherit permissions": "inherit",
            "Remove inheritance.": "noinherit",
            "delete": "null",
        }
        acl_value = label_to_acl.get(acc_label, acc_label)

        if acl_value in ("inherit", "noinherit") and irods_path.dataobject_exists():
            self.ui.error_label.setText("WARNING: (no)inherit is not applicable to data objects.")
            return

        if acl_value not in ("inherit", "noinherit") and not user:
            self.ui.error_label.setText("Please provide a user.")
            return

        if not acc_label:
            self.ui.error_label.setText("Please provide an access level.")
            return

        try:
            self.service.set_acl(
                irods_path,
                user_name=user,
                user_zone=zone,
                access=acl_value,
                recursive=recursive,
            )

            # invalidate cache for this row
            self.model.acl_cache.pop(row, None)
            if "permissions" in self.model.updated_info_tabs:
                self.model.updated_info_tabs.remove("permissions")

            self._fill_current_info_tab()

        except (irods.exception.CAT_INVALID_USER, irods.exception.SYS_NOT_ALLOWED):
            self.ui.error_label.setText(f"Cannot update ACLs. {user}#{zone} not known.")
        except irods.exception.MSI_OPERATION_NOT_ALLOWED:
            self.ui.error_label.setText("iRODS server does not allow editing permissions.")
        except Exception as err:
            self.logger.exception("Permissions error for %s", irods_path)
            self.ui.error_label.setText(f"Error editing permissions: {err!r}")

    # ----------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------

    def _on_row_clicked(self) -> None:
        row = self.ui.browser_table.currentRow()
        if row < 0:
            return
        self.model.on_row_clicked(row)
        self._fill_current_info_tab()

    def _item_path(self, row: int) -> IrodsPath | None:
        if row is None or row < 0:
            return None
        item = self.ui.browser_table.item(row, 1)
        if not item:
            return None
        name = item.text()
        return self.model.current_path / name

    def _validate_selection(self) -> bool:
        self.ui.error_label.clear()
        if self.ui.browser_table.currentRow() == -1:
            self.ui.error_label.setText("Please select an item from the table.")
            return False
        return True

    def _clear_info_tabs(self) -> None:
        self.ui.acl_table.setRowCount(0)
        self.ui.meta_table.setRowCount(0)
        self.ui.replica_table.setRowCount(0)
        self.ui.preview_browser.clear()
        self.ui.no_meta_label.clear()

"""GUI logic for browser."""

import logging
from typing import Optional

import irods.exception
import PySide6.QtWidgets
from ibridges import IrodsPath

from ibridgesgui.browsertab.browser_model import BrowserModel
from ibridgesgui.browsertab.irods_browser_service import IrodsBrowserService
from ibridgesgui.gui_utils import populate_table
from ibridgesgui.popup_widgets import CreateCollection, DownloadData, Rename, UploadData


class BrowserController:
    """Orchestrates UI, model and iRODS service for the Browser tab."""

    def __init__(self, ui: PySide6.QtWidgets.QWidget, session, app_name: str):
        """Init."""
        self.ui = ui
        self.logger = logging.getLogger(app_name)
        self.service = IrodsBrowserService(session, self.logger)

        home = self.service.home_path()
        self.model = BrowserModel(home)
        self.ui.error_label.setWordWrap(True)

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
        self.ui.info_tabs.currentChanged.connect(self.ui.on_tab_changed)

        # metadata
        self.ui.meta_table.clicked.connect(self.ui.load_metadata_item)
        self.ui.add_meta_button.clicked.connect(lambda: self._metadata_edits("add"))
        self.ui.update_meta_button.clicked.connect(lambda: self._metadata_edits("update"))
        self.ui.delete_meta_button.clicked.connect(lambda: self._metadata_edits("delete"))

        # ACLs
        self.ui.acl_table.clicked.connect(self.ui.load_permission)
        self.ui.add_acl_button.clicked.connect(self._update_permission)

    def _set_path(self, irods_path: IrodsPath) -> None:
        """Central path setter using the model."""
        self.model.set_path(irods_path)
        self.ui.input_path.setText(str(irods_path))
        self._load_browser_table()
        self.ui.browser_table.clearSelection()

    def _refresh_browser(self) -> None:
        path = self.service.path_from_text(self.ui.input_path.text())
        self.ui.browser_table.clearSelection()
        self._set_path(path)

    def _go_to_parent(self) -> None:
        parent = self.service.parent_path(self.ui.input_path.text())
        self._set_path(parent)

    def _open_selected_path(self) -> None:
        _, irods_path = self._current_selection()
        if irods_path is None:
            return
        if irods_path.collection_exists():
            self._set_path(irods_path)

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
        _, irods_path = self._current_selection()
        dialog = Rename(irods_path, self.logger)
        dialog.exec()
        self._set_path(self.model.current_path)

    def download_data(self) -> None:
        """Call widget to download."""
        if not self._validate_selection():
            return
        _, irods_path = self._current_selection()
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
        _, irods_path = self._current_selection()

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

    def _load_browser_table(self) -> None:
        self.ui.error_label.clear()
        self.ui.clear_info_tabs()

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

    def _fill_current_info_tab(self) -> None:
        if not self._validate_selection():
            return

        row = self.ui.browser_table.currentRow()
        irods_path = self._item_path(row)
        tab_name = self.ui.info_tabs.currentWidget().objectName()

        if self.model.needs_tab_update(tab_name):
            try:
                self._fill_tab(tab_name)
                self.model.mark_tab_updated(tab_name)
            except Exception as err:
                self.logger.exception("Error loading %s of %s", tab_name, irods_path)
                self.ui.error_label.setText(f"Error loading {tab_name}: {err!r}")

    def _fill_tab(self, tab_name):
        row, irods_path = self._current_selection()
        if tab_name == "metadata":
            self._fill_metadata_tab(irods_path, row)
        elif tab_name == "permissions":
            self._fill_acl_tab(irods_path, row)
        elif tab_name == "replicas":
            self._fill_replicas_tab(irods_path, row)
        elif tab_name == "preview":
            self._fill_preview_tab(irods_path, row)

    def _fill_metadata_tab(self, irods_path, row):
        if row not in self.model.metadata_cache:
            data = self.service.get_metadata(irods_path)
            self.model.cache_metadata(row, data)
        else:
            data = self.model.metadata_cache[row]

        self.ui.render_metadata(data, irods_path)

    def get_possible_acl_strings(self):
        """Retrieve a list of GUI accepted and cleaned iRODS ACL skills."""
        return self.service.get_acl_strings()

    def _fill_acl_tab(self, irods_path, row):
        if row not in self.model.acl_cache:
            acls = self.service.get_acls(irods_path)
            clean = self.service.normalize_acls(acls)
            self.model.cache_acls(row, clean)
        else:
            clean = self.model.acl_cache[row]

        self.ui.render_acls(clean, irods_path)

    def _fill_replicas_tab(self, irods_path, row):
        if row not in self.model.replica_cache:
            replicas = self.service.get_replicas(irods_path)
            self.model.cache_replicas(row, replicas)
        else:
            replicas = self.model.replica_cache[row]

        self.ui.render_replicas(replicas)

    def _fill_preview_tab(self, irods_path, row):
        if row not in self.model.preview_cache:
            content = self.service.compute_preview(irods_path)
            self.model.cache_preview(row, content)
        else:
            content = self.model.preview_cache[row]

        self.ui.preview_browser.setText("\n".join(content))

    def _update_permission(self) -> None:
        if not self._validate_selection():
            return
        row, irods_path = self._current_selection()
        user = self.ui.acl_user_field.text()
        zone = self.ui.acl_zone_field.text()
        acc_label = self.ui.acl_box.currentText()

        recursive_map = {
            "True": True,
            "False": False,
        }
        recursive = recursive_map.get(self.ui.recursive_box.currentText(), False)

        label_to_acl = {
            "Newly added items to collection will inherit permissions": "inherit",
            "Remove inheritance.": "noinherit",
            "delete": "null",
        }
        acl_value = label_to_acl.get(acc_label, acc_label)

        if acl_value in ("inherit", "noinherit") and irods_path.dataobject_exists():
            self.ui.error_label.setText(
                "WARNING: (no)inherit is not applicable to data objects."
            )
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

            # NEW: use model helper instead of manual cache manipulation
            self.model.invalidate_acls(row)

            self._fill_current_info_tab()

        except (irods.exception.CAT_INVALID_USER, irods.exception.SYS_NOT_ALLOWED):
            self.ui.error_label.setText(f"Cannot update ACLs. {user}#{zone} not known.")
        except irods.exception.MSI_OPERATION_NOT_ALLOWED:
            self.ui.error_label.setText("iRODS server does not allow editing permissions.")
        except Exception as err:
            self.logger.exception("Permissions error for %s", irods_path)
            self.ui.error_label.setText(f"Error editing permissions: {err!r}")

    def _metadata_edits(self, operation: str):
        self.ui.error_label.clear()
        if not self._validate_selection():
            return

        row, irods_path = self._current_selection()
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
                self.service.update_metadata(
                    irods_path,
                    old_key,
                    old_val,
                    old_units,
                    new_key,
                    new_val,
                    new_units,
                )

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
            self.model.invalidate_metadata(row)
            self._fill_current_info_tab()

        except Exception as err:
            self.logger.exception("Metadata error for %s", irods_path)
            self.ui.error_label.setText(f"Metadata error: {err!r}")

    def _on_row_clicked(self) -> None:
        row = self.ui.browser_table.currentRow()
        if row < 0:
            return
        self.model.on_row_clicked(row)
        self._fill_current_info_tab()

    def _item_path(self, row: int) -> Optional[IrodsPath]:
        if row < 0:
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

    def _current_selection(self):
        row = self.ui.browser_table.currentRow()
        return row, self._item_path(row)

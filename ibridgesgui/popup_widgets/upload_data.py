"""Dialog for uploading files or folders to iRODS."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from ibridges import upload
from ibridges.exception import DataObjectExistsError
from PySide6 import QtWidgets

from ibridgesgui.config import (
    config_get_last_upload_path,
    config_set_last_upload_path,
    get_last_ienv_path,
)
from ibridgesgui.gui_utils import combine_operations, validate_metadata, prep_session_for_copy
from ibridgesgui.popup_widgets.base import TransferDialogBase, UiDialogMixin
from ibridgesgui.threads import TransferDataThread
from ibridgesgui.ui_files.uploadData import Ui_uploadData


class UploadData(UiDialogMixin, TransferDialogBase, Ui_uploadData):
    """Dialog for uploading files to iRODS.

    Method groups:
    - table row management
    - metadata selection
    - file/folder selection
    - upload execution and progress reporting
    """

    ui_filename = "uploadData.ui"
    MAX_COL_WIDTHS = {0: 450, 1: 300}

    def __init__(self, logger, session, irods_path) -> None:
        """Init."""
        TransferDialogBase.__init__(self)
        UiDialogMixin._init_ui(self)

        self.logger = logger
        self.session = session
        self.irods_path = irods_path
        self.transfer_thread: Optional[TransferDataThread] = None
        self.active_transfer = False

        self.destination_label.setText(str(irods_path))

        self.upload_button.clicked.connect(self._collect_upload_params)
        self.file_button.clicked.connect(self._select_files)
        self.folder_button.clicked.connect(self._select_folder)
        self.hide_button.clicked.connect(self.close)
        self.delete_row_button.clicked.connect(self._delete_selected_rows)

    def add_row(self, path: str, metadata: str) -> None:
        """Insert a new row into the upload table."""
        self.error_label.clear()
        if not path:
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(path))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(metadata))

        btn = QtWidgets.QPushButton("Metadata JSON")
        btn.state = "upload"  # type: ignore[attr-defined]
        btn.row = row  # type: ignore[attr-defined]
        btn.clicked.connect(lambda _, b=btn: self._toggle_metadata_button(b))

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(btn)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.table.setCellWidget(row, 2, container)

        self._resize_columns()

    def _delete_selected_rows(self) -> None:
        """Remove selected rows from the table."""
        rows = sorted(
            {idx.row() for idx in self.table.selectionModel().selectedRows()},
            reverse=True,
        )
        for row in rows:
            self.table.removeRow(row)

    def _resize_columns(self) -> None:
        """Resize table columns with maximum widths."""
        self.table.resizeColumnsToContents()
        for col, max_w in self.MAX_COL_WIDTHS.items():
            self.table.setColumnWidth(col, min(self.table.columnWidth(col), max_w))

    def _all_paths(self) -> List[str]:
        """Return all paths currently listed in the table."""
        paths = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            paths.append(item.text() if item else "")
        return paths

    def _toggle_metadata_button(self, btn: QtWidgets.QPushButton) -> None:
        """Switch between upload and delete metadata modes."""
        if getattr(btn, "state", "upload") == "upload":
            if self._upload_metadata(btn.row):  # type: ignore[attr-defined]
                btn.setText("❌")
                btn.state = "delete"  # type: ignore[attr-defined]
        else:
            self._clear_metadata(btn.row)  # type: ignore[attr-defined]
            btn.setText("Metadata JSON")
            btn.state = "upload"  # type: ignore[attr-defined]

    def _upload_metadata(self, row: int) -> bool:
        """Select a metadata file and assign it to the row."""
        self.error_label.clear()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Metadata File",
            "",
            "Metadata Files (*.json *.yaml *.yml);;All Files (*)",
        )

        try:
            if file_path and validate_metadata(Path(file_path)):
                self.table.item(row, 1).setText(file_path)
                self._resize_columns()
                return True
        except Exception as err:  # noqa: BLE001
            self.error_label.setText(str(err))
            return False

        return False

    def _clear_metadata(self, row: int) -> None:
        """Clear metadata for the given row."""
        self.table.item(row, 1).setText("")

    def _select_files(self) -> None:
        """Open file selector and add selected files."""
        last_path = config_get_last_upload_path() or Path("~").expanduser()
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Open File", dir=str(last_path))

        for selected_file in files:
            if selected_file in self._all_paths():
                continue
            config_set_last_upload_path(Path(selected_file).parent)
            self.add_row(selected_file, "")

        if files:
            config_set_last_upload_path(Path(files[-1]).parent)

    def _select_folder(self) -> None:
        """Open folder selector and add selected folder."""
        self.error_label.clear()
        last_path = config_get_last_upload_path() or Path("~").expanduser()
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", dir=str(last_path)
        )

        if not folder or folder in self._all_paths():
            return

        config_set_last_upload_path(Path(folder))
        self.add_row(folder, "")

    def _collect_upload_params(self) -> None:
        """Collect upload parameters from the table."""
        data: List[Tuple[Optional[Path], Optional[Path]]] = []

        for row in range(self.table.rowCount()):
            path_item = self.table.item(row, 0)
            meta_item = self.table.item(row, 1)

            path = Path(path_item.text()) if path_item and path_item.text() else None
            metadata = Path(meta_item.text()) if meta_item and meta_item.text() else None

            data.append((path, metadata))

        if not data:
            self.error_label.setText("Please select a file or folder to upload.")
            return

        self._start_upload(data)

    def _start_upload(self, data: List[Tuple[Optional[Path], Optional[Path]]]) -> None:
        """Start the upload process."""
        self.active_transfer = True
        self.set_wait_cursor()
        self.error_label.setText(f"Uploading to {self.irods_path} ...")
        env_path = prep_session_for_copy(self.session, self.error_label)
        if not env_path:
            self.force_unlock()
            return

        try:
            ops = combine_operations(
                [
                    upload(
                        path,
                        self.irods_path,
                        overwrite=self.overwrite.isChecked(),
                        dry_run=True,
                        metadata=metadata,
                    )
                    for path, metadata in data
                    if path is not None
                ]
            )

            if not ops.upload and not ops.meta_upload:
                self.error_label.setText("Data already present and up to date.")
                self.set_arrow_cursor()
                return

            self._enable_buttons(False)
            self.active_transfer = True

            self.transfer_thread = TransferDataThread(
                env_path, self.logger, ops, overwrite=self.overwrite.isChecked()
            )
            self.transfer_thread.result.connect(self._upload_finished)
            self.transfer_thread.current_progress.connect(self._upload_status)
            self.transfer_thread.start()

        except DataObjectExistsError:
            self.error_label.setText("Data already exists. Check 'overwrite' to overwrite.")
            self._enable_buttons(True)
            self.force_unlock()
        except Exception as err:  # noqa: BLE001
            self.error_label.setText(f"Could not start upload: {err}")
            self.force_unlock()
            self._enable_buttons(True)

    def _finish_upload(self) -> None:
        """Cleanup after upload thread finishes."""
        self.active_transfer = False
        self.set_arrow_cursor()
        self.transfer_thread = None

    def _upload_status(self, state) -> None:
        """Update progress bar and status text."""
        up_size, transferred, count, total, failed, md_state = state

        if up_size > 0:
            self.progress_bar.setValue(int(transferred * 100 / up_size))

        msg = f"{count} of {total} files; failed: {failed}."
        if md_state:
            msg += f" {md_state}"

        self.error_label.setText(msg)

    def _upload_finished(self, result: dict) -> None:
        """Handle upload completion."""
        self.active_transfer = False
        if result.get("error", "") == "":
            self.error_label.setText("Upload finished.")
        else:
            self.error_label.setText("Errors occurred during upload. Consult the logs.")
        self.hide_button.setEnabled(True)

    def _enable_buttons(self, enable: bool) -> None:
        """Enable or disable UI buttons."""
        self.upload_button.setEnabled(enable)
        self.folder_button.setEnabled(enable)
        self.file_button.setEnabled(enable)
        self.hide_button.setEnabled(enable)
        self.overwrite.setEnabled(enable)
        self.delete_row_button.setEnabled(enable)

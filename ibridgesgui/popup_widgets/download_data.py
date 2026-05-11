"""Dialog for downloading data from iRODS."""

from __future__ import annotations

from pathlib import Path

from ibridges import download
from PySide6 import QtCore, QtWidgets

from ibridgesgui.config import (
    config_get_last_download_path,
    config_set_last_download_path,
    get_last_ienv_path,
)
from ibridgesgui.popup_widgets.base import TransferDialogBase, UiDialogMixin
from ibridgesgui.threads import TransferDataThread
from ibridgesgui.ui_files.downloadData import Ui_downloadData


class DownloadData(UiDialogMixin, TransferDialogBase, Ui_downloadData):
    """Dialog for downloading data from iRODS.

    Method groups:
    - destination selection
    - metadata handling
    - download execution and progress reporting
    """

    ui_filename = "downloadData.ui"

    def __init__(self, logger, session, irods_path) -> None:
        """Init."""
        TransferDialogBase.__init__(self)
        UiDialogMixin._init_ui(self)

        self.logger = logger
        self.session = session
        self.irods_path = irods_path
        self.download_thread = None

        self.source_browser.append(self._irods_tree())

        timestamp = QtCore.QDateTime.currentDateTime().toString("MMddyyyy-hhmm")
        self.meta_filename = (
            f"ibridges_metadata_{self.irods_path.name.split('.')[0]}_{timestamp}.json"
        )
        self.meta_path: Path | None = None

        self.metadata.setText(f"Store metadata as\n{self.meta_filename}")

        self.folder_button.clicked.connect(self._select_folder)
        self.download_button.clicked.connect(self._collect_download_params)
        self.hide_button.clicked.connect(self.close)

        last_path = Path(config_get_last_download_path() or "")
        if last_path.is_dir():
            self.destination_label.setText(str(last_path))

    def _irods_tree(self) -> str:
        """Return a list of items inside the iRODS collection."""
        if self.irods_path.collection_exists():
            sub = [c.name for c in self.irods_path.collection.subcollections]
            objs = [o.name for o in self.irods_path.collection.data_objects]
            return "\n".join(sub + objs)
        return str(self.irods_path)

    def _select_folder(self) -> None:
        """Select the download destination."""
        self.error_label.clear()
        last_path = config_get_last_download_path() or Path("~").expanduser()

        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", dir=str(last_path)
        )
        if not folder:
            return

        self.destination_label.setText(folder)
        config_set_last_download_path(Path(folder))

    def _collect_download_params(self) -> None:
        """Collect parameters and start the download."""
        local_path = Path(self.destination_label.text())

        if not local_path.is_dir():
            self.error_label.setText("Select a valid download folder.")
            return

        if self.metadata.isChecked():
            self.meta_path = local_path / self.meta_filename

        self._start_download(local_path)

    def _start_download(self, local_path: Path) -> None:
        """Start the download process."""
        self.set_wait_cursor()
        self.error_label.setText(f"Downloading to {local_path} ...")

        env_path = Path(get_last_ienv_path())

        try:
            ops = download(
                self.irods_path,
                local_path,
                overwrite=self.overwrite.isChecked(),
                metadata=self.meta_path,
                dry_run=True,
            )

            if not ops.download and not ops.meta_download:
                self.error_label.setText("Data already present and up to date.")
                self.set_arrow_cursor()
                return

            self._enable_buttons(False)
            self.active_transfer = True

            self.download_thread = TransferDataThread(
                env_path, self.logger, ops, overwrite=self.overwrite.isChecked()
            )
            self.download_thread.result.connect(self._download_finished)
            self.download_thread.finished.connect(self._finish_download)
            self.download_thread.current_progress.connect(self._download_status)
            self.download_thread.start()

        except Exception as err:  # noqa: BLE001
            self.error_label.setText(f"Could not start download: {err}")
            self.set_arrow_cursor()
            self._enable_buttons(True)

    def _finish_download(self) -> None:
        """Cleanup after download thread finishes."""
        self.set_arrow_cursor()
        self.download_thread = None

    def _download_status(self, state) -> None:
        """Update progress bar and status text."""
        down_size, transferred, count, total, failed, md_state = state

        if down_size > 0:
            self.progress_bar.setValue(int(transferred * 100 / down_size))

        msg = f"{count} of {total} files; failed: {failed}."
        if md_state:
            msg += f" {md_state}"

        self.error_label.setText(msg)

    def _download_finished(self, result: dict) -> None:
        """Handle download completion."""
        self.active_transfer = False
        if result.get("error", "") == "":
            self.error_label.setText("Download finished.")
        else:
            self.error_label.setText("Errors occurred during download. Consult the logs.")

    def _enable_buttons(self, enable: bool) -> None:
        """Enable or disable UI buttons."""
        self.download_button.setEnabled(enable)
        self.folder_button.setEnabled(enable)
        self.overwrite.setEnabled(enable)
        self.hide_button.setEnabled(enable)
        self.metadata.setEnabled(enable)

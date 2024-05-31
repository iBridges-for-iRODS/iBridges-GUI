"""Thread classes for length iBridges functions."""

from pathlib import Path

from ibridges import IrodsPath, Session, download, search_data, sync
from irods.exception import CAT_NO_ACCESS_PERMISSION, NetworkException
from PyQt6.QtCore import QThread, pyqtSignal


class SearchThread(QThread):
    """Start iRODS search in an own thread using the same iRODS session."""

    succeeded = pyqtSignal(dict)

    def __init__(self, logger, ienv_path, path: str, checksum: str, key_vals: dict):
        """Pass searh parameters."""
        super().__init__()
        self.logger = logger
        self.thread_session = Session(irods_env=ienv_path)
        self.logger.debug("Search thread: created new session")
        self.sync_thread = None
        self.path = path
        self.checksum = checksum
        self.key_vals = key_vals

    def _delete_session(self):
        del self.thread_session
        try:
            self.logger.error("Search thread: Thread session still exists.")
        except (NameError, AttributeError):
            self.logger.debug("Search thread: Thread session successfully deleted.")

    def run(self):
        """Run the thread."""
        search_out = {}
        try:
            search_out["results"] = search_data(
                self.thread_session, path=self.path, checksum=self.checksum, key_vals=self.key_vals
            )
            self._delete_session()
        except NetworkException:
            self._delete_session()
            search_out["error"] = "Search takes too long. Please provide more parameters."
        self.succeeded.emit(search_out)

class TransferDataThread(QThread):
    """Upload data from local to iRODS."""

    transfer_out = {}
    transfer_out["error"] = ""
    succeeded = pyqtSignal(dict)
    current_progress = pyqtSignal(tuple)

    def init(self, ienv_path: Path, logger, diffs: dict, overwrite: bool):
        """Pass parameters."""
        super().__init__()
        self.logger = logger
        self.thread_session = Session(irods_env=ienv_path)
        self.logger.debug("Transfer data thread: Created new session.")
        self.diffs = diffs
        self.overwrite = overwrite

    def _delete_session(self):
        try:
            del self.thread_session
            self.logger.error("Transfer data thread: Thread session still exists.")
        except (NameError, AttributeError):
            self.logger.debug("Transfer data thread: Thread session successfully deleted.")

    def run(self):
        """Run the thread."""
        coll_count = 1
        coll_failed = 0
        count = 1
        failed = 0
        for coll in diff['create_collection']:
            try:    
                IrodsPath(session, coll).create_collection()
                coll_count+=1
                self.logger.info("Transfer data thread: Created collection %s", coll)
            except Exception as error:
                coll_failed += 1
                self.logger.exception("Transfer data thread: Could not create  %s; %s",
                                      coll, repr(error))
                transfer_out["error"] = (
                        transfer_out["error"]
                        + f"\nTransfer failed Cannot create {str(irods_path)}: {repr(error)}"
                        )
            self.current_progress.emit(coll_count, coll_failed, 0, 0)

        for local_path, irods_path in diff['upload']:
            try:
                upload(session, local_path, irods_path, resc_name = self.diff['resc_name'],
                        overwrite=self.overwrite, options = self.diff['options'])
                count+=1
                self.logger.info("Transfer data thread: Transfer %s -->  %s, overwrite %s",
                                 local_path, irods_path, self.overwrite)
            except Exception as error:
                failed+=1
                self.logger.exception("Transfer data thread: Could not transfer  %s --> %s; %s",
                                      local_path, irods_path, repr(error))
                transfer_out["error"] = (
                         transfer_out["error"]
                         + f"\nTransfer failed Cannot create {str(irods_path)}: {repr(error)}"
                         )
            self.current_progress.emit(coll_count, coll_failed, count, failed)
        self._delete_session()
        self.succeeded.emit(transfer_out)


class DownloadThread(QThread):
    """Download from iRODS to local FS."""

    succeeded = pyqtSignal(dict)
    current_progress = pyqtSignal(tuple)

    def __init__(self, ienv_path, logger, irods_paths: list, local_path: Path, overwrite: bool):
        """Pass download parameters."""
        super().__init__()
        self.logger = logger
        self.thread_session = Session(irods_env=ienv_path)
        self.logger.debug("Download thread: Created new session.")
        self.irods_paths = irods_paths
        self.local_path = local_path
        self.overwrite = overwrite

    def _delete_session(self):
        try:
            del self.thread_session
            self.logger.error("Download thread: Thread session still exists.")
        except (NameError, AttributeError):
            self.logger.debug("Download thread: Thread session successfully deleted.")

    def run(self):
        """Run the thread."""
        download_out = {}
        download_out["error"] = ""
        count = 1
        failed = 0

        for irods_path in self.irods_paths:
            if irods_path.exists():
                try:
                    download(self.thread_session, irods_path, self.local_path, self.overwrite)
                    self.logger.info(
                        "Downloading %s to %s, overwrite %s",
                        str(irods_path),
                        self.local_path,
                        self.overwrite,
                    )
                    count += 1
                except Exception as error:
                    failed += 1
                    self.logger.exception("Download failed: %s; %s", str(irods_path), repr(error))
                    download_out["error"] = (
                        download_out["error"]
                        + f"\nDownload failed {str(irods_path)}: {repr(error)}"
                    )
            else:
                failed += 1
                download_out["error"] = (
                    download_out["error"] + f"\nDownload failed. {str(irods_path)} does not exist."
                )
                self.logger.exception("Download failed: %s does not exist", str(irods_path))
            self.current_progress.emit((self.local_path, len(self.irods_paths), count, failed))
        self._delete_session()
        self.succeeded.emit(download_out)


class SyncThread(QThread):
    """Sync between iRODS and local FS."""

    succeeded = pyqtSignal(dict)

    def __init__(self, ienv_path, logger, source, target, dry_run: bool):
        """Pass download parameters."""
        super().__init__()

        self.logger = logger
        self.thread_session = Session(irods_env=ienv_path)
        self.logger.debug("Sync thread: created new session")
        self.source = source
        self.target = target
        self.dry_run = dry_run

    def _delete_session(self):
        del self.thread_session
        try:
            self.logger.error("Sync thread: Thread session still exists.")
        except (NameError, AttributeError):
            self.logger.debug("Sync thread: Thread session successfully deleted.")

    def run(self):
        """Run the thread."""
        sync_out = {}
        sync_out["error"] = ""

        try:
            result = sync(
                self.thread_session,
                self.source,
                self.target,
                dry_run=self.dry_run,
                copy_empty_folders=True,
            )
            self.logger.info(
                "Sync %s to %s, dry_run %s", str(self.source), str(self.target), str(self.dry_run)
            )
            if self.dry_run:
                sync_out["result"] = result

        except PermissionError as error:
            sync_out["error"] = f"Sync failed. No access to {error.filename}."
            self.logger.exception(
                "Sync failed: %s --> %s; %s", str(self.source), str(self.target), repr(error)
            )
        except CAT_NO_ACCESS_PERMISSION as error:
            sync_out["error"] = (
                "There is data in the iRODS collection which you are not allowed to access."
            )
            self.logger.exception(
                "Sync failed: %s --> %s; %s", str(self.source), str(self.target), repr(error)
            )
        except Exception as error:
            self.logger.exception(
                "Sync failed: %s --> %s; %s", str(self.source), str(self.target), repr(error)
            )
            sync_out["error"] = (
                sync_out["error"]
                + f"\nSync failed: {str(self.source)} --> {str(self.target)}: {repr(error)}"
            )
        self._delete_session()
        self.succeeded.emit(sync_out)

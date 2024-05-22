"""Thread classes for length iBridges functions."""
from pathlib import Path

from irods.exception import NetworkException, CAT_NO_ACCESS_PERMISSION
from PyQt6.QtCore import QThread, pyqtSignal

from ibridges import search_data, download, sync_data

class SearchThread(QThread):
    """Start iRODS search in an own thread using the same iRODS session."""

    succeeded = pyqtSignal(dict)

    def __init__(self, session, path: str, checksum: str, key_vals: dict):
        """Pass searh parameters."""
        super().__init__()
        self.session = session
        self.sync_thread = None
        self.path = path
        self.checksum = checksum
        self.key_vals = key_vals

    def run(self):
        """Run the thread."""
        search_out = {}
        try:
            search_out['results'] = search_data(self.session, path=self.path,
                                       checksum=self.checksum, key_vals=self.key_vals)
        except NetworkException:
            search_out['error'] = "Search takes too long. Please provide more parameters."
        self.succeeded.emit(search_out)

class DownloadThread(QThread):
    """Download from iRODS to local FS."""

    succeeded = pyqtSignal(dict)
    current_progress = pyqtSignal(tuple)

    def __init__(self, session, logger,
                 irods_paths: list, local_path: Path, overwrite: bool):
        """Pass download parameters."""
        super().__init__()
        self.session = session
        self.logger = logger
        self.irods_paths = irods_paths
        self.local_path = local_path
        self.overwrite = overwrite

    def run(self):
        """Run the thread."""
        download_out = {}
        download_out["error"] = ""
        count = 1
        failed = 0

        for irods_path in self.irods_paths:
            if irods_path.exists():
                try:
                    download(self.session, irods_path, self.local_path, self.overwrite)
                    self.logger.info("Downloading %s to %s, overwrite %s",
                                    str(irods_path), self.local_path, self.overwrite)
                    count+=1
                except Exception as error:
                    failed+=1
                    self.logger.error("Download failed: %s; %s", str(irods_path), repr(error))
                    download_out["error"] = download_out["error"] + \
                                            f"\nDownload failed {str(irods_path)}: {repr(error)}"
            else:
                failed+=1
                download_out["error"] = download_out["error"] + \
                                        f"\nDownload failed. {str(irods_path)} does not exist."
                self.logger.error("Download failed: %s does not exist", str(irods_path))
            self.current_progress.emit((self.local_path,len(self.irods_paths), count, failed))
        self.succeeded.emit(download_out)

class SyncThread(QThread):
    """Sync between iRODS and local FS."""

    succeeded = pyqtSignal(dict)

    def __init__(self, session, logger, source, target, dry_run: bool):
        """Pass download parameters."""
        super().__init__()
        self.session = session
        self.logger = logger
        self.source = source
        self.target = target
        self.dry_run = dry_run

    def run(self):
        """Run the thread."""
        sync_out = {}
        sync_out["error"] = ""

        try:
            result = sync_data(self.session, self.source, self.target,
                                dry_run=self.dry_run, copy_empty_folders=True)
            self.logger.info("Sync %s to %s, dry_run %s",
                             str(self.source), str(self.target), str(self.dry_run))
            if self.dry_run:
                sync_out["result"] = result
        except PermissionError as error:
            sync_out["error"] = f"Sync failed. No access to {error.filename}."
            self.logger.exception("Sync failed: %s --> %s; %s",
                                str(self.source), str(self.target), repr(error))
        except CAT_NO_ACCESS_PERMISSION as error:
            sync_out["error"] = \
                    "There is data in the iRODS collection you are not allowed to access."
            self.logger.exception("Sync failed: %s --> %s; %s",
                                str(self.source), str(self.target), repr(error))
        except Exception as error:
            self.logger.exception("Sync failed: %s --> %s; %s",
                                str(self.source), str(self.target), repr(error))
            sync_out["error"] = sync_out["error"] + \
                                    f"\nSync failed: {str(self.source)} --> {str(self.target)}: {repr(error)}"
        self.succeeded.emit(sync_out)

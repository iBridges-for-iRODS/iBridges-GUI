"""Thread classes for length iBridges functions."""
from pathlib import Path

from ibridges import download, search_data
from irods.exception import NetworkException
from PyQt6.QtCore import QThread, pyqtSignal


class SearchThread(QThread):
    """Start iRODS search in an own thread using the same iRODS session."""

    succeeded = pyqtSignal(dict)

    def __init__(self, session, path: str, checksum: str, key_vals: dict):
        """Pass searh parameters."""
        super().__init__()
        self.session = session
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
                    self.logger.info("Download failed: %s; %s", str(irods_path), repr(error))
                download_out["error"] = download_out["error"] + \
                                        f"\nDownload failed {str(irods_path)}: {repr(error)}"
            else:
                failed+=1
                download_out["error"] = download_out["error"] + \
                                        f"\nDownload failed. {str(irods_path)} does not exist."
                self.logger.info("Download failed: %s does not exist", str(irods_path))
            self.current_progress.emit((self.local_path,len(self.irods_paths), count, failed))
        self.succeeded.emit(download_out)

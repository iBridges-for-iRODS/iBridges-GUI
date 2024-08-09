"""Thread classes for length iBridges functions."""

from pathlib import Path

from ibridges import Session, search_data, sync
from ibridges.executor import Operations, _obj_get, _obj_put
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
        self.thread_session.close()
        if self.thread_session.irods_session is None:
            self.logger.debug("Search thread: Thread session successfully deleted.")
        else:
            self.logger.debug("Search thread: Thread session still exists.")

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
    """Transfer data between local and iRODS."""

    succeeded = pyqtSignal(dict)
    current_progress = pyqtSignal(list)

    def __init__(self, ienv_path: Path, logger, ops: Operations, overwrite: bool):
        """Pass parameters.

        ienv_path : Path
            path to the irods_environment.json to create a new session.
        logger : logging.Logger
            Logger
        ops : ibridges.Opertions
            Defines the data and metadata operations to perform. This thread currently uses:
            create_dir, create_collection, upload, download and execute_meta_download
            Please refer to the iBridges documentation: https://ibridges.readthedocs.io/
        """
        super().__init__()

        self.logger = logger
        self.thread_session = Session(irods_env=ienv_path)
        self.logger.debug("Transfer data thread: Created new session.")
        self.ops = ops
        self.overwrite = overwrite

        self.up_sizes = sum(lpath.stat().st_size for lpath, _ in self.ops.upload)
        self.down_sizes = sum(ipath.size for ipath, _ in self.ops.download)

    def _delete_session(self):
        self.thread_session.close()
        if self.thread_session.irods_session is None:
            self.logger.debug("Transfer data thread: Thread session successfully deleted.")
        else:
            self.logger.debug("Transfer data thread: Thread session still exists.")

    def run(self):
        """Run the thread."""
        obj_count = 0
        obj_failed = 0
        file_count = 0
        file_failed = 0
        transfer_out = {}
        transfer_out["error"] = ""
        transferred_size = 0

        self.ops.execute_create_coll(self.thread_session)
        self.ops.execute_create_dir()

        for local_path, irods_path in self.ops.upload:
            try:
                _obj_put(
                    self.thread_session,
                    local_path,
                    irods_path,
                    overwrite=self.overwrite,
                    options=self.ops.options,
                    resc_name=self.ops.resc_name,
                )
                transferred_size += local_path.stat().st_size
                obj_count += 1
                self.logger.info(
                    "Transfer data thread: Transfer %s -->  %s, overwrite %s",
                    local_path,
                    irods_path,
                    self.overwrite,
                )
            except Exception as error:
                obj_failed += 1
                self.logger.exception(
                    "Transfer data thread: Could not transfer  %s --> %s; %s",
                    local_path,
                    irods_path,
                    repr(error),
                )
                transfer_out["error"] = (
                    transfer_out["error"]
                    + f"\nTransfer failed, cannot upload {str(local_path)}: {repr(error)}"
                )
            self.current_progress.emit([self.up_sizes,
                                        transferred_size,
                                        obj_count,
                                        len(self.ops.upload),
                                        obj_failed])


        transferred_size = 0
        for irods_path, local_path in self.ops.download:
            try:
                _obj_get(
                    self.thread_session,
                    irods_path,
                    local_path,
                    overwrite=self.overwrite,
                    resc_name=self.ops.resc_name,
                    options=self.ops.options,
                )
                file_count += 1
                transferred_size += irods_path.size
                self.logger.info(
                    "Transfer data thread: Transfer %s -->  %s, overwrite %s",
                    irods_path,
                    local_path,
                    self.overwrite,
                )
            except Exception as error:
                file_failed += 1
                self.logger.exception(
                    "Transfer data thread: Could not transfer  %s --> %s; %s",
                    irods_path,
                    local_path,
                    repr(error),
                )
                transfer_out["error"] = (
                    transfer_out["error"]
                    + f"\nTransfer failed, cannot download {str(irods_path)}: {repr(error)}"
                )
            self.current_progress.emit([self.down_sizes,
                                       transferred_size,
                                       file_count,
                                       len(self.ops.download),
                                       file_failed])

        self.ops.execute_meta_download()
        self._delete_session()
        self.succeeded.emit(transfer_out)


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
        self.thread_session.close()
        if self.thread_session.irods_session is None:
            self.logger.debug("Sync thread: Thread session successfully deleted.")
        else:
            self.logger.debug("Sync thread: Thread session still exists.")

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

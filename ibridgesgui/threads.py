"""Thread classes for length iBridges functions."""

from pathlib import Path

import PySide6.QtCore
from PySide6.QtCore import QThread, Signal
from ibridges import IrodsPath, Session, search_data, sync
from ibridges.executor import Operations, _obj_get, _obj_put
from irods.exception import CAT_NO_ACCESS_PERMISSION, NetworkException

class BaseThread(QThread):
    """Base class for all iRODS worker threads."""

    result = Signal(dict)

    def __init__(self, logger, ienv_path: Path):
        super().__init__()
        self.logger = logger
        self.thread_session = Session(irods_env=ienv_path)
        self.logger.debug(f"{self.__class__.__name__}: Created new session")

    def cleanup_session(self):
        """Close the session and log the result."""
        self.thread_session.close()
        if self.thread_session.irods_session is None:
            self.logger.debug(f"{self.__class__.__name__}: Session successfully deleted.")
        else:
            self.logger.debug(f"{self.__class__.__name__}: Session still exists.")

    def emit_error(self, message: str):
        """Emit an error result."""
        self.result.emit({"error": message})

class SearchThread(BaseThread):
    """Start iRODS search in a separate thread."""

    result = Signal(dict)

    def __init__(
        self,
        logger,
        ienv_path: Path,
        search_path,
        path_pattern: str,
        meta_searches: list,
        checksum: str,
        case_sensitive: bool,
        item_type: str,
    ):
        super().__init__(logger, ienv_path)
        self.search_path = search_path
        self.path_pattern = path_pattern
        self.meta_searches = meta_searches
        self.checksum = checksum
        self.case_sensitive = case_sensitive
        self.item_type = item_type

    def run(self):
        try:
            from ibridges import search_data
            res = search_data(
                self.thread_session,
                path=self.search_path,
                path_pattern=self.path_pattern,
                checksum=self.checksum,
                metadata=self.meta_searches,
                case_sensitive=self.case_sensitive,
                item_type=self.item_type,
            )
            results = [str(ipath) for ipath in res]
            self.result.emit({"results": results})

        except Exception as exc:
            self.logger.exception("Search failed: %s", repr(exc))
            self.emit_error("Search failed or took too long. Please refine your parameters.")

        finally:
            self.cleanup_session()

class TransferDataThread(BaseThread):
    """Transfer data between local and iRODS."""

    current_progress = Signal(list)

    def __init__(self, ienv_path: Path, logger, ops, overwrite: bool):
        super().__init__(logger, ienv_path)
        self.ops = ops
        self.overwrite = overwrite

        self.up_sizes = sum(l.stat().st_size for l, _ in ops.upload)
        self.down_sizes = sum(i.size for i, _ in ops.download)

    # ------------------------------
    # Upload helpers
    # ------------------------------
    def _upload_files(self, transfer_out):
        transferred = 0
        obj_count = 0
        obj_failed = 0

        for local_path, irods_path in self.ops.upload:
            try:
                from ibridges.executor import _obj_put
                _obj_put(
                    self.thread_session,
                    local_path,
                    irods_path,
                    overwrite=self.overwrite,
                    options=self.ops.options,
                    resc_name=self.ops.resc_name,
                )
                transferred += local_path.stat().st_size
                obj_count += 1
                self.logger.info("Upload %s → %s", local_path, irods_path)

            except Exception as exc:
                obj_failed += 1
                msg = f"Upload failed for {local_path}: {repr(exc)}"
                self.logger.exception(msg)
                transfer_out["error"] += "\n" + msg

            self.current_progress.emit(
                [self.up_sizes, transferred, obj_count, len(self.ops.upload), obj_failed, ""]
            )

    # ------------------------------
    # Download helpers
    # ------------------------------
    def _download_files(self, transfer_out):
        transferred = 0
        file_count = 0
        file_failed = 0

        for irods_path, local_path in self.ops.download:
            try:
                from ibridges.executor import _obj_get
                _obj_get(
                    self.thread_session,
                    irods_path,
                    local_path,
                    overwrite=self.overwrite,
                    resc_name=self.ops.resc_name,
                    options=self.ops.options,
                )
                transferred += irods_path.size
                file_count += 1
                self.logger.info("Download %s → %s", irods_path, local_path)

            except Exception as exc:
                file_failed += 1
                msg = f"Download failed for {irods_path}: {repr(exc)}"
                self.logger.exception(msg)
                transfer_out["error"] += "\n" + msg

            self.current_progress.emit(
                [self.down_sizes, transferred, file_count, len(self.ops.download), file_failed, ""]
            )

    # ------------------------------
    # Metadata helpers
    # ------------------------------
    def _metadata_operations(self, transfer_out):
        try:
            self.ops.execute_meta_download()
        except Exception as exc:
            msg = f"Metadata download failed: {repr(exc)}"
            self.logger.exception(msg)
            transfer_out["error"] += "\n" + msg

        try:
            self.ops.execute_meta_upload()
        except Exception as exc:
            msg = f"Metadata upload failed: {repr(exc)}"
            self.logger.exception(msg)
            transfer_out["error"] += "\n" + msg

    # ------------------------------
    # Main run()
    # ------------------------------
    def run(self):
        transfer_out = {"error": ""}

        try:
            self.ops.execute_create_coll(self.thread_session)
            self.ops.execute_create_dir()

            self._upload_files(transfer_out)
            self._download_files(transfer_out)
            self._metadata_operations(transfer_out)

        finally:
            self.cleanup_session()
            self.result.emit(transfer_out)


class SyncThread(BaseThread):
    """Sync between iRODS and local FS."""

    def __init__(self, ienv_path, logger, source, target, dry_run: bool):
        super().__init__(logger, ienv_path)
        self.source = source
        self.target = target
        self.dry_run = dry_run

    def run(self):
        sync_out = {"error": ""}

        try:
            from ibridges import sync
            result = sync(
                self.source,
                self.target,
                dry_run=self.dry_run,
                copy_empty_folders=True,
            )
            self.logger.info("Sync %s → %s (dry_run=%s)", self.source, self.target, self.dry_run)

            if self.dry_run:
                sync_out["result"] = result

        except Exception as exc:
            msg = f"Sync failed: {repr(exc)}"
            self.logger.exception(msg)
            sync_out["error"] = msg

        finally:
            self.cleanup_session()
            self.result.emit(sync_out)

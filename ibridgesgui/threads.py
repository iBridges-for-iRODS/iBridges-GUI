"""Threads for iRODs operations."""

from __future__ import annotations

from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ibridges import IrodsPath, Session, search_data, sync
from ibridges.executor import Operations, _obj_get, _obj_put
from irods.exception import CAT_NO_ACCESS_PERMISSION, NetworkException
from PySide6.QtCore import QThread, Signal, QTimer
from ibridgesgui.config import is_session_from_config


class BaseIrodsThread(QThread):
    """Base class for all iRODS worker threads."""

    result: Signal = Signal(dict)

    def __init__(self, logger: Logger, ienv_path: Path) -> None:
        """Initialize the thread with a dedicated iRODS session.

        Parameters
        ----------
        logger : logging.Logger
            Logger instance used for debug and error output.
        ienv_path : Path
            Path to the irods_environment.json file used to create the session.

        """
        super().__init__()
        self.logger = logger
        self.thread_session: Session = Session(irods_env=ienv_path)

        if not is_session_from_config(self.thread_session):
            self.logger.error(
                    f"{self.__class__.__name__}: Session does not match saved environment")
            QTimer.singleShot(0, lambda: self.result.emit({
        "error": "The iRODS session does not match the saved configuration. "
                 "Please reset or restart the session."
            }))
            self.invalid_session = True
            return
 
        self.logger.debug(f"{self.__class__.__name__}: Created new session")

    def cleanup_session(self) -> None:
        """Close the iRODS session and log whether cleanup succeeded."""
        try:
            self.thread_session.close()
            self.logger.debug(f"{self.__class__.__name__}: Session closed.")
        except Exception as exc:
            self.logger.error(f"{self.__class__.__name__}: Failed to close session: {exc}")

    def emit_error(self, message: str) -> None:
        """Emit an error result dictionary."""
        self.result.emit({"error": message})


class SearchThread(BaseIrodsThread):
    """Thread that performs an iRODS search operation."""
    def __init__(
        self,
        logger: Logger,
        ienv_path: Path,
        search_path: IrodsPath,
        path_pattern: str,
        meta_searches: List[Tuple[str, str, str]],
        checksum: str,
        case_sensitive: bool,
        item_type: str,
    ) -> None:
        """Initialize the search thread with search parameters."""
        super().__init__(logger, ienv_path)
        self.search_path = search_path
        self.path_pattern = path_pattern
        self.meta_searches = meta_searches
        self.checksum = checksum
        self.case_sensitive = case_sensitive
        self.item_type = item_type

    def run(self) -> None:
        """Execute the search operation."""
        if getattr(self, "invalid_session", False):
            return

        try:
            results = search_data(
                self.thread_session,
                path=self.search_path,
                path_pattern=self.path_pattern,
                checksum=self.checksum,
                metadata=self.meta_searches,
                case_sensitive=self.case_sensitive,
                item_type=self.item_type,
            )

            stringified = [str(ipath) for ipath in results]
            self.result.emit({"results": stringified})

        except NetworkException:
            self.emit_error("Search takes too long. Please provide more parameters.")

        except Exception as exc:
            self.logger.exception("Search failed: %s", repr(exc))
            self.emit_error("Unexpected error during search.")

        finally:
            self.cleanup_session()


class TransferDataThread(BaseIrodsThread):
    """Thread that uploads, downloads, and transfers metadata."""
    current_progress: Signal = Signal(list)

    def __init__(
        self,
        ienv_path: Path,
        logger: Logger,
        ops: Operations,
        overwrite: bool,
    ) -> None:
        """Initialize the transfer thread with operations and settings."""
        super().__init__(logger, ienv_path)
        self.ops = ops
        self.overwrite = overwrite

        self.up_sizes: int = sum(local_path.stat().st_size for local_path, _ in ops.upload)
        self.down_sizes: int = sum(irods_path.size for irods_path, _ in ops.download)

    def _upload_files(self, transfer_out: Dict[str, str]) -> None:
        """Upload files defined in the Operations object."""
        transferred = 0
        obj_count = 0
        obj_failed = 0

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
                transferred += local_path.stat().st_size
                obj_count += 1
                self.logger.info("Uploaded %s → %s", local_path, irods_path)

            except Exception as exc:
                obj_failed += 1
                msg = f"Upload failed for {local_path}: {repr(exc)}"
                self.logger.exception(msg)
                transfer_out["error"] += "\n" + msg

            self.current_progress.emit(
                [self.up_sizes, transferred, obj_count, len(self.ops.upload), obj_failed, ""]
            )

    def _download_files(self, transfer_out: Dict[str, str]) -> None:
        """Download files defined in the Operations object."""
        transferred = 0
        file_count = 0
        file_failed = 0

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
                transferred += irods_path.size
                file_count += 1
                self.logger.info("Downloaded %s → %s", irods_path, local_path)

            except Exception as exc:
                file_failed += 1
                msg = f"Download failed for {irods_path}: {repr(exc)}"
                self.logger.exception(msg)
                transfer_out["error"] += "\n" + msg

            self.current_progress.emit(
                [self.down_sizes, transferred, file_count, len(self.ops.download), file_failed, ""]
            )

    def _metadata_operations(self, transfer_out: Dict[str, str]) -> None:
        """Execute metadata download and upload operations."""
        try:
            self.ops.execute_meta_download()
        except Exception as exc:
            msg = f"Metadata download failed: {repr(exc)}"
            self.logger.exception(msg)
            transfer_out["error"] += "\n" + msg

    def run(self) -> None:
        """Execute upload, download, and metadata operations."""
        transfer_out: Dict[str, str] = {"error": ""}
        if getattr(self, "invalid_session", False):
            return

        try:
            self.ops.execute_create_coll(self.thread_session)
            self.ops.execute_create_dir()

            self._upload_files(transfer_out)
            self._download_files(transfer_out)
            self._metadata_operations(transfer_out)

        finally:
            self.cleanup_session()
            self.result.emit(transfer_out)


class SyncThread(BaseIrodsThread):
    """Thread that performs iRODS/local filesystem synchronization."""
    def __init__(
        self,
        ienv_path: Path,
        logger: Logger,
        source: Any,
        target: Any,
        dry_run: bool,
    ) -> None:
        """Initialize the sync thread with source, target, and mode."""
        super().__init__(logger, ienv_path)
        self.source = source
        self.target = target
        self.dry_run = dry_run

    def run(self) -> None:
        """Execute the sync operation."""
        sync_out: Dict[str, Any] = {"error": ""}
        if getattr(self, "invalid_session", False):
            return


        try:
            result = sync(
                self.source,
                self.target,
                dry_run=self.dry_run,
                copy_empty_folders=True,
            )
            self.logger.info("Sync %s → %s (dry_run=%s)", self.source, self.target, self.dry_run)

            if self.dry_run:
                sync_out["result"] = result

        except PermissionError as exc:
            msg = f"No access to {exc.filename}"
            self.logger.exception(msg)
            sync_out["error"] = msg

        except CAT_NO_ACCESS_PERMISSION:
            msg = "There is data in the iRODS collection which you are not allowed to access."
            self.logger.exception(msg)
            sync_out["error"] = msg

        except Exception as exc:
            msg = f"Sync failed: {repr(exc)}"
            self.logger.exception(msg)
            sync_out["error"] = msg

        finally:
            self.cleanup_session()
            self.result.emit(sync_out)

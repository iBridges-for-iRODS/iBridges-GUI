"""iRODS functionality for sync."""
import logging
from pathlib import Path

from ibridges import IrodsPath

from ibridgesgui.config import get_last_ienv_path
from ibridgesgui.gui_utils import prep_session_for_copy
from ibridgesgui.threads import SyncThread, TransferDataThread


class SyncService:
    """Service layer for iRODS sync operations and threads."""

    def __init__(self, session, logger: logging.Logger):
        """Init."""
        self.session = session
        self.logger = logger

    def irods_root(self) -> IrodsPath:
        """Retrieve lowest visible level in the iRODS tree for the user."""
        lowest = IrodsPath(self.session).absolute()
        while lowest.parent.exists() and str(lowest) != "/":
            lowest = lowest.parent
        return lowest

    def prepare_env_for_diff(self, error_label) -> Path | None:
        """Prepare environment for diff (uses existing session)."""
        env_path = prep_session_for_copy(self.session, error_label)
        if env_path is None:
            return None
        return Path(env_path)

    def prepare_env_for_sync(self, error_label) -> Path | None:
        """Prepare environment for data sync (uses last ienv path)."""
        env_path_str = get_last_ienv_path()
        if not env_path_str:
            error_label.setText("No iRODS environment file found.")
            return None
        env_path = Path(env_path_str)
        if not env_path.exists():
            error_label.setText(f"Environment file not found: {env_path}")
            return None
        return env_path

    def start_diff_thread(self, env_path, source, target, on_result, on_finished):
        """Start SyncThread in dry-run mode to compute diffs."""
        try:
            thread = SyncThread(env_path, self.logger, source, target, dry_run=True)
        except Exception:
            on_result(
                {
                    "error": f"Could not instantiate a new session from {env_path}. "
                              "Check configuration.",
                    "result": None,
                }
            )
            return None

        thread.result.connect(on_result)
        thread.finished.connect(on_finished)
        thread.start()
        return thread

    def start_sync_thread(self, env_path, diffs, on_result, on_progress, on_finished):
        """Start TransferDataThread to perform actual sync."""
        try:
            thread = TransferDataThread(env_path, self.logger, diffs, overwrite=True)
        except Exception as err:
            on_result({"error": f"Could not instantiate a new session from {env_path}: {err}"})
            return None

        thread.current_progress.connect(on_progress)
        thread.result.connect(on_result)
        thread.finished.connect(on_finished)
        thread.start()
        return thread

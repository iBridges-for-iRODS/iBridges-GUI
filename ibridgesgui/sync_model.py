"""Model for the sync tab."""
from pathlib import Path
from typing import Optional


class SyncModel:
    """Holds all state for the Sync feature."""

    def __init__(self):
        """Init."""
        self.sync_source: Optional[str] = None  # "local" or "irods"
        self.local_path: Optional[Path] = None
        self.irods_path = None
        self.refresh_irods_index = None
        self.diffs = None

        # Optional future fields:
        self.status_message: str = ""
        self.progress_percent: int = 0
        self.total_files: int = 0
        self.completed_files: int = 0
        self.failed_files: int = 0

    def set_paths(self, local_path, irods_path, refresh_index):
        """Save seleted paths."""
        self.local_path = local_path
        self.irods_path = irods_path
        self.refresh_irods_index = refresh_index

    def clear(self):
        """Reset status."""
        self.sync_source = None
        self.local_path = None
        self.irods_path = None
        self.refresh_irods_index = None
        self.diffs = None
        self.status_message = ""
        self.progress_percent = 0
        self.total_files = 0
        self.completed_files = 0
        self.failed_files = 0

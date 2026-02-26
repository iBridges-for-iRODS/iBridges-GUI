from pathlib import Path
from typing import Optional


class SyncModel:
    """Holds state for the Sync feature."""

    def __init__(self):
        self.sync_source: Optional[str] = None  # "local" or "irods"
        self.local_path: Optional[Path] = None
        self.irods_path = None
        self.refresh_irods_index = None
        self.diffs = None  # result of dry_run

    def set_paths(self, local_path, irods_path, refresh_index):
        self.local_path = local_path
        self.irods_path = irods_path
        self.refresh_irods_index = refresh_index

    def clear(self):
        self.sync_source = None
        self.local_path = None
        self.irods_path = None
        self.refresh_irods_index = None
        self.diffs = None


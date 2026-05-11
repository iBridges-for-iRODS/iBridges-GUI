"""Browser model."""

import dataclasses
from typing import Any, Dict, Optional, Set

from ibridges import IrodsPath


@dataclasses.dataclass
class BrowserModel:
    """State container for the Browser tab.

    This model tracks all non‑UI state required by the browser view and
    controller. It acts as a lightweight state machine that records:

    - the current and previous iRODS paths
    - the currently selected row in the browser table
    - which information tabs have already been updated
    - cached metadata, ACLs, replicas, and previews for each row

    The model contains no Qt widgets and performs no iRODS I/O.
    All caches are keyed by table row index and are cleared automatically
    when the path or selection changes.
    """

    # Navigation state
    current_path: IrodsPath
    last_path: Optional[IrodsPath] = None

    # Selection state
    current_selected_row: int = -1
    last_selected_row: int = -1

    # Tracks which info tabs have been updated
    updated_info_tabs: Set[str] = dataclasses.field(default_factory=set)

    # Per-row caches
    metadata_cache: Dict[int, Any] = dataclasses.field(default_factory=dict)
    acl_cache: Dict[int, Any] = dataclasses.field(default_factory=dict)
    replica_cache: Dict[int, Any] = dataclasses.field(default_factory=dict)
    preview_cache: Dict[int, Any] = dataclasses.field(default_factory=dict)

    def set_path(self, new_path: IrodsPath) -> None:
        """Update the current path and reset selection + caches."""
        self.last_path = self.current_path
        self.current_path = new_path
        self.reset_selection_state()
        self.clear_all_caches()

    def has_path_changed(self) -> bool:
        """Return True if the path changed since the last update."""
        return self.last_path is None or self.last_path != self.current_path

    def reset_selection_state(self) -> None:
        """Reset selection and tab-update tracking."""
        self.last_selected_row = -1
        self.current_selected_row = -1
        self.updated_info_tabs.clear()

    def on_row_clicked(self, row: int) -> None:
        """Record row selection and invalidate tab-update tracking."""
        self.last_selected_row = self.current_selected_row
        self.current_selected_row = row
        self.updated_info_tabs.clear()

    def has_selection(self) -> bool:
        """Return True if a row is currently selected."""
        return self.current_selected_row >= 0

    def needs_tab_update(self, tab_name: str) -> bool:
        """Return True if the given tab needs to be refreshed."""
        if self.has_path_changed():
            return True
        if self.current_selected_row != self.last_selected_row:
            return True
        return tab_name not in self.updated_info_tabs

    def mark_tab_updated(self, tab_name: str) -> None:
        """Mark a tab as up-to-date."""
        self.updated_info_tabs.add(tab_name)

    def clear_all_caches(self) -> None:
        """Clear all per-row caches."""
        self.metadata_cache.clear()
        self.acl_cache.clear()
        self.replica_cache.clear()
        self.preview_cache.clear()

    # --- Cache invalidation helpers ---

    def invalidate_metadata(self, row: int) -> None:
        """Discard metadata info."""
        self.metadata_cache.pop(row, None)
        self.updated_info_tabs.discard("metadata")

    def invalidate_acls(self, row: int) -> None:
        """Discard acl info."""
        self.acl_cache.pop(row, None)
        self.updated_info_tabs.discard("permissions")

    def invalidate_replicas(self, row: int) -> None:
        """Discard replicas info."""
        self.replica_cache.pop(row, None)
        self.updated_info_tabs.discard("replicas")

    def invalidate_preview(self, row: int) -> None:
        """Discard preview info."""
        self.preview_cache.pop(row, None)
        self.updated_info_tabs.discard("preview")

    # Generic helpers

    def _cache_set(self, cache: Dict[int, Any], row: int, data: Any) -> None:
        cache[row] = data

    def _cache_get(self, cache: Dict[int, Any], row: int) -> Optional[Any]:
        return cache.get(row)

    # Metadata cache

    def cache_metadata(self, row: int, data: Any) -> None:
        """Cache metadata info."""
        self._cache_set(self.metadata_cache, row, data)

    def get_cached_metadata(self, row: int) -> Optional[Any]:
        """Retrieve cahced metadata info."""
        return self._cache_get(self.metadata_cache, row)

    # ACL cache

    def cache_acls(self, row: int, data: Any) -> None:
        """Cache acl info."""
        self._cache_set(self.acl_cache, row, data)

    def get_cached_acls(self, row: int) -> Optional[Any]:
        """Retrieve cached acl info."""
        return self._cache_get(self.acl_cache, row)

    # Replica cache

    def cache_replicas(self, row: int, data: Any) -> None:
        """Cache replicas info."""
        self._cache_set(self.replica_cache, row, data)

    def get_cached_replicas(self, row: int) -> Optional[Any]:
        """Retrieve cached replicas info."""
        return self._cache_get(self.replica_cache, row)

    # Preview cache

    def cache_preview(self, row: int, data: Any) -> None:
        """Cache preview info."""
        self._cache_set(self.preview_cache, row, data)

    def get_cached_preview(self, row: int) -> Optional[Any]:
        """Retrieve cached preview info."""
        return self._cache_get(self.preview_cache, row)

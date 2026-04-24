"""Browser model."""
import dataclasses
from typing import Any, Dict, List, Optional

from ibridges import IrodsPath


@dataclasses.dataclass
class BrowserModel:
    """State machine + cache for the Browser tab."""

    # --- core navigation state ---
    current_path: IrodsPath
    last_path: Optional[IrodsPath] = None

    current_selected_row: int = -1
    last_selected_row: int = -1

    # --- tab update tracking ---
    updated_info_tabs: List[str] = dataclasses.field(default_factory=list)

    # --- per-row caches ---
    metadata_cache: Dict[int, Any] = dataclasses.field(default_factory=dict)
    acl_cache: Dict[int, Any] = dataclasses.field(default_factory=dict)
    replica_cache: Dict[int, Any] = dataclasses.field(default_factory=dict)
    preview_cache: Dict[int, Any] = dataclasses.field(default_factory=dict)

    # ----------------------------------------------------------------------
    # Path handling
    # ----------------------------------------------------------------------

    def set_path(self, new_path: IrodsPath) -> None:
        """Update path and reset all selection + tab state."""
        self.last_path = self.current_path
        self.current_path = new_path
        self.reset_selection_cache()
        self.clear_all_caches()

    def path_changed(self) -> bool:
        """Test if new path is chosen."""
        return self.last_path is None or self.last_path != self.current_path

    # ----------------------------------------------------------------------
    # Selection handling
    # ----------------------------------------------------------------------

    def reset_selection_cache(self) -> None:
        """Restore inital state."""
        self.last_selected_row = -1
        self.current_selected_row = -1
        self.updated_info_tabs.clear()

    def on_row_clicked(self, row: int) -> None:
        """Record row selection and invalidate tab cache."""
        self.last_selected_row = self.current_selected_row
        self.current_selected_row = row
        self.updated_info_tabs.clear()

    def has_selection(self) -> bool:
        """Test if row is selected in browser table.."""
        return self.current_selected_row >= 0

    # ----------------------------------------------------------------------
    # Tab update logic
    # ----------------------------------------------------------------------

    def needs_tab_update(self, tab_name: str) -> bool:
        """Determine whether a tab needs to be refreshed."""
        if self.path_changed():
            return True
        if self.current_selected_row != self.last_selected_row:
            return True
        return tab_name not in self.updated_info_tabs

    def mark_tab_updated(self, tab_name: str) -> None:
        """Update a selected info tab."""
        if tab_name not in self.updated_info_tabs:
            self.updated_info_tabs.append(tab_name)

    # ----------------------------------------------------------------------
    # Caching
    # ----------------------------------------------------------------------

    def clear_all_caches(self) -> None:
        """Clear."""
        self.metadata_cache.clear()
        self.acl_cache.clear()
        self.replica_cache.clear()
        self.preview_cache.clear()

    def cache_metadata(self, row: int, data: Any) -> None:
        """Cache changes."""
        self.metadata_cache[row] = data

    def get_cached_metadata(self, row: int) -> Optional[Any]:
        """Read cached info."""
        return self.metadata_cache.get(row)

    def cache_acls(self, row: int, data: Any) -> None:
        """Cache changes."""
        self.acl_cache[row] = data

    def get_cached_acls(self, row: int) -> Optional[Any]:
        """Read cached info."""
        return self.acl_cache.get(row)

    def cache_replicas(self, row: int, data: Any) -> None:
        """Cache changes."""
        self.replica_cache[row] = data

    def get_cached_replicas(self, row: int) -> Optional[Any]:
        """Read cached info."""
        return self.replica_cache.get(row)

    def cache_preview(self, row: int, data: Any) -> None:
        """Cache changes."""
        self.preview_cache[row] = data

    def get_cached_preview(self, row: int) -> Optional[Any]:
        """Read cached info."""
        return self.preview_cache.get(row)

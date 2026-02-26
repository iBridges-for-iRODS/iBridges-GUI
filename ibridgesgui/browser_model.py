"""State functionality for browser."""
import dataclasses
from typing import List

from ibridges import IrodsPath


@dataclasses.dataclass
class BrowserModel:
    """Pure state for the Browser tab."""

    current_path: IrodsPath
    last_selected_row: int = -1
    current_selected_row: int = -1
    updated_info_tabs: List[str] = dataclasses.field(default_factory=list)

    def reset_selection_cache(self) -> None:
        """Reset selections in browser."""
        self.last_selected_row = -1
        self.current_selected_row = -1
        self.updated_info_tabs.clear()

    def on_row_clicked(self, row: int) -> None:
        """Save current selected row."""
        self.updated_info_tabs.clear()
        self.last_selected_row = self.current_selected_row
        self.current_selected_row = row

    def mark_tab_updated(self, tab_name: str) -> None:
        """Mark tabs in lower section of browser for update."""
        if tab_name not in self.updated_info_tabs:
            self.updated_info_tabs.append(tab_name)

    def needs_tab_update(self, tab_name: str, row: int) -> bool:
        """Determine whether lower tab needs update."""
        return self.last_selected_row != row or tab_name not in self.updated_info_tabs

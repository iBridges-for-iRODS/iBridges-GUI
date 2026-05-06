from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any


class PluginManager:
    """Discovers and manages third‑party tab providers."""

    GROUP_NAME = "ibridges.gui_tab"

    def __init__(self) -> None:
        self.providers = self._load_providers()

    def _load_providers(self) -> list[Any]:
        """Load all installed tab providers via entry points."""
        eps = entry_points().select(group=self.GROUP_NAME)
        return [entry.load() for entry in eps]

    def get_provider(self, name: str) -> Any:
        """Return the provider class matching the given tab name."""
        for provider in self.providers:
            if getattr(provider, "name", None) == name:
                return provider

        msg = (
            f"Cannot find provider with name {name!r}. "
            "Ensure the plugin is installed."
        )
        raise ValueError(msg)

    def list_providers(self) -> list[Any]:
        """Return all discovered provider classes."""
        return self.providers

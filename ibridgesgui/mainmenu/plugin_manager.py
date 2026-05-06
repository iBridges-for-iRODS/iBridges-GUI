"""Manage gui plugins."""
from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any


class PluginManager:
    """Discovers and manages third‑party tab providers."""

    GROUP_NAME = "ibridges.gui_tab"

    def __init__(self) -> None:
        """Init."""
        self.providers = self._load_providers()


    def _load_providers(self) -> list:
        """Load all installed tab providers via entry points."""
        eps = entry_points()
    
        # Python 3.10+ EntryPoints object
        if hasattr(eps, "select") and not isinstance(eps, dict):
            try:
                eps = eps.select(group=self.GROUP_NAME)
            except Exception:
                eps = []
    
        # Python 3.8/3.9 dict
        elif isinstance(eps, dict):
            eps = eps.get(self.GROUP_NAME, [])
    
        # Older importlib_metadata list/tuple
        elif isinstance(eps, (list, tuple)):
            eps = [ep for ep in eps if getattr(ep, "group", None) == self.GROUP_NAME]
    
        # MagicMock, None, or anything unexpected
        else:
            eps = []
    
        providers = []
        for ep in eps:
            try:
                providers.append(ep.load())
            except Exception as exc:
                print(f"Failed to load provider {ep}: {exc}")
    
        return providers


    def get_provider(self, name: str) -> Any:
        """Return the provider class matching the given tab name."""
        for provider in self.providers:
            if getattr(provider, "name", None) == name:
                return provider

        raise ValueError(
            f"Cannot find provider with name {name!r}. " "Ensure the plugin is installed."
        )

    def list_providers(self) -> list[Any]:
        """Return all discovered provider classes."""
        return self.providers

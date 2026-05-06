"""Wrapper around config.py."""
from pathlib import Path

from ibridgesgui.config import (
    _get_config,
    _save_config,
    config_get_last_download_path,
    config_get_last_upload_path,
    config_set_last_download_path,
    config_set_last_upload_path,
    get_last_ienv_name,
    get_log_level,
    get_prev_settings,
    save_current_settings,
    set_last_ienv,
    set_log_level,
)


class ConfigManager:
    """Thin wrapper around the existing functional config system.

    This class exposes a clean API for SessionManager while internally
    delegating to the existing functions in config.py.
    """

    def __init__(self):
        """Init."""
        self._config = _get_config() or {}

    def get_cached_password(self, env_path: Path) -> str | None:
        """Password caching get from config."""
        cached = self._config.get("cached_passwords", {})
        return cached.get(str(env_path))

    def save_current_settings(self, env_path: Path) -> None:
        """Delegate to the existing function."""
        save_current_settings(env_path)
        self._config = _get_config() or {}

    def get_last_env(self) -> str | None:
        """Delegate to existing function."""
        return get_last_ienv_name()

    def set_last_ienv(self, alias: str | None, path: str) -> None:
        """Save last used environment in the format '<alias> - <path>'."""
        set_last_ienv(alias, path)
        self._config = _get_config() or {}

    # Log level
    def get_log_level(self) -> str | None:
        """Delegate to existing function."""
        return get_log_level()

    def set_log_level(self, level: str) -> None:
        """Delegate to existing function."""
        set_log_level(level)
        self._config = _get_config() or {}

    # Tabs
    def load_tabs(self) -> list[str]:
        """Return list of tabs that should be restored."""
        return self._config.get("tabs", [])

    def save_tabs(self, tabs: list[str]) -> None:
        """Persist list of open tabs."""
        self._config["tabs"] = tabs
        _save_config(self._config)

    # Upload/download paths
    def set_last_upload_path(self, path: Path) -> None:
        """Delegate to existing function."""
        config_set_last_upload_path(path)
        self._config = _get_config() or {}

    def get_last_upload_path(self) -> Path:
        """Delegate to existing function."""
        return config_get_last_upload_path()

    def set_last_download_path(self, path: Path) -> None:
        """Delegate to existing function."""
        config_set_last_download_path(path)
        self._config = _get_config() or {}

    def get_last_download_path(self) -> str | None:
        """Delegate to existing function."""
        return config_get_last_download_path()

    def get_prev_settings(self) -> dict:
        """Delegate to existing function."""
        return get_prev_settings()

    def reload(self) -> None:
        """Reload config settings."""
        self._config = _get_config() or {}

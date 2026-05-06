"""Configuration and logging utilities for iBridges-GUI.

This module provides:
- Logging setup
- GUI configuration management
- iRODS environment validation
- Session origin detection
- Integration with iBridges CLI configuration
"""

from __future__ import annotations

import datetime
import json
import logging
import logging.handlers
import sys
from json import JSONDecodeError
from pathlib import Path
from typing import Union

from ibridges.cli.config import IbridgesConf
from ibridges.session import Session, _translate_irods_error
from irods.auth.pam import PamLoginException
from irods.connection import PlainTextPAMPasswordError
from irods.exception import (
    CAT_INVALID_AUTHENTICATION,
    CAT_INVALID_USER,
    PAM_AUTH_PASSWORD_FAILED,
    PAM_AUTH_PASSWORD_INVALID_TTL,
    NetworkException,
)
from irods.session import iRODSSession

try:
    from importlib_metadata import version  # Python < 3.10
except ImportError:
    from importlib.metadata import version  # type: ignore


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LOG_LEVEL = {
    "fulldebug": logging.DEBUG - 5,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

CONFIG_DIR = Path("~", ".ibridges").expanduser()
CONFIG_FILE = CONFIG_DIR / "ibridges_gui.json"
IRODSA = Path.home() / ".irods" / ".irodsA"


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------


def ensure_log_config_location() -> None:
    """Ensure the location for logs and config files exists."""
    CONFIG_DIR.mkdir(parents=True, mode=0o700, exist_ok=True)


def ensure_irods_location() -> None:
    """Ensure that ~/.irods exists."""
    irods_loc = Path("~/.irods").expanduser()
    irods_loc.mkdir(mode=0o700, exist_ok=True)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def init_logger(app_name: str, log_level: str) -> logging.Logger:
    """Create and configure a logger for the application."""
    ensure_log_config_location()

    logger = logging.getLogger(app_name)
    logfile = CONFIG_DIR / f"{app_name}.log"

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.handlers.RotatingFileHandler(logfile, "a", 100000, 1)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL.get(log_level, LOG_LEVEL["info"]))

    try:
        release = version("ibridgesgui")
    except Exception:
        release = ""

    # Startup banner
    with logfile.open("a", encoding="utf-8") as logfd:
        logfd.write("\n\n" + "_" * 50 + "\n" + "_" * 50 + "\n")
        logfd.write(
            f"\t Starting iBridges-GUI {release}\n\t{datetime.datetime.now().isoformat()}\n"
        )
        logfd.write("_" * 50 + "\n" + "_" * 50 + "\n")

    return logger


# ---------------------------------------------------------------------------
# Config file I/O
# ---------------------------------------------------------------------------


def _read_json(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(file_path: Path, content: dict) -> None:
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(content, handle, indent=4)


def _get_config() -> dict | None:
    """Load the GUI config file, handling empty or malformed files."""
    try:
        return _read_json(CONFIG_FILE)
    except FileNotFoundError:
        return None
    except JSONDecodeError as err:
        if err.msg == "Expecting value":  # empty file
            return None
        print(f"CANNOT START APP: {CONFIG_FILE} incorrectly formatted.")
        sys.exit(1)


def _save_config(conf: dict) -> None:
    ensure_log_config_location()
    _write_json(CONFIG_FILE, conf)


# ---------------------------------------------------------------------------
# GUI config: last environment
# ---------------------------------------------------------------------------


def get_last_ienv_name() -> str | None:
    raw = _get_config().get("gui_last_env")
    if not raw:
        return None

    parts = raw.split(" - ", 1)
    alias = parts[0].strip()
    return alias or None


def get_last_ienv_path() -> str | None:
    raw = _get_config().get("gui_last_env")
    if not raw:
        return None

    parts = raw.split(" - ", 1)
    if len(parts) < 2:
        return None

    path = parts[1].strip()
    return path or None


def set_last_ienv(alias: str | None, path: str) -> None:
    """Save last used environment in the format '<alias> - <path>'."""
    config = _get_config() or {}

    alias = alias or ""  # allow empty alias
    config["gui_last_env"] = f"{alias} - {path}"

    _save_config(config)


# ---------------------------------------------------------------------------
# GUI config: log level
# ---------------------------------------------------------------------------


def get_log_level() -> str | None:
    """Return log level."""
    config = _get_config()
    return config.get("log_level") if config else None


def set_log_level(level: str) -> None:
    """Set log level."""
    config = _get_config() or {}
    config["log_level"] = level
    _save_config(config)


# ---------------------------------------------------------------------------
# GUI config: tabs
# ---------------------------------------------------------------------------


def config_add_tab(tab_provider: object) -> None:
    """Add a new tab name to the config."""
    try:
        obj_str = str(tab_provider).split("'")[1]
    except IndexError:
        obj_str = tab_provider

    config = _get_config() or {}
    tabs = set(config.get("tabs", []))
    tabs.add(obj_str)
    config["tabs"] = list(tabs)
    _save_config(config)


def config_remove_tab(tab_provider: object) -> None:
    """Remove a tab name from he config."""
    try:
        obj_str = str(tab_provider).split("'")[1]
    except IndexError:
        obj_str = tab_provider

    config = _get_config() or {}
    tabs = config.get("tabs", [])
    if obj_str in tabs:
        tabs.remove(obj_str)
        config["tabs"] = tabs
        _save_config(config)


def get_tabs() -> list:
    """List all tab names."""
    config = _get_config() or {}
    return config.get("tabs", [])


# ---------------------------------------------------------------------------
# GUI config: upload/download paths
# ---------------------------------------------------------------------------


def config_set_last_upload_path(path: Path) -> None:
    """Save the last location from which data was uploaded."""
    config = _get_config() or {}
    config["last_upload_path"] = str(path)
    _save_config(config)


def config_get_last_upload_path() -> str | None:
    """Get the last location from which data was uploaded."""
    config = _get_config() or {}
    return config.get("last_upload_path")


def config_set_last_download_path(path: Path) -> None:
    """Save the last download destination."""
    config = _get_config() or {}
    config["last_download_path"] = str(path)
    _save_config(config)


def config_get_last_download_path() -> Path:
    """Return last download path as a Path object, or Path.home() if missing."""
    config = _get_config() or {}
    raw = config.get("last_download_path")

    if raw:
        return Path(raw).expanduser()

    return Path.home()


# ---------------------------------------------------------------------------
# GUI config: settings
# ---------------------------------------------------------------------------


def get_prev_settings() -> dict:
    """Get previous settings."""
    config = _get_config() or {}
    return config.get("settings", {})


def save_current_settings(env_path_name: Path) -> None:
    """Store the environment with the currently scrambled password in irodsA."""
    ibridges_conf = IbridgesConf(None)

    with IRODSA.open("r", encoding="utf-8") as f:
        pw = f.read()

    try:
        ienv_path, ienv_entry = ibridges_conf.get_entry(env_path_name)
    except KeyError:
        ienv_path = env_path_name
        ienv_entry = {}

    if ienv_entry.get("irodsa_backup") != pw:
        ienv_entry["irodsa_backup"] = pw
        ibridges_conf.servers[str(ienv_path)] = ienv_entry
        ibridges_conf.save()

    # Remove legacy GUI-stored passwords
    config = _get_config()
    if config and "settings" in config and str(env_path_name) in config["settings"]:
        del config["settings"][str(env_path_name)]
        _save_config(config)


# ---------------------------------------------------------------------------
# iRODS session origin detection (hybrid method)
# ---------------------------------------------------------------------------


def is_session_from_config(session: Session) -> bool:
    """Determine whether the given session was created from the last-used iRODS environment file.

    Compare current session parameters to the parameters in the last used
    env file.
    """
    last_env_path = get_last_ienv_path()
    if not last_env_path:
        return False

    last_env_path = Path(last_env_path)

    try:
        env = _read_json(last_env_path)
    except Exception:
        return False

    return (
        session.host == env.get("irods_host")
        and session.port == env.get("irods_port")
        and session.zone == env.get("irods_zone_name")
        and session.username == env.get("irods_user_name")
        and session.home == env.get("irods_home")
        and session.default_resc == env.get("irods_default_resource")
    )


# ---------------------------------------------------------------------------
# iRODS environment validation
# ---------------------------------------------------------------------------


def check_irods_config(ienv: Union[Path, dict], include_network: bool = True) -> str:
    """Validate an iRODS environment file or dict."""
    if isinstance(ienv, Path):
        try:
            env = _read_json(ienv)
        except FileNotFoundError:
            return f"{ienv} not found."
        except JSONDecodeError as err:
            return f"{ienv} not well formatted.\n {err.msg} at position {err.pos}."
    else:
        env = ienv

    # Required fields
    required = [
        ("irods_host", '"irods_host" is missing in environment.'),
        ("irods_port", '"irods_port" is missing in environment.'),
        ("irods_home", 'Please set an "irods_home".'),
        ("irods_default_resource", 'Please set an "irods_default_resource".'),
    ]
    for key, msg in required:
        if key not in env:
            return msg

    if not isinstance(env["irods_port"], int):
        return (
            '"irods_port" must be a number. It looks like it is stored as text — '
            "please remove the quotation marks."
        )

    if include_network:
        if not Session.network_check(env["irods_host"], env["irods_port"]):
            return (
                f"Unable to connect to the server.\n"
                f"- The network may be unavailable\n"
                f"- The server name '{env['irods_host']}' may be incorrect\n"
                f"- The port '{env['irods_port']}' may be incorrect"
            )

        try:
            sess = iRODSSession(password="bogus", **env)
            _ = sess.server_version

        except (
            TypeError,
            RuntimeError,
            NetworkException,
            AttributeError,
            PamLoginException,
            PlainTextPAMPasswordError,
            ValueError,
            CAT_INVALID_USER,
        ) as err:
            # Use iBridges' own error translator
            translated = _translate_irods_error(err)
            return str(translated)

        except ModuleNotFoundError as err:
            return (
                f'The authentication scheme "{err.name}" does not exist. '
                'Please check "irods_authentication_scheme".'
            )

        except (
            PAM_AUTH_PASSWORD_INVALID_TTL,
            CAT_INVALID_AUTHENTICATION,
            PAM_AUTH_PASSWORD_FAILED,
        ):
            return "All checks passed successfully."

    return "All checks passed successfully."


# ---------------------------------------------------------------------------
# Saving iRODS environment files
# ---------------------------------------------------------------------------


def save_irods_config(env_path: Union[Path, str], conf: dict) -> None:
    """Save current settings."""
    env_path = Path(env_path)
    if env_path.suffix != ".json":
        raise ValueError("Filetype needs to be '.json'.")
    _write_json(env_path, conf)


# ---------------------------------------------------------------------------
# CLI environments + extra files ~/.irods
# ---------------------------------------------------------------------------


def load_envs_from_cli_and_fs(irods_config_dir: Path) -> dict[str, tuple[Path, dict]]:
    """
    Load all server environments from the CLI config,
    and extend them with any .json files found in ~/.irods.
    """

    conf = IbridgesConf(None)
    cli_servers = conf.servers  # dict: env_path_str → entry_dict

    aliases_envs: dict[str, tuple[Path, dict]] = {}

    # 1. Load all CLI-defined servers
    for env_path_str, entry in cli_servers.items():
        env_path = Path(env_path_str).expanduser()
        alias = entry.get("alias", env_path.name)
        aliases_envs[alias] = (env_path, entry)

    # 2. Add any .json env files in ~/.irods that are NOT in CLI config
    for env_file in irods_config_dir.glob("*.json"):
        env_file = env_file.expanduser()

        # Check if this file is already represented in CLI config
        if not any(env_file == p for (p, _) in aliases_envs.values()):
            alias = env_file.name  # fallback alias
            aliases_envs[alias] = (env_file, {"alias": alias})

    return aliases_envs

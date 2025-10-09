"""Setting up logger and configuration files."""

import datetime
import json
import logging
import logging.handlers
import sys
from json import JSONDecodeError
from pathlib import Path
from typing import Union

from ibridges.cli.config import IbridgesConf
from ibridges.session import Session
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

try:  # Python < 3.10 (backport)
    from importlib_metadata import version  # type: ignore
except ImportError:
    from importlib.metadata import version  # type: ignore [assignment]

LOG_LEVEL = {
    "fulldebug": logging.DEBUG - 5,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

CONFIG_DIR = Path("~", ".ibridges").expanduser()
CONFIG_FILE = CONFIG_DIR.joinpath("ibridges_gui.json")
IRODSA = Path.home() / ".irods" / ".irodsA"


def ensure_log_config_location():
    """Ensure the location for logs and config files."""
    CONFIG_DIR.mkdir(parents=True, mode=0o700, exist_ok=True)


def ensure_irods_location():
    """Ensure that .irods exists in user's home."""
    irods_loc = Path("~/.irods").expanduser()
    irods_loc.mkdir(mode=0o700, exist_ok=True)


# logging functions
def init_logger(app_name: str, log_level: str) -> logging.Logger:
    """Create a logger for the app.

    app_name : str
        Name of the app, will be used as file name
    log_level : str
        String that will be mapped to python's log levels, default is info
    """
    logger = logging.getLogger(app_name)
    logfile = CONFIG_DIR.joinpath(f"{app_name}.log")

    # Direct logging to logfile
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler = logging.handlers.RotatingFileHandler(logfile, "a", 100000, 1)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(LOG_LEVEL.get(log_level, LOG_LEVEL["info"]))
    try:
        release = version("ibridgesgui")
    except Exception:
        release = ""

    # Logger greeting when app is started
    with open(logfile, "a", encoding="utf-8") as logfd:
        logfd.write("\n\n")
        underscores = f"{'_' * 50}\n"
        logfd.write(underscores * 2)
        logfd.write(
            f"\t Starting iBridges-GUI {release}\n\t{datetime.datetime.now().isoformat()}\n"
        )
        logfd.write(underscores * 2)

    return logger


# ibridges config functions
def get_last_ienv_name() -> Union[None, str]:
    """Retrieve last used environment name as in the login drop down from the config file."""
    config = _get_config()
    if config is not None:
        return config.get("gui_last_env")
    return None


def get_last_ienv_path() -> Union[None, str]:
    """Retrieve the last successfully used environment file."""
    name = get_last_ienv_name()
    if name:
        return name.split(" - ")[1]
    return None


def set_last_ienv(ienv: str):
    """Save the last used environment path to the config file.

    ienv_path : Path
        Path to last environment
    """
    config = _get_config()
    if config is not None:
        config["gui_last_env"] = ienv
    else:
        config = {"gui_last_env": ienv}
    _save_config(config)


def get_log_level() -> Union[None, str]:
    """Retrieve log level from config."""
    config = _get_config()
    if config is not None:
        return config.get("log_level")
    return None


def set_log_level(level: str):
    """Save log level to config."""
    config = _get_config()
    if config is not None:
        config["log_level"] = level
    else:
        config = {"log_level": level}
    _save_config(config)


def config_add_tab(tab_provider: object):
    """Add a tab name to the config file."""
    try:
        # third party plugin class name
        obj_str = str(tab_provider).split("'")[1]
    except IndexError:
        # ibridges native tab name
        obj_str = tab_provider
    config = _get_config()
    if config is not None:
        tabs = set(config.get("tabs", []))
        tabs.add(obj_str)
        config["tabs"] = list(tabs)
    else:
        config = {"tabs": [obj_str]}
    _save_config(config)


def config_remove_tab(tab_provider: object):
    """Remove a tab from the config file."""
    config = _get_config()
    try:
        # third party plugin class name
        obj_str = str(tab_provider).split("'")[1]
    except IndexError:
        # ibridges native tab name
        obj_str = tab_provider
    if config is not None and "tabs" in config:
        tabs = config.get("tabs", [])
        if obj_str in tabs:
            tabs.remove(obj_str)
            config["tabs"] = tabs
            _save_config(config)


def config_set_last_upload_path(path: Path):
    """Store the folder of the upload dialog."""
    config = _get_config()
    config["last_upload_path"] = str(path)
    _save_config(config)


def config_get_last_upload_path():
    """Get the last used upload location."""
    config = _get_config()
    return config.get("last_upload_path", None)


def config_set_last_download_path(path: Path):
    """Store the folder of download dialog."""
    config = _get_config()
    config["last_download_path"] = str(path)
    _save_config(config)


def config_get_last_download_path():
    """Get the lats used download location."""
    config = _get_config()
    return config.get("last_download_path", None)


def get_tabs() -> list:
    """Get list of previously chosen tird party tab providers."""
    config = _get_config()
    return config.get("tabs", [])


def _save_config(conf: dict):
    ensure_log_config_location()
    _write_json(CONFIG_FILE, conf)


def _get_config() -> Union[None, dict]:
    try:
        return _read_json(CONFIG_FILE)
    except FileNotFoundError:
        return None
    except JSONDecodeError as err:
        # empty file
        if err.msg == "Expecting value":
            return None
        print(f"CANNOT START APP: {CONFIG_FILE} incorrectly formatted.")
        sys.exit(1)


def save_current_settings(env_path_name: Path):
    """Store the environment with the currently scrambled password in irodsA.

    Will be stored in ibridges_cli.json and in ibridges_gui.json.
    """
    ibridges_conf = IbridgesConf(None)
    with open(IRODSA, "r", encoding="utf-8") as f:
        pw = f.read()
    try:
        ienv_path, ienv_entry = ibridges_conf.get_entry(env_path_name)
    except KeyError:
        ienv_path = env_path_name
        ienv_entry = {}
    if ienv_entry.get("irodsa_backup", "") != pw:
        ienv_entry["irodsa_backup"] = pw
        ibridges_conf.servers[str(ienv_path)] = ienv_entry
        ibridges_conf.save()

    # Till ibridges gui 2.0.0 empty passwords from gui config
    # In ibridges gui 2.0.0 no passwords and envs will be stored in gui config
    config = _get_config()
    if config is not None:
        if "settings" in config and str(env_path_name) in config["settings"]:
            del config["settings"][str(env_path_name)]
            _save_config(config)


def get_prev_settings() -> dict:
    """Extract the settings from the configuration."""
    config = _get_config()
    if config is None:
        return {}
    return config.get("settings", {})


# irods config functions


def is_session_from_config(session: Session) -> Union[Session, None]:
    """Create a new session from the given session.

    For the QThreads we need an own session to avoid hickups.
    We will verify that the given session was instantiated by the
    parameters saved in the ibridges configuration.
    """
    ienv_path = get_last_ienv_path()
    try:
        env = _read_json(ienv_path)
    except Exception:
        return False

    if (
        session.host == env.get("irods_host", -1)
        and session.port == env.get("irods_port", -1)
        and session.zone == env.get("irods_zone_name", -1)
        and session.username == env.get("irods_user_name")
        and session.home == env.get("irods_home", -1)
        and session.default_resc == env.get("irods_default_resource", -1)
    ):
        return True
    return False


def check_irods_config(ienv: Union[Path, dict], include_network=True) -> str:
    """Check whether an iRODS configuration file is correct.

    Parameters
    ----------
    ienv : Path or dict
        Path to the irods_environment.json or the dictionary conatining the json.

    include_network : bool
        If true connect to server and check more parameters. Otherwise only
        existence of parameters in the environment.json will be checked.

    Returns
    -------
    str :
        Error message why login with the settings would fail.
        "All checks passed successfully" in case all seems to be fine.

    """
    if isinstance(ienv, Path):
        try:
            env = _read_json(ienv)
        except FileNotFoundError:
            return f"{ienv} not found."
        except JSONDecodeError as err:
            print(repr(err))
            return f"{ienv} not well formatted.\n {err.msg} at position {err.pos}."
    else:
        env = ienv
    # check host and port and connectivity
    if "irods_host" not in env:
        return '"irods_host" is missing in environment.'
    if "irods_port" not in env:
        return '"irods_port" is missing in environment.'
    if "irods_home" not in env:
        return 'Please set an "irods_home".'
    if "irods_default_resource" not in env:
        return 'Please set an "irods_default_resource".'
    if not isinstance(env["irods_port"], int):
        return '"irods_port" needs to be an integer, remove quotes.'
    if include_network:
        if not Session.network_check(env["irods_host"], env["irods_port"]):
            return f'No connection: Network might be down or\n \
                    server name {env["irods_host"]} is incorrect or\n \
                    port {env["irods_port"]} is incorrect.'
        # check authentication scheme
        try:
            sess = iRODSSession(password="bogus", **env)
            _ = sess.server_version
        except TypeError as err:
            return repr(err)
        except NetworkException as err:
            return repr(err)
        except AttributeError as err:
            return repr(err)
        except PamLoginException as err:
            # irods4.3+ specific
            return f'Adjust "irods_authentication_scheme" {err.args}'
        except ModuleNotFoundError as err:
            # irods4.3+ uses string in authenticationscheme as class
            return f'"irods_authentication_scheme": "{err.name}" does not exist'

        except PlainTextPAMPasswordError:
            return (
                'Value of "irods_client_server_negotiation" needs to be'
                + ' "request_server_negotiation".'
            )

        except CAT_INVALID_AUTHENTICATION:
            return 'Wrong "irods_authentication_scheme".'
        except ValueError as err:
            if "scheme" in err.args[0]:
                return 'Value of "irods_authentication_scheme" not recognised.'
            return f"{err.args}"

        # password incorrect but rest is fine
        except (PAM_AUTH_PASSWORD_INVALID_TTL, CAT_INVALID_USER, PAM_AUTH_PASSWORD_FAILED):
            return "All checks passed successfully."
    # all tests passed
    return "All checks passed successfully."


def save_irods_config(env_path: Union[Path, str], conf: dict):
    """Save an irods environment as json in ~/.irods.

    Parmeters
    ---------
    env_name : str
        file name
    """
    env_path = Path(env_path)
    if env_path.suffix == ".json":
        _write_json(env_path, conf)
    else:
        raise ValueError("Filetype needs to be '.json'.")


def combine_envs_gui_cli() -> dict[str, (tuple[Path, str])]:
    """Read in the saved aliases from the CLI and combine with the GUI environments."""
    cli_servers = IbridgesConf(None).servers
    gui = get_prev_settings()
    aliases = {}

    for env_path, gui_irodsa in gui.items():
        if env_path in cli_servers:
            cli_entry = cli_servers[env_path]
            # env files in cli do not always carry an alias
            alias = cli_entry.get("alias", Path(env_path).name)
            # Use latest GUI password if differs from CLI
            if "irodsa_backup" in cli_entry and gui_irodsa != cli_entry["irodsa_backup"]:
                aliases[alias] = (Path(env_path), gui_irodsa)
            else:
                # aliases do not always have a pw
                irodsa = cli_entry.get("irodsa_backup", gui_irodsa)
                aliases[alias] = (Path(env_path), irodsa)

        else:
            # GUI saved environments do not have an alias, use env file name
            aliases[Path(env_path).name] = (Path(env_path), gui_irodsa)

    # add cli aliases which are not in the gui config
    for env_path in cli_servers:
        if env_path not in gui.keys():
            alias = cli_servers[env_path].get("alias", Path(env_path).name)
            irodsa = cli_servers[env_path].get("irodsa_backup", None)
            aliases[alias] = (env_path, irodsa)

    return aliases


def _read_json(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(file_path: Path, content: dict):
    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(content, handle, indent=4)

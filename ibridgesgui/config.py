"""Setting up logger and configuration files"""
from pathlib import Path
from typing import Union

import logging
import logging.handlers
import datetime
import socket
import sys

import json
from json import JSONDecodeError

from irods.session import iRODSSession
from irods.exception import NetworkException, CAT_INVALID_USER, PAM_AUTH_PASSWORD_FAILED
from ibridges.session import LoginError

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


def ensure_log_config_location():
    """The location for logs and config files"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# logging functions
def init_logger(app_name: str, log_level: str) -> logging.Logger:
    """
    Create a logger for an app

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

    # Logger greeting when app is started
    with open(logfile, "a", encoding="utf-8") as logfd:
        logfd.write("\n\n")
        underscores = f"{'_' * 50}\n"
        logfd.write(underscores * 2)
        logfd.write(f"\t Starting iBridges-GUI \n\t{datetime.datetime.now().isoformat()}\n")
        logfd.write(underscores * 2)

    return logger

# ibridges config functions
def get_last_ienv_path() -> Union[None, str]:
    """Retrieve last used environment path from the config file"""
    config = _get_config()
    if config is not None:
        return config.get("gui_last_env")
    return None

def set_last_ienv_path(ienv_path: Path):
    """
    Save the last used environment path to the config file

    ienv_path : Path
        Path to last environment
    """
    config = _get_config()
    if config is not None:
        config["gui_last_env"] = ienv_path
    else:
        config = {"gui_last_env": ienv_path}
    _save_config(config)

def get_log_level() -> Union[None, str]:
    """Retrieve log level from config"""
    config = _get_config()
    if config is not None:
        return config.get("log_level")
    return None

def set_log_level(level: str):
    """Save log level to config"""
    config = _get_config()
    if config is not None:
        config["log_level"] = level
    else:
        config = {"log_level": level}
    _save_config(config)

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

# irods config functions
def check_irods_config(ienv: Union[Path, dict]) -> str:
    """
    Checks whether an iRODS cofiguration file is correct.

    Parameters:
    -----------
    conf_path : Path
        Path to the irods_environment.json

    Returns:
    --------
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
            return f"{ienv} not well formatted.\n{err.msg}"
    else:
        env = ienv
    # check host and port and connectivity
    if "irods_host" not in env:
        return '"irods_host" is missing in environment.'
    if "irods_port" not in env:
        return '"irods_port" is missing in environment.'
    if not isinstance(env["irods_port"], int):
        return '"irods_port" needs to be an integer, remove quotes.'
    if not _network_check(env["irods_host"], env["irods_port"]):
        return f'No connection: {env["irods_host"]} or {env["irods_port"]} are incorrect.'
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

    # password incorrect but rest is fine
    except (ValueError, CAT_INVALID_USER, PAM_AUTH_PASSWORD_FAILED):
        return "All checks passed successfully."

    # all tests passed
    return "All checks passed successfully."

def save_irods_config(env_path: Union[Path, str], conf: dict):
    """
    Saves an irods environment as json in ~/.irods

    Parmeters
    ---------
    env_name : str
        file name
    """
    env_path = Path(env_path)
    if env_path.suffix == ".json":
        _write_json(env_path, conf)
    else:
        raise TypeError("Filetype needs to be '.json'.")

def _network_check(hostname: str, port: int) -> bool:
    """Check connectivity to an iRODS server.

    Parameters
    ----------
    hostname : str
        FQDN/IP of an iRODS server.

    Returns
    -------
    bool
        Connection to `hostname` possible.

    """
    if hostname is None or port is None:
        raise LoginError("No host or port set in environment file.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.settimeout(10.0)
            sock.connect((hostname, port))
            return True
        except socket.error:
            return False

def _read_json(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as handle:
        return json.load(handle)

def _write_json(file_path: Path, content: dict):
    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(content, handle)

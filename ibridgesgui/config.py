"""Setting up logger and configuration files"""
from pathlib import Path
from typing import Union

import logging
import logging.handlers
import datetime
import json
import sys

LOG_LEVEL = {
    'fulldebug': logging.DEBUG - 5,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

CONFIG_DIR = Path("~/.ibridges").expanduser()
CONFIG_FILE = CONFIG_DIR.joinpath("ibridges_gui.json")

def ensure_log_config_location():
    """The location for logs and config files"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def init_logger(app_name: str, log_level: str) -> logging.Logger:
    """
    Create a logger for an app

    app_name : str
        Name of the app, will be used as file name
    log_level : str
        String that will be mapped to python's log levels, default is info
    """
    logger = logging.getLogger(app_name)
    logfile = CONFIG_DIR.joinpath(f'{app_name}.log')

    # Direct logging to logfile
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(logfile, 'a', 100000, 1)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(LOG_LEVEL.get(log_level, LOG_LEVEL['info']))

    # Logger greeting when app is started
    with open(logfile, 'a', encoding='utf-8') as logfd:
        logfd.write('\n\n')
        underscores = f'{"_" * 50}\n'
        logfd.write(underscores * 2)
        logfd.write(f'\t Starting iBridges-GUI \n\t{datetime.datetime.now().isoformat()}\n')
        logfd.write(underscores * 2)

    return logger

def _get_config() -> Union[None, dict]:
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return None
    except json.decoder.JSONDecodeError as err:
        # empty file
        if err.msg == "Expecting value":
            return None
        print(f"CANNOT START APP: {CONFIG_FILE} incorrectly formatted.")
        sys.exit(1)

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
        config['gui_last_env'] = ienv_path
    else:
        config = {'gui_last_env': ienv_path}
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
        config['log_level'] = level
    else:
        config = {'log_level': level}
    _save_config(config)

def _save_config(conf: dict):
    ensure_log_config_location()
    with open(CONFIG_FILE, "w", encoding="utf-8") as handle:
        json.dump(conf, handle)

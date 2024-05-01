"""Setting up logger and configuration files"""
from pathlib import Path
import logging
import logging.handlers
import datetime

LOG_LEVEL = {
    'fulldebug': logging.DEBUG - 5,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

def _log_config_location() -> Path:
    """The location for logs and config files"""
    logdir = Path("~/.ibridges").expanduser()
    logdir.mkdir(parents=True, exist_ok=True)
    return logdir

def init_logger(app_name: str, log_level: str) -> logging.Logger: 
    logger = logging.getLogger(app_name)
    logfile = _log_config_location().joinpath(f'{app_name}.log')

    # Direct logging to logfile
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(logfile, 'a', 100000, 1)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if log_level in LOG_LEVEL:
        logger.setLevel(LOG_LEVEL[log_level])
    else:
        logger.setLevel(LOG_LEVEL["info"])

    # Logger greeting when app is started
    with open(logfile, 'a', encoding='utf-8') as logfd:
        logfd.write('\n\n')
        underscores = f'{"_" * 50}\n'
        logfd.write(underscores * 2)
        logfd.write(f'\t Starting iBridges-GUI \n\t{datetime.datetime.now().isoformat()}\n')
        logfd.write(underscores * 2)

    return logger


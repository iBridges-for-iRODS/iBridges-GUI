"""main app."""
from __future__ import annotations

import os
import sys

import setproctitle
from PySide6.QtWidgets import QApplication, QStackedWidget

from ibridgesgui import config as config_module
from ibridgesgui.mainmenu import ConfigManager
from ibridgesgui.mainmenu.main_window import MainWindow

THIS_APPLICATION = "ibridges-gui"


def main(session=None) -> None:
    """Start app."""
    setproctitle.setproctitle(THIS_APPLICATION)

    # Load GUI config
    cfg = ConfigManager()

    # Logging level from config
    level = cfg.get_log_level() or "debug"

    # IMPORTANT: call init_logger from the MODULE, not the ConfigManager
    logger = config_module.init_logger(THIS_APPLICATION, level)
    logger.info("Starting application")

    # Ensure ~/.irods exists
    config_module.ensure_irods_location()

    # Set working directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Qt app
    app = QApplication(sys.argv)
    container = QStackedWidget()

    # Main window
    window = MainWindow(THIS_APPLICATION, session, cfg)
    container.addWidget(window)
    container.show()

    app.exec()


if __name__ == "__main__":
    main()

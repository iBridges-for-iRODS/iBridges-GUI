"""Logging tab."""

import logging
import sys

import PySide6

from ibridgesgui.config import CONFIG_DIR
from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.ui_files.tabLogging import Ui_tabLogging


class QPlainTextEditLogger(logging.Handler, PySide6.QtCore.QObject):
    """log handler."""

    def __init__(self, widget: PySide6.QtWidgets.QPlainTextEdit):
        """Initialize the log handler."""
        PySide6.QtCore.QObject.__init__(self)
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record: logging.LogRecord):
        """Pass `record` to all connected slots."""
        msg = self.format(record) + "\n"
        self.widget.insertPlainText(msg)


class LogViewer(PySide6.QtWidgets.QWidget, Ui_tabLogging):
    """Set iBridges logging in GUI."""

    def __init__(self, logger):
        """Initialise the tab."""
        super().__init__()
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabLogging.ui", self)

        self.logger = logger
        self.log_label.setText(str(CONFIG_DIR))
        self.log_text = QPlainTextEditLogger(self.log_browser)
        self.log_text.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s")
        )
        self.logger.addHandler(self.log_text)
        self.logger.setLevel(logging.DEBUG)

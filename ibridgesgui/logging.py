"""Logging tab."""

import logging
import sys

import PyQt6

from ibridgesgui.config import CONFIG_DIR
from ibridgesgui.gui_utils import UI_FILE_DIR
from ibridgesgui.ui_files.tabLogging import Ui_tabLogging


class QPlainTextEditLogger(logging.Handler, PyQt6.QtCore.QObject):
    """A log handler."""

    append_plain_text = PyQt6.QtCore.pyqtSignal(str)

    def __init__(self, widget: PyQt6.QtWidgets.QTextBrowser):
        """Initialize the log handler."""
        super().__init__()
        PyQt6.QtCore.QObject.__init__(self)
        self.widget = widget
        self.widget.setReadOnly(True)
        self.append_plain_text.connect(self.widget.append)

    def emit(self, record: logging.LogRecord):
        """Pass `record` to all connected slots."""
        #msg = self.format(record)
        msg = record.getMessage()
        self.append_plain_text.emit(msg)



class Logging(PyQt6.QtWidgets.QWidget, Ui_tabLogging):
    """Set iBridges logging in GUI."""

    def __init__(self, logger):
        """Initialise the tab."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi(UI_FILE_DIR / "tabLogging.ui", self)

        self.logger = logger
        self.log_label.setText(str(CONFIG_DIR))
        self.logging.append("")
        log_handler = QPlainTextEditLogger(self.logging)
        self.logger.addHandler(log_handler)

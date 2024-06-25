"""Logging tab."""

import logging
import sys

import PyQt6

from ibridgesgui.config import CONFIG_DIR
from ibridgesgui.gui_utils import UI_FILE_DIR
from ibridgesgui.ui_files.tabLogging import Ui_tabLogging


class QTextEditLogger(logging.Handler, PyQt6.QtCore.QObject):
    append_plain_text = PyQt6.QtCore.pyqtSignal(str)

    def __init__(self, text_browser):
        super().__init__()
        PyQt6.QtCore.QObject.__init__(self)
        self.widget = text_browser
        self.widget.setReadOnly(True)
        self.append_plain_text.connect(self.widget.insertPlainText)

    def emit(self, record):
        msg = self.format(record)+"\n"
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
        self.log_text = QTextEditLogger(self.log_browser)
        self.log_text.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s'))
        self.logger.addHandler(self.log_text)
        self.logger.setLevel(logging.DEBUG)

    def closeEvent(self):
        print("close logging tab")
        self.logger.removeHandler(self.log_text)


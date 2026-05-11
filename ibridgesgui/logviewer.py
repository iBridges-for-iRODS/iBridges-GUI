"""Log tab."""
import logging
import sys

from PySide6 import QtCore, QtWidgets

from ibridgesgui.config import CONFIG_DIR
from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui
from ibridgesgui.ui_files.tabLogging import Ui_tabLogging


class QPlainTextEditLogger(logging.Handler):
    """Logging handler that writes to a QPlainTextEdit."""

    def __init__(self, widget):
        """Init."""
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        """Append to current text in Editor."""
        msg = self.format(record)
        QtCore.QMetaObject.invokeMethod(
            self.widget,
            "append",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, msg),
        )


class LogViewer(QtWidgets.QWidget, Ui_tabLogging):
    """Logging tab."""

    def __init__(self, logger):
        """Init."""
        super().__init__()
        self._load_ui()

        self.logger = logger
        self.log_label.setText(str(CONFIG_DIR))

        self._attach_logger()

    def _load_ui(self):
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabLogging.ui", self)

    def _attach_logger(self):
        handler = QPlainTextEditLogger(self.log_browser)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s"
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self._handler = handler

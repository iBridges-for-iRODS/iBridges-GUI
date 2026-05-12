"""Welcome tab."""

import sys
from datetime import datetime

from PySide6 import QtCore, QtGui, QtWidgets

from ibridgesgui.gui_utils import LOGO_DIR, UI_FILE_DIR, load_ui
from ibridgesgui.ui_files.welcome import Ui_Welcome


class Welcome(QtWidgets.QWidget, Ui_Welcome):
    """Welcome page."""

    def __init__(self):
        """Init."""
        super().__init__()
        self._load_ui()
        self._setup_logo()
        self._setup_layout()

    def _load_ui(self):
        """Load UI from .ui file or compiled version."""
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "welcome.ui", self)

    def _setup_logo(self):
        """Choose seasonal or default logo."""
        logo_file = (
            "christmas-logo.png"
            if datetime.today().month == 12
            else "logo.png"
        )
        pixmap = QtGui.QPixmap(str(LOGO_DIR / logo_file))

        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)

        self.tag_label = QtWidgets.QLabel(
            "Bridging Science and Research Data Management."
        )
        self.tag_label.setAlignment(QtCore.Qt.AlignCenter)

    def _setup_layout(self):
        """Build the layout for the welcome screen."""
        layout = QtWidgets.QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.logo_label)
        layout.addWidget(self.tag_label)
        layout.addStretch(1)
        self.setLayout(layout)

"""Welcome tab."""

import sys

import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic

from ibridgesgui.gui_utils import LOGO_DIR, UI_FILE_DIR
from ibridgesgui.ui_files.welcome import Ui_Welcome


class Welcome(PyQt6.QtWidgets.QWidget, Ui_Welcome):
    """Welcome page."""

    def __init__(self):
        """Initialize welcome tab."""
        super().__init__()
        if getattr(sys, "frozen", False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi(UI_FILE_DIR / "welcome.ui", self)

        self.pixmap = PyQt6.QtGui.QPixmap(str(LOGO_DIR / "logo.png"))
        self.logo = PyQt6.QtWidgets.QLabel()
        self.logo.setPixmap(self.pixmap)
        self.logo.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.logo.resize(self.pixmap.width(), self.pixmap.height())

        self.tag = PyQt6.QtWidgets.QLabel()
        self.tag.setText("Bridging Science and Research Data Management.")
        self.tag.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)

        self.grid = PyQt6.QtWidgets.QGridLayout()
        self.grid.addWidget(PyQt6.QtWidgets.QLabel(), 0, 1)
        self.grid.addWidget(self.logo, 1, 1)
        self.grid.addWidget(self.tag, 2, 1)
        self.setLayout(self.grid)

        self.setGeometry(150, 150, 300, 300)

        self.show()

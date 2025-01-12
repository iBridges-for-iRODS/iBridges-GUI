"""Welcome tab."""

import sys
from datetime import datetime

import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets

from ibridgesgui.gui_utils import LOGO_DIR, UI_FILE_DIR, load_ui
from ibridgesgui.ui_files.welcome import Ui_Welcome


class Welcome(PySide6.QtWidgets.QWidget, Ui_Welcome):
    """Welcome page."""

    def __init__(self):
        """Initialize welcome tab."""
        super().__init__()
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "welcome.ui", self)

        if datetime.today().month == 12:
            self.pixmap = PySide6.QtGui.QPixmap(str(LOGO_DIR / "christmas-logo.png"))
        else:
            self.pixmap = PySide6.QtGui.QPixmap(str(LOGO_DIR / "logo.png"))
        self.logo = PySide6.QtWidgets.QLabel()
        self.logo.setPixmap(self.pixmap)
        self.logo.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.logo.resize(self.pixmap.width(), self.pixmap.height())

        self.tag = PySide6.QtWidgets.QLabel()
        self.tag.setText("Bridging Science and Research Data Management.")
        self.tag.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignCenter)

        self.grid = PySide6.QtWidgets.QGridLayout()
        self.grid.addWidget(PySide6.QtWidgets.QLabel(), 0, 1)
        self.grid.addWidget(self.logo, 1, 1)
        self.grid.addWidget(self.tag, 2, 1)
        self.setLayout(self.grid)

        self.setGeometry(150, 150, 300, 300)

        self.show()

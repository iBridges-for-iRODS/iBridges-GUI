"""Info tab."""

import sys

from ibridges.resources import Resources
from PySide6 import QtCore, QtWidgets

from ibridgesgui.config import CONFIG_DIR
from ibridgesgui.gui_utils import UI_FILE_DIR, load_ui, populate_table, populate_textfield
from ibridgesgui.ui_files.tabInfo import Ui_tabInfo


class Info(QtWidgets.QWidget, Ui_tabInfo):
    """Tab showing iRODS system information."""

    def __init__(self, session):
        """Init."""
        super().__init__()
        self._load_ui()
        self.session = session

        self.refresh_button.clicked.connect(self.refresh_info)
        self.refresh_info()

    def _load_ui(self):
        if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
            super().setupUi(self)
        else:
            load_ui(UI_FILE_DIR / "tabInfo.ui", self)

    def refresh_info(self):
        """Refetch infor from iRODS."""
        with self._wait_cursor():
            info = self._collect_info()
            self._update_ui(info)

    def _collect_info(self):
        user_type, user_groups = self.session.get_user_info()
        return {
            "zone": self.session.zone,
            "username": self.session.username,
            "user_type": user_type,
            "groups": user_groups,
            "log_dir": str(CONFIG_DIR),
            "default_resc": self.session.default_resc,
            "server": self.session.host,
            "version": ".".join(map(str, self.session.server_version)),
            "resources": Resources(self.session).root_resources,
        }

    def _update_ui(self, info):
        self.zone_label.setText(info["zone"])
        self.user_label.setText(info["username"])
        self.type_label.setText(info["user_type"])
        populate_textfield(self.groups_browser, info["groups"])
        self.log_label.setText(info["log_dir"])
        self.resc_label.setText(info["default_resc"])
        self.server_label.setText(info["server"])
        self.version_label.setText(info["version"])

        resources = [
            tuple("" if v is None else v for v in row)
            for row in info["resources"]
        ]

        populate_table(self.resc_table, len(resources), resources)

        self._autosize_columns(self.resc_table)

    def _autosize_columns(self, table):
        header = table.horizontalHeader()
        for col in range(header.count()):
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

    @staticmethod
    def _wait_cursor():
        class CursorContext:
            """Helper class to steer cursor appearance."""

            def __enter__(self):
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

            def __exit__(self, exc_type, exc, tb):
                QtWidgets.QApplication.restoreOverrideCursor()

        return CursorContext()

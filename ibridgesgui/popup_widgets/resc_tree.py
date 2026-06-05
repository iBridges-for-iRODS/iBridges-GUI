"""Popup to show resource tree."""
from ibridges.resources import Resources
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog, QHeaderView, QTreeWidgetItem

from ibridgesgui.popup_widgets.base import UiDialogMixin
from ibridgesgui.ui_files.rescTree import Ui_rescTree


class RescInfoDialog(QDialog, Ui_rescTree, UiDialogMixin):
    """Popup with resource tree."""

    ui_filename = "rescTree.ui"

    def __init__(self, session, parent=None):
        """Init."""
        super().__init__(parent)
        self._init_ui()
        self.setWindowTitle("Resource Tree")

        self.resc_view.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        self.rescs = Resources(session)
        self.ok_button.clicked.connect(self.accept)

        QtCore.QTimer.singleShot(0, self._adjust_columns)

    def _adjust_columns(self):
        header = self.resc_view.header()

        # Allow columns to shrink below Qt's default minimum
        header.setMinimumSectionSize(0)

        # IMPORTANT: override Qt's default behavior for the LAST column
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.resc_view.setColumnWidth(2, 20)

        # Now set column 1
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.resc_view.setColumnWidth(1, 60)

        # Finally set column 0 to stretch
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.resc_view.setColumnWidth(0, 300)

    def _populate_tree(self):
        self.resc_view.clear()
        resc_dict = self.rescs.resources()

        # Build ID → name mapping
        id_to_name = {}
        for name in resc_dict:
            res_obj = self.rescs.get_resource(name)
            id_to_name[str(res_obj.id)] = name

        items = {}
        for name, fields in resc_dict.items():
            res_obj = self.rescs.get_resource(name)
            rtype = res_obj.type
            display_name = f"{name} ({rtype})"

            size = fields.get("free_space", 0)
            status = fields.get("status", "")

            items[name] = QTreeWidgetItem([
                display_name,
                str(size),
                "" if status is None else str(status)
            ])

        roots = [r[0] for r in self.rescs.root_resources]

        for name, fields in resc_dict.items():
            parent_id = fields.get("parent")
            if parent_id:
                parent_name = id_to_name.get(str(parent_id))
                if parent_name in items:
                    items[parent_name].addChild(items[name])

        # Add root items
        for root in roots:
            self.resc_view.addTopLevelItem(items[root])

        self.resc_view.expandAll()
        QtCore.QTimer.singleShot(0, self._adjust_columns)
        self.error_label.clear()

    # ruff: noqa: N802  # Qt override
    # pylint: disable=invalid-name
    def showEvent(self, event):
        """Populate tree after pop up is opened."""
        super().showEvent(event)
        self.error_label.setText("Loading…")
        QtCore.QTimer.singleShot(0, self._populate_tree)
        QtCore.QTimer.singleShot(50, self._populate_tree)

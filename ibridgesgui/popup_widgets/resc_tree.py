"""Popup to show resource tree."""
from typing import override

from ibridges.resources import Resources
from PySide6 import QtCore
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QHeaderView

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

        self.rescs = Resources(session)

        QtCore.QTimer.singleShot(0, self._adjust_columns)

    def _adjust_columns(self):
        header = self.resc_view.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.resc_view.setColumnWidth(0, 300)

    def _populate_tree(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Resource (Type)", "Size", "Status"])

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

            items[name] = [
                    QStandardItem(display_name),
                    QStandardItem(str(size)),
                    QStandardItem("" if status is None else str(status))
                    ]

        roots = [r[0] for r in self.rescs.root_resources]

        for name, fields in resc_dict.items():
            parent_id = fields.get("parent")
            if parent_id:
                parent_name = id_to_name.get(str(parent_id))
                if parent_name in items:
                    items[parent_name][0].appendRow(items[name])

        for root in roots:
            model.appendRow(items[root])

        self.resc_view.setModel(model)
        self.resc_view.expandAll()
        QtCore.QTimer.singleShot(0, self._adjust_columns)
        self.error_label.clear()

    @override
    def showEvent(self, event):
        """Populate tree after pop up is opened."""
        super().showEvent(event)
        self.error_label.setText("Loading…")
        QtCore.QTimer.singleShot(0, self._populate_tree)

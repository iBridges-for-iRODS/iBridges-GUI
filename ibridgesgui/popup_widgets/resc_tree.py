"""Popup to show resource tree."""
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
        self._populate_tree()

        QtCore.QTimer.singleShot(0, self._adjust_columns)

    def _adjust_columns(self):
        header = self.resc_view.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.resc_view.setColumnWidth(0, 300)

    def _populate_tree(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Resource", "Size", "Status"])

        resc_dict = self.rescs.resources()

        # Build ID → name mapping
        id_to_name = {}
        for name in resc_dict:
            res_obj = self.rescs.get_resource(name)
            id_to_name[str(res_obj.id)] = name

        # Create items for each resource
        items = {}
        for name, fields in resc_dict.items():
            size = fields.get("free_space", 0)
            status = fields.get("status", "")
            items[name] = [
                QStandardItem(name),
                QStandardItem(str(size)),
                QStandardItem("" if status is None else str(status))
            ]

        # Build hierarchy
        roots = []

        for name, fields in resc_dict.items():
            parent_id = fields.get("parent")

            if parent_id is None:
                roots.append(name)
            else:
                parent_name = id_to_name.get(str(parent_id))
                if parent_name and parent_name in items:
                    # Attach child to parent
                    items[parent_name][0].appendRow(items[name])
                else:
                    # Orphan → treat as root
                    roots.append(name)

        # Add only root nodes to the model
        for root in roots:
            model.appendRow(items[root])

        self.resc_view.setModel(model)
        self.resc_view.expandAll()

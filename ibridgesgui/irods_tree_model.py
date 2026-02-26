"""Tree model for iRODS collections with lazy loading and path lookup."""

import irods
import irods.exception
from PySide6 import QtCore, QtGui, QtWidgets
from ibridges import IrodsPath


class IrodsTreeModel(QtGui.QStandardItemModel):
    """Model for an iRODS tree view with lazy loading and path lookup."""

    # Column indices for clarity
    COL_NAME = 0
    COL_LEVEL = 1
    COL_ID = 2
    COL_PARENT_ID = 3
    COL_TYPE = 4       # "C" or "d"
    COL_PATH = 5       # absolute iRODS path

    def __init__(self, tree_view, irods_root_path: IrodsPath):
        super().__init__()
        self.tree_view = tree_view
        self.session = irods_root_path.session
        self.irods_root_path = irods_root_path

        self.clear()

    # ----------------------------------------------------------------------
    # Tree initialization
    # ----------------------------------------------------------------------

    def init_tree(self):
        """Draw the first level of the iRODS filesystem."""
        self.setRowCount(0)
        root_item = self.invisibleRootItem()

        root_coll = IrodsPath(self.session, self.irods_root_path).collection
        root_row = self._tree_row_from_irods_item(root_coll, parent_id=-1, level=-1, display_path=True)
        root_item.appendRow(root_row)

        # Add dummy child to enable lazy expansion
        root_node = root_item.child(root_item.rowCount() - 1)
        root_node.appendRow([QtGui.QStandardItem()])  # dummy

    # ----------------------------------------------------------------------
    # Node creation helpers
    # ----------------------------------------------------------------------

    def _tree_row_from_irods_item(self, item, parent_id, level, display_path=False):
        icon_provider = QtWidgets.QFileIconProvider()

        if display_path:
            display = QtGui.QStandardItem(item.path)
        else:
            display = QtGui.QStandardItem(item.name)

        if isinstance(item, irods.collection.iRODSCollection):
            display.setIcon(icon_provider.icon(QtWidgets.QFileIconProvider.Folder))
            datatype = "C"
        else:
            display.setIcon(icon_provider.icon(QtWidgets.QFileIconProvider.File))
            datatype = "d"

        return [
            display,
            QtGui.QStandardItem(str(level + 1)),
            QtGui.QStandardItem(str(item.id)),
            QtGui.QStandardItem(str(parent_id)),
            QtGui.QStandardItem(datatype),
            QtGui.QStandardItem(item.path),
        ]

    # ----------------------------------------------------------------------
    # Lazy loading
    # ----------------------------------------------------------------------

    def refresh_subtree(self, index: QtCore.QModelIndex):
        """Refresh the subtree under the given index."""
        item = self.itemFromIndex(index)
        parent = item.parent() or self.invisibleRootItem()
        row = item.row()

        # Extract metadata from parent row
        tree_item_data = [
            parent.child(row, col).data(0)
            for col in range(parent.columnCount())
        ]
        abs_path = tree_item_data[self.COL_PATH]
        irods_path = IrodsPath(self.session, abs_path)

        if irods_path.collection_exists():
            self.delete_subtree(item)
            self.add_subtree(item, tree_item_data)

    def delete_subtree(self, tree_item):
        tree_item.removeRows(0, tree_item.rowCount())

    def add_subtree(self, tree_item, tree_item_data):
        _, level, _, _, _, abs_path = tree_item_data
        parent_coll = IrodsPath(self.session, abs_path).collection

        subcolls = [c for c in parent_coll.subcollections if c.path != "/"]
        dataobjs = parent_coll.data_objects

        for item in subcolls + dataobjs:
            row = self._tree_row_from_irods_item(item, parent_coll.id, int(level))
            tree_item.appendRow(row)

            new_node = tree_item.child(tree_item.rowCount() - 1)
            if isinstance(item, irods.collection.iRODSCollection):
                new_node.appendRow([QtGui.QStandardItem()])  # dummy

    # ----------------------------------------------------------------------
    # Path lookup API (new)
    # ----------------------------------------------------------------------

    def index_from_irods_path(self, target_path: IrodsPath):
        """Return the QModelIndex corresponding to an IrodsPath."""
        target_str = str(target_path)
        root_index = self.index(0, 0)
        return self._find_index_recursively(root_index, target_str)

    def _find_index_recursively(self, index, target_path_str):
        if not index.isValid():
            return QtCore.QModelIndex()
    
        # Compare COL_PATH of this row
        path_index = index.sibling(index.row(), self.COL_PATH)
        if path_index.data() == target_path_str:
            return index
    
        # Recurse into children
        item = self.itemFromIndex(index)
        for row in range(item.rowCount()):
            child = item.child(row, 0)
            if child is None:
                continue
            result = self._find_index_recursively(child.index(), target_path_str)
            if result.isValid():
                return result
    
        return QtCore.QModelIndex()
    
    # ----------------------------------------------------------------------
    # Convenience
    # ----------------------------------------------------------------------

    def irods_path_from_tree_index(self, model_index):
        """Convert a tree index to an IrodsPath."""
        item = self.itemFromIndex(model_index)
        row = item.row()
        parent = item.parent() or self.invisibleRootItem()
        abs_path = parent.child(row, self.COL_PATH).data(0)
        return IrodsPath(self.session, abs_path)

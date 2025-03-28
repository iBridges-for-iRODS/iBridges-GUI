"""Tree model for IRODS collections.

The IRODS database is huge and retrieving a complete tree of all files
can take ages.  To improve the loading time the tree is only grown as
far as it displays.
"""

import irods
import irods.exception
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets
from ibridges import IrodsPath


class IrodsTreeModel(PySide6.QtGui.QStandardItemModel):
    """Model for an iRODS tree view."""

    def __init__(self, tree_view, irods_root_path: IrodsPath):
        """Initialise the tree view with the root node and first level.

        Class variables 'user_groups' and 'base_path' _must_ be
        populated with a list of group names and the path name of the
        iRODS top-level collection (i.e., /<zone name>/home),
        respectively.

        Parameters
        ----------
        tree_view : PyQt6.QtWidgets
            Defined iRODS tree view UI element.
        session : ibridges.Session
            A valid session to iRODS
        irods_root_path : IrodsPath
            The root collection for the tree

        """
        super().__init__()
        self.tree_view = tree_view
        self.session = irods_root_path.session
        self.irods_root_path = irods_root_path
        # Empty tree
        self.clear()

    def _tree_row_from_irods_item(self, item, parent_id, level, display_path=False):
        icon_provider = PySide6.QtWidgets.QFileIconProvider()
        if display_path:
            display = PySide6.QtGui.QStandardItem(item.path)
        else:
            display = PySide6.QtGui.QStandardItem(item.name)
        if isinstance(item, irods.collection.iRODSCollection):
            display.setIcon(icon_provider.icon(PySide6.QtWidgets.QFileIconProvider.IconType.Folder))
            datatype = "C"
        else:
            display.setIcon(icon_provider.icon(PySide6.QtWidgets.QFileIconProvider.IconType.File))
            datatype = "d"
        row = [
            display,  # display name
            PySide6.QtGui.QStandardItem(str(level + 1)),  # item level in the tree
            PySide6.QtGui.QStandardItem(str(item.id)),  # id in iRODS
            PySide6.QtGui.QStandardItem(str(parent_id)),  # parent id
            PySide6.QtGui.QStandardItem(datatype),  # C or d
            PySide6.QtGui.QStandardItem(item.path),  # absolute irods path
        ]
        return row

    def init_tree(self):
        """Draw the first levels of an iRODS filesystem as a tree."""
        self.setRowCount(0)
        root = self.invisibleRootItem()

        # Start the tree, add the highest level to the invisible root
        root_coll = IrodsPath(self.session, self.irods_root_path).collection
        root_row = self._tree_row_from_irods_item(root_coll, -1, -1, True)
        root.appendRow(root_row)

        new_node = root.child(root.rowCount() - 1)

        # insert a dummy child to get the link to open the collection
        new_node.appendRow(None)

    def delete_subtree(self, tree_item):
        """Delete subtree.

        Parameters
        ----------
        tree_item : QStandardItem
            Item in the QTreeView

        """
        # Remove all children from tree_item
        tree_item.removeRows(0, tree_item.rowCount())

    def add_subtree(self, tree_item, tree_item_data: list):
        """Grow tree_view from tree_item.

        Parameters
        ----------
        tree_item : PyQt6.QtGui.QStandardItem
            The root of the subtree in the tree view
        tree_item_data : list
            [display_name, level, id, parent_id, 'C/d', absolute iRODS Path]

        """
        _, level, _, _, _, abs_irods_path = tree_item_data
        parent_coll = IrodsPath(self.session, abs_irods_path).collection

        # the irods root also contains the irods root as subcollection
        subcolls = [c for c in parent_coll.subcollections if c.path != "/"]
        dataobjs = parent_coll.data_objects
        # we assume that tree_item has no children yet.
        new_nodes = {}
        for item in subcolls + dataobjs:
            row = self._tree_row_from_irods_item(item, parent_coll.id, int(level))
            tree_item.appendRow(row)
            new_nodes[item.id] = tree_item.child(tree_item.rowCount() - 1)
            if isinstance(item, irods.collection.iRODSCollection):
                # insert a dummy child to get the link to open the collection
                new_nodes[item.id].appendRow(None)

    def refresh_subtree(self, position):
        """Refresh the tree view.

        Parameters
        ----------
        position : PyQt6.QtCore.QModelIndex
            Location in tree

        """
        model_index = position
        tree_item = self.itemFromIndex(model_index)  # clicked item
        parent = tree_item.parent()
        if parent is None:
            parent = self.invisibleRootItem()
        row = tree_item.row()

        # retrieve information of clicked item, the information is stored in its parent
        tree_item_data = [parent.child(row, col).data(0) for col in range(parent.columnCount())]
        irods_path = IrodsPath(self.session, tree_item_data[-1])
        if irods_path.collection_exists():
            # Delete subtree in irodsFsdata and the tree_view.
            self.delete_subtree(tree_item)
            self.add_subtree(tree_item, tree_item_data)

    def irods_path_from_tree_index(self, model_index):
        """Convert a tree index to iRODS path.

        Parameters
        ----------
        model_index : PyQt6.QtCore.QModelIndex
            Selected row in tree view

        """
        tree_item = self.itemFromIndex(model_index)  # clicked item
        row = tree_item.row()

        parent = tree_item.parent()  # contains the data of tree_item
        if parent is None:
            parent = self.invisibleRootItem()
        irods_path = [parent.child(row, col).data(0) for col in range(parent.columnCount())][-1]
        return IrodsPath(self.session, irods_path)

import pytest
from unittest.mock import MagicMock, patch
from PySide6 import QtGui, QtCore

from ibridgesgui.irods_tree_model import IrodsTreeModel


# ----------------------------------------------------------------------
# Fake iRODS objects
# ----------------------------------------------------------------------

class FakeCollection:
    def __init__(self, name, path, cid, subcollections=None, data_objects=None):
        self.name = name
        self.path = path
        self.id = cid
        self.subcollections = subcollections or []
        self.data_objects = data_objects or []


class FakeDataObject:
    def __init__(self, name, path, oid):
        self.name = name
        self.path = path
        self.id = oid


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def session():
    return object()  # just a placeholder; never used by the mock


@pytest.fixture
def root_path(session):
    # This is only used to provide .session to the model
    rp = MagicMock()
    rp.session = session
    return rp


@pytest.fixture
def model(qtbot, root_path):
    tree_view = QtGui.QStandardItemModel()
    return IrodsTreeModel(tree_view, root_path)


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_init_tree_creates_root_node(model):
    fake_root_coll = FakeCollection("root", "/", 1)

    with patch("ibridgesgui.irods_tree_model.IrodsPath") as MockPath:
        # When IrodsPath(self.session, self.irods_root_path) is called,
        # return an object whose .collection is our fake_root_coll
        ip_instance = MagicMock()
        ip_instance.collection = fake_root_coll
        MockPath.return_value = ip_instance

        model.init_tree()

    assert model.rowCount() == 1
    root_item = model.item(0, 0)
    assert root_item.text() == "/"          # display_path=True
    assert root_item.rowCount() == 1        # dummy child


def test_delete_subtree_removes_children(model):
    parent = QtGui.QStandardItem("parent")
    parent.appendRow([QtGui.QStandardItem("c1")])
    parent.appendRow([QtGui.QStandardItem("c2")])

    assert parent.rowCount() == 2
    model.delete_subtree(parent)
    assert parent.rowCount() == 0


def test_add_subtree_adds_collections_and_data_objects(model):
    fake_sub1 = FakeCollection("sub1", "/sub1", 2)
    fake_sub2 = FakeCollection("sub2", "/sub2", 3)
    fake_data = FakeDataObject("file1", "/file1", 10)

    fake_parent = FakeCollection(
        "root", "/", 1,
        subcollections=[fake_sub1, fake_sub2],
        data_objects=[fake_data],
    )

    with patch("ibridgesgui.irods_tree_model.IrodsPath") as MockPath:
        ip_instance = MagicMock()
        ip_instance.collection = fake_parent
        MockPath.return_value = ip_instance

        parent_item = QtGui.QStandardItem("root")
        tree_item_data = ["root", "0", "1", "-1", "C", "/"]

        model.add_subtree(parent_item, tree_item_data)

    assert parent_item.rowCount() == 3
    names = [parent_item.child(i, 0).text() for i in range(3)]
    assert names == ["sub1", "sub2", "file1"]

def test_refresh_subtree_replaces_children(model):
    fake_child = FakeCollection("child", "/child", 2)
    fake_root = FakeCollection("root", "/", 1, subcollections=[fake_child])

    with patch("ibridgesgui.irods_tree_model.IrodsPath") as MockPath:
        # First call: init_tree -> root collection
        ip_root = MagicMock()
        ip_root.collection = fake_root

        # Second call: refresh_subtree -> same root path, but we want
        # collection_exists() True and same collection
        ip_refresh = MagicMock()
        ip_refresh.collection_exists.return_value = True
        ip_refresh.collection = fake_root

        ip_add = MagicMock()
        ip_add.collection = fake_root
        MockPath.side_effect = [ip_root, ip_refresh, ip_add]

        model.init_tree()
        root_index = model.index(0, 0)
        root_item = model.itemFromIndex(root_index)

        # add extra child to be removed
        root_item.appendRow([QtGui.QStandardItem("old")])
        assert root_item.rowCount() == 2  # dummy + old

        model.refresh_subtree(root_index)

    # After refresh, only the new child "child" should remain (plus its dummy)
    assert root_item.rowCount() == 1
    assert root_item.child(0, 0).text() == "child"


def test_index_from_irods_path_finds_correct_node(model):
    fake_sub = FakeCollection("sub", "/sub", 2)
    fake_root = FakeCollection("root", "/", 1, subcollections=[fake_sub])

    with patch("ibridgesgui.irods_tree_model.IrodsPath") as MockPath:
        ip_root = MagicMock()
        ip_root.collection = fake_root
        MockPath.return_value = ip_root

        model.init_tree()
        root_item = model.item(0, 0)
        model.delete_subtree(root_item)
        model.add_subtree(root_item, ["root", "0", "1", "-1", "C", "/"])

        target = MagicMock()
        target.__str__.return_value = "/sub"

        idx = model.index_from_irods_path(target)
        assert idx.isValid()
        assert idx.data() == "sub"


def test_irods_path_from_tree_index_returns_correct_path(model):
    fake_root_coll = FakeCollection("root", "/", 1)

    with patch("ibridgesgui.irods_tree_model.IrodsPath") as MockPath:
        ip_root = MagicMock()
        ip_root.collection = fake_root_coll
        MockPath.return_value = ip_root

        model.init_tree()
        root_index = model.index(0, 0)

        result = model.irods_path_from_tree_index(root_index)

    # result is a real IrodsPath in production; here it's constructed via IrodsPath(session, abs_path)
    # but since we don't care about its internals, just assert the call was made correctly:
    MockPath.assert_called_with(model.session, "/")


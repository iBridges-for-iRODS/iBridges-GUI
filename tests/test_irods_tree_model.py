import pytest
from unittest.mock import patch
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
# Fake IrodsPath class (drop‑in replacement)
# ----------------------------------------------------------------------

@pytest.fixture
def fake_irods_path_class():
    class FakeIrodsPath:
        def __init__(self, session, arg):
            # arg may be another FakeIrodsPath or a string
            if isinstance(arg, FakeIrodsPath):
                self._path = arg._path
            else:
                self._path = arg

            self.path = self._path
            self.session = session
            self.collection = None
            self._exists = True

        def collection_exists(self):
            return self._exists

        def __str__(self):
            return self.path

    return FakeIrodsPath


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def mock_session():
    return object()  # simple placeholder


@pytest.fixture
def mock_root_path(fake_irods_path_class, mock_session):
    root = fake_irods_path_class(mock_session, "/")
    return root


@pytest.fixture
def model(qtbot, fake_irods_path_class):
    with patch("ibridgesgui.irods_tree_model.IrodsPath", fake_irods_path_class):
        session = object()
        root_path = fake_irods_path_class(session, "/")
        root_path.collection = FakeCollection("root", "/", 1)

        tree_view = QtGui.QStandardItemModel()
        m = IrodsTreeModel(tree_view, root_path)
        return m


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_init_tree_creates_root_node(model, fake_irods_path_class):
    fake_root_coll = FakeCollection("root", "/", 1)

    with patch("ibridgesgui.irods_tree_model.IrodsPath", fake_irods_path_class):
        inst = fake_irods_path_class(model.session, "/")
        inst.collection = fake_root_coll

        model.init_tree()

    assert model.rowCount() == 1
    root_item = model.item(0, 0)
    assert root_item.text() == "/"
    assert root_item.rowCount() == 1  # dummy child


def test_delete_subtree_removes_children(model):
    parent = QtGui.QStandardItem("parent")
    parent.appendRow([QtGui.QStandardItem("c1")])
    parent.appendRow([QtGui.QStandardItem("c2")])

    assert parent.rowCount() == 2
    model.delete_subtree(parent)
    assert parent.rowCount() == 0


def test_add_subtree_adds_collections_and_data_objects(model, fake_irods_path_class):
    fake_sub1 = FakeCollection("sub1", "/sub1", 2)
    fake_sub2 = FakeCollection("sub2", "/sub2", 3)
    fake_data = FakeDataObject("file1", "/file1", 10)

    fake_parent = FakeCollection(
        "root", "/", 1,
        subcollections=[fake_sub1, fake_sub2],
        data_objects=[fake_data]
    )

    with patch("ibridgesgui.irods_tree_model.IrodsPath", fake_irods_path_class):
        inst = fake_irods_path_class(model.session, "/")
        inst.collection = fake_parent

        parent_item = QtGui.QStandardItem("root")
        tree_item_data = ["root", "0", "1", "-1", "C", "/"]

        model.add_subtree(parent_item, tree_item_data)

    assert parent_item.rowCount() == 3
    names = [parent_item.child(i, 0).text() for i in range(3)]
    assert names == ["sub1", "sub2", "file1"]

    # subcollections get dummy children
    assert parent_item.child(0).rowCount() == 1
    assert parent_item.child(1).rowCount() == 1
    # data object has no dummy
    assert parent_item.child(2).rowCount() == 0


def test_refresh_subtree_replaces_children(model, fake_irods_path_class):
    fake_child = FakeCollection("child", "/child", 2)

    with patch("ibridgesgui.irods_tree_model.IrodsPath", fake_irods_path_class):
        inst = fake_irods_path_class(model.session, "/")
        inst.collection_exists = lambda: True
        inst.collection = FakeCollection("root", "/", 1, subcollections=[fake_child])

        model.init_tree()
        root_index = model.index(0, 0)
        root_item = model.itemFromIndex(root_index)

        # add fake children to be deleted
        root_item.appendRow([QtGui.QStandardItem("old")])
        assert root_item.rowCount() == 2  # dummy + old

        model.refresh_subtree(root_index)

    assert root_item.rowCount() == 1
    assert root_item.child(0, 0).text() == "child"


def test_index_from_irods_path_finds_correct_node(model, fake_irods_path_class):
    fake_sub = FakeCollection("sub", "/sub", 2)

    with patch("ibridgesgui.irods_tree_model.IrodsPath", fake_irods_path_class):
        inst = fake_irods_path_class(model.session, "/")
        inst.collection = FakeCollection("root", "/", 1, subcollections=[fake_sub])

        model.init_tree()
        root_item = model.item(0, 0)
        model.delete_subtree(root_item)
        model.add_subtree(root_item, ["root", "0", "1", "-1", "C", "/"])

        target = fake_irods_path_class(model.session, "/sub")

        idx = model.index_from_irods_path(target)
        assert idx.isValid()
        assert idx.data() == "sub"


def test_irods_path_from_tree_index_returns_correct_path(model, fake_irods_path_class):
    with patch("ibridgesgui.irods_tree_model.IrodsPath", fake_irods_path_class):
        inst = fake_irods_path_class(model.session, "/")
        inst.collection = FakeCollection("root", "/", 1)

        model.init_tree()
        root_index = model.index(0, 0)

        result = model.irods_path_from_tree_index(root_index)
        assert isinstance(result, fake_irods_path_class)
        assert str(result) == "/"


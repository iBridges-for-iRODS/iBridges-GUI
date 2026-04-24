import pytest
from unittest.mock import MagicMock, patch
from ibridgesgui.browsertab.irods_browser_service import IrodsBrowserService


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def service(session, logger):
    return IrodsBrowserService(session, logger)


# -------------------------
# PATH HANDLING
# -------------------------

def test_path_from_text(service, session):
    p = service.path_from_text("/tempZone/home/user")
    assert p.session is session
    assert str(p) == "/tempZone/home/user"


def test_home_path(service, session):
    p = service.home_path()
    assert p.session is session


def test_parent_path(service, session):
    p = service.parent_path("/tempZone/home/user/file.txt")
    assert p.session is session
    assert str(p) == "/tempZone/home/user"


# -------------------------
# COLLECTION LISTING
# -------------------------

def test_list_collection(service):
    path = MagicMock()
    path.collection.subcollections = ["c1", "c2"]
    path.collection.data_objects = ["d1", "d2"]

    subs, objs = service.list_collection(path)
    assert subs == ["c1", "c2"]
    assert objs == ["d1", "d2"]


# -------------------------
# STREAMING
# -------------------------

def test_stream_obj(service):
    stream = MagicMock()
    stream.read.return_value = b"hello world"

    path = MagicMock()
    path.open.return_value.__enter__.return_value = stream

    result = service.stream_obj(path)
    assert result == ["hello world"]


# -------------------------
# PREVIEW
# -------------------------

def test_preview_collection(service):
    path = MagicMock()
    path.collection_exists.return_value = True
    path.dataobject_exists.return_value = False

    sub = MagicMock()
    sub.name = "sub1"
    obj = MagicMock()
    obj.name = "file1"

    service.list_collection = MagicMock(return_value=([sub], [obj]))

    result = service.compute_preview(path)
    assert "Collections:" in result[0]
    assert "sub1" in result
    assert "DataObjects:" in result
    assert "file1" in result


def test_preview_text_file(service):
    path = MagicMock()
    path.collection_exists.return_value = False
    path.dataobject_exists.return_value = True
    path.name = "test.txt"

    service.stream_obj = MagicMock(return_value=["hello"])

    result = service.compute_preview(path)
    assert result == ["hello"]


def test_preview_non_text_file(service):
    path = MagicMock()
    path.collection_exists.return_value = False
    path.dataobject_exists.return_value = True
    path.name = "binary.bin"

    result = service.compute_preview(path)
    assert "No Preview" in result[0]


def test_preview_stream_error(service):
    path = MagicMock()
    path.collection_exists.return_value = False
    path.dataobject_exists.return_value = True
    path.name = "test.txt"

    service.stream_obj = MagicMock(side_effect=Exception("boom"))

    result = service.compute_preview(path)
    assert "Storage resource might be down." in result[-1]


# -------------------------
# REPLICAS
# -------------------------

@patch("ibridgesgui.browsertab.irods_browser_service.obj_replicas")
def test_get_replicas_no_dataobject(mock_repl, service):
    path = MagicMock()
    path.dataobject_exists.return_value = False

    assert service.get_replicas(path) == []
    mock_repl.assert_not_called()


@patch("ibridgesgui.browsertab.irods_browser_service.obj_replicas")
def test_get_replicas_with_dataobject(mock_repl, service):
    path = MagicMock()
    path.dataobject_exists.return_value = True
    path.dataobject = MagicMock()

    mock_repl.return_value = ["r1", "r2"]

    assert service.get_replicas(path) == ["r1", "r2"]
    mock_repl.assert_called_once_with(path.dataobject)


# -------------------------
# METADATA
# -------------------------

def test_get_metadata(service):
    avu = MagicMock()
    avu.name = "k"
    avu.value = "v"
    avu.units = "u"

    path = MagicMock()
    path.meta = [avu]

    result = service.get_metadata(path)
    assert result == [("k", "v", "u")]


def test_add_metadata(service):
    path = MagicMock()
    service.add_metadata(path, "k", "v", "u")
    path.meta.add.assert_called_once_with("k", "v", "u")


def test_update_metadata(service):
    item = MagicMock()
    path = MagicMock()
    path.meta.__getitem__.return_value = item

    service.update_metadata(path, "old", "oldv", "oldu", "new", "newv", "newu")

    assert item.key == "new"
    assert item.value == "newv"
    assert item.units == "newu"


def test_delete_metadata(service):
    path = MagicMock()
    service.delete_metadata(path, "k", "v", "u")
    path.meta.delete.assert_called_once_with("k", "v", "u")


# -------------------------
# ACLs
# -------------------------

def test_normalize_acls(service):
    acls = [
        ("u", "z", "read_object", "flag"),
        ("u2", "z2", "modify_object", "flag2"),
        ("u3", "z3", "own", "flag3"),
    ]
    clean = service.normalize_acls(acls)

    assert clean[0][2] == "read"
    assert clean[1][2] == "write"
    assert clean[2][2] == "own"


@patch("ibridgesgui.browsertab.irods_browser_service.get_irods_item")
@patch("ibridgesgui.browsertab.irods_browser_service.Permissions")
def test_get_acls(mock_perms, mock_item, service):
    path = MagicMock()
    path.collection_exists.return_value = True
    path.collection.inheritance = "yes"

    perm_obj = MagicMock()
    perm_obj.user_name = "u"
    perm_obj.user_zone = "z"
    perm_obj.access_name = "read"

    mock_perms.return_value = [perm_obj]

    result = service.get_acls(path)
    assert result == [("u", "z", "read", "yes")]


@patch("ibridgesgui.browsertab.irods_browser_service.get_irods_item")
@patch("ibridgesgui.browsertab.irods_browser_service.Permissions")
def test_set_acl(mock_perms, mock_item, service):
    path = MagicMock()
    perms = mock_perms.return_value

    service.set_acl(path, "u", "z", "read", True)
    perms.set.assert_called_once_with(
        perm="read",
        user="u",
        zone="z",
        recursive=True,
    )


# -------------------------
# TABLE ROWS
# -------------------------

@patch("ibridgesgui.browsertab.irods_browser_service.obj_replicas")
def test_list_table_rows(mock_repl, service):
    subcoll = MagicMock()
    subcoll.name = "sub"
    subcoll.create_time.strftime.return_value = "01-01-2020"
    subcoll.modify_time.strftime.return_value = "01-01-2020 10:00"

    obj = MagicMock()
    obj.name = "file.txt"
    obj.size = 123
    obj.checksum = "abc"
    obj.create_time.strftime.return_value = "02-01-2020"
    obj.modify_time.strftime.return_value = "02-01-2020 11:00"

    mock_repl.return_value = [(None, None, None, None, 5)]

    path = MagicMock()
    path.collection.subcollections = [subcoll]
    path.collection.data_objects = [obj]

    rows = service.list_table_rows(path)

    assert rows[0][0] == "C-"
    assert rows[1][0] == 5
    assert rows[1][1] == "file.txt"


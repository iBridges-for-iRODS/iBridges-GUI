import pytest
from unittest.mock import MagicMock, patch
from ibridgesgui.irods_browser_service import IrodsBrowserService


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def service(session, logger):
    return IrodsBrowserService(session, logger)


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


def test_list_collection(service):
    path = MagicMock()
    path.collection.subcollections = ["c1", "c2"]
    path.collection.data_objects = ["d1", "d2"]

    subs, objs = service.list_collection(path)
    assert subs == ["c1", "c2"]
    assert objs == ["d1", "d2"]


def test_stream_obj(service):
    stream = MagicMock()
    stream.read.return_value = b"hello world"

    path = MagicMock()
    path.open.return_value.__enter__.return_value = stream

    result = service.stream_obj(path)
    assert result == ["hello world"]


@patch("ibridgesgui.irods_browser_service.obj_replicas")
def test_replicas_for_no_dataobject(mock_repl, service):
    path = MagicMock()
    path.dataobject_exists.return_value = False

    assert service.replicas_for(path) == []
    mock_repl.assert_not_called()


@patch("ibridgesgui.irods_browser_service.obj_replicas")
def test_replicas_for_with_dataobject(mock_repl, service):
    path = MagicMock()
    path.dataobject_exists.return_value = True
    path.dataobject = MagicMock()

    mock_repl.return_value = ["r1", "r2"]

    assert service.replicas_for(path) == ["r1", "r2"]
    mock_repl.assert_called_once_with(path.dataobject)


def test_add_metadata(service):
    path = MagicMock()
    service.add_metadata(path, "k", "v", "u")
    path.meta.add.assert_called_once_with("k", "v", "u")


def test_update_metadata_same_key(service):
    path = MagicMock()
    path.meta.__getitem__.return_value = ("old", "units")

    service.update_metadata(path, "k", "k", "new", "u2")
    path.meta.__setitem__.assert_called_once_with("k", ("new", "u2"))


def test_update_metadata_new_key(service):
    item = MagicMock()
    path = MagicMock()
    path.meta.__getitem__.return_value = item

    service.update_metadata(path, "old", "new", "v", "u")
    assert item.key == "new"
    assert item.value == "v"
    assert item.units == "u"


def test_delete_metadata(service):
    path = MagicMock()
    service.delete_metadata(path, "k", "v", "u")
    path.meta.delete.assert_called_once_with("k", "v", "u")


@patch("ibridgesgui.irods_browser_service.get_irods_item")
@patch("ibridgesgui.irods_browser_service.Permissions")
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


@patch("ibridgesgui.irods_browser_service.get_irods_item")
@patch("ibridgesgui.irods_browser_service.Permissions")
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


@patch("ibridgesgui.irods_browser_service.obj_replicas")
def test_list_table_rows(mock_repl, service):
    # Mock collection
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

    assert rows[0][0] == "C-"  # collection row
    assert rows[1][0] == 5     # replica max
    assert rows[1][1] == "file.txt"


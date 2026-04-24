# tests/test_browser_model.py
import pytest
from unittest.mock import MagicMock
from ibridges import IrodsPath
from ibridgesgui.browsertab.browser_model import BrowserModel

class DummySession:
    irods_session = True

@pytest.fixture
def model():
    return BrowserModel(current_path=IrodsPath(DummySession(), "/tempZone/home/user"))


def test_set_path_resets_state(model):
    old_path = model.current_path
    new_path = IrodsPath(DummySession(), "/tempZone/home/user/new")

    model.set_path(new_path)

    assert model.current_path == new_path
    assert model.last_path == old_path
    assert model.current_selected_row == -1
    assert model.last_selected_row == -1
    assert model.updated_info_tabs == []
    assert model.metadata_cache == {}
    assert model.acl_cache == {}
    assert model.replica_cache == {}
    assert model.preview_cache == {}


def test_path_changed(model):
    assert model.path_changed() is True  # last_path is None initially
    model.last_path = model.current_path
    assert model.path_changed() is False


def test_on_row_clicked_updates_selection(model):
    model.on_row_clicked(3)
    assert model.current_selected_row == 3
    assert model.last_selected_row == -1
    assert model.updated_info_tabs == []

    model.on_row_clicked(5)
    assert model.last_selected_row == 3
    assert model.current_selected_row == 5


def test_needs_tab_update(model):
    model.last_path = model.current_path
    model.current_selected_row = 1
    model.last_selected_row = 1
    model.updated_info_tabs = ["metadata"]

    assert model.needs_tab_update("metadata") is False
    assert model.needs_tab_update("permissions") is True  # not updated yet

    model.last_selected_row = 0
    assert model.needs_tab_update("metadata") is True  # row changed


def test_caching(model):
    model.cache_metadata(1, {"a": 1})
    assert model.get_cached_metadata(1) == {"a": 1}

    model.cache_acls(2, ["acl"])
    assert model.get_cached_acls(2) == ["acl"]

    model.cache_replicas(3, ["rep"])
    assert model.get_cached_replicas(3) == ["rep"]

    model.cache_preview(4, "preview")
    assert model.get_cached_preview(4) == "preview"


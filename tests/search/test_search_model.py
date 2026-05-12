import pytest
from unittest.mock import MagicMock, patch

from ibridgesgui.searchtab.search_model import SearchModel


@pytest.fixture
def fake_session():
    return MagicMock()


@pytest.fixture
def model(fake_session):
    return SearchModel(fake_session)


# ---------------------------------------------------------
# validate(): collection does not exist
# ---------------------------------------------------------

def test_validate_collection_not_exists(model):
    with patch("ibridgesgui.searchtab.search_model.IrodsPath") as MockPath:
        path_obj = MagicMock()
        path_obj.collection_exists.return_value = False
        MockPath.return_value = path_obj

        msg, params = model.validate(
            search_path="/zone/home",
            path_pattern="*",
            checksum="",
            case_sensitive=False,
            item_type="data_object",
            meta_fields=[],
        )

        assert msg is not None
        assert "does not exist" in msg
        assert params is None


# ---------------------------------------------------------
# validate(): no criteria provided
# ---------------------------------------------------------

def test_validate_no_criteria(model):
    with patch("ibridgesgui.searchtab.search_model.IrodsPath") as MockPath:
        path_obj = MagicMock()
        path_obj.collection_exists.return_value = True
        MockPath.return_value = path_obj

        msg, params = model.validate(
            search_path="/zone/home",
            path_pattern="",
            checksum="",
            case_sensitive=False,
            item_type="data_object",
            meta_fields=[],
        )

        assert msg == "Please provide some search criteria."
        assert params is None


# ---------------------------------------------------------
# validate(): MetaSearch creation
# ---------------------------------------------------------

def test_validate_meta_search_creation(model):
    with patch("ibridgesgui.searchtab.search_model.IrodsPath") as MockPath, \
         patch("ibridgesgui.searchtab.search_model.MetaSearch") as MockMeta:

        path_obj = MagicMock()
        path_obj.collection_exists.return_value = True
        MockPath.return_value = path_obj

        meta_fields = [
            ("key1", "val1", "u1"),   # full triple
            ("", "", ""),             # ignored
            ("k2", "", ""),           # value/unit default to "%"
        ]

        msg, params = model.validate(
            search_path="/zone/home",
            path_pattern="*",
            checksum="",
            case_sensitive=True,
            item_type="collection",
            meta_fields=meta_fields,
        )

        assert msg is None
        assert params is not None

        # Two MetaSearch objects created
        assert MockMeta.call_count == 2

        MockMeta.assert_any_call("key1", "val1", "u1")
        MockMeta.assert_any_call("k2", "%", "%")


# ---------------------------------------------------------
# validate(): successful return structure
# ---------------------------------------------------------

def test_validate_success_params(model):
    with patch("ibridgesgui.searchtab.search_model.IrodsPath") as MockPath, \
         patch("ibridgesgui.searchtab.search_model.MetaSearch") as MockMeta:

        path_obj = MagicMock()
        path_obj.collection_exists.return_value = True
        MockPath.return_value = path_obj

        MockMeta.return_value = "META"

        msg, params = model.validate(
            search_path="/zone/home",
            path_pattern="abc",
            checksum="123",
            case_sensitive=True,
            item_type="data_object",
            meta_fields=[("k", "v", "u")],
        )

        assert msg is None
        assert params["search_path"] is path_obj
        assert params["path_pattern"] == "abc"
        assert params["checksum"] == "123"
        assert params["case_sensitive"] is True
        assert params["item_type"] == "data_object"
        assert params["meta_searches"] == ["META"]


# ---------------------------------------------------------
# set_results()
# ---------------------------------------------------------

def test_set_results_resets_batch(model):
    model.current_batch = 5
    model.set_results([1, 2, 3])

    assert model.results == [1, 2, 3]
    assert model.current_batch == 0


# ---------------------------------------------------------
# next_batch()
# ---------------------------------------------------------

def test_next_batch_basic(model):
    model.set_results(list(range(100)))

    batch1 = model.next_batch(batch_size=10)
    batch2 = model.next_batch(batch_size=10)

    assert batch1 == list(range(0, 10))
    assert batch2 == list(range(10, 20))


def test_next_batch_short_final(model):
    model.set_results([1, 2, 3, 4])

    batch1 = model.next_batch(batch_size=3)
    batch2 = model.next_batch(batch_size=3)

    assert batch1 == [1, 2, 3]
    assert batch2 == [4]


def test_next_batch_empty_results(model):
    model.set_results([])

    batch = model.next_batch(batch_size=10)
    assert batch == []


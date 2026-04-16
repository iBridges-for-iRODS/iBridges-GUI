import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from ibridgesgui.synctab.irods_sync_service import SyncService


@pytest.fixture
def service():
    return SyncService(session=MagicMock(), logger=MagicMock())


# -------------------------
# irods_root
# -------------------------

def test_irods_root_stops_at_first_non_existing_parent(service):
    # Create three levels: p0 -> p1 -> p2
    p0 = MagicMock()
    p1 = MagicMock()
    p2 = MagicMock()

    # absolute() returns p0 (the starting point)
    p0.absolute.return_value = p0

    # Parent chain
    p0.parent = p1
    p1.parent = p2
    p2.parent = p2  # doesn't matter, exists() will stop before this

    # exists() behavior
    p1.exists.return_value = True   # first parent exists
    p2.exists.return_value = False  # second parent does NOT exist → stop here

    # str() must not be "/"
    p0.__str__.return_value = "/zone/home/user"
    p1.__str__.return_value = "/zone/home"
    p2.__str__.return_value = "/zone"

    with patch("ibridgesgui.synctab.irods_sync_service.IrodsPath", return_value=p0):
        root = service.irods_root()

    # Should stop at p1, because p2.exists() is False
    assert root is p1


# -------------------------
# prepare_env_for_diff
# -------------------------

def test_prepare_env_for_diff_success(service):
    with patch("ibridgesgui.synctab.irods_sync_service.prep_session_for_copy", return_value="/tmp/env"):
        result = service.prepare_env_for_diff(error_label=MagicMock())
        assert isinstance(result, Path)
        assert str(result) == "/tmp/env"


def test_prepare_env_for_diff_failure(service):
    with patch("ibridgesgui.synctab.irods_sync_service.prep_session_for_copy", return_value=None):
        result = service.prepare_env_for_diff(error_label=MagicMock())
        assert result is None


# -------------------------
# prepare_env_for_sync
# -------------------------

def test_prepare_env_for_sync_missing_env_path(service):
    error_label = MagicMock()

    with patch("ibridgesgui.synctab.irods_sync_service.get_last_ienv_path", return_value=""):
        result = service.prepare_env_for_sync(error_label)

    assert result is None
    error_label.setText.assert_called_once()


def test_prepare_env_for_sync_file_not_found(service):
    error_label = MagicMock()

    with patch("ibridgesgui.synctab.irods_sync_service.get_last_ienv_path", return_value="/nope"):
        with patch("pathlib.Path.exists", return_value=False):
            result = service.prepare_env_for_sync(error_label)

    assert result is None
    error_label.setText.assert_called_once()


def test_prepare_env_for_sync_success(service):
    with patch("ibridgesgui.synctab.irods_sync_service.get_last_ienv_path", return_value="/tmp/env"):
        with patch("pathlib.Path.exists", return_value=True):
            result = service.prepare_env_for_sync(error_label=MagicMock())

    assert isinstance(result, Path)
    assert str(result) == "/tmp/env"


# -------------------------
# start_diff_thread
# -------------------------

def test_start_diff_thread_success(service):
    fake_thread = MagicMock()

    with patch("ibridgesgui.synctab.irods_sync_service.SyncThread", return_value=fake_thread):
        result = service.start_diff_thread(
            env_path="/tmp/env",
            source="src",
            target="dst",
            on_result=MagicMock(),
            on_finished=MagicMock(),
        )

    assert result is fake_thread
    fake_thread.start.assert_called_once()


def test_start_diff_thread_instantiation_error(service):
    with patch("ibridgesgui.synctab.irods_sync_service.SyncThread", side_effect=Exception("boom")):
        on_result = MagicMock()
        result = service.start_diff_thread(
            env_path="/tmp/env",
            source="src",
            target="dst",
            on_result=on_result,
            on_finished=MagicMock(),
        )

    assert result is None
    on_result.assert_called_once()
    assert "Could not instantiate" in on_result.call_args[0][0]["error"]


# -------------------------
# start_sync_thread
# -------------------------

def test_start_sync_thread_success(service):
    fake_thread = MagicMock()

    with patch("ibridgesgui.synctab.irods_sync_service.TransferDataThread", return_value=fake_thread):
        result = service.start_sync_thread(
            env_path="/tmp/env",
            diffs=MagicMock(),
            on_result=MagicMock(),
            on_progress=MagicMock(),
            on_finished=MagicMock(),
        )

    assert result is fake_thread
    fake_thread.start.assert_called_once()


def test_start_sync_thread_instantiation_error(service):
    with patch("ibridgesgui.synctab.irods_sync_service.TransferDataThread", side_effect=Exception("boom")):
        on_result = MagicMock()
        result = service.start_sync_thread(
            env_path="/tmp/env",
            diffs=MagicMock(),
            on_result=on_result,
            on_progress=MagicMock(),
            on_finished=MagicMock(),
        )

    assert result is None
    on_result.assert_called_once()
    assert "Could not instantiate" in on_result.call_args[0][0]["error"]


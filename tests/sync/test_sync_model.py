# tests/test_sync_model.py

from pathlib import Path
from ibridgesgui.synctab.sync_model import SyncModel


def test_model_initial_state():
    model = SyncModel()
    assert model.sync_source is None
    assert model.local_path is None
    assert model.irods_path is None
    assert model.refresh_irods_index is None
    assert model.diffs is None
    assert model.status_message == ""
    assert model.progress_percent == 0
    assert model.total_files == 0
    assert model.completed_files == 0
    assert model.failed_files == 0


def test_model_set_paths():
    model = SyncModel()
    lp = Path("/tmp/local")
    ip = "/zone/home/user"
    idx = object()

    model.set_paths(lp, ip, idx)

    assert model.local_path == lp
    assert model.irods_path == ip
    assert model.refresh_irods_index == idx


def test_model_clear():
    model = SyncModel()
    model.sync_source = "local"
    model.local_path = Path("/tmp/x")
    model.irods_path = "/irods/x"
    model.refresh_irods_index = 123
    model.diffs = ["dummy"]
    model.status_message = "msg"
    model.progress_percent = 50
    model.total_files = 10
    model.completed_files = 5
    model.failed_files = 1

    model.clear()

    assert model.sync_source is None
    assert model.local_path is None
    assert model.irods_path is None
    assert model.refresh_irods_index is None
    assert model.diffs is None
    assert model.status_message == ""
    assert model.progress_percent == 0
    assert model.total_files == 0
    assert model.completed_files == 0
    assert model.failed_files == 0

# tests/test_sync_controller.py

from unittest.mock import MagicMock, patch
from ibridgesgui.sync_controller import SyncController
from ibridgesgui.sync_model import SyncModel


def test_direction_local_to_irods(fake_view):
    controller = SyncController(fake_view, session=MagicMock(), app_name="test")
    controller._sync_diff = MagicMock()

    controller.local_to_irods()

    assert controller.model.sync_source == "local"
    controller._sync_diff.assert_called_once()


def test_direction_irods_to_local(fake_view):
    controller = SyncController(fake_view, session=MagicMock(), app_name="test")
    controller._sync_diff = MagicMock()

    controller.irods_to_local()

    assert controller.model.sync_source == "irods"
    controller._sync_diff.assert_called_once()

def test_sync_diff_end_nothing_to_sync(fake_view):
    controller = SyncController(fake_view, session=MagicMock(), app_name="test")

    fake_output = {
        "error": "",
        "result": MagicMock(upload=[], download=[])
    }

    controller._sync_diff_end(fake_output)

    fake_view.error_label.setText.assert_called_with(
        "Nothing to synchronise — everything is already up to date."
    )
    assert controller.model.sync_source is None
    assert controller.model.diffs is None

def test_sync_diff_end_with_diffs(fake_view):
    controller = SyncController(fake_view, session=MagicMock(), app_name="test")

    fake_src = MagicMock()
    fake_dst = MagicMock()
    fake_output = {
        "error": "",
        "result": MagicMock(upload=[(fake_src, fake_dst)], download=[])
    }

    controller._sync_diff_end(fake_output)

    fake_view.sync_button.show.assert_called_once()
    assert controller.model.diffs is not None

def test_sync_data_status_updates_progress(fake_view, qtbot):
    controller = SyncController(fake_view, session=MagicMock(), app_name="test")

    state = [100, 50, 1, 2, 0, ""]

    controller._sync_data_status(state)

    fake_view.progress_bar.setValue.assert_called_with(50)
    fake_view.error_label.setText.assert_called_with("1 of 2 files; failed: 0.")


def test_sync_data_end_success(fake_view):
    controller = SyncController(fake_view, session=MagicMock(), app_name="test")
    controller.model.refresh_irods_index = MagicMock()
    controller.irods_model = MagicMock()

    controller._sync_data_end({"error": ""})

    fake_view.error_label.setText.assert_called_with("Data synchronisation complete.")
    assert controller.model.sync_source is None


def test_sync_data_end_error(fake_view):
    controller = SyncController(fake_view, session=MagicMock(), app_name="test")

    controller._sync_data_end({"error": "boom"})

    fake_view.error_label.setText.assert_called_with("boom")
    assert controller.model.sync_source is None




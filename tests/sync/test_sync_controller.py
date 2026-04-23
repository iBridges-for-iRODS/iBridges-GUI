# tests/test_sync_controller.py

from unittest.mock import MagicMock, patch
from ibridgesgui.synctab.sync_controller import SyncController


def make_controller(fake_view):
    with patch.object(SyncController, "init_sync", return_value=None):
        controller = SyncController(fake_view, session=MagicMock(), app_name="test")

    # Inject fake models that init_sync() would normally create
    controller.local_fs_model = MagicMock()
    controller.irods_model = MagicMock()

    return controller


def test_direction_local_to_irods(fake_view):
    controller = make_controller(fake_view)
    controller._sync_diff = MagicMock()

    controller.local_to_irods()

    assert controller.model.sync_source == "local"
    controller._sync_diff.assert_called_once()


def test_direction_irods_to_local(fake_view):
    controller = make_controller(fake_view)
    controller._sync_diff = MagicMock()

    controller.irods_to_local()

    assert controller.model.sync_source == "irods"
    controller._sync_diff.assert_called_once()

# gather paths
def test_gather_paths_no_local_selection(fake_view):
    controller = make_controller(fake_view)
    fake_view.local_fs_tree.selectedIndexes.return_value = []

    assert controller._gather_paths() is None
    fake_view.error_label.setText.assert_called_with("Please select a directory.")


def test_gather_paths_local_is_file(fake_view):
    controller = make_controller(fake_view)
    idx = MagicMock()
    fake_view.local_fs_tree.selectedIndexes.return_value = [idx]
    controller.local_fs_model.filePath.return_value = "/tmp/file.txt"

    with patch("pathlib.Path.is_file", return_value=True):
        assert controller._gather_paths() is None
        fake_view.error_label.setText.assert_called_with(
            "Please select a directory, not a file."
        )


def test_gather_paths_no_irods_selection(fake_view):
    controller = make_controller(fake_view)
    fake_view.local_fs_tree.selectedIndexes.return_value = [MagicMock()]
    controller.local_fs_model.filePath.return_value = "/tmp"

    fake_view.irods_tree.selectedIndexes.return_value = []

    assert controller._gather_paths() is None
    fake_view.error_label.setText.assert_called_with("Please select a collection.")


def test_gather_paths_irods_is_dataobject(fake_view):
    controller = make_controller(fake_view)
    fake_view.local_fs_tree.selectedIndexes.return_value = [MagicMock()]
    controller.local_fs_model.filePath.return_value = "/tmp"

    idx = MagicMock()
    fake_view.irods_tree.selectedIndexes.return_value = [idx]

    fake_path = MagicMock()
    fake_path.dataobject_exists.return_value = True
    controller.irods_model.irods_path_from_tree_index.return_value = fake_path

    assert controller._gather_paths() is None
    fake_view.error_label.setText.assert_called_with(
        "Please select a collection, not a data object."
    )

# test sync threads
#happy tests
def test_sync_diff_local_source(fake_view):
    controller = make_controller(fake_view)

    local = MagicMock()
    irods = MagicMock()
    irods_index = MagicMock()
    controller._gather_paths = MagicMock(return_value=(local, irods, MagicMock(), irods_index))
    controller._start_sync_diff = MagicMock()
    controller.model.sync_source = "local"

    controller._sync_diff()

    assert controller.model.refresh_irods_index == irods_index
    controller._start_sync_diff.assert_called_once_with(local, irods)


def test_sync_diff_irods_source(fake_view):
    controller = make_controller(fake_view)

    local = MagicMock()
    irods = MagicMock()
    irods_index = MagicMock()
    controller._gather_paths = MagicMock(return_value=(local, irods, MagicMock(), irods_index))
    controller._start_sync_diff = MagicMock()
    controller.model.sync_source = "irods"

    controller._sync_diff()

    controller._start_sync_diff.assert_called_once_with(irods, local)

@patch("ibridgesgui.synctab.sync_controller.SyncThread")
@patch("ibridgesgui.synctab.sync_controller.prep_session_for_copy")
def test_start_sync_diff_starts_thread(mock_prep, mock_thread, fake_view):
    controller = make_controller(fake_view)
    mock_prep.return_value = "/tmp/ienv"

    controller._start_sync_diff("src", "dst")

    mock_prep.assert_called_once()
    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()
    fake_view.error_label.setText.assert_called_with("Calculating differences...")


#failure tests

def test_start_sync_diff_env_missing(fake_view):
    controller = make_controller(fake_view)

    with patch("ibridgesgui.synctab.sync_controller.prep_session_for_copy", return_value=None):
        controller._finish_sync_diff = MagicMock()
        controller._start_sync_diff("src", "dst")

        controller._finish_sync_diff.assert_called_once()

def test_finish_sync_diff_resets_ui(fake_view):
    controller = make_controller(fake_view)

    controller._finish_sync_diff()

    fake_view.local_to_irods_button.setEnabled.assert_called_with(True)
    fake_view.irods_to_local_button.setEnabled.assert_called_with(True)
    fake_view.create_coll_button.setEnabled.assert_called_with(True)
    fake_view.create_dir_button.setEnabled.assert_called_with(True)
    fake_view.assert_cursor_called()

def test_sync_diff_end_nothing_to_sync(fake_view):
    controller = make_controller(fake_view)

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


# test data transfer thread

def test_start_data_sync_env_missing(fake_view):
    controller = make_controller(fake_view)

    with patch("ibridgesgui.synctab.sync_controller.get_last_ienv_path", return_value="/nope"):
        with patch("pathlib.Path.exists", return_value=False):
            controller._finish_sync_data = MagicMock()
            controller._start_data_sync()

            fake_view.error_label.setText.assert_called_with(
                "Could not find iRODS environment file."
            )
            controller._finish_sync_data.assert_called_once()

@patch("ibridgesgui.synctab.sync_controller.TransferDataThread")
@patch("ibridgesgui.synctab.sync_controller.get_last_ienv_path")
def test_start_data_sync_starts_thread(mock_get_env, mock_thread, fake_view):
    controller = make_controller(fake_view)
    mock_get_env.return_value = "/tmp/ienv"

    with patch("pathlib.Path.exists", return_value=True):
        controller._start_data_sync()

    mock_get_env.assert_called_once()
    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()
    fake_view.error_label.setText.assert_called_with("Synchronising data...")


def test_sync_data_status_throttled(fake_view):
    controller = make_controller(fake_view)
    controller._last_update = 99999999  # very recent

    state = [100, 50, 1, 2, 0, ""]
    controller._sync_data_status(state)

    fake_view.progress_bar.setValue.assert_not_called()

def test_sync_data_end_nothing_to_sync(fake_view):
    controller = make_controller(fake_view)
    controller.model.diffs = MagicMock(upload=[], download=[])

    controller._sync_data_end({"error": ""})

    fake_view.error_label.setText.assert_called_with("Nothing to synchronise.")


def test_sync_diff_end_with_diffs(fake_view):
    controller = make_controller(fake_view)

    fake_src = MagicMock()
    fake_dst = MagicMock()
    fake_output = {
        "error": "",
        "result": MagicMock(upload=[(fake_src, fake_dst)], download=[])
    }

    controller._sync_diff_end(fake_output)

    fake_view.sync_button.show.assert_called_once()
    assert controller.model.diffs is not None

def test_sync_data_end_with_diffs_refreshes_index(fake_view):
    controller = make_controller(fake_view)
    controller.model.diffs = MagicMock(upload=[1], download=[])
    controller.model.refresh_irods_index = MagicMock()
    expected_callback = controller.model.refresh_irods_index  # capture before clear()
    controller.irods_model.refresh_subtree = MagicMock()

    controller._sync_data_end({"error": ""})

    controller.irods_model.refresh_subtree.assert_called_once_with(expected_callback)



def test_sync_diff_end_error(fake_view):
    controller = make_controller(fake_view)
    controller.model.clear = MagicMock()

    controller._sync_diff_end({"error": "boom", "result": None})

    fake_view.error_label.setText.assert_called_with("boom")
    controller.model.clear.assert_called_once()


def test_sync_data_status_updates_progress(fake_view, qtbot):
    controller = make_controller(fake_view)

    state = [100, 50, 1, 2, 0, ""]

    controller._sync_data_status(state)

    fake_view.progress_bar.setValue.assert_called_with(50)
    fake_view.error_label.setText.assert_called_with("1 of 2 files; failed: 0.")


def test_sync_data_end_success(fake_view):
    controller = make_controller(fake_view)
    controller.model.refresh_irods_index = MagicMock()
    controller.irods_model = MagicMock()

    controller._sync_data_end({"error": ""})

    fake_view.error_label.setText.assert_called_with("Data synchronisation complete.")
    assert controller.model.sync_source is None


def test_sync_data_end_error(fake_view):
    controller = make_controller(fake_view)

    controller._sync_data_end({"error": "boom"})

    fake_view.error_label.setText.assert_called_with("boom")
    assert controller.model.sync_source is None

def test_finish_sync_data_resets_ui(fake_view):
    controller = make_controller(fake_view)

    controller._finish_sync_data()

    fake_view.sync_button.hide.assert_called_once()
    fake_view.assert_cursor_called()

# create collection button

def test_create_collection_no_selection(fake_view):
    controller = make_controller(fake_view)
    fake_view.irods_tree.selectedIndexes.return_value = []

    controller.create_collection()

    fake_view.error_label.setText.assert_called_with(
        "Please select a parent collection."
    )


def test_create_collection_wrong_type(fake_view):
    controller = make_controller(fake_view)
    idx = MagicMock()
    fake_view.irods_tree.selectedIndexes.return_value = [idx]

    fake_path = MagicMock()
    fake_path.collection_exists.return_value = False
    controller.irods_model.irods_path_from_tree_index.return_value = fake_path

    controller.create_collection()

    fake_view.error_label.setText.assert_called_with(
        "Please select a collection, not a data object."
    )

# create dir button

def test_create_dir_no_selection(fake_view):
    controller = make_controller(fake_view)
    fake_view.local_fs_tree.selectedIndexes.return_value = []

    controller.create_dir()

    fake_view.error_label.setText.assert_called_with("Please select a parent directory.")


def test_create_dir_wrong_type(fake_view):
    controller = make_controller(fake_view)
    idx = MagicMock()
    fake_view.local_fs_tree.selectedIndexes.return_value = [idx]
    controller.local_fs_model.filePath.return_value = "/tmp/file.txt"

    with patch("pathlib.Path.is_dir", return_value=False):
        controller.create_dir()

    fake_view.error_label.setText.assert_called_with(
        "Please select a directory, not a file."
    )


# helper function to enable and disable buttons
def test_enable_buttons(fake_view):
    controller = make_controller(fake_view)
    fake_view.set_ui_busy(True)

    fake_view.local_to_irods_button.setEnabled.assert_called_with(False)


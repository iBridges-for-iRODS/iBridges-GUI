# tests/search/test_search_controller.py

from unittest.mock import MagicMock
import pytest
from PySide6.QtCore import QObject, Signal


class FakeSearchThread(QObject):
    result = Signal(object)
    finished = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.started = False

    def start(self):
        self.started = True


class FakeDownloadThread(QObject):
    result = Signal(object)
    finished = Signal()
    current_progress = Signal(tuple)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.started = False

    def start(self):
        self.started = True


# ---------------------------------------------------------
# Basic state and busy handling
# ---------------------------------------------------------

def test_initial_state(controller):
    assert controller.busy is False
    assert controller.model is not None


def test_set_busy_disables_and_enables_buttons(controller, fake_view_search):
    controller._set_busy(True)
    assert not fake_view_search.search_button.isEnabled()
    assert not fake_view_search.download_button.isEnabled()
    assert not fake_view_search.clear_button.isEnabled()
    assert not fake_view_search.load_more_button.isEnabled()

    controller._set_busy(False)
    assert fake_view_search.search_button.isEnabled()
    assert fake_view_search.download_button.isEnabled()
    assert fake_view_search.clear_button.isEnabled()
    assert fake_view_search.load_more_button.isEnabled()


# ---------------------------------------------------------
# Search: on_search
# ---------------------------------------------------------

def test_on_search_validation_error_resets_busy(controller, fake_view_search):
    controller.model.validate.return_value = ("Invalid input", None)

    try:
        controller.on_search()
    except Exception as e:
        print("EXCEPTION:", type(e, e))
    #assert controller.busy is False
    #fake_view_search.error_label.setText.assert_called_with("Invalid input")


def test_on_search_sets_busy_and_starts_thread(controller, fake_view_search, monkeypatch):
    # Provide required UI values
    fake_view_search.search_path_field.text.return_value = "/zone/home"
    fake_view_search.path_pattern_field.text.return_value = "*"
    fake_view_search.checksum_field.text.return_value = ""
    fake_view_search.case_sensitive_box.isChecked.return_value = False

    fake_view_search.radio_object.isChecked.return_value = True
    fake_view_search.radio_object.text.return_value = "Object"
    fake_view_search.radio_group.checkedButton.return_value = fake_view_search.radio_object

    # Validation succeeds
    controller.model.validate.return_value = (
        None,
        {
            "search_path": "/zone/home",
            "path_pattern": "*",
            "checksum": "",
            "case_sensitive": False,
            "item_type": "data_object",
            "meta_searches": [],
        },
    )

    # Patch env_path so controller does NOT return early
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search_controller.prep_session_for_copy",
        lambda session, label: "/tmp/fake_env",
    )

    # Patch SearchThread
    fake_thread = FakeSearchThread()
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search_controller.SearchThread",
        lambda **kwargs: fake_thread,
    )

    controller.on_search()

    assert controller.busy is True
    assert fake_thread.started is True


# ---------------------------------------------------------
# Search: _on_search_finished
# ---------------------------------------------------------

def test_on_search_finished_error(controller, fake_view_search, monkeypatch, qtbot):
    data = {"error": "Something went wrong"}
    controller._search_results_data = data

    controller._on_search_finished()

    fake_view_search.error_label.setText.assert_called_with("Something went wrong")


def test_on_search_finished_no_results(controller, fake_view_search, monkeypatch, qtbot):
    data = {"results": []}
    controller._search_results_data = data

    controller._on_search_finished()

    fake_view_search.error_label.setText.assert_called_with("No objects or collections found.")


def test_on_search_finished_success(controller, fake_view_search, monkeypatch, qtbot):
    data = {"results": ["/zone/home/file1", "/zone/home/file2"]}
    controller._search_results_data = data

    controller.model.next_batch.return_value = data["results"]
    controller._format_batch = MagicMock(return_value=[("row1",), ("row2",)])

    controller._on_search_finished()

    controller.model.set_results.assert_called_with(data["results"])
    fake_view_search.show_result_elements.assert_called_once()
    fake_view_search.display_results.assert_called_once()
    fake_view_search.error_label.setText.assert_any_call("Search complete.")


# ---------------------------------------------------------
# Download: on_download
# ---------------------------------------------------------

def test_on_download_no_selection_resets_busy(controller, fake_view_search, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search_controller.QTimer.singleShot",
        lambda delay, func: func()
    )

    fake_view_search.get_selected_paths.return_value = []

    controller.on_download()

    assert controller.busy is False
    fake_view_search.error_label.setText.assert_called_with("No data selected.")
    fake_view_search.set_normal_cursor.assert_called_once()


def test_on_download_cancel_folder(controller, fake_view_search, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search_controller.QTimer.singleShot",
        lambda delay, func: func()
    )

    fake_view_search.get_selected_paths.return_value = ["/zone/home/file1"]
    fake_view_search.ask_download_destination.return_value = (None, True)

    controller.on_download()

    assert controller.busy is False
    fake_view_search.set_normal_cursor.assert_called_once()


def test_on_download_overwrite_false(controller, fake_view_search, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search_controller.QTimer.singleShot",
        lambda delay, func: func()
    )

    fake_view_search.get_selected_paths.return_value = ["/zone/home/file1"]
    fake_view_search.ask_download_destination.return_value = ("/tmp", False)

    controller.on_download()

    assert controller.busy is False
    fake_view_search.set_normal_cursor.assert_called_once()


def test_on_download_env_path_none(controller, fake_view_search, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search_controller.QTimer.singleShot",
        lambda delay, func: func()
    )

    fake_view_search.get_selected_paths.return_value = ["/zone/home/file1"]
    fake_view_search.ask_download_destination.return_value = ("/tmp", True)

    import ibridgesgui.searchtab.search_controller as search_controller_module  # adjust
    monkeypatch.setattr(
        search_controller_module,
        "prep_session_for_copy",
        lambda session, label: None,
    )

    controller.on_download()

    assert controller.busy is False
    fake_view_search.error_label.setText.assert_called_with(
        "No download. Cannot create new irods session."
    )


def test_on_download_starts_thread(controller, fake_view_search, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search_controller.QTimer.singleShot",
        lambda delay, func: func()
    )

    fake_view_search.get_selected_paths.return_value = ["/zone/home/file1"]
    fake_view_search.ask_download_destination.return_value = ("/tmp", True)

    import ibridgesgui.searchtab.search_controller as search_controller_module  # adjust

    monkeypatch.setattr(
        search_controller_module,
        "prep_session_for_copy",
        lambda session, label: "/tmp/irods_env",
    )
    monkeypatch.setattr(
        search_controller_module,
        "download",
        lambda p, folder, overwrite, dry_run: f"op({p},{folder})",
    )
    monkeypatch.setattr(
        search_controller_module,
        "combine_operations",
        lambda ops: ops,
    )

    fake_thread = FakeDownloadThread()
    monkeypatch.setattr(
        search_controller_module,
        "TransferDataThread",
        lambda **kwargs: fake_thread,
    )

    controller.on_download()

    assert controller.busy is True
    assert fake_thread.started is True
    fake_view_search.error_label.setText.assert_called_with("Downloading ...")


# ---------------------------------------------------------
# Download: progress and finished
# ---------------------------------------------------------

def test_on_download_progress_updates_label(controller, fake_view_search):
    controller._on_download_progress((None, None, 3, 10, 1, None))
    fake_view_search.error_label.setText.assert_called_with("3 of 10 files; failed: 1.")


def test_on_download_finished_error(controller, fake_view_search, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search_controller.QTimer.singleShot",
        lambda delay, func: func()
    )

    controller._download_result = {"error": "Download failed"}

    controller._on_download_finished_cleanup()

    fake_view_search.error_label.setText.assert_called_with("Download failed")


def test_on_download_finished_success(controller, fake_view_search, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.searchtab.search_controller.QTimer.singleShot",
        lambda delay, func: func()
    )

    controller._download_result = {"ok": True}

    controller._on_download_finished_cleanup()

    fake_view_search.error_label.setText.assert_called_with("Download complete.")


# ---------------------------------------------------------
# Table batching and formatting
# ---------------------------------------------------------

def test_on_load_more_appends_rows(controller, fake_view_search):
    controller.model.next_batch.return_value = ["/zone/home/file1"]
    controller._format_batch = MagicMock(return_value=[("row1",)])

    controller.on_load_more()

    fake_view_search.append_results.assert_called_once()


def test_update_load_more_visibility_shows_and_hides(controller, fake_view_search):
    controller.model.results = list(range(60))
    controller.model.current_batch = 1  # already loaded one batch

    controller._update_load_more_visibility(batch_size=25)
    assert fake_view_search.load_more_button.show.called

    controller.model.current_batch = 3  # all loaded
    fake_view_search.load_more_button.show.reset_mock()
    fake_view_search.load_more_button.hide.reset_mock()

    controller._update_load_more_visibility(batch_size=25)
    assert fake_view_search.load_more_button.hide.called


def test_format_batch_uses_irods_path(controller, monkeypatch):
    class FakeIrodsPath:
        def __init__(self, session, path):
            self._path = path
            self.size = 123
            self.dataobject = MagicMock()
            self.collection = MagicMock()
            self.dataobject.create_time.strftime.return_value = "01-01-2020"
            self.dataobject.modify_time.strftime.return_value = "02-01-2020"
            self.collection.create_time.strftime.return_value = "03-01-2020"
            self.collection.modify_time.strftime.return_value = "04-01-2020"

        def __str__(self):
            return self._path

        def dataobject_exists(self):
            return "file" in self._path

        def collection_exists(self):
            return "coll" in self._path

        @property
        def parent(self):
            return "/parent"

    import ibridgesgui.searchtab.search_controller as search_controller_module  # adjust
    monkeypatch.setattr(search_controller_module, "IrodsPath", FakeIrodsPath)

    batch = ["/zone/home/file1", "/zone/home/coll1"]
    rows = controller._format_batch(batch)

    assert rows[0][0] == "-d"
    assert rows[1][0] == "-C"


# ---------------------------------------------------------
# Misc UI actions
# ---------------------------------------------------------

def test_on_clear(controller, fake_view_search):
    controller.on_clear()
    fake_view_search.search_table.setRowCount.assert_called_with(0)
    fake_view_search.error_label.clear.assert_called_once()


def test_on_select_all(controller, fake_view_search):
    fake_view_search.search_table.rowCount.return_value = 3

    #fake_view_search.select_all_box.setChecked(True)
    fake_view_search.select_all_box.isChecked.return_value = True
    controller.on_select_all()
    assert fake_view_search.search_table.selectRow.call_count == 3

    fake_view_search.search_table.selectRow.reset_mock()
    fake_view_search.search_table.clearSelection.reset_mock()

    fake_view_search.select_all_box.isChecked.return_value = False
    controller.on_select_all()
    fake_view_search.search_table.clearSelection.assert_called_once()


def test_on_send_to_browser_collection(controller, fake_view_search, fake_browsercontroller, monkeypatch):
    fake_view_search.search_table.currentIndex.return_value.row.return_value = 0
    fake_item = MagicMock()
    fake_item.text.return_value = "/zone/home/coll1"
    fake_view_search.search_table.item.return_value = fake_item

    class FakeIrodsPath:
        def __init__(self, session, path):
            self._path = path

        def collection_exists(self):
            return True

        @property
        def parent(self):
            return "/parent"

        def __str__(self):
            return self._path

    import ibridgesgui.searchtab.search_controller as search_controller_module  # adjust
    monkeypatch.setattr(search_controller_module, "IrodsPath", FakeIrodsPath)

    controller.on_send_to_browser()

    fake_browsercontroller._set_path.assert_called_once()


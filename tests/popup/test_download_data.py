import pytest
from pathlib import Path
from ibridgesgui.popup_widgets.download_data import DownloadData


@pytest.fixture
def dialog(qtbot, monkeypatch, fake_irods_path, patch_env_path, dummy_ops):
    # Patch download() to return dummy ops
    #monkeypatch.setattr(
    #    "ibridgesgui.popup_widgets.download_data.download",
    #    lambda *args, **kwargs: dummy_ops,
    #)

    d = DownloadData(logger=None, session=None, irods_path=fake_irods_path)
    qtbot.addWidget(d)
    d.show()
    return d


def test_irods_tree(fake_irods_path):
    d = DownloadData(logger=None, session=None, irods_path=fake_irods_path)
    tree = d._irods_tree()
    assert "sub1" in tree
    assert "file1" in tree

def test_select_folder(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "dest"
    folder.mkdir()

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getExistingDirectory",
        lambda *a, **k: str(folder)
    )

    dialog._select_folder()
    assert dialog.destination_label.text() == str(folder)

def test_collect_download_params_invalid(dialog):
    dialog.destination_label.setText("/does/not/exist")
    dialog._collect_download_params()
    assert dialog.error_label.text() == "Select a valid download folder."

def test_collect_download_params_valid(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "dest"
    folder.mkdir()

    dialog.destination_label.setText(str(folder))

    called = {}
    monkeypatch.setattr(dialog, "_start_download", lambda p: called.setdefault("path", p))

    dialog._collect_download_params()
    assert called["path"] == folder

class FakeOpsEmpty:
    download = []
    meta_download = []

def test_start_download_no_ops(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "dest"
    folder.mkdir()

    # Fake ops: no download, no metadata
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.download",
        lambda *a, **k: FakeOpsEmpty()
    )

    # Fake session prep so it doesn't crash
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.prep_session_for_copy",
        lambda *a, **k: tmp_path
    )

    dialog._start_download(folder)

    assert dialog.error_label.text() == "Data already present and up to date."

class FakeOps:
    def __init__(self):
        self.download = ["file"]
        self.meta_download = []
        self.total_size = 1
        self.meta_size = 0


class DummySignal:
    def connect(self, *a, **k):
        pass

    def emit(self, *a, **k):
        pass


class FakeThread:
    def __init__(self, *a, **k):
        self.result = DummySignal()
        self.finished = DummySignal()
        self.current_progress = DummySignal()
        self._running = False

    def start(self):
        self._running = True
        self.finished.emit()

    def isRunning(self):
        return self._running

    def quit(self):
        self._running = False

    def wait(self):
        pass


def test_start_download_thread(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "dest"
    folder.mkdir()

    # Set destination folder in UI
    dialog.destination_label.setText(str(folder))

    # Ensure overwrite checkbox is in a valid state
    dialog.overwrite.setChecked(True)

    # Fake ops: download + metadata present
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.download",
        lambda *a, **k: FakeOps()
    )

    # Fake session prep so it doesn't crash
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.prep_session_for_copy",
        lambda *a, **k: tmp_path
    )

    # Fake thread class
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.TransferDataThread",
        FakeThread
    )

    dialog._start_download(folder)

    assert dialog.active_transfer is True

def test_download_status(dialog):
    dialog._download_status((100, 50, 3, 10, 1, "meta ok"))
    assert dialog.progress_bar.value() == 50
    assert "3 of 10 files; failed: 1. meta ok" in dialog.error_label.text()


def test_download_finished_success(dialog):
    dialog._download_finished({"error": ""})
    assert dialog.error_label.text() == "Download finished."

def test_download_finished_error(dialog):
    dialog._download_finished({"error": "boom"})
    assert dialog.error_label.text() == "Errors occurred during download. Consult the logs."


def test_start_download_sets_active_transfer(dialog, monkeypatch, tmp_path):
    dialog.destination_label.setText(str(tmp_path))

    # Mock prep_session_for_copy so it doesn't crash
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.prep_session_for_copy",
        lambda *a, **k: tmp_path
    )

    # Mock download() to return ops
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.download",
        lambda *a, **k: FakeOps()
    )

    # Mock thread
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.TransferDataThread",
        FakeThread
    )

    dialog.overwrite.setChecked(True)

    dialog._collect_download_params()

    assert dialog.active_transfer is True


def test_finish_download_resets_state(dialog):
    dialog.active_transfer = True
    dialog._download_finished({"error": ""})
    assert dialog.active_transfer is False  # now cleared


def test_enable_buttons(dialog):
    dialog._enable_buttons(False)
    assert not dialog.download_button.isEnabled()
    assert not dialog.folder_button.isEnabled()
    assert not dialog.overwrite.isEnabled()
    assert not dialog.metadata.isEnabled()


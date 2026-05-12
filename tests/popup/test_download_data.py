import pytest
from pathlib import Path
from ibridgesgui.popup_widgets.download_data import DownloadData


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def dialog(qtbot, fake_irods_path, patch_env_path, dummy_ops):
    """Create and show the DownloadData dialog."""
    d = DownloadData(logger=None, session=None, irods_path=fake_irods_path)
    qtbot.addWidget(d)
    d.show()
    return d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def set_dest(dialog, path):
    dialog.destination_label.setText(str(path))

def err(dialog):
    return dialog.error_label.text()


# ---------------------------------------------------------------------------
# IRODS tree
# ---------------------------------------------------------------------------

def test_irods_tree(fake_irods_path):
    d = DownloadData(logger=None, session=None, irods_path=fake_irods_path)
    tree = d._irods_tree()
    assert "sub1" in tree
    assert "file1" in tree


# ---------------------------------------------------------------------------
# Folder selection
# ---------------------------------------------------------------------------

def test_select_folder(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "dest"
    folder.mkdir()

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getExistingDirectory",
        lambda *a, **k: str(folder),
    )

    dialog._select_folder()
    assert dialog.destination_label.text() == str(folder)


# ---------------------------------------------------------------------------
# Collecting download parameters
# ---------------------------------------------------------------------------

def test_collect_download_params_invalid(dialog):
    set_dest(dialog, "/does/not/exist")
    dialog._collect_download_params()
    assert err(dialog) == "Select a valid download folder."


def test_collect_download_params_valid(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "dest"
    folder.mkdir()

    set_dest(dialog, folder)

    called = {}
    monkeypatch.setattr(dialog, "_start_download", lambda p: called.setdefault("path", p))

    dialog._collect_download_params()
    assert called["path"] == folder


# ---------------------------------------------------------------------------
# Starting download
# ---------------------------------------------------------------------------

class FakeOpsEmpty:
    download = []
    meta_download = []


def test_start_download_no_ops(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "dest"
    folder.mkdir()

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.download",
        lambda *a, **k: FakeOpsEmpty(),
    )
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.prep_session_for_copy",
        lambda *a, **k: tmp_path,
    )

    dialog._start_download(folder)
    assert err(dialog) == "Data already present and up to date."


class FakeOps:
    def __init__(self):
        self.download = ["file"]
        self.meta_download = []
        self.total_size = 1
        self.meta_size = 0


class DummySignal:
    def connect(self, *a, **k): pass
    def emit(self, *a, **k): pass


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

    def wait(self): pass


def test_start_download_thread(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "dest"
    folder.mkdir()

    set_dest(dialog, folder)
    dialog.overwrite.setChecked(True)

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.download",
        lambda *a, **k: FakeOps(),
    )
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.prep_session_for_copy",
        lambda *a, **k: tmp_path,
    )
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.TransferDataThread",
        FakeThread,
    )

    dialog._start_download(folder)
    assert dialog.active_transfer is True


# ---------------------------------------------------------------------------
# Download progress + finish
# ---------------------------------------------------------------------------

def test_download_status(dialog):
    dialog._download_status((100, 50, 3, 10, 1, "meta ok"))
    assert dialog.progress_bar.value() == 50
    assert "3 of 10 files; failed: 1. meta ok" in err(dialog)


def test_download_finished_success(dialog):
    dialog._download_finished({"error": ""})
    assert err(dialog) == "Download finished."


def test_download_finished_error(dialog):
    dialog._download_finished({"error": "boom"})
    assert err(dialog) == "Errors occurred during download. Consult the logs."


def test_start_download_sets_active_transfer(dialog, monkeypatch, tmp_path):
    set_dest(dialog, tmp_path)
    dialog.overwrite.setChecked(True)

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.prep_session_for_copy",
        lambda *a, **k: tmp_path,
    )
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.download",
        lambda *a, **k: FakeOps(),
    )
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.TransferDataThread",
        FakeThread,
    )

    dialog._collect_download_params()
    assert dialog.active_transfer is True


def test_finish_download_resets_state(dialog):
    dialog.active_transfer = True
    dialog._download_finished({"error": ""})
    assert dialog.active_transfer is False


# ---------------------------------------------------------------------------
# Button enabling
# ---------------------------------------------------------------------------

def test_enable_buttons(dialog):
    dialog._enable_buttons(False)
    assert not dialog.download_button.isEnabled()
    assert not dialog.folder_button.isEnabled()
    assert not dialog.overwrite.isEnabled()
    assert not dialog.metadata.isEnabled()


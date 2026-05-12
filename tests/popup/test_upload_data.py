import pytest
from pathlib import Path
from ibridgesgui.popup_widgets.upload_data import UploadData


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_prep(monkeypatch, tmp_path):
    """Ensure prep_session_for_copy always succeeds."""
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.prep_session_for_copy",
        lambda *a, **k: tmp_path,
    )


@pytest.fixture
def dialog(qtbot, monkeypatch, fake_irods_path, patch_env_path, dummy_ops):
    """Create and show the UploadData dialog with patched upload ops."""
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.upload",
        lambda *a, **k: dummy_ops,
    )
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.combine_operations",
        lambda ops: dummy_ops,
    )

    d = UploadData(logger=None, session=None, irods_path=fake_irods_path)
    qtbot.addWidget(d)
    d.show()
    return d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def err(dialog):
    return dialog.error_label.text()

def row(dialog, r, c):
    return dialog.table.item(r, c).text()

def metadata_button(dialog, row=0):
    return dialog.table.cellWidget(row, 2).layout().itemAt(0).widget()


# ---------------------------------------------------------------------------
# Row management
# ---------------------------------------------------------------------------

def test_add_row(dialog):
    assert dialog.table.rowCount() == 0

    dialog.add_row("/tmp/file.txt", "meta.json")

    assert dialog.table.rowCount() == 1
    assert row(dialog, 0, 0) == "/tmp/file.txt"
    assert row(dialog, 0, 1) == "meta.json"
    assert dialog.table.cellWidget(0, 2) is not None


def test_delete_selected_rows(dialog):
    dialog.add_row("/tmp/a", "")
    dialog.add_row("/tmp/b", "")

    dialog.table.selectRow(0)
    dialog._delete_selected_rows()

    assert dialog.table.rowCount() == 1
    assert row(dialog, 0, 0) == "/tmp/b"


# ---------------------------------------------------------------------------
# Metadata toggle button
# ---------------------------------------------------------------------------

def test_toggle_metadata_button(dialog, monkeypatch, tmp_path):
    dialog.add_row("/tmp/a", "")

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.validate_metadata",
        lambda p: True,
    )

    btn = metadata_button(dialog)

    # First click → upload metadata
    meta_file = tmp_path / "meta.json"
    meta_file.write_text("{}")

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        lambda *a, **k: (str(meta_file), ""),
    )

    btn.click()
    assert btn.state == "delete"
    assert btn.text() == "❌"

    # Second click → clear metadata
    btn.click()
    assert btn.state == "upload"
    assert row(dialog, 0, 1) == ""


# ---------------------------------------------------------------------------
# File & folder selection
# ---------------------------------------------------------------------------

def test_select_files(dialog, monkeypatch, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("x")
    f2.write_text("y")

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getOpenFileNames",
        lambda *a, **k: ([str(f1), str(f2)], ""),
    )

    dialog._select_files()

    assert dialog.table.rowCount() == 2
    assert row(dialog, 0, 0) == str(f1)
    assert row(dialog, 1, 0) == str(f2)


def test_select_folder(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getExistingDirectory",
        lambda *a, **k: str(folder),
    )

    dialog._select_folder()

    assert dialog.table.rowCount() == 1
    assert row(dialog, 0, 0) == str(folder)


# ---------------------------------------------------------------------------
# Collect upload params
# ---------------------------------------------------------------------------

def test_collect_upload_params_empty(dialog):
    dialog._collect_upload_params()
    assert err(dialog) == "Please select a file or folder to upload."


def test_collect_upload_params_valid(dialog, monkeypatch):
    dialog.add_row("/tmp/a", "/tmp/meta.json")

    called = {}
    monkeypatch.setattr(dialog, "_start_upload", lambda data: called.setdefault("ok", data))

    dialog._collect_upload_params()

    assert "ok" in called
    assert called["ok"][0][0] == Path("/tmp/a")
    assert called["ok"][0][1] == Path("/tmp/meta.json")


# ---------------------------------------------------------------------------
# Upload start
# ---------------------------------------------------------------------------

def test_start_upload_data_exists(dialog, monkeypatch, tmp_path):
    from ibridgesgui.popup_widgets.upload_data import DataObjectExistsError

    dialog.overwrite.setChecked(False)

    def fake_upload(*a, **k):
        raise DataObjectExistsError()

    monkeypatch.setattr("ibridgesgui.popup_widgets.upload_data.upload", fake_upload)

    dialog._start_upload([(Path("/tmp/a"), None)])

    assert err(dialog) == "Data already exists. Check 'overwrite' to overwrite."


def test_start_upload_generic_error(dialog, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.upload",
        lambda *a, **k: (_ for _ in ()).throw(Exception("boom")),
    )

    dialog._start_upload([(Path("/tmp/a"), None)])

    assert "Could not start upload: boom" in err(dialog)


class FakeOps:
    upload = []
    meta_upload = []


def test_start_upload_no_ops(dialog, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.combine_operations",
        lambda ops: FakeOps(),
    )

    dialog._start_upload([(Path("/tmp/a"), None)])

    assert err(dialog) == "Data already present and up to date."


# ---------------------------------------------------------------------------
# Upload progress + finish
# ---------------------------------------------------------------------------

def test_upload_status(dialog):
    dialog._upload_status((100, 50, 3, 10, 1, "metadata ok"))
    assert dialog.progress_bar.value() == 50
    assert "3 of 10 files; failed: 1. metadata ok" in err(dialog)


def test_upload_finished_success(dialog):
    dialog._upload_finished({"error": ""})
    assert err(dialog) == "Upload finished."


def test_upload_finished_error(dialog):
    dialog._upload_finished({"error": "x"})
    assert err(dialog) == "Errors occurred during upload. Consult the logs."


# ---------------------------------------------------------------------------
# UI behavior
# ---------------------------------------------------------------------------

def test_hide_button_calls_close(dialog):
    dialog.active_transfer = True
    dialog.hide_button.click()
    assert not dialog.isVisible()


def test_start_upload_sets_active_transfer(dialog, monkeypatch, tmp_path):
    dialog.add_row("/tmp/file.txt", "")

    monkeypatch.setattr(dialog, "session", object())
    monkeypatch.setattr(dialog, "_enable_buttons", lambda *a, **k: None)
    monkeypatch.setattr(dialog, "transfer_thread", None)
    monkeypatch.setattr(dialog, "set_wait_cursor", lambda *a, **k: None)
    monkeypatch.setattr(dialog, "set_arrow_cursor", lambda *a, **k: None)

    monkeypatch.setattr(
        dialog,
        "_start_upload",
        lambda data: setattr(dialog, "active_transfer", True),
    )

    dialog._collect_upload_params()
    assert dialog.active_transfer is True


def test_finish_upload_resets_state(dialog):
    dialog.active_transfer = True
    dialog.tranfer_thread = object()
    dialog._finish_upload()
    assert dialog.active_transfer is False
    assert dialog.transfer_thread is None


def test_enable_buttons(dialog):
    dialog._enable_buttons(False)
    assert not dialog.upload_button.isEnabled()
    assert not dialog.folder_button.isEnabled()
    assert not dialog.file_button.isEnabled()
    assert not dialog.hide_button.isEnabled()
    assert not dialog.overwrite.isEnabled()


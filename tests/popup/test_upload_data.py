import pytest
from pathlib import Path
from ibridgesgui.popup_widgets.upload_data import UploadData


@pytest.fixture
def dialog(qtbot, monkeypatch, fake_irods_path, patch_env_path, dummy_ops):
    # Patch upload() to return dummy ops
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.upload",
        lambda *args, **kwargs: dummy_ops,
    )

    # Patch combine_operations() to return dummy ops
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.combine_operations",
        lambda ops: dummy_ops,
    )

    d = UploadData(logger=None, session=None, irods_path=fake_irods_path)
    qtbot.addWidget(d)
    d.show()
    return d


def test_add_row(dialog):
    assert dialog.table.rowCount() == 0

    dialog.add_row("/tmp/file.txt", "meta.json")

    assert dialog.table.rowCount() == 1
    assert dialog.table.item(0, 0).text() == "/tmp/file.txt"
    assert dialog.table.item(0, 1).text() == "meta.json"

    # metadata button exists
    container = dialog.table.cellWidget(0, 2)
    assert container is not None


def test_delete_selected_rows(dialog, qtbot):
    dialog.add_row("/tmp/a", "")
    dialog.add_row("/tmp/b", "")

    dialog.table.selectRow(0)
    dialog._delete_selected_rows()

    assert dialog.table.rowCount() == 1
    assert dialog.table.item(0, 0).text() == "/tmp/b"


def test_toggle_metadata_button(dialog, monkeypatch, tmp_path):
    dialog.add_row("/tmp/a", "")

    # Fake metadata validation
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.validate_metadata",
        lambda p: True
    )

    btn = dialog.table.cellWidget(0, 2).layout().itemAt(0).widget()

    # First click → upload metadata
    meta_file = tmp_path / "meta.json"
    meta_file.write_text("{}")

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        lambda *a, **k: (str(meta_file), "")
    )

    btn.click()
    assert btn.state == "delete"
    assert btn.text() == "❌"

    # Second click → clear metadata
    btn.click()
    assert btn.state == "upload"
    assert dialog.table.item(0, 1).text() == ""

def test_select_files(dialog, monkeypatch, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("x")
    f2.write_text("y")

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getOpenFileNames",
        lambda *a, **k: ([str(f1), str(f2)], "")
    )

    dialog._select_files()

    assert dialog.table.rowCount() == 2
    assert dialog.table.item(0, 0).text() == str(f1)
    assert dialog.table.item(1, 0).text() == str(f2)

def test_select_folder(dialog, monkeypatch, tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getExistingDirectory",
        lambda *a, **k: str(folder)
    )

    dialog._select_folder()

    assert dialog.table.rowCount() == 1
    assert dialog.table.item(0, 0).text() == str(folder)

def test_collect_upload_params_empty(dialog):
    dialog._collect_upload_params()
    assert dialog.error_label.text() == "Please select a file or folder to upload."


def test_collect_upload_params_valid(dialog, monkeypatch):
    dialog.add_row("/tmp/a", "/tmp/meta.json")

    called = {}

    monkeypatch.setattr(dialog, "_start_upload", lambda data: called.setdefault("ok", data))

    dialog._collect_upload_params()

    assert "ok" in called
    assert called["ok"][0][0] == Path("/tmp/a")
    assert called["ok"][0][1] == Path("/tmp/meta.json")


def test_start_upload_data_exists(dialog, monkeypatch):
    from ibridgesgui.popup_widgets.upload_data import DataObjectExistsError

    dialog.overwrite.setChecked(False)

    def fake_upload(*a, **k):
        raise DataObjectExistsError()

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.upload",
        fake_upload
    )

    dialog._start_upload([(Path("/tmp/a"), None)])

    assert dialog.error_label.text() == "Data already exists. Check 'overwrite' to overwrite."

def test_start_upload_generic_error(dialog, monkeypatch):
    def fake_upload(*a, **k):
        raise Exception("boom")

    monkeypatch.setattr("ibridgesgui.popup_widgets.upload_data.upload", fake_upload)

    dialog._start_upload([(Path("/tmp/a"), None)])

    assert "Could not start upload: boom" in dialog.error_label.text()


class FakeOps:
    upload = []
    meta_upload = []

def test_start_upload_no_ops(dialog, monkeypatch):
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.upload_data.combine_operations",
        lambda ops: FakeOps()
    )

    dialog._start_upload([(Path("/tmp/a"), None)])

    assert dialog.error_label.text() == "Data already present and up to date."



def test_upload_status(dialog):
    dialog._upload_status((100, 50, 3, 10, 1, "metadata ok"))
    assert dialog.progress_bar.value() == 50
    assert "3 of 10 files; failed: 1. metadata ok" in dialog.error_label.text()

def test_upload_finished_success(dialog):
    dialog._upload_finished({"error": ""})
    assert dialog.error_label.text() == "Upload finished."

def test_upload_finished_error(dialog):
    dialog._upload_finished({"error": "x"})
    assert dialog.error_label.text() == "Errors occurred during upload. Consult the logs."


def test_hide_button_calls_close(dialog):
    dialog.active_transfer = True
    dialog.hide_button.click()
    assert dialog.isVisible()


def test_start_upload_sets_active_transfer(dialog):
    dialog.add_row("/tmp/file.txt", "")
    dialog._collect_upload_params()
    assert dialog.active_transfer is True


def test_finish_upload_resets_state(dialog):
    dialog.active_transfer = True
    dialog._finish_upload()
    assert dialog.active_transfer is False
    assert dialog.upload_thread is None


def test_enable_buttons(dialog):
    dialog._enable_buttons(False)
    assert not dialog.upload_button.isEnabled()
    assert not dialog.folder_button.isEnabled()
    assert not dialog.file_button.isEnabled()
    assert not dialog.hide_button.isEnabled()
    assert not dialog.overwrite.isEnabled()


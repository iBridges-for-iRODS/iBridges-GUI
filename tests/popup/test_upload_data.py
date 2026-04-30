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
    dialog.add_row("/tmp/file.txt", "")
    assert dialog.table.rowCount() == 1


def test_delete_row(dialog):
    dialog.add_row("/tmp/file.txt", "")
    dialog.table.selectRow(0)
    dialog._delete_selected_rows()
    assert dialog.table.rowCount() == 0


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


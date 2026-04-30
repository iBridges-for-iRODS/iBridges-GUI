import pytest
from pathlib import Path
from ibridgesgui.popup_widgets.download_data import DownloadData


@pytest.fixture
def dialog(qtbot, monkeypatch, fake_irods_path, patch_env_path, dummy_ops):
    # Patch download() to return dummy ops
    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.download_data.download",
        lambda *args, **kwargs: dummy_ops,
    )

    d = DownloadData(logger=None, session=None, irods_path=fake_irods_path)
    qtbot.addWidget(d)
    d.show()
    return d


def test_hide_button_calls_close(dialog):
    dialog.active_transfer = True
    dialog.hide_button.click()
    assert dialog.isVisible()


def test_start_download_sets_active_transfer(dialog):
    dialog.destination_label.setText(str(Path.cwd()))
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


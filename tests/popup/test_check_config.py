from pathlib import Path
import pytest
from PySide6.QtWidgets import QMessageBox
from ibridgesgui.popup_widgets.check_config import CheckConfig


@pytest.fixture
def dialog(qtbot, patch_config, fake_logger):
    d = CheckConfig(logger=fake_logger, env_path=patch_config["dir"])
    qtbot.addWidget(d)
    d.show()
    return d


def test_load_env_file_valid(dialog, patch_config):
    env_file = patch_config["file"]

    dialog._load_env_file(env_file)

    text = dialog.env_field.toPlainText()
    assert "localhost" in text
    assert "tempZone" in text
    assert dialog.error_label.text() == ""

def test_load_env_file_invalid(dialog, tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json", encoding="utf-8")

    dialog._load_env_file(bad_file)

    # env_field should remain empty
    assert dialog.env_field.toPlainText() == ""

    # error_label should contain the JSON error message
    assert dialog.error_label.text() != ""

def test_envbox_selection_loads_file(dialog, patch_config):
    names = [dialog.envbox.itemText(i) for i in range(dialog.envbox.count())]
    idx = names.index("test_env.json")

    dialog.envbox.setCurrentIndex(idx)
    dialog.load()

    text = dialog.env_field.toPlainText()
    assert "localhost" in text

def test_save_env_valid_json(dialog, patch_config, monkeypatch):
    called = {}

    def fake_save(path, data):
        called["path"] = path
        called["data"] = data

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.check_config.save_irods_config",
        fake_save
    )

    # Select the existing file
    dialog.envbox.setCurrentText("test_env.json")

    # Put valid JSON in the editor
    dialog.env_field.setPlainText('{"host": "example.org"}')

    dialog.save_env()

    assert "path" in called
    assert "example.org" in called["data"]["host"]
    assert "Configuration saved as" in dialog.error_label.text()


def test_save_env_invalid_json(dialog, patch_config):
    dialog.envbox.setCurrentText("test_env.json")
    dialog.env_field.setPlainText("not json")

    dialog.save_env()

    assert dialog.error_label.text() == "Incorrectly formatted. Click 'Check' for details."

def test_save_env_no_file_selected(dialog):
    dialog.envbox.setCurrentText("")  # empty entry
    dialog.env_field.setPlainText('{"host": "example.org"}')

    dialog.save_env()

    assert dialog.error_label.text() == "Choose 'Save as' to save"


import pytest
from pathlib import Path
from ibridgesgui.popup_widgets.check_config import CheckConfig


@pytest.fixture
def dialog(qtbot, patch_config, fake_logger):
    """Create and show the CheckConfig dialog."""
    d = CheckConfig(logger=fake_logger, env_path=patch_config["dir"])
    qtbot.addWidget(d)
    d.show()
    return d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_editor(dialog):
    return dialog.env_field.toPlainText()

def set_editor(dialog, text):
    dialog.env_field.setPlainText(text)

def error(dialog):
    return dialog.error_label.text()


# ---------------------------------------------------------------------------
# Loading environment files
# ---------------------------------------------------------------------------

def test_load_env_file_valid(dialog, patch_config):
    dialog._load_env_file(patch_config["file"])

    text = read_editor(dialog)
    assert "localhost" in text
    assert "tempZone" in text
    assert error(dialog) == ""


def test_load_env_file_invalid(dialog, tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json", encoding="utf-8")

    dialog._load_env_file(bad_file)

    assert read_editor(dialog) == ""
    assert error(dialog) != ""


def test_envbox_selection_loads_file(dialog, patch_config):
    # Select the known file
    idx = [dialog.envbox.itemText(i) for i in range(dialog.envbox.count())].index("test_env.json")
    dialog.envbox.setCurrentIndex(idx)

    dialog.load()
    assert "localhost" in read_editor(dialog)


# ---------------------------------------------------------------------------
# Saving existing environment files
# ---------------------------------------------------------------------------

def test_save_env_valid_json(dialog, patch_config, monkeypatch):
    called = {}

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.check_config.save_irods_config",
        lambda path, data: called.update(path=path, data=data),
    )

    dialog.envbox.setCurrentText("test_env.json")
    set_editor(dialog, '{"host": "example.org"}')

    dialog.save_env()

    assert called["path"].name == "test_env.json"
    assert called["data"]["host"] == "example.org"
    assert "Configuration saved as" in error(dialog)


def test_save_env_invalid_json(dialog):
    dialog.envbox.setCurrentText("test_env.json")
    set_editor(dialog, "not json")

    dialog.save_env()

    assert error(dialog) == "Incorrectly formatted. Click 'Check' for details."


def test_save_env_no_file_selected(dialog):
    dialog.envbox.setCurrentText("")
    set_editor(dialog, '{"host": "example.org"}')

    dialog.save_env()

    assert error(dialog) == "Choose 'Save as' to save"


# ---------------------------------------------------------------------------
# Save As
# ---------------------------------------------------------------------------

def test_save_env_as_cancel(dialog, monkeypatch):
    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getSaveFileName",
        lambda *a, **k: ("", ""),
    )

    set_editor(dialog, '{"host": "example.org"}')
    dialog.save_env_as()

    assert error(dialog) == ""


def test_save_env_as_wrong_extension(dialog, monkeypatch):
    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getSaveFileName",
        lambda *a, **k: ("/tmp/test_env", ""),
    )

    set_editor(dialog, '{"host": "example.org"}')
    dialog.save_env_as()

    assert error(dialog) == "ERROR: File must have .json extension."


def test_save_env_as_valid(dialog, monkeypatch):
    called = {}

    monkeypatch.setattr(
        "ibridgesgui.popup_widgets.check_config.save_irods_config",
        lambda path, data: called.update(path=path, data=data),
    )

    monkeypatch.setattr(
        "PySide6.QtWidgets.QFileDialog.getSaveFileName",
        lambda *a, **k: ("/tmp/test_env.json", ""),
    )

    set_editor(dialog, '{"host": "example.org"}')
    dialog.save_env_as()

    assert called["path"] == "/tmp/test_env.json"
    assert called["data"]["host"] == "example.org"
    assert "Configuration saved as" in error(dialog)


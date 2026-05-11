import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QTableWidget, QTextEdit, QApplication, QTableWidgetItem

from ibridgesgui import gui_utils


# ---------------------------------------------------------------------------
# UI LOADING
# ---------------------------------------------------------------------------

def test_load_ui_changes_and_restores_cwd(tmp_path, monkeypatch):
    ui_file = tmp_path / "test.ui"
    ui_file.write_text("<ui></ui>")

    # Use a real QObject so connectSlotsByName works
    from PySide6.QtCore import QObject
    mock_widget = QObject()

    monkeypatch.setattr(
        gui_utils,
        "UiLoader",
        MagicMock(return_value=MagicMock(load=lambda _: mock_widget)),
    )

    old_cwd = Path.cwd()
    widget = gui_utils.load_ui(str(ui_file))

    assert widget is mock_widget
    assert Path.cwd() == old_cwd


# ---------------------------------------------------------------------------
# TABLE WIDGETS
# ---------------------------------------------------------------------------

def test_populate_table(qtbot):
    table = QTableWidget()
    table.setColumnCount(2)  # REQUIRED
    qtbot.addWidget(table)

    data = [["A", "B"], ["C", "D"]]
    gui_utils.populate_table(table, 2, data)

    assert table.rowCount() == 2
    assert table.item(0, 0).text() == "A"
    assert table.item(1, 1).text() == "D"

def test_append_table(qtbot):
    table = QTableWidget()
    table.setColumnCount(2)  # REQUIRED
    qtbot.addWidget(table)

    gui_utils.populate_table(table, 1, [["X", "Y"]])
    gui_utils.append_table(table, 1, [["A", "B"], ["C", "D"]])

    assert table.rowCount() == 3
    assert table.item(1, 0).text() == "A"
    assert table.item(2, 1).text() == "D"


# ---------------------------------------------------------------------------
# TEXT FIELD
# ---------------------------------------------------------------------------

def test_populate_textfield_string(qtbot):
    text = QTextEdit()
    qtbot.addWidget(text)

    gui_utils.populate_textfield(text, "Hello")

    assert "Hello" in text.toPlainText()


def test_populate_textfield_list(qtbot):
    text = QTextEdit()
    qtbot.addWidget(text)

    gui_utils.populate_textfield(text, ["A", "B", "C"])

    assert text.toPlainText().splitlines() == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# SCHEMA LOADING
# ---------------------------------------------------------------------------

def test_load_schema_reads_json(monkeypatch, tmp_path):
    schema_file = tmp_path / "ibridges_metadata_schema.json"
    schema_file.write_text(json.dumps({"type": "object"}))

    # Patch importlib.resources.files to point to tmp_path
    class FakeFiles:
        def joinpath(self, name):
            return schema_file

    monkeypatch.setattr(gui_utils.pkg_resources, "files", lambda _: FakeFiles())

    schema = gui_utils.load_schema()
    assert schema == {"type": "object"}


# ---------------------------------------------------------------------------
# METADATA VALIDATION
# ---------------------------------------------------------------------------

def test_validate_metadata_valid(tmp_path, monkeypatch):
    schema = {"type": "object", "properties": {"x": {"type": "number"}}}
    monkeypatch.setattr(gui_utils, "load_schema", lambda: schema)

    md = tmp_path / "meta.json"
    md.write_text(json.dumps({"x": 5}))

    assert gui_utils.validate_metadata(md) is True


def test_validate_metadata_invalid_json(tmp_path):
    md = tmp_path / "meta.json"
    md.write_text("{invalid json}")

    with pytest.raises(ValueError):
        gui_utils.validate_metadata(md)


def test_validate_metadata_schema_error(tmp_path, monkeypatch):
    schema = {"type": "object", "properties": {"x": {"type": "number"}}}
    monkeypatch.setattr(gui_utils, "load_schema", lambda: schema)

    md = tmp_path / "meta.json"
    md.write_text(json.dumps({"x": "not a number"}))

    with pytest.raises(gui_utils.ValidationError):
        gui_utils.validate_metadata(md)


# ---------------------------------------------------------------------------
# IRODS HELPERS
# ---------------------------------------------------------------------------

def test_get_irods_item_collection(monkeypatch):
    mock_path = MagicMock()
    mock_path.collection_exists.return_value = True
    mock_path.collection = "COLL"

    assert gui_utils.get_irods_item(mock_path) == "COLL"


def test_get_irods_item_dataobject(monkeypatch):
    mock_path = MagicMock()
    mock_path.collection_exists.return_value = False
    mock_path.dataobject = "OBJ"

    assert gui_utils.get_irods_item(mock_path) == "OBJ"


# ---------------------------------------------------------------------------
# SESSION PREP
# ---------------------------------------------------------------------------

def test_prep_session_for_copy_valid(monkeypatch):
    monkeypatch.setattr(gui_utils, "is_session_from_config", lambda _: True)
    monkeypatch.setattr(gui_utils, "get_last_ienv_path", lambda: "env.json")

    result = gui_utils.prep_session_for_copy("session", MagicMock())
    assert result == Path.home() / ".irods" / "env.json"


def test_prep_session_for_copy_invalid(monkeypatch):
    monkeypatch.setattr(gui_utils, "is_session_from_config", lambda _: False)

    label = MagicMock()
    result = gui_utils.prep_session_for_copy("session", label)

    assert result is None
    label.setText.assert_called_once()


# ---------------------------------------------------------------------------
# COMBINE OPERATIONS
# ---------------------------------------------------------------------------

def test_combine_operations():
    op1 = MagicMock(
        create_dir={"a"},
        create_collection={"x"},
        meta_upload=["m1"],
        download=[1],
        upload=[10],
    )
    op2 = MagicMock(
        create_dir={"b"},
        create_collection={"y"},
        meta_upload=["m2"],
        download=[2],
        upload=[20],
    )

    combined = gui_utils.combine_operations([op1, op2])

    assert combined.create_dir == {"a", "b"}
    assert combined.create_collection == {"x", "y"}
    assert combined.meta_upload == ["m1", "m2"]
    assert combined.download == [1, 2]
    assert combined.upload == [10, 20]

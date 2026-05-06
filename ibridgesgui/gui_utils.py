"""Handy and reusable functions for the GUI."""

# ruff: noqa: N802
# pylint: disable=R0903, R1705, C0103

import importlib.resources as pkg_resources
import json
import os
import sys
from pathlib import Path
from typing import Iterable, Optional, Union

import PySide6.QtCore
import PySide6.QtUiTools
import PySide6.QtWidgets
from ibridges import IrodsPath
from ibridges.executor import Operations
from jsonschema import ValidationError, validate

import ibridgesgui.md_schemas
from ibridgesgui.config import get_last_ienv_path, is_session_from_config

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files


if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
    UI_FILE_DIR = Path("ui_files")
    LOGO_DIR = Path("icons")
else:
    UI_FILE_DIR = files(__package__) / "ui_files"
    LOGO_DIR = files(__package__) / "icons"


class UiLoader(PySide6.QtUiTools.QUiLoader):
    """UILoader that supports custom widgets and attribute binding."""

    def __init__(self, base_instance=None):
        """Init."""
        super().__init__(base_instance)
        self.base_instance = base_instance

    def createWidget(self, class_name, parent=None, name=""):
        """Create Widget from ui."""
        if parent is None and self.base_instance:
            return self.base_instance

        widget = super().createWidget(class_name, parent, name)
        if self.base_instance and name:
            setattr(self.base_instance, name, widget)
        return widget


def load_ui(ui_file: str, base_instance=None):
    """Load a .ui file while temporarily switching to its directory.

    This ensures that relative paths (e.g., images) inside the .ui file resolve correctly.
    """
    ui_path = Path(ui_file).resolve()
    ui_dir = ui_path.parent

    # Save current working directory
    old_cwd = Path.cwd()

    try:
        os.chdir(ui_dir)
        loader = UiLoader(base_instance)
        widget = loader.load(str(ui_path))
        PySide6.QtCore.QMetaObject.connectSlotsByName(widget)
        return widget

    finally:
        # Restore original working directory
        os.chdir(old_cwd)


def populate_table(table_widget, rows: int, data_by_row: Iterable[Iterable]):
    """Fill a QTableWidget with data."""
    table_widget.setRowCount(rows)

    for row, data in enumerate(data_by_row):
        for col, item in enumerate(data):
            table_widget.setItem(row, col, PySide6.QtWidgets.QTableWidgetItem(str(item)))

    table_widget.resizeColumnsToContents()


def append_table(table_widget, curr_len_table: int, data_by_row: Iterable[Iterable]):
    """Append rows to an existing QTableWidget."""
    new_rows = curr_len_table + len(data_by_row)
    table_widget.setRowCount(new_rows)

    for data in data_by_row:
        for col, item in enumerate(data):
            table_widget.setItem(curr_len_table, col, PySide6.QtWidgets.QTableWidgetItem(str(item)))
        curr_len_table += 1

    table_widget.resizeColumnsToContents()


def populate_textfield(text_widget, text_by_row: Union[str, Iterable[str]]):
    """Fill a QTextEdit/QPlainTextEdit with text."""
    text_widget.clear()

    if isinstance(text_by_row, str):
        text_widget.append(text_by_row)
    else:
        for row in text_by_row:
            text_widget.append(row)


def load_schema() -> dict:
    """Load the iBridges metadata schema."""
    try:
        schema_path = pkg_resources.files(ibridgesgui.md_schemas).joinpath(
            "ibridges_metadata_schema.json"
        )
        with schema_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        # Fallback for frozen executable
        md_schema_path = (
            Path(__file__).parent.parent / "md_schemas" / "ibridges_metadata_schema.json"
        )
        with md_schema_path.open("r", encoding="utf-8") as f:
            return json.load(f)


def validate_metadata(md_path: Path) -> bool:
    """Validate a JSON metadata file against the schema."""
    if not md_path.is_file():
        raise FileNotFoundError(f"Metadata file not found: {md_path}")

    try:
        with md_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in metadata file: {e}") from e

    schema_data = load_schema()

    try:
        validate(instance=data, schema=schema_data)
    except ValidationError as e:
        raise ValidationError(f"Metadata validation failed: {e.message}") from e

    return True


def get_irods_item(irods_path: IrodsPath):
    """Return the iRODS collection or data object behind a path."""
    return irods_path.collection if irods_path.collection_exists() else irods_path.dataobject


def prep_session_for_copy(session, error_label) -> Optional[Path]:
    """Return a save path or set an error message."""
    if is_session_from_config(session):
        return Path.home() / ".irods" / get_last_ienv_path()

    error_label.setText(
        "The ibridges config changed during the session. Please reset or restart the session."
    )
    return None


def combine_operations(operations: list[Operations]) -> Operations:
    """Merge multiple Operations objects into one."""
    base = operations[0]

    base.create_dir = set().union(*(op.create_dir for op in operations))
    base.create_collection = set().union(*(op.create_collection for op in operations))
    base.meta_upload = set().union(*(op.meta_upload for op in operations))

    for op in operations[1:]:
        base.download.extend(op.download)
        base.upload.extend(op.upload)

    return base

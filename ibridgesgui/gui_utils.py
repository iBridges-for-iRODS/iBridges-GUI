"""Handy and reusable functions for the GUI."""
# ruff: noqa: N802 # Overriding a pyside6 function that is not snake_case
# pylint: disable=R0903, R1705, C0103

import os
import pathlib
import sys
from typing import Union

import irods
import PySide6.QtCore
import PySide6.QtUiTools
import PySide6.QtWidgets
from ibridges import IrodsPath
from ibridges.executor import Operations

from ibridgesgui.config import get_last_ienv_path, is_session_from_config

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

if getattr(sys, "frozen", False) or ("__compiled__" in globals()):
    UI_FILE_DIR = pathlib.Path("ui_files")
    LOGO_DIR = pathlib.Path("icons")
else:
    UI_FILE_DIR = files(__package__) / "ui_files"
    LOGO_DIR = files(__package__) / "icons"


class UiLoader(PySide6.QtUiTools.QUiLoader):
    """UILoader to allow custom widgets."""

    def __init__(self, base_instance):
        """Initialise the UiLoader."""
        PySide6.QtUiTools.QUiLoader.__init__(self, base_instance)
        self.base_instance = base_instance

    def createWidget(self, class_name, parent=None, name=""):
        """Create a widget for the UI loader."""
        if parent is None and self.base_instance:
            return self.base_instance
        else:
            # create a new widget for child widgets
            widget = PySide6.QtUiTools.QUiLoader.createWidget(self, class_name, parent, name)
            if self.base_instance:
                setattr(self.base_instance, name, widget)
            return widget


def load_ui(ui_file, base_instance=None):
    """Load ui, as available in pyqt."""
    ui_dir = os.path.dirname(ui_file)
    os.chdir(ui_dir)
    loader = UiLoader(base_instance)
    widget = loader.load(ui_file)
    PySide6.QtCore.QMetaObject.connectSlotsByName(widget)
    return widget


# Widget utils
def populate_table(table_widget, rows: int, data_by_row: list):
    """Populate a table-like pyqt widget with data."""
    table_widget.setRowCount(0)
    table_widget.setRowCount(rows)

    for row, data in enumerate(data_by_row):
        for col, item in enumerate(data):
            table_widget.setItem(row, col, PySide6.QtWidgets.QTableWidgetItem(str(item)))
    table_widget.resizeColumnsToContents()


def append_table(table_widget, curr_len_table, data_by_row):
    """Append more rows to an existing table widget."""
    table_widget.setRowCount(curr_len_table + len(data_by_row))
    for data in data_by_row:
        for col, item in enumerate(data):
            table_widget.setItem(curr_len_table, col, PySide6.QtWidgets.QTableWidgetItem(str(item)))
        curr_len_table += 1
    table_widget.resizeColumnsToContents()


def populate_textfield(text_widget, text_by_row: Union[str, list]):
    """Populate a text viewer or editor with text."""
    text_widget.clear()
    if isinstance(text_by_row, str):
        text_widget.append(text_by_row)
    else:
        for row in text_by_row:
            text_widget.append(row)


# iBridges/iRODS utils
def get_irods_item(irods_path: IrodsPath):
    """Get the item behind an iRODS path."""
    if irods_path.collection_exists():
        item = irods_path.collection
    else:
        item = irods_path.dataobject
    return item


def get_coll_dict(root_coll: irods.collection.iRODSCollection) -> dict:
    """Create a recursive metadata dictionary for `coll`.

    Parameters
    ----------
    root_coll : irods.collection.iRODSCollection
        Root collection for the metadata gathering.

    Returns
    -------
    dict
        Keys of logical paths, values

    """
    return {
        this_coll.path: [data_obj.name for data_obj in data_objs]
        for this_coll, _, data_objs in root_coll.walk()
    }


def prep_session_for_copy(session, error_label) -> pathlib.Path:
    """Either return a save path to create a new session from or sets message in error label."""
    if is_session_from_config(session):
        return pathlib.Path.home().joinpath(".irods", get_last_ienv_path())

    text = "The ibridges config changed during the session."
    text += "Please reset or restart the session."
    error_label.setText(text)
    return None


def combine_operations(operations: list[Operations]) -> Operations:
    """Combine the operations of several upload or download dry-runs."""
    ops = operations[0]
    ops.create_dir = set().union(*[o.create_dir for o in operations])
    ops.create_collection = set().union(*[o.create_collection for o in operations])
    for op in operations[1:]:
        ops.download.extend(op.download)
        ops.upload.extend(op.upload)

    return ops


# OS utils
def get_downloads_dir() -> pathlib.Path:
    """Find the platform-dependent 'Downloads' directory.

    Returns
    -------
    pathlib.Path
        Absolute path to 'Downloads' directory.

    """
    # Linux and Mac Download folders
    if pathlib.Path.home().joinpath("Downloads").is_dir():
        return pathlib.Path.home().joinpath("Downloads")

    # Try to create Downloads
    pathlib.Path.home().joinpath("Downloads").mkdir(parents=True)
    return pathlib.Path.home().joinpath("Downloads")

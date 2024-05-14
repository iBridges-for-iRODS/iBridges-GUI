"""Handy and reusable functions for the GUI."""
import pathlib
from importlib.resources import files
from typing import Union

import irods
import PyQt6
from ibridges import get_collection, get_dataobject
from ibridges.path import IrodsPath

UI_FILE_DIR = files(__package__) / "ui_files"

# Widget utils
def populate_table(table_widget, rows: int, data_by_row: list):
    """Populate a table-like pyqt widget with data."""
    table_widget.setRowCount(rows)
    for row, data in enumerate(data_by_row):
        for col, item in enumerate(data):
            table_widget.setItem(row, col, PyQt6.QtWidgets.QTableWidgetItem(str(item)))
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
    try:
        item = get_collection(irods_path.session, irods_path)
    except ValueError:
        item = get_dataobject(irods_path.session, irods_path)
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
    return {this_coll.path: [data_obj.name for data_obj in data_objs]
            for this_coll, _, data_objs in root_coll.walk()}

# OS utils
def get_downloads_dir() -> pathlib.Path:
    """Find the platform-dependent 'Downloads' directory.

    Returns
    -------
    pathlib.Path
        Absolute path to 'Downloads' directory.

    """
    # Linux and Mac Download folders
    if pathlib.Path("~", "Downloads").expanduser().is_dir():
        return pathlib.Path("~", "Downloads").expanduser()

    # Try to create Downloads
    pathlib.Path("~", "Downloads").expanduser().mkdir(parents=True)
    return pathlib.Path("~", "Downloads").expanduser()

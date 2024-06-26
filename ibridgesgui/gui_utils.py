"""Handy and reusable functions for the GUI."""

import pathlib
from typing import Union

import irods
import PyQt6
from ibridges import IrodsPath, download

from ibridgesgui.config import get_last_ienv_path, is_session_from_config

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files


UI_FILE_DIR = files(__package__) / "ui_files"
LOGO_DIR = files(__package__) / "icons"


# Widget utils
def populate_table(table_widget, rows: int, data_by_row: list):
    """Populate a table-like pyqt widget with data."""
    table_widget.setRowCount(0)
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


def combine_diffs(session, sources: list, destination: Union[IrodsPath, pathlib.Path]) -> dict:
    """Combine the diffs of several upload or download dry-runs."""
    combined_diffs = {
        "create_dir": set(),
        "create_collection": set(),
        "upload": [],
        "download": [],
        "resc_name": "",
        "options": None,
    }
    if isinstance(destination, pathlib.Path):
        for ipath in sources:
            diff = download(session, ipath, destination, dry_run=True, overwrite=True)
            combined_diffs["download"].extend(diff["download"])
            combined_diffs["create_dir"] = combined_diffs["create_dir"].union(diff["create_dir"])
    elif isinstance(destination, IrodsPath):
        print("not implemented yet")
    return combined_diffs


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

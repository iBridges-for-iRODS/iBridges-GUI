"""Handy and reusable functions for the GUI"""
import pathlib
from importlib.resources import files

import irods
import PyQt6
from typing import Union

from ibridges import get_collection, get_dataobject
from ibridges.path import IrodsPath

UI_FILE_DIR = files(__package__) / "ui_files"

# Widget utils
def populate_table(table_widget, rows: int, data_by_row: list):

    table_widget.setRowCount(rows)
    for row, data in enumerate(data_by_row):
        for col, item in enumerate(data):
            table_widget.setItem(row, col, PyQt6.QtWidgets.QTableWidgetItem(str(item)))
    table_widget.resizeColumnsToContents()

def populate_textfield(text_widget, text_by_row: Union[str, list]):
    text_widget.clear()
    if isinstance(text_by_row, str):
        text_widget.append(text_by_row)
    else:
        for row in text_by_row:
            text_widget.append(row)

# iBridges/iRODS utils
def get_irods_item(irods_path: IrodsPath):
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
    if isinstance(pathlib.Path('~'), pathlib.PosixPath):
        return pathlib.Path('~', 'Downloads').expanduser()
    else:
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            return pathlib.Path(winreg.QueryValueEx(key, downloads_guid)[0])

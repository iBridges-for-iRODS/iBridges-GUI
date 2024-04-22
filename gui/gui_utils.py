"""Handy and reusable functions for the GUI"""
import PyQt6
import irods
from ibridges import get_collection, get_dataobject

def populate_table(tableWidget, rows, data_by_row):

    tableWidget.setRowCount(rows)
    for row, data in enumerate(data_by_row):
        for col, item in enumerate(data):
            tableWidget.setItem(row, col, PyQt6.QtWidgets.QTableWidgetItem(str(item)))
    tableWidget.resizeColumnsToContents()    

def get_irods_item(irods_path):
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

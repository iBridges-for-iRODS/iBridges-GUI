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

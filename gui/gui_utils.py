"""Handy and reusable functions for the GUI"""
import PyQt6


def populate_table(tableWidget, rows, data_by_row):

    tableWidget.setRowCount(rows)
    for row, data in enumerate(data_by_row):
        for col, item in enumerate(data):
            tableWidget.setItem(row, col, PyQt6.QtWidgets.QTableWidgetItem(item))
    tableWidget.resizeColumnsToContents()    


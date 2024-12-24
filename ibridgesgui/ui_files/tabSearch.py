# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tabSearch.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_tabSearch(object):
    def setupUi(self, tabSearch):
        if not tabSearch.objectName():
            tabSearch.setObjectName(u"tabSearch")
        tabSearch.resize(984, 619)
        tabSearch.setMinimumSize(QSize(0, 500))
        tabSearch.setStyleSheet(u"QWidget\n"
"{\n"
"    background-color: rgb(211,211,211);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244);\n"
"    font: 16pt\n"
"}\n"
"\n"
"QLabel#error_label\n"
"{\n"
"    color: rgb(220, 130, 30);\n"
"}\n"
"\n"
"QLineEdit, QTextEdit, QTableWidget\n"
"{\n"
"   background-color:  rgb(245, 244, 244)\n"
"}\n"
"\n"
"QPushButton\n"
"{\n"
"	background-color: rgb(21, 165, 137);\n"
"    color: rgb(245, 244, 244);\n"
"}\n"
"\n"
"QPushButton#home_button, QPushButton#parent_button, QPushButton#refresh_button\n"
"{\n"
"    background-color: rgb(245, 244, 244);\n"
"}\n"
"\n"
"QTabWidget#info_tabs\n"
"{\n"
"     background-color: background-color: rgb(211,211,211);\n"
"}\n"
"\n"
"")
        self.verticalLayout_3 = QVBoxLayout(tabSearch)
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_6 = QLabel(tabSearch)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 2, 2, 1, 1)

        self.label_5 = QLabel(tabSearch)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)

        self.search_path_field = QLineEdit(tabSearch)
        self.search_path_field.setObjectName(u"search_path_field")

        self.gridLayout_2.addWidget(self.search_path_field, 0, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 3, 1, 1, 1)

        self.path_pattern_field = QLineEdit(tabSearch)
        self.path_pattern_field.setObjectName(u"path_pattern_field")

        self.gridLayout_2.addWidget(self.path_pattern_field, 3, 2, 1, 1)

        self.label_3 = QLabel(tabSearch)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)

        self.checksum_field = QLineEdit(tabSearch)
        self.checksum_field.setObjectName(u"checksum_field")

        self.gridLayout_2.addWidget(self.checksum_field, 4, 2, 1, 1)

        self.label_2 = QLabel(tabSearch)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout_2.addItem(self.verticalSpacer_4, 1, 2, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.verticalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(tabSearch)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 1, 1, 1, 1)

        self.val1 = QLineEdit(tabSearch)
        self.val1.setObjectName(u"val1")

        self.gridLayout.addWidget(self.val1, 2, 1, 1, 1)

        self.label1 = QLabel(tabSearch)
        self.label1.setObjectName(u"label1")

        self.gridLayout.addWidget(self.label1, 0, 0, 1, 1)

        self.val3 = QLineEdit(tabSearch)
        self.val3.setObjectName(u"val3")

        self.gridLayout.addWidget(self.val3, 4, 1, 1, 1)

        self.units1 = QLineEdit(tabSearch)
        self.units1.setObjectName(u"units1")

        self.gridLayout.addWidget(self.units1, 2, 2, 1, 1)

        self.units3 = QLineEdit(tabSearch)
        self.units3.setObjectName(u"units3")

        self.gridLayout.addWidget(self.units3, 4, 2, 1, 1)

        self.units2 = QLineEdit(tabSearch)
        self.units2.setObjectName(u"units2")

        self.gridLayout.addWidget(self.units2, 3, 2, 1, 1)

        self.key3 = QLineEdit(tabSearch)
        self.key3.setObjectName(u"key3")

        self.gridLayout.addWidget(self.key3, 4, 0, 1, 1)

        self.key4 = QLineEdit(tabSearch)
        self.key4.setObjectName(u"key4")

        self.gridLayout.addWidget(self.key4, 5, 0, 1, 1)

        self.label_7 = QLabel(tabSearch)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 1, 2, 1, 1)

        self.key2 = QLineEdit(tabSearch)
        self.key2.setObjectName(u"key2")

        self.gridLayout.addWidget(self.key2, 3, 0, 1, 1)

        self.val2 = QLineEdit(tabSearch)
        self.val2.setObjectName(u"val2")

        self.gridLayout.addWidget(self.val2, 3, 1, 1, 1)

        self.label_4 = QLabel(tabSearch)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)

        self.units4 = QLineEdit(tabSearch)
        self.units4.setObjectName(u"units4")

        self.gridLayout.addWidget(self.units4, 5, 2, 1, 1)

        self.val4 = QLineEdit(tabSearch)
        self.val4.setObjectName(u"val4")

        self.gridLayout.addWidget(self.val4, 5, 1, 1, 1)

        self.key1 = QLineEdit(tabSearch)
        self.key1.setObjectName(u"key1")

        self.gridLayout.addWidget(self.key1, 2, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalSpacer_5 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_5)

        self.case_sensitive_box = QCheckBox(tabSearch)
        self.case_sensitive_box.setObjectName(u"case_sensitive_box")

        self.verticalLayout.addWidget(self.case_sensitive_box)

        self.verticalSpacer_6 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.search_button = QPushButton(tabSearch)
        self.search_button.setObjectName(u"search_button")
        font = QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        self.search_button.setFont(font)
        self.search_button.setAutoDefault(False)

        self.horizontalLayout_5.addWidget(self.search_button)

        self.clear_button = QPushButton(tabSearch)
        self.clear_button.setObjectName(u"clear_button")
        self.clear_button.setFont(font)
        self.clear_button.setStyleSheet(u"")

        self.horizontalLayout_5.addWidget(self.clear_button)

        self.load_more_button = QPushButton(tabSearch)
        self.load_more_button.setObjectName(u"load_more_button")

        self.horizontalLayout_5.addWidget(self.load_more_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.download_button = QPushButton(tabSearch)
        self.download_button.setObjectName(u"download_button")
        self.download_button.setFont(font)
        self.download_button.setStyleSheet(u"")

        self.horizontalLayout_5.addWidget(self.download_button)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.error_label = QLabel(tabSearch)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout.addWidget(self.error_label)

        self.search_table = QTableWidget(tabSearch)
        if (self.search_table.columnCount() < 5):
            self.search_table.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setText(u"Type");
        self.search_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.search_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.search_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.search_table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.search_table.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.search_table.setObjectName(u"search_table")
        self.search_table.setMinimumSize(QSize(0, 250))
        self.search_table.setMaximumSize(QSize(16777215, 400))
        self.search_table.setStyleSheet(u"")
        self.search_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.search_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.search_table.setAlternatingRowColors(False)
        self.search_table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.search_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.search_table.setSortingEnabled(True)
        self.search_table.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.search_table)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)


        self.retranslateUi(tabSearch)

        self.search_button.setDefault(True)


        QMetaObject.connectSlotsByName(tabSearch)
    # setupUi

    def retranslateUi(self, tabSearch):
        tabSearch.setWindowTitle(QCoreApplication.translate("tabSearch", u"Form", None))
        self.label_6.setText(QCoreApplication.translate("tabSearch", u"Search Wildcard is: %", None))
        self.label_5.setText(QCoreApplication.translate("tabSearch", u"Checksum", None))
        self.label_3.setText(QCoreApplication.translate("tabSearch", u"Obj/Coll name", None))
        self.label_2.setText(QCoreApplication.translate("tabSearch", u"Search in", None))
        self.label.setText(QCoreApplication.translate("tabSearch", u"Value", None))
        self.label1.setText(QCoreApplication.translate("tabSearch", u"Search by Metadata", None))
        self.label_7.setText(QCoreApplication.translate("tabSearch", u"Units", None))
        self.label_4.setText(QCoreApplication.translate("tabSearch", u"Key", None))
        self.case_sensitive_box.setText(QCoreApplication.translate("tabSearch", u"Case sensitive", None))
        self.search_button.setText(QCoreApplication.translate("tabSearch", u"Search", None))
        self.clear_button.setText(QCoreApplication.translate("tabSearch", u"Clear Results", None))
        self.load_more_button.setText(QCoreApplication.translate("tabSearch", u"Next 25", None))
        self.download_button.setText(QCoreApplication.translate("tabSearch", u"Download Selection", None))
        self.error_label.setText("")
        ___qtablewidgetitem = self.search_table.horizontalHeaderItem(1)
        ___qtablewidgetitem.setText(QCoreApplication.translate("tabSearch", u"Path", None));
        ___qtablewidgetitem1 = self.search_table.horizontalHeaderItem(2)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("tabSearch", u"Size [bytes]", None));
        ___qtablewidgetitem2 = self.search_table.horizontalHeaderItem(3)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("tabSearch", u"Created", None));
        ___qtablewidgetitem3 = self.search_table.horizontalHeaderItem(4)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("tabSearch", u"Modified", None));
    # retranslateUi


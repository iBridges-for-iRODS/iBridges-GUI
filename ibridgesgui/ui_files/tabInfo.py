# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tabInfo.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QTextBrowser,
    QWidget)

class Ui_tabInfo(object):
    def setupUi(self, tabInfo):
        if not tabInfo.objectName():
            tabInfo.setObjectName(u"tabInfo")
        tabInfo.resize(640, 572)
        tabInfo.setStyleSheet(u"QWidget\n"
"{\n"
"    background-color: rgb(245, 244, 244);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244)\n"
"}\n"
"\n"
"QLabel\n"
"{\n"
"  background-color: rgb(211,211,211);\n"
"}\n"
"\n"
"QLabel#error_label\n"
"{\n"
"    color: rgb(252, 152, 3);\n"
"}\n"
"\n"
"QPushButton\n"
"{\n"
"	background-color: rgb(21, 165, 137);\n"
"    color: rgb(245, 244, 244);\n"
"}\n"
"\n"
"QTextEdit, QTableWidget\n"
"{\n"
"     background-color: rgb(245, 244, 244)\n"
"}\n"
"")
        self.horizontalLayout = QHBoxLayout(tabInfo)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.zone_label = QLabel(tabInfo)
        self.zone_label.setObjectName(u"zone_label")

        self.gridLayout.addWidget(self.zone_label, 3, 2, 1, 1)

        self.user_label = QLabel(tabInfo)
        self.user_label.setObjectName(u"user_label")

        self.gridLayout.addWidget(self.user_label, 4, 2, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_5, 13, 0, 1, 1)

        self.type_label = QLabel(tabInfo)
        self.type_label.setObjectName(u"type_label")

        self.gridLayout.addWidget(self.type_label, 5, 2, 1, 1)

        self.label_2 = QLabel(tabInfo)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 14, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.refresh_button = QPushButton(tabInfo)
        self.refresh_button.setObjectName(u"refresh_button")
        font = QFont()
        font.setBold(False)
        font.setItalic(False)
        self.refresh_button.setFont(font)

        self.horizontalLayout_3.addWidget(self.refresh_button)


        self.gridLayout.addLayout(self.horizontalLayout_3, 19, 2, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_4, 6, 0, 1, 1)

        self.label_13 = QLabel(tabInfo)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout.addWidget(self.label_13, 15, 0, 1, 1)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_6, 16, 0, 1, 1)

        self.label_12 = QLabel(tabInfo)
        self.label_12.setObjectName(u"label_12")
        font1 = QFont()
        font1.setPointSize(18)
        font1.setBold(False)
        font1.setItalic(False)
        self.label_12.setFont(font1)

        self.gridLayout.addWidget(self.label_12, 12, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 18, 2, 1, 1)

        self.label_11 = QLabel(tabInfo)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font1)

        self.gridLayout.addWidget(self.label_11, 0, 0, 1, 1)

        self.label_4 = QLabel(tabInfo)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 11, 0, 1, 1)

        self.label_5 = QLabel(tabInfo)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 7, 0, 1, 1)

        self.label_10 = QLabel(tabInfo)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 5, 0, 1, 1)

        self.resc_label = QLabel(tabInfo)
        self.resc_label.setObjectName(u"resc_label")

        self.gridLayout.addWidget(self.resc_label, 8, 2, 1, 1)

        self.label_8 = QLabel(tabInfo)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 8, 0, 1, 1)

        self.resc_table = QTableWidget(tabInfo)
        if (self.resc_table.columnCount() < 3):
            self.resc_table.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.resc_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.resc_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.resc_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.resc_table.setObjectName(u"resc_table")
        self.resc_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resc_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.resc_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.gridLayout.addWidget(self.resc_table, 17, 2, 1, 1)

        self.groups_browser = QTextBrowser(tabInfo)
        self.groups_browser.setObjectName(u"groups_browser")

        self.gridLayout.addWidget(self.groups_browser, 7, 2, 1, 1)

        self.label_3 = QLabel(tabInfo)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.label_9 = QLabel(tabInfo)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 17, 0, 1, 1)

        self.version_label = QLabel(tabInfo)
        self.version_label.setObjectName(u"version_label")

        self.gridLayout.addWidget(self.version_label, 15, 2, 1, 1)

        self.log_label = QLabel(tabInfo)
        self.log_label.setObjectName(u"log_label")

        self.gridLayout.addWidget(self.log_label, 9, 2, 1, 1)

        self.label_6 = QLabel(tabInfo)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 9, 0, 1, 1)

        self.server_label = QLabel(tabInfo)
        self.server_label.setObjectName(u"server_label")

        self.gridLayout.addWidget(self.server_label, 14, 2, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_3, 10, 0, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)


        self.retranslateUi(tabInfo)

        QMetaObject.connectSlotsByName(tabInfo)
    # setupUi

    def retranslateUi(self, tabInfo):
        tabInfo.setWindowTitle(QCoreApplication.translate("tabInfo", u"Form", None))
        self.zone_label.setText("")
        self.user_label.setText("")
        self.type_label.setText("")
        self.label_2.setText(QCoreApplication.translate("tabInfo", u"Server", None))
        self.refresh_button.setText(QCoreApplication.translate("tabInfo", u"Refresh", None))
        self.label_13.setText(QCoreApplication.translate("tabInfo", u"Version", None))
        self.label_12.setText(QCoreApplication.translate("tabInfo", u"Server Information", None))
        self.label_11.setText(QCoreApplication.translate("tabInfo", u"Client Information", None))
        self.label_4.setText(QCoreApplication.translate("tabInfo", u"Username", None))
        self.label_5.setText(QCoreApplication.translate("tabInfo", u"User's groups", None))
        self.label_10.setText(QCoreApplication.translate("tabInfo", u"Usertype", None))
        self.resc_label.setText("")
        self.label_8.setText(QCoreApplication.translate("tabInfo", u"Default resource", None))
        ___qtablewidgetitem = self.resc_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("tabInfo", u"Name", None));
        ___qtablewidgetitem1 = self.resc_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("tabInfo", u"Status", None));
        ___qtablewidgetitem2 = self.resc_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("tabInfo", u"Free Space", None));
        self.label_3.setText(QCoreApplication.translate("tabInfo", u"Zone", None))
        self.label_9.setText(QCoreApplication.translate("tabInfo", u"Resources", None))
        self.version_label.setText("")
        self.log_label.setText("")
        self.label_6.setText(QCoreApplication.translate("tabInfo", u"iBridges Logfiles", None))
        self.server_label.setText("")
    # retranslateUi


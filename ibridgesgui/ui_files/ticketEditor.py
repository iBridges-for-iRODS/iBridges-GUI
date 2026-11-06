# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ticketEditor.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCalendarWidget, QCheckBox,
    QDialog, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QTreeView, QVBoxLayout,
    QWidget)

class Ui_ticketEditor(object):
    def setupUi(self, ticketEditor):
        if not ticketEditor.objectName():
            ticketEditor.setObjectName(u"ticketEditor")
        ticketEditor.resize(1000, 750)
        ticketEditor.setStyleSheet(u"QWidget\n"
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
        self.verticalLayout_3 = QVBoxLayout(ticketEditor)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.irods_tree_view = QTreeView(ticketEditor)
        self.irods_tree_view.setObjectName(u"irods_tree_view")
        self.irods_tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.horizontalLayout_2.addWidget(self.irods_tree_view)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_2 = QLabel(ticketEditor)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.expiry_calendar = QCalendarWidget(ticketEditor)
        self.expiry_calendar.setObjectName(u"expiry_calendar")

        self.verticalLayout_2.addWidget(self.expiry_calendar)

        self.expiry_checkbox = QCheckBox(ticketEditor)
        self.expiry_checkbox.setObjectName(u"expiry_checkbox")

        self.verticalLayout_2.addWidget(self.expiry_checkbox)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(ticketEditor)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.read_button = QRadioButton(ticketEditor)
        self.read_button.setObjectName(u"read_button")
        self.read_button.setChecked(True)

        self.horizontalLayout_3.addWidget(self.read_button)

        self.write_button = QRadioButton(ticketEditor)
        self.write_button.setObjectName(u"write_button")

        self.horizontalLayout_3.addWidget(self.write_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.create_ticket_button = QPushButton(ticketEditor)
        self.create_ticket_button.setObjectName(u"create_ticket_button")

        self.horizontalLayout.addWidget(self.create_ticket_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.error_label = QLabel(ticketEditor)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout_3.addWidget(self.error_label)

        self.label = QLabel(ticketEditor)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.verticalLayout_3.addWidget(self.label)

        self.ticket_table = QTableWidget(ticketEditor)
        if (self.ticket_table.columnCount() < 4):
            self.ticket_table.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.ticket_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.ticket_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.ticket_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.ticket_table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.ticket_table.setObjectName(u"ticket_table")
        self.ticket_table.setMaximumSize(QSize(1000, 16777215))

        self.verticalLayout_3.addWidget(self.ticket_table)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.close_button = QPushButton(ticketEditor)
        self.close_button.setObjectName(u"close_button")

        self.horizontalLayout_4.addWidget(self.close_button)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.retranslateUi(ticketEditor)

        QMetaObject.connectSlotsByName(ticketEditor)
    # setupUi

    def retranslateUi(self, ticketEditor):
        ticketEditor.setWindowTitle(QCoreApplication.translate("ticketEditor", u"Dialog", None))
        self.label_2.setText(QCoreApplication.translate("ticketEditor", u"Expiry Date", None))
        self.expiry_checkbox.setText(QCoreApplication.translate("ticketEditor", u"No Expiry Date", None))
        self.label_3.setText(QCoreApplication.translate("ticketEditor", u"Acess Mode", None))
        self.read_button.setText(QCoreApplication.translate("ticketEditor", u"Read", None))
        self.write_button.setText(QCoreApplication.translate("ticketEditor", u"Write", None))
        self.create_ticket_button.setText(QCoreApplication.translate("ticketEditor", u"Create Ticket", None))
        self.error_label.setText("")
        self.label.setText(QCoreApplication.translate("ticketEditor", u"Existing Tickets", None))
        ___qtablewidgetitem = self.ticket_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ticketEditor", u"Ticket", None))
        ___qtablewidgetitem1 = self.ticket_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ticketEditor", u"iRODS Path", None))
        ___qtablewidgetitem2 = self.ticket_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ticketEditor", u"Expiry Date", None))
        ___qtablewidgetitem3 = self.ticket_table.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ticketEditor", u"Delete", None))
        self.close_button.setText(QCoreApplication.translate("ticketEditor", u"Close", None))
    # retranslateUi


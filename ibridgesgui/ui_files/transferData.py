# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'transferData.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QTableView, QVBoxLayout, QWidget)

class Ui_transferData(object):
    def setupUi(self, transferData):
        if not transferData.objectName():
            transferData.setObjectName(u"transferData")
        transferData.resize(973, 395)
        transferData.setStyleSheet(u"QWidget\n"
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
        self.gridLayout = QGridLayout(transferData)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton = QPushButton(transferData)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(transferData)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_2.addWidget(self.pushButton_2)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)

        self.error_label = QLabel(transferData)
        self.error_label.setObjectName(u"error_label")

        self.gridLayout.addWidget(self.error_label, 8, 0, 1, 7)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(transferData)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        self.label_2.setFont(font)

        self.verticalLayout.addWidget(self.label_2)

        self.overwrite = QCheckBox(transferData)
        self.overwrite.setObjectName(u"overwrite")

        self.verticalLayout.addWidget(self.overwrite)

        self.checkBox = QCheckBox(transferData)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout.addWidget(self.checkBox)


        self.gridLayout.addLayout(self.verticalLayout, 5, 0, 1, 1)

        self.label = QLabel(transferData)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.local_to_irods_button = QPushButton(transferData)
        self.local_to_irods_button.setObjectName(u"local_to_irods_button")
        self.local_to_irods_button.setMinimumSize(QSize(100, 0))
        icon = QIcon()
        icon.addFile(u"../icons/arrow-right.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.local_to_irods_button.setIcon(icon)
        self.local_to_irods_button.setIconSize(QSize(50, 50))

        self.gridLayout.addWidget(self.local_to_irods_button, 3, 2, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cancel_button = QPushButton(transferData)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)

        self.stop_button = QPushButton(transferData)
        self.stop_button.setObjectName(u"stop_button")

        self.horizontalLayout.addWidget(self.stop_button)


        self.gridLayout.addLayout(self.horizontalLayout, 5, 3, 1, 1)

        self.label_3 = QLabel(transferData)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 3, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 4, 1, 1, 1)

        self.tableView = QTableView(transferData)
        self.tableView.setObjectName(u"tableView")

        self.gridLayout.addWidget(self.tableView, 3, 1, 1, 1)

        self.tableView_2 = QTableView(transferData)
        self.tableView_2.setObjectName(u"tableView_2")

        self.gridLayout.addWidget(self.tableView_2, 3, 3, 1, 1)


        self.retranslateUi(transferData)

        QMetaObject.connectSlotsByName(transferData)
    # setupUi

    def retranslateUi(self, transferData):
        transferData.setWindowTitle(QCoreApplication.translate("transferData", u"Form", None))
        self.pushButton.setText(QCoreApplication.translate("transferData", u"Open Files", None))
        self.pushButton_2.setText(QCoreApplication.translate("transferData", u"Open Folders", None))
        self.error_label.setText("")
        self.label_2.setText(QCoreApplication.translate("transferData", u"Options:", None))
        self.overwrite.setText(QCoreApplication.translate("transferData", u"Overwrite existing data", None))
        self.checkBox.setText(QCoreApplication.translate("transferData", u"Download metadata as\n"
"ibridges_metadata.json", None))
        self.label.setText(QCoreApplication.translate("transferData", u"Select data to upload", None))
        self.local_to_irods_button.setText("")
        self.cancel_button.setText(QCoreApplication.translate("transferData", u"Cancel", None))
        self.stop_button.setText(QCoreApplication.translate("transferData", u"Stop", None))
        self.label_3.setText("")
    # retranslateUi


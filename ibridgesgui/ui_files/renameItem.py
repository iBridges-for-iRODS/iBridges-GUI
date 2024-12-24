# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'renameItem.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QLineEdit, QSizePolicy, QTextBrowser,
    QVBoxLayout, QWidget)

class Ui_renameItem(object):
    def setupUi(self, renameItem):
        if not renameItem.objectName():
            renameItem.setObjectName(u"renameItem")
        renameItem.resize(500, 279)
        renameItem.setMinimumSize(QSize(500, 200))
        renameItem.setMaximumSize(QSize(500, 300))
        renameItem.setStyleSheet(u"QWidget\n"
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
        self.verticalLayout = QVBoxLayout(renameItem)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(renameItem)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.item_path_label = QTextBrowser(renameItem)
        self.item_path_label.setObjectName(u"item_path_label")

        self.verticalLayout.addWidget(self.item_path_label)

        self.label_2 = QLabel(renameItem)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.item_path_input = QLineEdit(renameItem)
        self.item_path_input.setObjectName(u"item_path_input")

        self.verticalLayout.addWidget(self.item_path_input)

        self.error_label = QLabel(renameItem)
        self.error_label.setObjectName(u"error_label")
        self.error_label.setStyleSheet(u"")

        self.verticalLayout.addWidget(self.error_label)

        self.buttonBox = QDialogButtonBox(renameItem)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(renameItem)
        self.buttonBox.accepted.connect(renameItem.accept)
        self.buttonBox.rejected.connect(renameItem.reject)

        QMetaObject.connectSlotsByName(renameItem)
    # setupUi

    def retranslateUi(self, renameItem):
        renameItem.setWindowTitle(QCoreApplication.translate("renameItem", u"Rename/Move", None))
        self.label.setText(QCoreApplication.translate("renameItem", u"Rename or move:", None))
        self.label_2.setText(QCoreApplication.translate("renameItem", u"to new location:", None))
        self.error_label.setText("")
    # retranslateUi


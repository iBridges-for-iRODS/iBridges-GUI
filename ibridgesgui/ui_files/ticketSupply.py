# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ticketSupply.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_ticketSupply(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(747, 187)
        Dialog.setStyleSheet(u"QWidget\n"
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
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.ticket_string = QLineEdit(Dialog)
        self.ticket_string.setObjectName(u"ticket_string")

        self.gridLayout.addWidget(self.ticket_string, 0, 1, 1, 1)

        self.irods_path = QLineEdit(Dialog)
        self.irods_path.setObjectName(u"irods_path")

        self.gridLayout.addWidget(self.irods_path, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.error_label = QLabel(Dialog)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout.addWidget(self.error_label)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"iRODS Path", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Ticket", None))
        self.error_label.setText("")
    # retranslateUi


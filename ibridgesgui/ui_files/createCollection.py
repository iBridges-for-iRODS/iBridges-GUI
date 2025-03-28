# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'createCollection.ui'
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
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QTextBrowser, QVBoxLayout, QWidget)

class Ui_createCollection(object):
    def setupUi(self, createCollection):
        if not createCollection.objectName():
            createCollection.setObjectName(u"createCollection")
        createCollection.resize(500, 251)
        createCollection.setMinimumSize(QSize(500, 200))
        createCollection.setMaximumSize(QSize(500, 300))
        createCollection.setStyleSheet(u"QWidget\n"
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
        self.verticalLayout = QVBoxLayout(createCollection)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(createCollection)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QTextBrowser(createCollection)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.label_3 = QLabel(createCollection)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.coll_path_input = QLineEdit(createCollection)
        self.coll_path_input.setObjectName(u"coll_path_input")

        self.verticalLayout.addWidget(self.coll_path_input)

        self.error_label = QLabel(createCollection)
        self.error_label.setObjectName(u"error_label")
        self.error_label.setStyleSheet(u"")

        self.verticalLayout.addWidget(self.error_label)

        self.buttonBox = QDialogButtonBox(createCollection)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(createCollection)
        self.buttonBox.accepted.connect(createCollection.accept)
        self.buttonBox.rejected.connect(createCollection.reject)

        QMetaObject.connectSlotsByName(createCollection)
    # setupUi

    def retranslateUi(self, createCollection):
        createCollection.setWindowTitle(QCoreApplication.translate("createCollection", u"New Collection", None))
        self.label_2.setText(QCoreApplication.translate("createCollection", u"Parent path:", None))
        self.label_3.setText(QCoreApplication.translate("createCollection", u"New name", None))
        self.error_label.setText("")
    # retranslateUi


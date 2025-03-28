# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'irodsLogin.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_irodsLogin(object):
    def setupUi(self, irodsLogin):
        if not irodsLogin.objectName():
            irodsLogin.setObjectName(u"irodsLogin")
        irodsLogin.resize(770, 332)
        irodsLogin.setMinimumSize(QSize(770, 320))
        irodsLogin.setStyleSheet(u"QWidget\n"
"{\n"
"    background-color: rgb(211,211,211);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244)\n"
"}\n"
"\n"
"QLabel#irods_label\n"
"{\n"
"   color: rgb(21, 165, 137)\n"
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
"\n"
"")
        self.gridLayout_2 = QGridLayout(irodsLogin)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_2, 0, 1, 1, 1)

        self.envbox = QComboBox(irodsLogin)
        self.envbox.setObjectName(u"envbox")

        self.gridLayout.addWidget(self.envbox, 3, 2, 1, 2)

        self.password_field = QLineEdit(irodsLogin)
        self.password_field.setObjectName(u"password_field")
        self.password_field.setStyleSheet(u"")
        self.password_field.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.password_field, 6, 2, 1, 2)

        self.label_4 = QLabel(irodsLogin)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 3, 1, 1, 1)

        self.label_3 = QLabel(irodsLogin)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(16777215, 16777215))
        self.label_3.setStyleSheet(u"")

        self.gridLayout.addWidget(self.label_3, 5, 3, 1, 1)

        self.irods_label = QLabel(irodsLogin)
        self.irods_label.setObjectName(u"irods_label")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        self.irods_label.setFont(font)

        self.gridLayout.addWidget(self.irods_label, 1, 1, 1, 1)

        self.label_1 = QLabel(irodsLogin)
        self.label_1.setObjectName(u"label_1")

        self.gridLayout.addWidget(self.label_1, 6, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 2, 1, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.error_label = QLabel(irodsLogin)
        self.error_label.setObjectName(u"error_label")
        self.error_label.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.error_label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cancel_button = QPushButton(irodsLogin)
        self.cancel_button.setObjectName(u"cancel_button")
        font1 = QFont()
        font1.setPointSize(16)
        self.cancel_button.setFont(font1)

        self.horizontalLayout.addWidget(self.cancel_button)

        self.connect_button = QPushButton(irodsLogin)
        self.connect_button.setObjectName(u"connect_button")
        font2 = QFont()
        font2.setPointSize(16)
        font2.setBold(False)
        font2.setItalic(False)
        self.connect_button.setFont(font2)
        self.connect_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.connect_button)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_3, 0, 1, 1, 1)


        self.retranslateUi(irodsLogin)

        self.connect_button.setDefault(True)


        QMetaObject.connectSlotsByName(irodsLogin)
    # setupUi

    def retranslateUi(self, irodsLogin):
        irodsLogin.setWindowTitle(QCoreApplication.translate("irodsLogin", u"Dialog", None))
        self.password_field.setText("")
        self.label_4.setText(QCoreApplication.translate("irodsLogin", u" iRODS environment file:", None))
        self.label_3.setText("")
        self.irods_label.setText(QCoreApplication.translate("irodsLogin", u"iRODS Login", None))
        self.label_1.setText(QCoreApplication.translate("irodsLogin", u"Password", None))
        self.error_label.setText("")
        self.cancel_button.setText(QCoreApplication.translate("irodsLogin", u"Cancel", None))
        self.connect_button.setText(QCoreApplication.translate("irodsLogin", u"Connect", None))
    # retranslateUi


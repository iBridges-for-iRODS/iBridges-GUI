# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configCheck.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_configCheck(object):
    def setupUi(self, configCheck):
        if not configCheck.objectName():
            configCheck.setObjectName(u"configCheck")
        configCheck.resize(1034, 373)
        configCheck.setStyleSheet(u"QWidget\n"
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
        self.verticalLayout_2 = QVBoxLayout(configCheck)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.envbox = QComboBox(configCheck)
        self.envbox.setObjectName(u"envbox")

        self.horizontalLayout.addWidget(self.envbox)

        self.new_button = QPushButton(configCheck)
        self.new_button.setObjectName(u"new_button")

        self.horizontalLayout.addWidget(self.new_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.env_field = QTextEdit(configCheck)
        self.env_field.setObjectName(u"env_field")

        self.verticalLayout.addWidget(self.env_field)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.check_button = QPushButton(configCheck)
        self.check_button.setObjectName(u"check_button")

        self.horizontalLayout_4.addWidget(self.check_button)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.error_label = QLabel(configCheck)
        self.error_label.setObjectName(u"error_label")

        self.horizontalLayout_4.addWidget(self.error_label)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.save_button = QPushButton(configCheck)
        self.save_button.setObjectName(u"save_button")

        self.horizontalLayout_2.addWidget(self.save_button)

        self.save_as_button = QPushButton(configCheck)
        self.save_as_button.setObjectName(u"save_as_button")

        self.horizontalLayout_2.addWidget(self.save_as_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.close_button = QPushButton(configCheck)
        self.close_button.setObjectName(u"close_button")

        self.horizontalLayout_2.addWidget(self.close_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.retranslateUi(configCheck)

        QMetaObject.connectSlotsByName(configCheck)
    # setupUi

    def retranslateUi(self, configCheck):
        configCheck.setWindowTitle(QCoreApplication.translate("configCheck", u"Dialog", None))
        self.new_button.setText(QCoreApplication.translate("configCheck", u"New Config", None))
        self.check_button.setText(QCoreApplication.translate("configCheck", u"Check", None))
        self.error_label.setText("")
        self.save_button.setText(QCoreApplication.translate("configCheck", u"Save", None))
        self.save_as_button.setText(QCoreApplication.translate("configCheck", u"Save as", None))
        self.close_button.setText(QCoreApplication.translate("configCheck", u"Close", None))
    # retranslateUi


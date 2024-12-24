# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ExampleTab.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QTreeView, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(767, 429)
        Form.setStyleSheet(u"QWidget\n"
"{\n"
"	background-color: rgb(54, 54, 54);\n"
"	color: rgb(86, 184, 139);\n"
"    border-color: rgb(217, 174, 23);\n"
"}\n"
"\n"
"QLineEdit\n"
"{\n"
"	background-color: rgb(85, 87, 83);\n"
"	border-color: rgb(217, 174, 23);\n"
"}\n"
"\n"
"QTreeView\n"
"{\n"
"background-color: rgb(85, 87, 83);\n"
"}\n"
"\n"
"QLabel#error_label\n"
"{\n"
"	color: rgb(217, 174, 23);\n"
"}")
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_2)

        self.error_label = QLabel(Form)
        self.error_label.setObjectName(u"error_label")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.error_label)

        self.textField = QLineEdit(Form)
        self.textField.setObjectName(u"textField")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.textField)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout.setItem(1, QFormLayout.FieldRole, self.verticalSpacer)


        self.horizontalLayout.addLayout(self.formLayout)

        self.irodsTreeView = QTreeView(Form)
        self.irodsTreeView.setObjectName(u"irodsTreeView")

        self.horizontalLayout.addWidget(self.irodsTreeView)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"Info Text", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Error Label", None))
        self.error_label.setText("")
    # retranslateUi


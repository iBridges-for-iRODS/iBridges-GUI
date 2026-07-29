# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rescTree.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_rescTree(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(600, 464)
        Dialog.setStyleSheet(u"QWidget\n"
"{\n"
"     background-color: rgb(211,211,211);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244)\n"
"}\n"
"\n"
"QLabel#error_label\n"
"{\n"
"    color: rgb(220, 130, 30);\n"
"}\n"
"\n"
"\n"
"QTreeView\n"
"{\n"
"     background-color: rgb(245, 244, 244)\n"
"}\n"
"\n"
"QPushButton\n"
"{\n"
"	background-color: rgb(21, 165, 137);\n"
"    color: rgb(245, 244, 244);\n"
"}")
        self.horizontalLayout = QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.resc_view = QTreeWidget(Dialog)
        self.resc_view.setObjectName(u"resc_view")

        self.verticalLayout.addWidget(self.resc_view)

        self.error_label = QLabel(Dialog)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout.addWidget(self.error_label)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.ok_button = QPushButton(Dialog)
        self.ok_button.setObjectName(u"ok_button")

        self.verticalLayout_2.addWidget(self.ok_button)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_2)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        ___qtreewidgetitem = self.resc_view.headerItem()
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("Dialog", u"Status", None))
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Dialog", u"Free Space", None))
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Dialog", u"Name (Type)", None))
        self.error_label.setText("")
        self.ok_button.setText(QCoreApplication.translate("Dialog", u"OK", None))
    # retranslateUi


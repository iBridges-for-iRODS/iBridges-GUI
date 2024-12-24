# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'welcome.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QWidget)

class Ui_Welcome(object):
    def setupUi(self, Welcome):
        if not Welcome.objectName():
            Welcome.setObjectName(u"Welcome")
        Welcome.resize(401, 300)
        Welcome.setStyleSheet(u"QWidget\n"
"{\n"
"    background-color: rgb(211,211,211);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244);\n"
"    \n"
"	font: 16pt\n"
"}\n"
"\n"
"QLabel\n"
"{\n"
"  background-color: rgb(211,211,211);\n"
"}\n"
"\n"
"QLabel#error_label\n"
"{\n"
"   color: rgb(220, 130, 30);\n"
"}\n"
"\n"
"QTabBar::tab:top:selected {\n"
"    background-color: rgb(21, 165, 137);\n"
"    color: rgb(88, 88, 90);\n"
"}\n"
"\n"
"")

        self.retranslateUi(Welcome)

        QMetaObject.connectSlotsByName(Welcome)
    # setupUi

    def retranslateUi(self, Welcome):
        Welcome.setWindowTitle(QCoreApplication.translate("Welcome", u"Form", None))
    # retranslateUi


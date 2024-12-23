# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tabLogging.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QTextBrowser,
    QVBoxLayout, QWidget)

class Ui_tabLogging(object):
    def setupUi(self, tabLogging):
        if not tabLogging.objectName():
            tabLogging.setObjectName(u"tabLogging")
        tabLogging.resize(400, 244)
        tabLogging.setStyleSheet(u"QWidget\n"
"{\n"
"    background-color: rgb(211,211,211);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244)\n"
"}\n"
"\n"
"QLabel\n"
"{\n"
"  background-color: rgb(211,211,211);\n"
"}\n"
"\n"
"QTextBrowser\n"
"{\n"
"     background-color: rgb(245, 244, 244)\n"
"}\n"
"")
        self.verticalLayout = QVBoxLayout(tabLogging)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.log_label = QLabel(tabLogging)
        self.log_label.setObjectName(u"log_label")

        self.verticalLayout.addWidget(self.log_label)

        self.log_browser = QTextBrowser(tabLogging)
        self.log_browser.setObjectName(u"log_browser")

        self.verticalLayout.addWidget(self.log_browser)


        self.retranslateUi(tabLogging)

        QMetaObject.connectSlotsByName(tabLogging)
    # setupUi

    def retranslateUi(self, tabLogging):
        tabLogging.setWindowTitle(QCoreApplication.translate("tabLogging", u"Form", None))
        self.log_label.setText(QCoreApplication.translate("tabLogging", u"Log file", None))
    # retranslateUi


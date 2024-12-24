# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'downloadData.ui'
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
    QLabel, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QTextBrowser, QWidget)

class Ui_downloadData(object):
    def setupUi(self, downloadData):
        if not downloadData.objectName():
            downloadData.setObjectName(u"downloadData")
        downloadData.resize(936, 395)
        downloadData.setStyleSheet(u"QWidget\n"
"{\n"
"    background-color: rgb(211,211,211);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244);\n"
"    font: 16pt\n"
"}\n"
"\n"
"QProgressBar::chunk\n"
"{\n"
"  background-color: rgb(21, 165, 137);\n"
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
        self.gridLayout = QGridLayout(downloadData)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.download_button = QPushButton(downloadData)
        self.download_button.setObjectName(u"download_button")

        self.horizontalLayout.addWidget(self.download_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.hide_button = QPushButton(downloadData)
        self.hide_button.setObjectName(u"hide_button")

        self.horizontalLayout.addWidget(self.hide_button)


        self.gridLayout.addLayout(self.horizontalLayout, 8, 1, 1, 1)

        self.metadata = QCheckBox(downloadData)
        self.metadata.setObjectName(u"metadata")

        self.gridLayout.addWidget(self.metadata, 6, 1, 1, 1)

        self.destination_label = QLabel(downloadData)
        self.destination_label.setObjectName(u"destination_label")

        self.gridLayout.addWidget(self.destination_label, 1, 1, 1, 1)

        self.label = QLabel(downloadData)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_3 = QLabel(downloadData)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 2, 1, 1)

        self.label_4 = QLabel(downloadData)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 7, 1, 1, 1)

        self.overwrite = QCheckBox(downloadData)
        self.overwrite.setObjectName(u"overwrite")

        self.gridLayout.addWidget(self.overwrite, 5, 1, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.folder_button = QPushButton(downloadData)
        self.folder_button.setObjectName(u"folder_button")

        self.horizontalLayout_3.addWidget(self.folder_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)

        self.label_5 = QLabel(downloadData)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)

        self.label_2 = QLabel(downloadData)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)

        self.error_label = QLabel(downloadData)
        self.error_label.setObjectName(u"error_label")

        self.gridLayout.addWidget(self.error_label, 12, 0, 1, 4)

        self.source_browser = QTextBrowser(downloadData)
        self.source_browser.setObjectName(u"source_browser")

        self.gridLayout.addWidget(self.source_browser, 3, 1, 1, 1)

        self.progress_bar = QProgressBar(downloadData)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)

        self.gridLayout.addWidget(self.progress_bar, 9, 1, 1, 1)


        self.retranslateUi(downloadData)

        QMetaObject.connectSlotsByName(downloadData)
    # setupUi

    def retranslateUi(self, downloadData):
        downloadData.setWindowTitle(QCoreApplication.translate("downloadData", u"Download", None))
        self.download_button.setText(QCoreApplication.translate("downloadData", u"Download", None))
        self.hide_button.setText(QCoreApplication.translate("downloadData", u"Close window", None))
        self.metadata.setText(QCoreApplication.translate("downloadData", u"Download metadata as ibridges_metadata.json", None))
        self.destination_label.setText("")
        self.label.setText(QCoreApplication.translate("downloadData", u"Download to:", None))
        self.label_3.setText("")
        self.label_4.setText("")
        self.overwrite.setText(QCoreApplication.translate("downloadData", u"Overwrite existing data", None))
        self.folder_button.setText(QCoreApplication.translate("downloadData", u"Open Folders", None))
        self.label_5.setText(QCoreApplication.translate("downloadData", u"Downloading", None))
        self.label_2.setText(QCoreApplication.translate("downloadData", u"Options:", None))
        self.error_label.setText("")
    # retranslateUi


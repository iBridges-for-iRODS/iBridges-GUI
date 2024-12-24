# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'uploadData.ui'
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

class Ui_uploadData(object):
    def setupUi(self, uploadData):
        if not uploadData.objectName():
            uploadData.setObjectName(u"uploadData")
        uploadData.resize(936, 395)
        uploadData.setStyleSheet(u"QWidget\n"
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
        self.gridLayout = QGridLayout(uploadData)
        self.gridLayout.setObjectName(u"gridLayout")
        self.destination_label = QLabel(uploadData)
        self.destination_label.setObjectName(u"destination_label")

        self.gridLayout.addWidget(self.destination_label, 2, 2, 1, 1)

        self.overwrite = QCheckBox(uploadData)
        self.overwrite.setObjectName(u"overwrite")

        self.gridLayout.addWidget(self.overwrite, 3, 2, 1, 1)

        self.label_5 = QLabel(uploadData)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)

        self.label_4 = QLabel(uploadData)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 3, 1, 1)

        self.label_3 = QLabel(uploadData)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 4, 1, 1)

        self.label = QLabel(uploadData)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(uploadData)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.folder_button = QPushButton(uploadData)
        self.folder_button.setObjectName(u"folder_button")

        self.horizontalLayout_3.addWidget(self.folder_button)

        self.file_button = QPushButton(uploadData)
        self.file_button.setObjectName(u"file_button")

        self.horizontalLayout_3.addWidget(self.file_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 2, 1, 1)

        self.error_label = QLabel(uploadData)
        self.error_label.setObjectName(u"error_label")

        self.gridLayout.addWidget(self.error_label, 9, 0, 1, 6)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.upload_button = QPushButton(uploadData)
        self.upload_button.setObjectName(u"upload_button")

        self.horizontalLayout.addWidget(self.upload_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.hide_button = QPushButton(uploadData)
        self.hide_button.setObjectName(u"hide_button")

        self.horizontalLayout.addWidget(self.hide_button)


        self.gridLayout.addLayout(self.horizontalLayout, 4, 2, 1, 1)

        self.sources_list = QTextBrowser(uploadData)
        self.sources_list.setObjectName(u"sources_list")

        self.gridLayout.addWidget(self.sources_list, 1, 2, 1, 1)

        self.progress_bar = QProgressBar(uploadData)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)

        self.gridLayout.addWidget(self.progress_bar, 5, 2, 1, 1)


        self.retranslateUi(uploadData)

        QMetaObject.connectSlotsByName(uploadData)
    # setupUi

    def retranslateUi(self, uploadData):
        uploadData.setWindowTitle(QCoreApplication.translate("uploadData", u"Upload", None))
        self.destination_label.setText("")
        self.overwrite.setText(QCoreApplication.translate("uploadData", u"Overwrite existing data", None))
        self.label_5.setText(QCoreApplication.translate("uploadData", u"Uploading to", None))
        self.label_4.setText("")
        self.label_3.setText("")
        self.label.setText(QCoreApplication.translate("uploadData", u"Upload data", None))
        self.label_2.setText(QCoreApplication.translate("uploadData", u"Options:", None))
        self.folder_button.setText(QCoreApplication.translate("uploadData", u"Select Folders", None))
        self.file_button.setText(QCoreApplication.translate("uploadData", u"Select Files", None))
        self.error_label.setText("")
        self.upload_button.setText(QCoreApplication.translate("uploadData", u"Upload", None))
        self.hide_button.setText(QCoreApplication.translate("uploadData", u"Close Window", None))
    # retranslateUi


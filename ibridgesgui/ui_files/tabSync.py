# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tabSync.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QTreeView, QVBoxLayout,
    QWidget)

class Ui_tabSync(object):
    def setupUi(self, tabSync):
        if not tabSync.objectName():
            tabSync.setObjectName(u"tabSync")
        tabSync.resize(1234, 749)
        tabSync.setStyleSheet(u"QWidget\n"
"{\n"
"    background-color: rgb(211,211,211);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244)\n"
"}\n"
"\n"
"QProgressBar::chunk\n"
"{\n"
"  background-color: rgb(21, 165, 137);\n"
"  width: 5px;\n"
"}\n"
"\n"
"QLabel#error_label\n"
"{\n"
"    color: rgb(220, 130, 30);\n"
"}\n"
"\n"
"QLineEdit, QTextEdit, QTableWidget, QTreeView\n"
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
"QPushButton#local_to_irods_button, QPushButton#irods_to_local_button\n"
"{\n"
"    background-color: rgb(211,211,211);\n"
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
        self.layoutWidget = QWidget(tabSync)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 1231, 771))
        self.verticalLayout_11 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.label_19 = QLabel(self.layoutWidget)
        self.label_19.setObjectName(u"label_19")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.label_19.setFont(font)
        self.label_19.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.label_19)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.create_dir_button = QPushButton(self.layoutWidget)
        self.create_dir_button.setObjectName(u"create_dir_button")

        self.horizontalLayout_13.addWidget(self.create_dir_button)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_13.addWidget(self.label)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_9)


        self.verticalLayout_5.addLayout(self.horizontalLayout_13)

        self.local_fs_tree = QTreeView(self.layoutWidget)
        self.local_fs_tree.setObjectName(u"local_fs_tree")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.local_fs_tree.sizePolicy().hasHeightForWidth())
        self.local_fs_tree.setSizePolicy(sizePolicy1)
        self.local_fs_tree.setStyleSheet(u"")
        self.local_fs_tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.local_fs_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.local_fs_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.local_fs_tree.setHeaderHidden(True)

        self.verticalLayout_5.addWidget(self.local_fs_tree)

        self.verticalLayout_5.setStretch(2, 1)

        self.horizontalLayout_5.addLayout(self.verticalLayout_5)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_11)

        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalSpacer_21 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_21)

        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.local_to_irods_button = QPushButton(self.layoutWidget)
        self.local_to_irods_button.setObjectName(u"local_to_irods_button")
        self.local_to_irods_button.setMinimumSize(QSize(100, 0))
        icon = QIcon()
        icon.addFile(u"../icons/arrow-right.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.local_to_irods_button.setIcon(icon)
        self.local_to_irods_button.setIconSize(QSize(50, 50))

        self.gridLayout_7.addWidget(self.local_to_irods_button, 0, 1, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_3, 0, 2, 1, 1)

        self.irods_to_local_button = QPushButton(self.layoutWidget)
        self.irods_to_local_button.setObjectName(u"irods_to_local_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.irods_to_local_button.sizePolicy().hasHeightForWidth())
        self.irods_to_local_button.setSizePolicy(sizePolicy2)
        self.irods_to_local_button.setMinimumSize(QSize(100, 0))
        icon1 = QIcon()
        icon1.addFile(u"../icons/arrow-left.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.irods_to_local_button.setIcon(icon1)
        self.irods_to_local_button.setIconSize(QSize(50, 50))

        self.gridLayout_7.addWidget(self.irods_to_local_button, 3, 1, 1, 1)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_12, 0, 0, 1, 1)

        self.verticalSpacer_11 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.gridLayout_7.addItem(self.verticalSpacer_11, 1, 1, 1, 1)


        self.verticalLayout_15.addLayout(self.gridLayout_7)

        self.verticalSpacer_12 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_12)


        self.horizontalLayout_5.addLayout(self.verticalLayout_15)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_13)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.label_20 = QLabel(self.layoutWidget)
        self.label_20.setObjectName(u"label_20")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy3)
        self.label_20.setFont(font)
        self.label_20.setTextFormat(Qt.PlainText)
        self.label_20.setAlignment(Qt.AlignCenter)

        self.verticalLayout_16.addWidget(self.label_20)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_14)

        self.create_coll_button = QPushButton(self.layoutWidget)
        self.create_coll_button.setObjectName(u"create_coll_button")

        self.horizontalLayout_15.addWidget(self.create_coll_button)


        self.verticalLayout_16.addLayout(self.horizontalLayout_15)

        self.irods_tree = QTreeView(self.layoutWidget)
        self.irods_tree.setObjectName(u"irods_tree")
        sizePolicy1.setHeightForWidth(self.irods_tree.sizePolicy().hasHeightForWidth())
        self.irods_tree.setSizePolicy(sizePolicy1)
        self.irods_tree.setStyleSheet(u"")
        self.irods_tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.irods_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.irods_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.irods_tree.setHeaderHidden(True)

        self.verticalLayout_16.addWidget(self.irods_tree)

        self.verticalLayout_16.setStretch(2, 1)

        self.horizontalLayout_5.addLayout(self.verticalLayout_16)

        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(4, 1)

        self.verticalLayout_11.addLayout(self.horizontalLayout_5)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_11.addItem(self.verticalSpacer)

        self.error_label = QLabel(self.layoutWidget)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout_11.addWidget(self.error_label)

        self.progress_bar = QProgressBar(self.layoutWidget)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)

        self.verticalLayout_11.addWidget(self.progress_bar)

        self.verticalSpacer_13 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.verticalLayout_11.addItem(self.verticalSpacer_13)

        self.diff_table = QTableWidget(self.layoutWidget)
        if (self.diff_table.columnCount() < 3):
            self.diff_table.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.diff_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.diff_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.diff_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.diff_table.setObjectName(u"diff_table")
        self.diff_table.setMinimumSize(QSize(0, 300))
        self.diff_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.diff_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.verticalLayout_11.addWidget(self.diff_table)

        self.sync_button = QPushButton(self.layoutWidget)
        self.sync_button.setObjectName(u"sync_button")

        self.verticalLayout_11.addWidget(self.sync_button)

        self.verticalSpacer_2 = QSpacerItem(20, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_11.addItem(self.verticalSpacer_2)


        self.retranslateUi(tabSync)

        QMetaObject.connectSlotsByName(tabSync)
    # setupUi

    def retranslateUi(self, tabSync):
        tabSync.setWindowTitle(QCoreApplication.translate("tabSync", u"Form", None))
        self.label_19.setText(QCoreApplication.translate("tabSync", u"LOCAL", None))
        self.create_dir_button.setText(QCoreApplication.translate("tabSync", u"Create Folder", None))
        self.label.setText("")
        self.local_to_irods_button.setText("")
        self.irods_to_local_button.setText("")
        self.label_20.setText(QCoreApplication.translate("tabSync", u"IRODS", None))
        self.create_coll_button.setText(QCoreApplication.translate("tabSync", u"Create Collection", None))
        self.error_label.setText("")
        ___qtablewidgetitem = self.diff_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("tabSync", u"Source", None));
        ___qtablewidgetitem1 = self.diff_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("tabSync", u"Destination", None));
        ___qtablewidgetitem2 = self.diff_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("tabSync", u"Size in Bytes", None));
        self.sync_button.setText(QCoreApplication.translate("tabSync", u"Synchronise", None))
    # retranslateUi


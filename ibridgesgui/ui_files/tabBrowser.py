# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tabBrowser.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QComboBox,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTableWidget, QTableWidgetItem, QTextBrowser,
    QVBoxLayout, QWidget)

class Ui_tabBrowser(object):
    def setupUi(self, tabBrowser):
        if not tabBrowser.objectName():
            tabBrowser.setObjectName(u"tabBrowser")
        tabBrowser.resize(1278, 843)
        tabBrowser.setStyleSheet(u"QWidget\n"
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
        self.verticalLayout = QVBoxLayout(tabBrowser)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_13 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.verticalLayout.addItem(self.verticalSpacer_13)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(tabBrowser)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.input_path = QLineEdit(tabBrowser)
        self.input_path.setObjectName(u"input_path")
        self.input_path.setFont(font)
        self.input_path.setStyleSheet(u"")
        self.input_path.setEchoMode(QLineEdit.Normal)
        self.input_path.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.input_path, 0, 1, 1, 1)

        self.refresh_button = QPushButton(tabBrowser)
        self.refresh_button.setObjectName(u"refresh_button")
        icon = QIcon()
        icon.addFile(u"../icons/refresh.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.refresh_button.setIcon(icon)

        self.gridLayout.addWidget(self.refresh_button, 0, 2, 1, 1)

        self.parent_button = QPushButton(tabBrowser)
        self.parent_button.setObjectName(u"parent_button")
        self.parent_button.setEnabled(True)
        icon1 = QIcon()
        icon1.addFile(u"../icons/arrow-up.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.parent_button.setIcon(icon1)

        self.gridLayout.addWidget(self.parent_button, 0, 3, 1, 1)

        self.home_button = QPushButton(tabBrowser)
        self.home_button.setObjectName(u"home_button")
        icon2 = QIcon()
        icon2.addFile(u"../icons/home.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.home_button.setIcon(icon2)

        self.gridLayout.addWidget(self.home_button, 0, 4, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")

        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.create_coll_button = QPushButton(tabBrowser)
        self.create_coll_button.setObjectName(u"create_coll_button")

        self.horizontalLayout_5.addWidget(self.create_coll_button)

        self.rename_button = QPushButton(tabBrowser)
        self.rename_button.setObjectName(u"rename_button")

        self.horizontalLayout_5.addWidget(self.rename_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_2)

        self.upload_button = QPushButton(tabBrowser)
        self.upload_button.setObjectName(u"upload_button")

        self.horizontalLayout_5.addWidget(self.upload_button)

        self.download_button = QPushButton(tabBrowser)
        self.download_button.setObjectName(u"download_button")

        self.horizontalLayout_5.addWidget(self.download_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.delete_button = QPushButton(tabBrowser)
        self.delete_button.setObjectName(u"delete_button")

        self.horizontalLayout_5.addWidget(self.delete_button)


        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.browser_table = QTableWidget(tabBrowser)
        if (self.browser_table.columnCount() < 6):
            self.browser_table.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setText(u"Status");
        self.browser_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.browser_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.browser_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.browser_table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.browser_table.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.browser_table.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.browser_table.setObjectName(u"browser_table")
        self.browser_table.setMinimumSize(QSize(0, 250))
        self.browser_table.setStyleSheet(u"")
        self.browser_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.browser_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.browser_table.setTabKeyNavigation(False)
        self.browser_table.setProperty(u"showDropIndicator", False)
        self.browser_table.setDragDropOverwriteMode(False)
        self.browser_table.setAlternatingRowColors(False)
        self.browser_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.browser_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.browser_table.setSortingEnabled(False)
        self.browser_table.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.browser_table)

        self.verticalSpacer_12 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.verticalLayout.addItem(self.verticalSpacer_12)

        self.info_tabs = QTabWidget(tabBrowser)
        self.info_tabs.setObjectName(u"info_tabs")
        self.info_tabs.setStyleSheet(u"")
        self.metadata = QWidget()
        self.metadata.setObjectName(u"metadata")
        self.horizontalLayout = QHBoxLayout(self.metadata)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.meta_table = QTableWidget(self.metadata)
        if (self.meta_table.columnCount() < 3):
            self.meta_table.setColumnCount(3)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.meta_table.setHorizontalHeaderItem(0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.meta_table.setHorizontalHeaderItem(1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.meta_table.setHorizontalHeaderItem(2, __qtablewidgetitem8)
        self.meta_table.setObjectName(u"meta_table")
        self.meta_table.setMinimumSize(QSize(600, 200))
        self.meta_table.setStyleSheet(u"")
        self.meta_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.meta_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.meta_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.meta_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.meta_table.setSortingEnabled(True)

        self.horizontalLayout.addWidget(self.meta_table)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.add_meta_button = QPushButton(self.metadata)
        self.add_meta_button.setObjectName(u"add_meta_button")
        self.add_meta_button.setFont(font)

        self.gridLayout_2.addWidget(self.add_meta_button, 11, 2, 1, 1)

        self.meta_units_field = QLineEdit(self.metadata)
        self.meta_units_field.setObjectName(u"meta_units_field")

        self.gridLayout_2.addWidget(self.meta_units_field, 7, 2, 1, 1)

        self.label_5 = QLabel(self.metadata)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 5, 2, 1, 1)

        self.meta_key_field = QLineEdit(self.metadata)
        self.meta_key_field.setObjectName(u"meta_key_field")

        self.gridLayout_2.addWidget(self.meta_key_field, 7, 0, 1, 1)

        self.delete_meta_button = QPushButton(self.metadata)
        self.delete_meta_button.setObjectName(u"delete_meta_button")
        self.delete_meta_button.setFont(font)

        self.gridLayout_2.addWidget(self.delete_meta_button, 13, 2, 1, 1)

        self.meta_value_field = QLineEdit(self.metadata)
        self.meta_value_field.setObjectName(u"meta_value_field")

        self.gridLayout_2.addWidget(self.meta_value_field, 7, 1, 1, 1)

        self.label_4 = QLabel(self.metadata)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 5, 0, 1, 1)

        self.label_3 = QLabel(self.metadata)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)

        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)

        self.update_meta_button = QPushButton(self.metadata)
        self.update_meta_button.setObjectName(u"update_meta_button")
        self.update_meta_button.setFont(font)

        self.gridLayout_2.addWidget(self.update_meta_button, 12, 2, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_3, 8, 2, 1, 1)

        self.label_6 = QLabel(self.metadata)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 5, 1, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout_2)

        self.info_tabs.addTab(self.metadata, "")
        self.preview = QWidget()
        self.preview.setObjectName(u"preview")
        self.preview.setFont(font)
        self.preview.setAutoFillBackground(False)
        self.verticalLayout_2 = QVBoxLayout(self.preview)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.preview_browser = QTextBrowser(self.preview)
        self.preview_browser.setObjectName(u"preview_browser")

        self.verticalLayout_2.addWidget(self.preview_browser)

        self.info_tabs.addTab(self.preview, "")
        self.permissions = QWidget()
        self.permissions.setObjectName(u"permissions")
        self.horizontalLayout_2 = QHBoxLayout(self.permissions)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.acl_table = QTableWidget(self.permissions)
        if (self.acl_table.columnCount() < 4):
            self.acl_table.setColumnCount(4)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.acl_table.setHorizontalHeaderItem(0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.acl_table.setHorizontalHeaderItem(1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.acl_table.setHorizontalHeaderItem(2, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.acl_table.setHorizontalHeaderItem(3, __qtablewidgetitem12)
        self.acl_table.setObjectName(u"acl_table")
        self.acl_table.setMinimumSize(QSize(600, 200))
        self.acl_table.setStyleSheet(u"")
        self.acl_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.acl_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.acl_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.acl_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.acl_table.setSortingEnabled(True)

        self.horizontalLayout_2.addWidget(self.acl_table)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_11 = QLabel(self.permissions)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font)

        self.gridLayout_4.addWidget(self.label_11, 0, 0, 1, 1)

        self.label_13 = QLabel(self.permissions)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_4.addWidget(self.label_13, 4, 0, 1, 1)

        self.label_8 = QLabel(self.permissions)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_4.addWidget(self.label_8, 4, 1, 1, 1)

        self.label_10 = QLabel(self.permissions)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_4.addWidget(self.label_10, 4, 2, 1, 1)

        self.label_7 = QLabel(self.permissions)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_4.addWidget(self.label_7, 4, 3, 1, 1)

        self.acl_user_field = QLineEdit(self.permissions)
        self.acl_user_field.setObjectName(u"acl_user_field")

        self.gridLayout_4.addWidget(self.acl_user_field, 6, 0, 1, 1)

        self.acl_zone_field = QLineEdit(self.permissions)
        self.acl_zone_field.setObjectName(u"acl_zone_field")

        self.gridLayout_4.addWidget(self.acl_zone_field, 6, 1, 1, 1)

        self.acl_box = QComboBox(self.permissions)
        self.acl_box.addItem("")
        self.acl_box.addItem("")
        self.acl_box.addItem("")
        self.acl_box.addItem("")
        self.acl_box.setObjectName(u"acl_box")
        self.acl_box.setEnabled(False)

        self.gridLayout_4.addWidget(self.acl_box, 6, 2, 1, 1)

        self.recursive_box = QComboBox(self.permissions)
        self.recursive_box.addItem("")
        self.recursive_box.addItem("")
        self.recursive_box.setObjectName(u"recursive_box")
        self.recursive_box.setEnabled(False)

        self.gridLayout_4.addWidget(self.recursive_box, 6, 3, 1, 1)

        self.add_acl_button = QPushButton(self.permissions)
        self.add_acl_button.setObjectName(u"add_acl_button")
        self.add_acl_button.setFont(font)

        self.gridLayout_4.addWidget(self.add_acl_button, 6, 4, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_2, 8, 0, 1, 1)

        self.owner = QLabel(self.permissions)
        self.owner.setObjectName(u"owner")

        self.gridLayout_4.addWidget(self.owner, 9, 0, 1, 1)

        self.owner_label = QLabel(self.permissions)
        self.owner_label.setObjectName(u"owner_label")

        self.gridLayout_4.addWidget(self.owner_label, 9, 1, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout_4)

        self.info_tabs.addTab(self.permissions, "")
        self.replicas = QWidget()
        self.replicas.setObjectName(u"replicas")
        self.horizontalLayout_3 = QHBoxLayout(self.replicas)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.replica_table = QTableWidget(self.replicas)
        if (self.replica_table.columnCount() < 5):
            self.replica_table.setColumnCount(5)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.replica_table.setHorizontalHeaderItem(0, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.replica_table.setHorizontalHeaderItem(1, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.replica_table.setHorizontalHeaderItem(2, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.replica_table.setHorizontalHeaderItem(3, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.replica_table.setHorizontalHeaderItem(4, __qtablewidgetitem17)
        self.replica_table.setObjectName(u"replica_table")
        self.replica_table.setStyleSheet(u"")
        self.replica_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.replica_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.replica_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.replica_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.replica_table.setSortingEnabled(True)

        self.horizontalLayout_3.addWidget(self.replica_table)

        self.info_tabs.addTab(self.replicas, "")

        self.verticalLayout.addWidget(self.info_tabs)

        self.no_meta_label = QLabel(tabBrowser)
        self.no_meta_label.setObjectName(u"no_meta_label")

        self.verticalLayout.addWidget(self.no_meta_label)

        self.error_label = QLabel(tabBrowser)
        self.error_label.setObjectName(u"error_label")
        self.error_label.setStyleSheet(u"")

        self.verticalLayout.addWidget(self.error_label)


        self.retranslateUi(tabBrowser)

        self.info_tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(tabBrowser)
    # setupUi

    def retranslateUi(self, tabBrowser):
        tabBrowser.setWindowTitle(QCoreApplication.translate("tabBrowser", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("tabBrowser", u"iRODS path: ", None))
        self.input_path.setText(QCoreApplication.translate("tabBrowser", u"/zoneName/home/user", None))
        self.input_path.setPlaceholderText("")
        self.refresh_button.setText("")
        self.parent_button.setText("")
        self.home_button.setText("")
        self.create_coll_button.setText(QCoreApplication.translate("tabBrowser", u"Create Collection", None))
        self.rename_button.setText(QCoreApplication.translate("tabBrowser", u"Rename/Move", None))
        self.upload_button.setText(QCoreApplication.translate("tabBrowser", u"Upload", None))
        self.download_button.setText(QCoreApplication.translate("tabBrowser", u"Download", None))
        self.delete_button.setText(QCoreApplication.translate("tabBrowser", u"Delete", None))
        ___qtablewidgetitem = self.browser_table.horizontalHeaderItem(1)
        ___qtablewidgetitem.setText(QCoreApplication.translate("tabBrowser", u"Name", None));
        ___qtablewidgetitem1 = self.browser_table.horizontalHeaderItem(2)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("tabBrowser", u"Size [bytes]", None));
        ___qtablewidgetitem2 = self.browser_table.horizontalHeaderItem(3)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("tabBrowser", u"Checksum/Fingerprint", None));
        ___qtablewidgetitem3 = self.browser_table.horizontalHeaderItem(4)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("tabBrowser", u"Created", None));
        ___qtablewidgetitem4 = self.browser_table.horizontalHeaderItem(5)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("tabBrowser", u"Modified", None));
        ___qtablewidgetitem5 = self.meta_table.horizontalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("tabBrowser", u"Key", None));
        ___qtablewidgetitem6 = self.meta_table.horizontalHeaderItem(1)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("tabBrowser", u"Value", None));
        ___qtablewidgetitem7 = self.meta_table.horizontalHeaderItem(2)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("tabBrowser", u"Units", None));
        self.add_meta_button.setText(QCoreApplication.translate("tabBrowser", u"Add", None))
        self.label_5.setText(QCoreApplication.translate("tabBrowser", u"Units", None))
        self.delete_meta_button.setText(QCoreApplication.translate("tabBrowser", u"Delete", None))
        self.label_4.setText(QCoreApplication.translate("tabBrowser", u"Key", None))
        self.label_3.setText(QCoreApplication.translate("tabBrowser", u"Edit", None))
        self.update_meta_button.setText(QCoreApplication.translate("tabBrowser", u"Update", None))
        self.label_6.setText(QCoreApplication.translate("tabBrowser", u"Value", None))
        self.info_tabs.setTabText(self.info_tabs.indexOf(self.metadata), QCoreApplication.translate("tabBrowser", u"Metadata", None))
        self.info_tabs.setTabText(self.info_tabs.indexOf(self.preview), QCoreApplication.translate("tabBrowser", u"Preview", None))
        ___qtablewidgetitem8 = self.acl_table.horizontalHeaderItem(0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("tabBrowser", u"User", None));
        ___qtablewidgetitem9 = self.acl_table.horizontalHeaderItem(1)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("tabBrowser", u"Zone", None));
        ___qtablewidgetitem10 = self.acl_table.horizontalHeaderItem(2)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("tabBrowser", u"Access", None));
        ___qtablewidgetitem11 = self.acl_table.horizontalHeaderItem(3)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("tabBrowser", u"Inherit", None));
        self.label_11.setText(QCoreApplication.translate("tabBrowser", u"Edit", None))
        self.label_13.setText(QCoreApplication.translate("tabBrowser", u"User name", None))
        self.label_8.setText(QCoreApplication.translate("tabBrowser", u"Zone", None))
        self.label_10.setText(QCoreApplication.translate("tabBrowser", u"Access", None))
        self.label_7.setText(QCoreApplication.translate("tabBrowser", u"Apply to all\n"
"in collection", None))
        self.acl_box.setItemText(0, QCoreApplication.translate("tabBrowser", u"read", None))
        self.acl_box.setItemText(1, QCoreApplication.translate("tabBrowser", u"write", None))
        self.acl_box.setItemText(2, QCoreApplication.translate("tabBrowser", u"own", None))
        self.acl_box.setItemText(3, QCoreApplication.translate("tabBrowser", u"delete", None))

        self.recursive_box.setItemText(0, QCoreApplication.translate("tabBrowser", u"False", None))
        self.recursive_box.setItemText(1, QCoreApplication.translate("tabBrowser", u"True", None))

        self.add_acl_button.setText(QCoreApplication.translate("tabBrowser", u"Add/Update", None))
        self.owner.setText(QCoreApplication.translate("tabBrowser", u"Owner: ", None))
        self.owner_label.setText("")
        self.info_tabs.setTabText(self.info_tabs.indexOf(self.permissions), QCoreApplication.translate("tabBrowser", u"Permissions", None))
        ___qtablewidgetitem12 = self.replica_table.horizontalHeaderItem(0)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("tabBrowser", u"Replica", None));
        ___qtablewidgetitem13 = self.replica_table.horizontalHeaderItem(1)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("tabBrowser", u"Hierarchy", None));
        ___qtablewidgetitem14 = self.replica_table.horizontalHeaderItem(2)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("tabBrowser", u"Checksum", None));
        ___qtablewidgetitem15 = self.replica_table.horizontalHeaderItem(3)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("tabBrowser", u"Size [bytes]", None));
        ___qtablewidgetitem16 = self.replica_table.horizontalHeaderItem(4)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("tabBrowser", u"Status", None));
        self.info_tabs.setTabText(self.info_tabs.indexOf(self.replicas), QCoreApplication.translate("tabBrowser", u"Replicas", None))
        self.no_meta_label.setText("")
        self.error_label.setText("")
    # retranslateUi


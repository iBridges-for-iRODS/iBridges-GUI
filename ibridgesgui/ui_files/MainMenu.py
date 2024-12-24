# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainMenu.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1300, 850)
        MainWindow.setMinimumSize(QSize(1300, 850))
        icon = QIcon()
        icon.addFile(u"../icons/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"QWidget\n"
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
        MainWindow.setIconSize(QSize(400, 400))
        self.action_close_session = QAction(MainWindow)
        self.action_close_session.setObjectName(u"action_close_session")
        font = QFont()
        self.action_close_session.setFont(font)
        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName(u"action_exit")
        self.action_exit.setFont(font)
        self.actionSearch = QAction(MainWindow)
        self.actionSearch.setObjectName(u"actionSearch")
        self.actionSearch.setFont(font)
        self.actionSaveConfig = QAction(MainWindow)
        self.actionSaveConfig.setObjectName(u"actionSaveConfig")
        self.actionSaveConfig.setFont(font)
        self.action_connect = QAction(MainWindow)
        self.action_connect.setObjectName(u"action_connect")
        self.action_check_configuration = QAction(MainWindow)
        self.action_check_configuration.setObjectName(u"action_check_configuration")
        self.action_add_configuration = QAction(MainWindow)
        self.action_add_configuration.setObjectName(u"action_add_configuration")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tab_widget = QTabWidget(self.centralwidget)
        self.tab_widget.setObjectName(u"tab_widget")
        self.tab_widget.setMinimumSize(QSize(600, 500))
        font1 = QFont()
        font1.setPointSize(16)
        font1.setBold(False)
        font1.setItalic(False)
        self.tab_widget.setFont(font1)
        self.tab_widget.setUsesScrollButtons(True)

        self.verticalLayout.addWidget(self.tab_widget)

        self.error_label = QLabel(self.centralwidget)
        self.error_label.setObjectName(u"error_label")

        self.verticalLayout.addWidget(self.error_label)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1300, 24))
        self.menubar.setFont(font1)
        self.main_menu = QMenu(self.menubar)
        self.main_menu.setObjectName(u"main_menu")
        self.main_menu.setFont(font1)
        self.config_menu = QMenu(self.menubar)
        self.config_menu.setObjectName(u"config_menu")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.main_menu.menuAction())
        self.menubar.addAction(self.config_menu.menuAction())
        self.main_menu.addAction(self.action_connect)
        self.main_menu.addAction(self.action_close_session)
        self.main_menu.addAction(self.action_exit)
        self.config_menu.addAction(self.action_check_configuration)
        self.config_menu.addAction(self.action_add_configuration)

        self.retranslateUi(MainWindow)

        self.tab_widget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_close_session.setText(QCoreApplication.translate("MainWindow", u"Close Connection", None))
        self.action_exit.setText(QCoreApplication.translate("MainWindow", u"Exit iBridges", None))
        self.actionSearch.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.actionSaveConfig.setText(QCoreApplication.translate("MainWindow", u"Save configuration", None))
        self.action_connect.setText(QCoreApplication.translate("MainWindow", u"Connect to iRODS", None))
        self.action_check_configuration.setText(QCoreApplication.translate("MainWindow", u"Check Configuration", None))
        self.action_add_configuration.setText(QCoreApplication.translate("MainWindow", u"Add Configuration", None))
        self.error_label.setText("")
        self.main_menu.setTitle(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.config_menu.setTitle(QCoreApplication.translate("MainWindow", u"Configure", None))
    # retranslateUi


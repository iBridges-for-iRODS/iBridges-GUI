# Form implementation generated from reading ui file 'ibridgesgui/ui_files/tabLogging.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_tabLogging(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 244)
        Form.setStyleSheet("QWidget\n"
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
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.log_label = QtWidgets.QLabel(parent=Form)
        self.log_label.setObjectName("log_label")
        self.verticalLayout.addWidget(self.log_label)
        self.log_browser = QtWidgets.QTextBrowser(parent=Form)
        self.log_browser.setObjectName("log_browser")
        self.verticalLayout.addWidget(self.log_browser)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.log_label.setText(_translate("Form", "Log file"))
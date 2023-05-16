#!/usr/bin/env python3
"""iBridges GUI startup script.

"""
import datetime
import logging
import logging.handlers
import os
import setproctitle
import sys
import json

import irods.exception
import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic

import gui
import irodsConnector
import utils

# Global constants
LOG_LEVEL = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}
THIS_APPLICATION = 'iBridges'

# Application globals
app = PyQt6.QtWidgets.QApplication(sys.argv)
widget = PyQt6.QtWidgets.QStackedWidget()

# Work around a PRC XML issue handling special characters
os.environ['PYTHON_IRODSCLIENT_DEFAULT_XML'] = 'QUASI_XML'


class IrodsLoginWindow(PyQt6.QtWidgets.QDialog,
                       gui.ui_files.irodsLoginConfigEditor.Ui_irodsLoginConfigEditor):
    """Definition and initialization of the iRODS login window.

    """
    icommands = False
    this_application = ''
    context = utils.context.Context()

    def __init__(self):
        super().__init__()
        self.irods_path = utils.path.LocalPath(utils.context.IRODS_DIR).expanduser()
        self._load_gui()
        self._init_envbox()
        self._init_password()

        # inits for config editing
        self._ibridgesconf_display()
        self._irodsconf_display()

    def _load_gui(self):
        """

        """
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi("gui/ui_files/irodsLoginConfigEditor.ui", self)
        self.connectButton.clicked.connect(self.login_function)
        self.ticketButton.clicked.connect(self.ticket_login)
        self.passwordField.setEchoMode(PyQt6.QtWidgets.QLineEdit.EchoMode.Password)
        # config editing
        self.saveConfig.clicked.connect(self.saveConfigs)
        self.ienvAdd.clicked.connect(self.ienvAddLine)
        self.ibridgesAdd.clicked.connect(self.ibridgesAddLine)
        self.ienvDel.clicked.connect(self.ienvDelLine)
        self.ibridgesDel.clicked.connect(self.ibridgesDelLine)

    def _init_envbox(self):
        """Populate environment drop-down.

        """
        env_jsons = [
            path.name for path in
            self.irods_path.glob('irods_environment*json')]
        if len(env_jsons) == 0:
            self.envError.setText(f'ERROR: no "irods_environment*json" files found in {self.irods_path}')
        self.envbox.clear()
        self.envbox.addItems(env_jsons)
        envname = ''
        if 'last_ienv' in self.context.ibridges_configuration.config and \
                self.context.ibridges_configuration.config['last_ienv'] in env_jsons:
            envname = self.context.ibridges_configuration.config['last_ienv']
        elif 'irods_environment.json' in env_jsons:
            envname = 'irods_environment.json'
        index = 0
        if envname:
            index = self.envbox.findText(envname)
        self.envbox.setCurrentIndex(index)

    def _init_password(self):
        """

        """
        if self.context.irods_connector.password:
            self.passwordField.setText(self.context.irods_connector.password)

    def _reset_mouse_and_error_labels(self):
        """Reset cursor and clear error text

        """
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        self.passError.setText('')
        self.envError.setText('')

    def setup_standard(self):
        """Check the state of the radio button for using the pure Python
        client.

        """
        if self.standardButton.isChecked():
            self._init_envbox()
            self.icommands = False

    def setup_icommands(self):
        """Check the state of the radio button for using iCommands.
        This includes a check for the existance of the iCommands on the
        current system.

        """
        if self.selectIcommandsButton.isChecked():
            self.icommandsError.setText('')
            if self.conn.icommands:
                self.icommands = True
                # TODO support arbitrary iRODS environment file for iCommands
            else:
                self.icommandsError.setText('ERROR: no iCommands found')
                self.standardButton.setChecked(True)

    def login_function(self):
        """Check connectivity and log in to iRODS handling common errors.

        """
        # Replacement connector (required for new sessions)
        if not self.context.irods_connector:
            logging.debug('Setting new instance of the IrodsConnector')
            self.context.irods_connector = irodsConnector.manager.IrodsConnector()
        irods_env_file = self.irods_path.joinpath(self.envbox.currentText())
        self.context.irods_env_file = irods_env_file
        logging.debug(f'IRODS ENVIRONMENT FILE SET: {irods_env_file.name}')
        self.envError.setText('')
        if not (self.context.irods_environment.config and self.context.ienv_is_complete()):
            message = 'iRODS environment missing or incomplete.'
            logging.error(message)
            self.context.irods_environment.reset()
            self.passError.clear()
            self.envError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        if not utils.utils.can_connect(self.context.irods_environment.config.get('irods_host', '')):
            message = 'No network connection to server'
            logging.warning(message)
            self.envError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.WaitCursor))
        self.context.ibridges_configuration.config['last_ienv'] = irods_env_file.name
        self.context.save_ibridges_configuration()
        password = self.passwordField.text()
        self.context.irods_connector.password = password
        logging.debug(f'IRODS PASSWORD SET: {"*"*len(password)*2}')
        try:
            self.context.irods_connector.irods_env_file = self.context.irods_env_file
            self.context.irods_connector.irods_environment = self.context.irods_environment
            self.context.irods_connector.ibridges_configuration = self.context.ibridges_configuration
            self.context.irods_connector.connect()
        except (irods.exception.CAT_INVALID_AUTHENTICATION,
                irods.exception.PAM_AUTH_PASSWORD_FAILED,
                irods.exception.CAT_INVALID_USER,
                ConnectionRefusedError):
            message = 'Wrong password!  Try again'
            logging.error(message)
            self.envError.clear()
            self.passError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        except irods.exception.CAT_PASSWORD_EXPIRED:
            message = 'Cached password expired!  Re-enter password'
            logging.error(message)
            self.envError.clear()
            self.passError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        except irods.exception.NetworkException:
            message = 'iRODS server down!  Check and try again'
            logging.error(message)
            self.passError.clear()
            self.envError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        except Exception as unknown:
            message = f'Something unexpected occurred: {unknown!r}'
            logging.exception(message)
            self.envError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        # widget is a global variable
        browser = gui.mainmenu.mainmenu(widget)
        if len(widget) == 1:
            widget.addWidget(browser)
        self._reset_mouse_and_error_labels()
        widget.setCurrentIndex(widget.currentIndex()+1)

    def ticket_login(self):
        """Log in to iRODS using a ticket.

        """
        # widget is a global variable
        browser = gui.mainmenu.mainmenu(widget)
        browser.menuOptions.clear()
        browser.menuOptions.deleteLater()
        if len(widget) == 1:
            widget.addWidget(browser)
        self._reset_mouse_and_error_labels()
        # self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        widget.setCurrentIndex(widget.currentIndex()+1)

    # Config edit functionality
    def _table_to_json(self, table):
        dictionary = {}
        for row in range(table.rowCount()):
            key = table.item(row, 0).text()
            val = table.item(row, 1).text()
            if key == '' or val == '':
                continue
            
            if val.isnumeric():
                dictionary[key] = int(val)
            elif val.lower() == "true":
                dictionary[key] = True
            elif val.lower() == "false":
                dictionary[key] = False
            elif ',' in val:
                val = val.replace('[', "").replace(']', "")
                val = val.replace("'", "").replace('"', "")
                val = val.replace(" ", "")
                dictionary[key] = val.split(',')
            else:
                dictionary[key] = val
        return dictionary

    def _check_irods_keys(self, irodsDict):
        mandatory_keys = ['irods_host', 'irods_port', 'irods_user_name', 'irods_zone_name']
        for key, val in irodsDict.items():
            if key not in utils.irods_config_keys.irods_config_keys:
                self.configErrorLabel.setText(f"iRODS config ERROR: {key} is not an iRODS key")
                return False
            
        if set(mandatory_keys).issubset(irodsDict.keys()):
            return True
        else:
            self.configErrorLabel.setText(f"iRODS config ERROR: Ay least one is missing or not set {mandatory_keys}")
            return False

    def saveConfigs(self):
        self.configErrorLabel.clear()
        keys = utils.irods_config_keys.irods_config_keys
        ibridgesDict = self._table_to_json(self.ibridgesDisplay)
        irodsDict = self._table_to_json(self.irodsDisplay)
        message = ''
        if irodsDict:
            success = self._check_irods_keys(irodsDict)
            if success:
                with open(self.irods_path.joinpath(self.envbox.currentText()), 'w') as f:
                    f.write(json.dumps(irodsDict, indent = 0))
                    message = f'iRODS conf written to {self.irods_path.joinpath(self.envbox.currentText())}'
            else: 
                return
        else: 
            return

        if ibridgesDict:
            for key, val in ibridgesDict.items():
                self.context.ibridges_configuration.config[key] = val
            self.context.save_ibridges_configuration()
            message = message + f'\nibridges conf written to {self.context.ibridges_conf_file}'
        
        self.configErrorLabel.setText(message)

    def ienvAddLine(self):
        currentRowCount = self.irodsDisplay.rowCount()
        self.irodsDisplay.insertRow(currentRowCount)
        self.irodsDisplay.setItem(currentRowCount, 0, PyQt6.QtWidgets.QTableWidgetItem(""))
        self.irodsDisplay.setItem(currentRowCount, 1, PyQt6.QtWidgets.QTableWidgetItem(""))

    def ibridgesAddLine(self):
        currentRowCount = self.ibridgesDisplay.rowCount()
        self.ibridgesDisplay.insertRow(currentRowCount)
        self.ibridgesDisplay.setItem(currentRowCount, 0, PyQt6.QtWidgets.QTableWidgetItem(""))
        self.ibridgesDisplay.setItem(currentRowCount, 1, PyQt6.QtWidgets.QTableWidgetItem(""))

    def ienvDelLine(self):
        selected = self.irodsDisplay.selectedIndexes()
        if selected:
            idx = selected[0]
            self.irodsDisplay.removeRow(idx.row())

    def ibridgesDelLine(self):
        selected = self.ibridgesDisplay.selectedIndexes()
        if selected:
            idx = selected[0]
            self.ibridgesDisplay.removeRow(idx.row())

    def _ibridgesconf_display(self):
        self.ibridgesDisplay.setRowCount(len(self.context.ibridges_configuration.config.keys()))
        self.ibridgesDisplay.setColumnWidth(0, 200)
        self.ibridgesDisplay.setColumnWidth(1, 200)
        for row, key in enumerate(self.context.ibridges_configuration.config):
            self.ibridgesDisplay.setItem(row, 0, PyQt6.QtWidgets.QTableWidgetItem(key))
            self.ibridgesDisplay.setItem(
                    row, 1, 
                    PyQt6.QtWidgets.QTableWidgetItem(str(
                        self.context.ibridges_configuration.config[key])))

    def _irodsconf_display(self):
        temp_ienv_file = self.irods_path.joinpath(self.envbox.currentText())
        print(temp_ienv_file)
        if not os.path.isfile(temp_ienv_file):
            temp_ienv_file = os.path.join(temp_ienv_file, 'irods_environment.json')
            print("generate empty irods_environment.json")
            with open(temp_ienv_file, 'w') as ienv:
                ienv.write("{}")
            self._init_envbox()
        temp_ienv = utils.json_config.JsonConfig(temp_ienv_file)
        print(temp_ienv)
        self.irodsDisplay.setRowCount(len(temp_ienv.config))
        self.irodsDisplay.setColumnWidth(0, 200)
        self.irodsDisplay.setColumnWidth(1, 200)
        
        for row, key in enumerate(temp_ienv.config):
            self.irodsDisplay.setItem(row, 0, PyQt6.QtWidgets.QTableWidgetItem(key))
            self.irodsDisplay.setItem(row, 1, 
                                      PyQt6.QtWidgets.QTableWidgetItem(str(temp_ienv.config[key])))

def closeClean():

    context = utils.context.Context()
    if context.irods_connector:
        context.irods_connector.cleanup()

def main():
    """Main function

    """
    # Initialize logger first because Context may want to log as well.
    logdir = utils.path.LocalPath(utils.context.IBRIDGES_DIR).expanduser()
    utils.utils.init_logger(logdir, THIS_APPLICATION)
    # Singleton Context
    context = utils.context.Context()
    context.application_name = THIS_APPLICATION
    # Context is required to get the log_level from the configuration.
    verbose = context.ibridges_configuration.config.get('verbose', 'info')
    log_level = LOG_LEVEL.get(verbose, logging.INFO)
    utils.utils.set_log_level(log_level)
    context.irods_connector = irodsConnector.manager.IrodsConnector()
    setproctitle.setproctitle(context.application_name)
    login_window = IrodsLoginWindow()
    login_window.this_application = context.application_name
    widget.addWidget(login_window)
    widget.show()
    # app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(closeClean)
    app.exec()


if __name__ == "__main__":
    main()

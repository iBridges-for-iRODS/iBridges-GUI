#!/usr/bin/env python3
"""iBridges GUI startup script.

"""
import logging
import os
import setproctitle
import sys

import irods.exception
import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic

import gui
import irodsConnector
import utils

# Global constants
THIS_APPLICATION = 'iBridges'

# Application globals
app = PyQt6.QtWidgets.QApplication(sys.argv)
stacked_widget = PyQt6.QtWidgets.QStackedWidget()

# Work around a PRC XML issue handling special characters
os.environ['PYTHON_IRODSCLIENT_DEFAULT_XML'] = 'QUASI_XML'


class IrodsLoginWindow(PyQt6.QtWidgets.QDialog,
                       gui.ui_files.irodsLogin.Ui_irodsLogin):
    """The login widget.

    """
    cached_password = ''
    given_password = ''
    use_icommands = None
    this_application = ''
    context = utils.context.Context()

    def __init__(self):
        """Initialize the iRODS login window.

        """
        super().__init__()
        self.irods_path = utils.path.LocalPath(utils.context.IRODS_DIR).expanduser()
        self._load_gui()
        self._init_envbox()
        self._init_password()

    def _load_gui(self):
        """Initialize and connect the GUI elements.

        """
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi("gui/ui_files/irodsLogin.ui", self)
        self.selectIcommandsButton.toggled.connect(self.setup_icommands)
        self.standardButton.toggled.connect(self.setup_standard)
        self.connectButton.clicked.connect(self.login_function)
        self.ticketButton.clicked.connect(self.ticket_login)
        self.passwordField.setEchoMode(PyQt6.QtWidgets.QLineEdit.EchoMode.Password)

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
        """Store this initial cached password scraped from auth file and
        set it to the password field so the user sees that previous
        login credentials have been found.

        """
        self.cached_password = self.context.irods_connector.password
        self.passwordField.setText(self.cached_password)

    def reset_mouse_and_error_labels(self):
        """Reset cursor and clear any error text.

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
            self.use_icommands = False

    def setup_icommands(self):
        """Check the state of the radio button for using iCommands.
        This includes a check for the existence of the iCommands on the
        current system.

        """
        # TODO support arbitrary iRODS environment file for iCommands
        if self.selectIcommandsButton.isChecked():
            self.icommandsError.setText('')
            if self.context.irods_connector.icommands.has_icommands:
                self.use_icommands = True
            else:
                self.use_icommands = False
                self.icommandsError.setText('ERROR: no iCommands found')
                self.standardButton.setChecked(True)
            logging.debug('self.use_icommands=%s', self.use_icommands)

    def login_function(self):
        """Check connectivity and log in to iRODS handling common errors.

        The initial and subsequent sessions need to be handled
        differently.  Store the initial given password to see when the
        user has entered a new one.

        """
        irods_env_file = self.irods_path.joinpath(self.envbox.currentText())
        self.context.irods_env_file = irods_env_file
        logging.debug('IRODS ENVIRONMENT FILE SET: %s', irods_env_file.name)
        self.envError.setText('')
        if not (self.context.irods_environment.config and self.context.ienv_is_complete()):
            message = 'iRODS environment missing or incomplete.'
            logging.error(message)
            self.envError.setText(message)
            self.context.irods_environment.reset()
            self.passError.clear()
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        irods_host = self.context.irods_environment.config.get('irods_host', '')
        irods_port = self.context.irods_environment.config.get('irods_port', '')
        if not utils.utils.can_connect(irods_host, irods_port):
            message = 'No network connection to server: %s:%s'
            logging.warning(message, irods_host, irods_port)
            self.envError.setText(message % (irods_host, irods_port))
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.WaitCursor))
        self.context.irods_connector.use_icommands = self.use_icommands
        self.context.ibridges_configuration.config['last_ienv'] = irods_env_file.name
        self.context.save_ibridges_configuration()
        current_password = self.passwordField.text()
        known_passwords = (self.cached_password, self.given_password)
        # This a subsequent session if `given_password` is already set.
        if self.given_password and current_password in known_passwords:
            self.given_password = self.cached_password
        else:
            self.given_password = current_password
        self.context.irods_connector.password = self.given_password
        logging.debug('IRODS PASSWORD SET')
        self.context.irods_connector.irods_env_file = self.context.irods_env_file
        self.context.irods_connector.irods_environment = self.context.irods_environment
        self.context.irods_connector.ibridges_configuration = self.context.ibridges_configuration
        try:
            self.context.irods_connector.connect()
        except (irods.exception.CAT_INVALID_AUTHENTICATION,
                irods.exception.PAM_AUTH_PASSWORD_FAILED,
                irods.exception.CAT_INVALID_USER,
                ConnectionRefusedError):
            message = 'Wrong password!  Try again'
            logging.error(message)
            self.passError.setText(message)
            self.envError.clear()
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        except irods.exception.CAT_PASSWORD_EXPIRED:
            message = 'Cached password expired!  Re-enter password'
            logging.error(message)
            self.passError.setText(message)
            self.envError.clear()
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        except irods.exception.NetworkException:
            message = 'iRODS server down!  Check and try again'
            logging.error(message)
            self.envError.setText(message)
            self.passError.clear()
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        except Exception as error:
            message = 'Something unexpected occurred: %r'
            logging.error(message, error)
            self.envError.setText(message % error)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        # stacked_widget is a global variable
        browser = gui.mainmenu.MainMenu(stacked_widget)
        if len(stacked_widget) == 1:
            stacked_widget.addWidget(browser)
        self.reset_mouse_and_error_labels()
        stacked_widget.setCurrentIndex(stacked_widget.currentIndex()+1)

    def ticket_login(self):
        """Log in to iRODS using a ticket.

        """
        # stacked_widget is a global variable
        browser = gui.mainmenu.MainMenu(stacked_widget)
        browser.menuOptions.clear()
        browser.menuOptions.deleteLater()
        if len(stacked_widget) == 1:
            stacked_widget.addWidget(browser)
        self.reset_mouse_and_error_labels()
        # self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        stacked_widget.setCurrentIndex(stacked_widget.currentIndex()+1)


def close_clean():
    """Clean up connections in preparation to close application.

    """
    context = utils.context.Context()
    if context.irods_connector:
        context.irods_connector.cleanup()


def main():
    """Main function.

    Initialize the context singleton, create the login widget, and
    execute the main application thread.

    """
    # Initialize logger first because Context may want to log as well.
    utils.utils.init_logger(THIS_APPLICATION)
    # Singleton Context
    context = utils.context.Context()
    # Context is required to get the log_level from the configuration.
    # Here, it is taken from the configuration if not specified.
    utils.utils.set_log_level()
    context.application_name = THIS_APPLICATION
    context.irods_connector = irodsConnector.manager.IrodsConnector()
    setproctitle.setproctitle(context.application_name)
    login_window = IrodsLoginWindow()
    login_window.this_application = context.application_name
    stacked_widget.addWidget(login_window)
    stacked_widget.show()
    # app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(close_clean)
    app.exec()


if __name__ == "__main__":
    main()

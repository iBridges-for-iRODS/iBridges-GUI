"""Main menu window definition.

"""
import logging
import sys

import PyQt6
import PyQt6.QtCore
import PyQt6.QtWidgets
import PyQt6.uic

import gui
import utils


# TODO why define this here?  It is only used for the IrodsUpDownload
#      widget, and the logger is a singleton!  Can/should it be moved?
class QPlainTextEditLogger(logging.Handler, PyQt6.QtCore.QObject):
    """A (hopefully) thread safe log handler.

    """
    appendPlainText = PyQt6.QtCore.pyqtSignal(str)

    def __init__(self, widget: PyQt6.QtWidgets.QPlainTextEdit):
        """Initialize the log handler

        Parameters
        ----------
        widget : PyQt6.QtWidgets.QPlainTextEdit

        """

        super().__init__()
        PyQt6.QtCore.QObject.__init__(self)
        self.widget = widget
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendPlainText)

    def emit(self, record: logging.LogRecord):
        """Pass `record` to all connected slots.

        Parameters
        ----------
        record : logging.LogRecord

        """
        msg = self.format(record)
        self.appendPlainText.emit(msg)


class MainMenu(PyQt6.QtWidgets.QMainWindow,
               gui.ui_files.MainMenu.Ui_MainWindow,
               utils.context.ContextContainer):
    """Main menu widget.

    The main window where all tabs reside.  It is "stacked" on top of
    the login widget.

    """
    tab_ticket_access = None
    tab_amber_workflow = None
    tab_browser = None
    tab_up_download = None
    tab_eln_data = None
    tab_data_bundle = None
    tab_create_ticket = None
    tab_info = None

    def __init__(self, stacked_widget: PyQt6.QtWidgets.QStackedWidget):
        """Initialize the main window.

        This widget is stacked "on top of" the IrodsLoginWindow widget,
        both part of the `stacked_widget` defined as a global in the
        module defining the IrodsLoginWindow widget.

        Parameters
        ----------
        stacked_widget : PyQt6.QtWidgets.QStackedWidget
            Widget container holding top-level widgets, of which _this_
            widget is one.

        """
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi('gui/ui_files/MainMenu.ui', self)
        self.stacked_widget = stacked_widget
        # Menu actions
        self.actionExit.triggered.connect(self.program_exit)
        self.actionCloseSession.triggered.connect(self.close_session)
        if not self.ienv or not self.context.irods_connector:
            self.actionSearch.setEnabled(False)
            # self.actionSaveConfig.setEnabled(False)
            self.tab_ticket_access = gui.irodsTicketLogin.irodsTicketLogin()
            self.tabWidget.addTab(self.tab_ticket_access, 'Ticket Access')
        else:
            self.actionSearch.triggered.connect(self.search)
            self.actionSaveConfig.setEnabled(False)
            # self.actionSaveConfig.triggered.connect(self.saveConfig)
            # self.actionExportMetadata.triggered.connect(self.exportMeta)
            ui_tabs_lookup = {
                'tabAmberWorkflow': self.setup_tab_amber_workflow,
                'tabBrowser': self.setup_tab_browser,
                'tabCreateTicket': self.setup_tab_create_ticket,
                'tabDataBundle': self.setup_tab_data_bundle,
                'tabELNData': self.setup_tab_eln_data,
                'tabInfo': self.setup_tab_info,
                'tabUpDownload': self.setup_tab_up_download,
            }
            found = self.conf.get('ui_tabs', [])
            # Ensure browser and info always are shown.
            if 'tabBrowser' not in found:
                found.insert(0, 'tabBrowser')
            if 'tabInfo' not in found:
                found.append('tabInfo')
            expected = ui_tabs_lookup.keys()
            # TODO the browser tabs can take a while.  Use async to
            #      load other tabs at the same time?
            # Load tabs in the order the user has placed them in their
            # configuration.
            for uitab in found:
                if uitab in expected:
                    ui_tabs_lookup[uitab]()
                    logging.debug('Setup the %s tab', uitab)
                else:
                    logging.error(
                        'Unknown tab "%s" defined in iBridges config file', uitab)
                    logging.info(
                        'Only %s tabs supported', ", ".join(expected))
        self.tabWidget.setCurrentIndex(0)

    def setup_tab_amber_workflow(self):
        """Add AmberScript tab to the stacked tab widget.

        """
        self.tab_amber_workflow = gui.amberWorkflow.amberWorkflow()
        self.tabWidget.addTab(self.tab_amber_workflow, "AmberScript Connection")

    def setup_tab_browser(self):
        """Add browser tab to the stacked tab widget.

        This tab is required to support a search.

        """
        self.tab_browser = gui.IrodsBrowser.IrodsBrowser()
        self.tabWidget.addTab(self.tab_browser, 'Browser')

    def setup_tab_create_ticket(self):
        """Add ticket creation tab to the stacked tab widget.

        """
        self.tab_create_ticket = gui.irodsCreateTicket.irodsCreateTicket()
        self.tabWidget.addTab(self.tab_create_ticket, "Create access tokens")

    def setup_tab_data_bundle(self):
        """Add data bundling tab to the stacked tab widget.

        """
        self.tab_data_bundle = gui.IrodsDataBundle.IrodsDataBundle()
        self.tabWidget.addTab(self.tab_data_bundle, "Compress/bundle data")

    def setup_tab_eln_data(self):
        """Add ELN tab to the stacked tab widget.

        """
        self.tab_eln_data = gui.elabUpload.elabUpload()
        self.tabWidget.addTab(self.tab_eln_data, "ELN Data upload")

    def setup_tab_info(self):
        """Add session information tab to the stacked tab widget.

        """
        self.tab_info = gui.irodsInfo.irodsInfo()
        self.tabWidget.addTab(self.tab_info, "Info")

    def setup_tab_up_download(self):
        """Add data transfer tab to the stacked tab widget.

        """
        self.tab_up_download = gui.IrodsUpDownload.IrodsUpDownload()
        self.tabWidget.addTab(self.tab_up_download, "Data Transfers")
        # TODO why a log handler for only this widget?
        log_handler = QPlainTextEditLogger(self.tab_up_download.logs)
        logging.getLogger().addHandler(log_handler)

    # Connect functions
    def program_exit(self):
        """Exit confirmation and cleanup.

        """
        quit_msg = "Are you sure you want to exit the program?"
        reply = PyQt6.QtWidgets.QMessageBox.question(
            self, 'Message', quit_msg,
            PyQt6.QtWidgets.QMessageBox.StandardButton.Yes,
            PyQt6.QtWidgets.QMessageBox.StandardButton.No)
        if reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
            # connector must be destroyed directly, not a reference to it.
            if self.context.irods_connector:
                del self.context.irods_connector
            elif self.tab_ticket_access and self.tab_ticket_access.conn:
                self.tab_ticket_access.conn.close_session()
            sys.exit()
        else:
            pass

    def close_session(self):
        """Session cleanup.

        """
        quit_msg = "Are you sure you want to disconnect?"
        reply = PyQt6.QtWidgets.QMessageBox.question(
            self, 'Message', quit_msg,
            PyQt6.QtWidgets.QMessageBox.StandardButton.Yes,
            PyQt6.QtWidgets.QMessageBox.StandardButton.No)
        if reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
            if self.context.irods_connector:
                self.context.reset()
            elif self.tab_ticket_access and self.tab_ticket_access.conn:
                self.tab_ticket_access.conn.close_session()
            current_widget = self.stacked_widget.currentWidget()
            self.stacked_widget.setCurrentIndex(self.stacked_widget.currentIndex() - 1)
            self.stacked_widget.removeWidget(current_widget)
            # TODO why does this cause a crash?
            # currentWidget = self.stacked_widget.currentWidget()
            # currentWidget._init_envbox()
        else:
            pass

    def search(self):
        """Open search dialog widget.

        """
        search = gui.irodsSearch.irodsSearch(self.tab_browser.collTable)
        search.exec()

    def save_config(self):
        """Save iBridges configuration.

        """
        logging.warning('iBridges configuration cannot yet be saved.')
        # raise NotImplemented('iBridges configuration cannot yet be saved.')

    def export_meta(self):
        """Export metadata.

        """
        logging.warning('Metadata cannot yet be exported')
        # raise NotImplemented('Metadata cannot yet be exported')

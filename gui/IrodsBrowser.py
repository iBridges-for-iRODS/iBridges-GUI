"""Browser tab.

"""
import logging
import sys

import irods.exception
import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic

from ibridges import get_collection, get_dataobject
from ibridges import IrodsPath
from ibridges.data_operations import obj_replicas
from ibridges.meta import MetaData
from ibridges.permissions import Permissions

import gui
from gui.gui_utils import populate_table, get_irods_item

class IrodsBrowser(PyQt6.QtWidgets.QWidget,
                   gui.ui_files.tabBrowser.Ui_tabBrowser):
    """Browser view for iRODS session.

    """

    def __init__(self, session):
        """Initialize an iRODS browser view.

        """
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi("gui/ui_files/tabBrowser.ui", self)

        self.session = session
        self.current_browser_row = -1
        self.viewTabs.setCurrentIndex(0)
        
        # iRODS default home
        if self.session.home is not None:
            root_path = self.session.home
        else:
            root_path = f'/{self.session.zone}/home/{self.session.username}'
        try:
            self.root_coll = get_collection(self.session, root_path)
        except irods.exception.CollectionDoesNotExist:
            self.root_coll = get_collection(self.session, f'/{self.session.zone}/home')
        except irods.exception.NetworkException:
            self.errorLabel.setText(
                'iRODS NETWORK ERROR: No Connection, please check network')
        except:
            self.errorLabel.setText('Cannot set root collection. Set "irods_home" in your environment.json')
        self.resetPath()
        self.browse()


    def browse(self):
        """Initialize browser view GUI elements.
            Defines the signals and slots.
        """
        # Main navigation elements
        self.inputPath.returnPressed.connect(self.loadBrowserTable)
        self.refreshButton.clicked.connect(self.loadBrowserTable)
        self.homeButton.clicked.connect(self.resetPath)
        self.parentButton.clicked.connect(self.setParent)

        # Main manipulation buttons Upload/Download create collection
        #self.UploadButton.clicked.connect(self.fileUpload)
        #self.DownloadButton.clicked.connect(self.fileDownload)
        #self.createCollButton.clicked.connect(self.createCollection)
        
        # Browser table behaviour
        self.browserTable.doubleClicked.connect(self.updatePath)
        self.browserTable.clicked.connect(self.fillInfo)

        # Bottom tab view buttons
        # Metadata
        self.metadataTable.clicked.connect(self.edit_metadata)
        self.metaAddButton.clicked.connect(self.addIcatMeta)
        self.metaUpdateButton.clicked.connect(self.setIcatMeta)
        self.metaDeleteButton.clicked.connect(self.deleteIcatMeta)
        # ACLs
        self.aclTable.clicked.connect(self.edit_acl)
        self.aclAddButton.clicked.connect(self.update_icat_acl)
        # Delete        
        #self.dataDeleteButton.clicked.connect(self.deleteData)
        #self.loadDeleteSelectionButton.clicked.connect(self.loadSelection)


    def resetPath(self):
        """Reset browser table to root path"""
        self.inputPath.setText(self.root_coll.path)
        self.loadBrowserTable()


    def setParent(self):
        """Set browser path to parent of current collection and update browser table"""
        current_path = IrodsPath(self.session, self.inputPath.text())
        self.inputPath.setText(str(current_path.parent))
        self.loadBrowserTable()


    # @PyQt6.QtCore.pyqtSlot(PyQt6.QtCore.QModelIndex)
    def updatePath(self, index):
        """Takes path from inputPath and loads browser table"""
        self._clear_error_label()
        row = index.row()
        irods_path = self._get_object_path(row)
        if irods_path.collection_exists():
            self.inputPath.setText(str(irods_path))
            self.loadBrowserTable()


    def loadBrowserTable(self):
        """Loads main browser table"""
        self._clear_error_label()
        self._clear_view_tabs()
        obj_path = IrodsPath(self.session, self.inputPath.text())
        if obj_path.collection_exists():
            try:
                coll = get_collection(self.session, obj_path)

                coll_data = [('C-', subcoll.name, '', '',
                                subcoll.create_time.strftime('%d-%m-%Y'),
                                subcoll.modify_time.strftime('%d-%m-%Y %H:%m'))
                                for subcoll in coll.subcollections]
                obj_data = [(max(repl[4] for repl in obj_replicas(obj)),
                             obj.name, str(obj.size),
                             obj.checksum, obj.create_time.strftime('%d-%m-%Y'),
                             obj.modify_time.strftime('%d-%m-%Y %H:%m'))
                             for obj in coll.data_objects]

                populate_table(self.browserTable,
                                len(coll.data_objects)+len(coll.subcollections),
                                coll_data+obj_data)
                self.browserTable.resizeColumnsToContents()
            except Exception as e:
                self.browserTable.setRowCount(0)
                self.errorLabel.setText(repr(e))
        else:
            self.browserTable.setRowCount(0)
            self.errorLabel.setText("Collection does not exist.")


    def fillInfo(self, index):
        """Fill lower tabs with info"""
        self._clear_error_label()
        self._clear_view_tabs()
        self.metadataTable.setRowCount(0)
        self.aclTable.setRowCount(0)
        self.replicaTable.setRowCount(0)
        self.current_browser_row = self.browserTable.currentRow()
        irods_path = self._get_object_path(self.browserTable.currentRow())
        self._clear_view_tabs()
        try:
            self._fill_preview_tab(irods_path)
            self._fill_metadata_tab(irods_path)
            self._fill_acls_tab(irods_path)
            self._fill_replicas_tab(irods_path)
        except Exception as error:
            logging.error('Browser', exc_info=True)
            self.errorLabel.setText(repr(error))


    def setIcatMeta(self):
        try:
            self._metadata_edits("set")
        except Exception as error:
            self.errorLabel.setText(repr(error))

    def addIcatMeta(self):
        try:
            self._metadata_edits("add")
        except Exception as error:
            self.errorLabel.setText(repr(error))

    def deleteIcatMeta(self):
        try:
            self._metadata_edits("delete")
        except Exception as error:
            self.errorLabel.setText(repr(error))


    # @PyQt6.QtCore.pyqtSlot(PyQt6.QtCore.QModelIndex)
    def edit_metadata(self, index):
        self._clear_error_label()
        self.metaValueField.clear()
        self.metaUnitsField.clear()
        row = index.row()
        key = self.metadataTable.item(row, 0).text()
        value = self.metadataTable.item(row, 1).text()
        if self.metadataTable.item(row, 2):
            units = self.metadataTable.item(row, 2).text()
        else:
            units = ""
        self.metaKeyField.setText(key)
        self.metaValueField.setText(value)
        self.metaUnitsField.setText(units)

    # @PyQt6.QtCore.pyqtSlot(PyQt6.QtCore.QModelIndex)
    def edit_acl(self, index):
        self._clear_error_label()
        self.aclUserField.clear()
        self.aclZoneField.clear()
        self.aclBox.setCurrentText('')
        row = index.row()
        user_name = self.aclTable.item(row, 0).text()
        user_zone = self.aclTable.item(row, 1).text()
        acc_name = self.aclTable.item(row, 2).text()
        self.aclUserField.setText(user_name)
        self.aclZoneField.setText(user_zone)
        self.aclBox.setCurrentText(acc_name)


    def update_icat_acl(self):
        self.errorLabel.clear()
        if self.current_browser_row == -1:
            self.errorLabel.setText('Please select an object first!')
            return
        irods_path = self._get_object_path(self.current_browser_row)
        user_name = self.aclUserField.text()
        user_zone = self.aclZoneField.text()
        acc_name = self.aclBox.currentText()

        if acc_name in ('inherit', 'noinherit'):
            if irods_path.dataobject_exists():
                self.errorLabel.setText(
                    'WARNING: (no)inherit is not applicable to data objects')
                return
        elif user_name is "":
            self.errorLabel.setText("Please provide a user.")
            return
        elif acc_name == "":
            self.errorLabel.setText("Please provide an access level from the menu.")
            return
        recursive = self.recurseBox.currentText() == 'True'
        try:
            item = get_irods_item(irods_path)
            perm = Permissions(self.session, item)
            perm.set(perm=acc_name, user=user_name, zone=user_zone, recursive=recursive)
            self._fill_acls_tab(irods_path)
        except Exception as error:
            self.errorLabel.setText(repr(error))

# Internal functions
    def _clear_error_label(self):
        """Clear any error text."""
        self.errorLabel.clear()

    def _clear_view_tabs(self):
        """Clear the tabs view."""
        self.aclTable.setRowCount(0)
        self.metadataTable.setRowCount(0)
        self.replicaTable.setRowCount(0)
        self.previewBrowser.clear()

    def _fill_replicas_tab(self, irods_path):
        """Populate the table in the Replicas tab with the details of
        the replicas of the selected data object.

        Parameters
        ----------
        obj_path : str
            Path of iRODS collection or data object selected.

        """
        self.replicaTable.setRowCount(0)
        if irods_path.dataobject_exists():
            obj = get_dataobject(self.session, irods_path)
            populate_table(self.replicaTable, len(obj_replicas(obj)), obj_replicas(obj))
            self.replicaTable.setRowCount(len(obj.replicas))
        self.replicaTable.resizeColumnsToContents()

    def _fill_acls_tab(self, irods_path):
        """Populate the table in the ACLs tab.

        Parameters
        ----------
        obj_path : str
            Path of iRODS collection or data object selected.

        """
        self.aclTable.setRowCount(0)
        self.aclUserField.clear()
        self.aclZoneField.clear()
        self.aclBox.setCurrentText('')
        obj = None
        if irods_path.collection_exists():
            obj = get_collection(self.session, irods_path)
            inheritance = f'{obj.inheritance}'
        elif irods_path.dataobject_exists():
            obj = get_dataobject(self.session, irods_path)
            inheritance = ''
        if obj is not None:
            acls = Permissions(self.session, obj)
            acl_data = [(p.user_name, p.user_zone, p.access_name, inheritance) 
                        for p in acls]
            
            populate_table(self.aclTable, len(list(acls.__iter__())), acl_data)
        self.aclTable.resizeColumnsToContents()
        self.owner_label.setText(f'{obj.owner_name}')

    def _fill_metadata_tab(self, irods_path):
        """Populate the table in the metadata tab.

        Parameters
        ----------
        obj_path : str
            Full name of iRODS collection or data object selected.

        """
        self.metaKeyField.clear()
        self.metaValueField.clear()
        self.metaUnitsField.clear()
        item = None
        if irods_path.collection_exists():
            item = get_collection(self.session, irods_path)
        elif irods_path.dataobject_exists():
            item = get_dataobject(self.session, irods_path)
        if item is not None:
            meta = MetaData(item)
            populate_table(self.metadataTable, len(list(meta.__iter__())), meta)
        self.metadataTable.resizeColumnsToContents()

    def _fill_preview_tab(self, irods_path):
        """Populate the table in the metadata tab.

        Parameters
        ----------
        obj_path : str
            Full name of iRODS collection or data object selected.

        """
        if irods_path.collection_exists():
            obj = get_collection(self.session, irods_path)
            content = ['Collections:', '-----------------']
            content.extend([sc.name for sc in obj.subcollections])
            content.extend(['\n', 'DataObjects:', '-----------------'])
            content.extend([do.name for do in obj.data_objects])
            preview_string = '\n'.join(content)
            self.previewBrowser.append(preview_string)
        elif irods_path.dataobject_exists():
            obj = get_dataobject(self.session, irods_path)
            file_type = irods_path.parts[-1].split('.')[1]
            if file_type in ['txt', 'json', 'csv']:
                try:
                    with obj.open('r') as objfd:
                        preview_string = objfd.read(1024).decode('utf-8')
                    self.previewBrowser.append(preview_string)
                except Exception as error:
                    self.previewBrowser.append(
                        f'No Preview for: {irods_path}')
                    self.previewBrowser.append(repr(error))
                    self.previewBrowser.append(
                        "Storage resource might be down.")
            else:
                self.previewBrowser.append(
                    f'No Preview for: {irods_path}')

    def _get_object_path(self, row):
        #if table was populated from a search
        if self.browserTable.item(row, 1).text().startswith("/"+self.session.zone):
            sub_paths = self.browserTable.item(row, 1).text().strip("/").split("/")
            obj_path = "/"+"/".join(sub_paths[:len(sub_paths)-1])
            obj_name = sub_paths[-1]
        #if tables input path is valid
        else:
            obj_path = self.inputPath.text()
            obj_name = self.browserTable.item(row, 1).text()
        return IrodsPath(self.session, obj_path, obj_name)

    def _get_selected_objects(self):
        rows = {row.row() for row in self.browserTable.selectedIndexes()}
        objects = []
        for row in rows:
            item = self._get_irods_item_of_table_row(row)
            objects.append(item)
        return objects

    def loadSelection(self):
        # loads selection from main table into delete tab
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.WaitCursor))
        self.deleteSelectionBrowser.clear()
        path_name = self.inputPath.text()
        row = self.browserTable.currentRow()
        if row > -1:
            obj_name = self.browserTable.item(row, 1).text()
            obj_path = "/"+path_name.strip("/")+"/"+obj_name.strip("/")
            try:
                if self.conn.collection_exists(obj_path):
                    irodsDict = utils.utils.get_coll_dict(self.conn.get_collection(obj_path))
                elif self.conn.dataobject_exists(obj_path):
                    irodsDict = {self.conn.get_dataobject(obj_path).path: []}
                else:
                    self.errorLabel.setText("Load: nothing selected.")
                    pass
                for key in list(irodsDict.keys())[:20]:
                    self.deleteSelectionBrowser.append(key)
                    if len(irodsDict[key]) > 0:
                        for item in irodsDict[key]:
                            self.deleteSelectionBrowser.append('\t'+item)
                self.deleteSelectionBrowser.append('...')
            except irods.exception.NetworkException:
                self.errorLabel.setText(
                    "iRODS NETWORK ERROR: No Connection, please check network")
                self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))

    def deleteData(self):
        # Deletes all data in the deleteSelectionBrowser
        self.errorLabel.clear()
        data = self.deleteSelectionBrowser.toPlainText().split('\n')
        if data[0] != '':
            deleteItem = data[0].strip()
            quit_msg = "Delete all data in \n\n"+deleteItem+'\n'
            reply = PyQt6.QtWidgets.QMessageBox.question(
                self, 'Message', quit_msg,
                PyQt6.QtWidgets.QMessageBox.StandardButton.Yes,
                PyQt6.QtWidgets.QMessageBox.StandardButton.No)
            if reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    if self.conn.collection_exists(deleteItem):
                        item = self.conn.get_collection(deleteItem)
                    else:
                        item = self.conn.get_dataobject(deleteItem)
                    self.conn.delete_data(item)
                    self.deleteSelectionBrowser.clear()
                    self.loadBrowserTable()
                    self.errorLabel.clear()
                except Exception as error:
                    self.errorLabel.setText("ERROR DELETE DATA: "+repr(error))

    def createCollection(self):
        parent = "/"+self.inputPath.text().strip("/")
        creteCollWidget = gui.popupWidgets.irodsCreateCollection(parent)
        creteCollWidget.exec()
        self.loadBrowserTable()

    def fileUpload(self):
        fileSelect = PyQt6.QtWidgets.QFileDialog.getOpenFileName(self,
                        "Open File", "","All Files (*);;Python Files (*.py)")
        size = utils.utils.get_local_size([fileSelect[0]])
        buttonReply = PyQt6.QtWidgets.QMessageBox.question(
            self, 'Message Box', "Upload " + fileSelect[0],
            PyQt6.QtWidgets.QMessageBox.StandardButton.Yes | PyQt6.QtWidgets.QMessageBox.StandardButton.No,
            PyQt6.QtWidgets.QMessageBox.StandardButton.No)
        if buttonReply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                parentColl = self.conn.get_collection(
                    "/" + self.inputPath.text().strip("/"))
                self.conn.upload_data(
                    fileSelect[0], parentColl, None, size, force=self.force)
                self.loadBrowserTable()
            except irods.exception.NetworkException:
                self.errorLabel.setText(
                    "iRODS NETWORK ERROR: No Connection, please check network")
            except Exception as error:
                logging.error('Upload failed %s: %r', fileSelect[0], error)
                self.errorLabel.setText(repr(error))

    def fileDownload(self):
        if self.current_browser_row == -1:
            self.errorLabel.setText('Please select an object first!')
            return
        # If table is filled
        if self.browserTable.item(self.current_browser_row, 1) is not None:
            objName = self.browserTable.item(self.current_browser_row, 1).text()
            if self.browserTable.item(self.current_browser_row, 1).text().startswith("/" + self.conn.zone):
                parent = '/'.join(objName.split("/")[:len(objName.split("/"))-1])
                objName = objName.split("/")[len(objName.split("/"))-1]
            else:
                parent = self.inputPath.text()
            try:
                if self.conn.dataobject_exists(parent + '/' + objName):
                    downloadDir = utils.utils.get_downloads_dir()
                    buttonReply = PyQt6.QtWidgets.QMessageBox.question(
                        self, 'Message Box',
                        'Download\n'+parent+'/'+objName+'\tto\n'+downloadDir)
                    if buttonReply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
                        obj = self.conn.get_dataobject(parent + '/' + objName)
                        self.conn.download_data(obj, downloadDir, obj.size)
                        self.errorLabel.setText("File downloaded to: "+downloadDir)
            except irods.exception.NetworkException:
                self.errorLabel.setText(
                    "iRODS NETWORK ERROR: No Connection, please check network")
            except Exception as error:
                logging.error('Download failed %s/%s: %r', parent, objName, error)
                self.errorLabel.setText(repr(error))


    def update_icat_acl(self):
        self.errorLabel.clear()
        if self.current_browser_row == -1:
            self.errorLabel.setText('Please select an object first!')
            return
        irods_path = self._get_object_path(self.current_browser_row)
        user_name = self.aclUserField.text()
        user_zone = self.aclZoneField.text()
        acc_name = self.aclBox.currentText()

        if acc_name in ('inherit', 'noinherit'):
            if irods_path.dataobject_exists():
                self.errorLabel.setText(
                    'WARNING: (no)inherit is not applicable to data objects')
                return
        elif user_name is "":
            self.errorLabel.setText("Please provide a user.")
            return
        elif acc_name == "":
            self.errorLabel.setText("Please provide an access level from the menu.")
            return
        recursive = self.recurseBox.currentText() == 'True'
        try:
            item = get_irods_item(irods_path)
            perm = Permissions(self.session, item)
            perm.set(perm=acc_name, user=user_name, zone=user_zone, recursive=recursive)
            self._fill_acls_tab(irods_path)
        except Exception as error:
            self.errorLabel.setText(repr(error))

    def _metadata_edits(self, operation):
        self.errorLabel.clear()
        if self.current_browser_row == -1:
            self.errorLabel.setText('Please select an object first!')
        else:
            irods_path = self._get_object_path(self.current_browser_row)
            newKey = self.metaKeyField.text()
            newVal = self.metaValueField.text()
            newUnits = self.metaUnitsField.text()
            if newKey != "" and newVal != "":
                irods_path = self._get_object_path(self.current_browser_row)
                item = get_irods_item(irods_path)
                meta = MetaData(item)
                if operation == "add":
                    meta.add(newKey, newVal, newUnits)
                elif operation == "set":
                    meta.set(newKey, newVal, newUnits)
                elif operation == "delete":
                    meta.delete(newKey, newVal, newUnits)
                self._fill_metadata_tab(irods_path)


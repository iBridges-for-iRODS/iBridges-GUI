"""Browser tab."""
import sys
import logging
from pathlib import Path

import irods.exception
import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic
from ibridges import IrodsPath, download, get_collection, get_dataobject, upload
from ibridges.data_operations import obj_replicas
from ibridges.meta import MetaData
from ibridges.permissions import Permissions

import ibridgesgui as gui
from ibridgesgui.popup_widgets import CreateCollection
from ibridgesgui.gui_utils import (
    UI_FILE_DIR,
    get_coll_dict,
    get_downloads_dir,
    get_irods_item,
    populate_table,
)


class Browser(PyQt6.QtWidgets.QWidget,
              gui.ui_files.tabBrowser.Ui_tabBrowser):
    """Browser view for iRODS session.

    """

    def __init__(self, session, app_name):
        """Initialize an iRODS browser view.

        """
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi(UI_FILE_DIR / "tabBrowser.ui", self)

        self.logger = logging.getLogger(app_name)
        self.session = session
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
        except Exception as err:
            self.errorLabel.setText('Cannot set root collection. Set "irods_home" in your environment.json')
            self.logger.exception('Failed to set iRODS home: %s', err)
        self.reset_path()
        self.browse()


    def browse(self):
        """Initialize browser view GUI elements.
            Defines the signals and slots.
        """
        # Main navigation elements
        self.inputPath.returnPressed.connect(self.load_browser_table)
        self.refreshButton.clicked.connect(self.load_browser_table)
        self.refreshButton.setToolTip('Reload Collection')
        self.homeButton.clicked.connect(self.reset_path)
        self.homeButton.setToolTip('Load Home')
        self.parentButton.clicked.connect(self.set_parent)
        self.parentButton.setToolTip('Go one collection up')

        # Main manipulation buttons Upload/Download create collection
        self.UploadButton.clicked.connect(self.file_upload)
        self.folderUploadButton.clicked.connect(self.folder_upload)
        self.DownloadButton.clicked.connect(self.download)
        self.createCollButton.clicked.connect(self.create_collection)

        # Browser table behaviour
        self.browserTable.doubleClicked.connect(self.update_path)
        self.browserTable.clicked.connect(self.fill_info)

        # Bottom tab view buttons
        # Metadata
        self.metadataTable.clicked.connect(self.edit_metadata)
        self.metaAddButton.clicked.connect(self.add_icat_meta)
        self.metaUpdateButton.clicked.connect(self.set_icat_meta)
        self.metaDeleteButton.clicked.connect(self.delete_icat_meta)
        # ACLs
        self.aclTable.clicked.connect(self.edit_acl)
        self.aclAddButton.clicked.connect(self.update_icat_acl)
        # Delete
        self.dataDeleteButton.clicked.connect(self.delete_data)
        self.loadDeleteSelectionButton.clicked.connect(self.load_selection)


    def reset_path(self):
        """Reset browser table to root path"""
        self.inputPath.setText(self.root_coll.path)
        self.load_browser_table()


    def set_parent(self):
        """Set browser path to parent of current collection and update browser table"""
        current_path = IrodsPath(self.session, self.inputPath.text())
        self.inputPath.setText(str(current_path.parent))
        self.load_browser_table()


    # @PyQt6.QtCore.pyqtSlot(PyQt6.QtCore.QModelIndex)
    def update_path(self, index):
        """Takes path from inputPath and loads browser table"""
        self.errorLabel.clear()
        row = index.row()
        irods_path = self._get_item_path(row)
        if irods_path.collection_exists():
            self.inputPath.setText(str(irods_path))
            self.load_browser_table()

    def create_collection(self):
        """Create a new collection in current collection"""
        parent = IrodsPath(self.session, "/"+self.inputPath.text().strip("/"))
        coll_widget = CreateCollection(parent, self.logger)
        coll_widget.exec()
        self.load_browser_table()

    def folder_upload(self):
        """Select a folder and upload"""
        self.errorLabel.clear()
        select_dir = PyQt6.QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        path = self._fs_select(select_dir)
        if path is not None:
            self._upload(path)

    def file_upload(self):
        """Select a file and upload"""
        self.errorLabel.clear()
        select_file = PyQt6.QtWidgets.QFileDialog.getOpenFileName(self, "Open Filie")
        path = self._fs_select(select_file)
        if path is not None:
            self._upload(path)


    def download(self):
        """Download collection or data object"""
        self.errorLabel.clear()
        if self.browserTable.currentRow() == -1:
            self.errorLabel.setText('Please select a row from the table first!')
            return

        if self.browserTable.item(self.browserTable.currentRow(), 1) is not None:
            item_name = self.browserTable.item(self.browserTable.currentRow(), 1).text()
            path = IrodsPath(self.session, '/', *self.inputPath.text().split('/'), item_name)
            overwrite = self.overwrite.isChecked()
            download_dir = get_downloads_dir()
            if overwrite:
                write = "All data will be updated."
            else:
                write = "Only new data will be added."
            info = f'Download data:\n{path}\n\nto\n\n{download_dir}\n\n{write}'
            try:
                if path.exists():
                    button_reply = PyQt6.QtWidgets.QMessageBox.question(self, '', info)
                    if button_reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
                        if Path(download_dir).joinpath(item_name).exists() and not overwrite:
                            raise FileExistsError
                        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.BusyCursor))
                        self.logger.info('Downloading %s to %s, overwrite %s', path, download_dir,
                                         str(overwrite))
                        download(self.session, path, download_dir, overwrite=overwrite)
                        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
                        self.errorLabel.setText("Data downloaded to: "+str(download_dir))
                else:
                    self.errorLabel.setText(
                            f'Data {path.parent} does not exist.')
            except FileExistsError:
                self.errorLabel.setText(f'Data already exists in {download_dir}.'+\
                                        ' Check "overwrite" to overwrite the data.')
            except Exception as err:
                self.logger.exception('Downloading %s failed: %s', path, err)
                self.errorLabel.setText(f'Could not download {path}. Consult the logs.')

    def load_browser_table(self):
        """Loads main browser table"""
        self.errorLabel.clear()
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
            except Exception as exception:
                self.browserTable.setRowCount(0)
                self.errorLabel.setText(repr(exception))
        else:
            self.browserTable.setRowCount(0)
            self.errorLabel.setText("Collection does not exist.")


    def fill_info(self):
        """Fill lower tabs with info"""
        self.errorLabel.clear()
        self._clear_view_tabs()
        self.deleteSelectionBrowser.clear()
        self.metadataTable.setRowCount(0)
        self.aclTable.setRowCount(0)
        self.replicaTable.setRowCount(0)
        irods_path = self._get_item_path(self.browserTable.currentRow())
        self._clear_view_tabs()
        try:
            self._fill_preview_tab(irods_path)
            self._fill_metadata_tab(irods_path)
            self._fill_acls_tab(irods_path)
            self._fill_replicas_tab(irods_path)
        except Exception as error:
            self.errorLabel.setText(repr(error))
            raise


    def set_icat_meta(self):
        """Button metadata set"""
        try:
            self._metadata_edits("set")
        except Exception as error:
            self.errorLabel.setText(repr(error))

    def add_icat_meta(self):
        """Button metadata add"""
        try:
            self._metadata_edits("add")
        except Exception as error:
            self.errorLabel.setText(repr(error))

    def delete_icat_meta(self):
        """Button metadata delete"""
        try:
            self._metadata_edits("delete")
        except Exception as error:
            self.errorLabel.setText(repr(error))


    # @PyQt6.QtCore.pyqtSlot(PyQt6.QtCore.QModelIndex)
    def edit_metadata(self, index):
        """Load selected metadata into edit fields"""
        self.errorLabel.clear()
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
        """Load selected acl into editing fields"""
        self.errorLabel.clear()
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
        """Send acls to iRODS server"""
        self.errorLabel.clear()
        if self.browserTable.currentRow() == -1:
            self.errorLabel.setText('Please select a row from the table first!')
            return
        irods_path = self._get_item_path(self.browserTable.currentRow())
        user_name = self.aclUserField.text()
        user_zone = self.aclZoneField.text()
        acc_name = self.aclBox.currentText()

        if acc_name in ('inherit', 'noinherit'):
            if irods_path.dataobject_exists():
                self.errorLabel.setText(
                    'WARNING: (no)inherit is not applicable to data objects')
                return
        elif user_name == "":
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


    def load_selection(self):
        """loads selection from main table into delete tab"""
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.WaitCursor))
        self.deleteSelectionBrowser.clear()
        row = self.browserTable.currentRow()
        if row == -1:
            self.errorLabel.setText("Please select a row from the table first.")
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        item_path = self._get_item_path(row)
        if item_path.exists():
            item = get_irods_item(item_path)
            if item_path.collection_exists():
                data_dict = get_coll_dict(item)
                for key in list(data_dict.keys())[:20]:
                    self.deleteSelectionBrowser.append(key)
                    if len(data_dict[key]) > 0:
                        for item in data_dict[key]:
                            self.deleteSelectionBrowser.append('\t'+item)
                self.deleteSelectionBrowser.append('...')
            else:
                self.deleteSelectionBrowser.append(str(item_path))
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))

    def delete_data(self):
        """Deletes all data in the deleteSelectionBrowser"""
        self.errorLabel.clear()
        data = self.deleteSelectionBrowser.toPlainText().split('\n')
        if data[0] != '':
            item = data[0].strip()
            quit_msg = "Delete all data in \n\n"+item+'\n'
            reply = PyQt6.QtWidgets.QMessageBox.question(
                self, 'Message', quit_msg,
                PyQt6.QtWidgets.QMessageBox.StandardButton.Yes,
                PyQt6.QtWidgets.QMessageBox.StandardButton.No)
            if reply == PyQt6.QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    IrodsPath(self.session, item).remove()
                    self.deleteSelectionBrowser.clear()
                    self.load_browser_table()
                    self.errorLabel.clear()
                except Exception as error:
                    self.errorLabel.setText("ERROR DELETE DATA: "+repr(error))
# Internal functions
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
            acl_data = [(p.user_name, p.user_zone, p.access_name, inheritance) for p in acls]
            populate_table(self.aclTable, len(list(acls)), acl_data)
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
            populate_table(self.metadataTable, len(list(meta)), meta)
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
            file_type = ''
            obj = get_dataobject(self.session, irods_path)
            if '.' in irods_path.parts[-1]:
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

    def _get_item_path(self, row):
        item_name = self.browserTable.item(row, 1).text()
        return IrodsPath(self.session, '/', *self.inputPath.text().split('/'), item_name)

    def _metadata_edits(self, operation):
        self.errorLabel.clear()
        if self.browserTable.currentRow() == -1:
            self.errorLabel.setText('Please select an object first!')
        else:
            irods_path = self._get_item_path(self.browserTable.currentRow())
            new_key = self.metaKeyField.text()
            new_val = self.metaValueField.text()
            new_units = self.metaUnitsField.text()
            if new_key != "" and new_val != "":
                irods_path = self._get_item_path(self.browserTable.currentRow())
                item = get_irods_item(irods_path)
                meta = MetaData(item)
                if operation == "add":
                    meta.add(new_key, new_val, new_units)
                elif operation == "set":
                    meta.set(new_key, new_val, new_units)
                elif operation == "delete":
                    meta.delete(new_key, new_val, new_units)
                self._fill_metadata_tab(irods_path)

    def _fs_select(self, path_select):
        """Retrieve the path (file or folder) from a QFileDialog
           path_select: PyQt6.QtWidgets.QFileDialog.getExistingDirectory
                        PyQt6.QtWidgets.QFileDialog.getOpenFileName

        """
        yes_button = PyQt6.QtWidgets.QMessageBox.StandardButton.Yes
        if isinstance(path_select, tuple):
            path = path_select[0]
        else:
            path = path_select

        if path != '':
            if self.overwrite.isChecked():
                write = "All data will be updated."
            else:
                write = "Only new data will be added."
            info = f'Upload data:\n{path}\n\nto\n{self.inputPath.text()}\n\n{write}'
            reply = PyQt6.QtWidgets.QMessageBox.question(self, "", info)
            if reply == yes_button:
                return Path(path)
        return None

    def _upload(self, source):
        """Uploads data to path in inputPath"""
        overwrite = self.overwrite.isChecked()
        parent_path = IrodsPath(self.session, '/', *self.inputPath.text().split('/'))

        try:
            if parent_path.joinpath(source.name).exists() and not overwrite:
                raise FileExistsError
            self.logger.info('Uploading %s to %s, overwrite %s', source, parent_path, str(overwrite))
            upload(self.session, source, parent_path, overwrite=overwrite)
            self.load_browser_table()
        except FileExistsError:
            self.errorLabel.setText(f'Data already exists in {parent_path}.'+\
                                    ' Check "overwrite" to overwrite the data.')
        except irods.exception.CAT_NO_ACCESS_PERMISSION:
            self.errorLabel.setText(f'No permission to upload data to {parent_path}.')
            self.logger.info('Uploading %s to %s, overwrite %s failed. No permissions.',
                             source, parent_path, str(overwrite))
        except Exception as err:
            self.logger.exception('Failed to upload %s to %s: %s', source, parent_path, err)
            self.errorLabel.setText(f'Failed to upload {source}. Consult the logs.')

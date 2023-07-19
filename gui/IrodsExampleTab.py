"""An example tab.

"""
import sys

import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic

import gui
import irodsConnector
import utils
from gui.irodsTreeView import IrodsModel
from gui.ui_files.ExampleTab import Ui_ExampleTab

class IrodsExampleTab(PyQt6.QtWidgets.QWidget,
                      Ui_ExampleTab):
    """Example tab class.

    """
    conn = irodsConnector.manager.IrodsConnector()
    context = utils.context.Context()

    def __init__(self):
        """

        """
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi("gui/ui_files/ExampleTab.ui", self)
        self.ienv = self.context.irods_environment.config
        self.error_label.setText("Whooohoo")
        self._initialize_irods_model(self.irodsTreeView)
        self.irodsTreeView.clicked.connect(self.tree_function)

    def _initialize_irods_model(self, tree_view: PyQt6.QtWidgets.QWidget):
        """The iRODS tree view must be initialized.

        Parameters
        ----------
        tree_view : PyQt6.QtWidgets.QWidget
            Appropriate file tree instance.

        """
        self.irodsmodel = IrodsModel(tree_view)
        tree_view.setModel(self.irodsmodel)

        home_coll_str = utils.path.iRODSPath('/', self.conn.zone, 'home')
        irods_root_coll = self.ienv.get('irods_home', home_coll_str)

        self.irodsmodel.setHorizontalHeaderLabels(
            [irods_root_coll, 'Level', 'iRODS ID', 'parent ID', 'type'])
        tree_view.expanded.connect(self.irodsmodel.refresh_subtree)
        tree_view.clicked.connect(self.irodsmodel.refresh_subtree)
        self.irodsmodel.init_tree()

        tree_view.setHeaderHidden(True)
        tree_view.header().setDefaultSectionSize(180)
        tree_view.setColumnHidden(1, True)
        tree_view.setColumnHidden(2, True)
        tree_view.setColumnHidden(3, True)
        tree_view.setColumnHidden(4, True)

    def _get_paths_from_trees(self, tree_view: PyQt6.QtWidgets.QWidget,
                              local: bool = False) -> tuple:
        """Determine the pathname from the file tree selection.

        Parameters
        ----------
        tree_view : PyQt6.QtWidgets.QWidget
            Apropriate file tree instance.
        local : bool
            Whether it is a local tree.

        Returns
        -------
        tuple
            (tree index, pathname) of selection.

        """
        index = tree_view.selectedIndexes()[0]
        if local:
            path = self.localmodel.filePath(index)
        else:
            path = self.irodsmodel.irods_path_from_tree_index(index)
        return index, path

    def tree_function(self) -> tuple:
        """Get file tree information from selection.

        Returns
        -------
        tuple
            (tree index, pathname) of selection.

        """
        index, path = self._get_paths_from_trees(self.irodsTreeView)
        self.textField.setText(path)

        return index, path

import pytest
from unittest.mock import MagicMock
from ibridgesgui.browsertab.browser_controller import BrowserController
from ibridgesgui.browsertab.browser_model import BrowserModel
from ibridgesgui.browsertab.irods_browser_service import IrodsBrowserService


# -------------------------
# BASIC FIXTURES
# -------------------------

@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def model(make_irods_path):
    return BrowserModel(make_irods_path("/"))


# -------------------------
# UI FIXTURE
# -------------------------

@pytest.fixture
def ui():
    ui = MagicMock()

    # Explicit UI subwidgets
    ui.input_path = MagicMock()
    ui.browser_table = MagicMock()
    ui.info_tabs = MagicMock()
    ui.meta_table = MagicMock()
    ui.acl_table = MagicMock()
    ui.error_label = MagicMock()
    ui.preview_browser = MagicMock()

    # Path input
    ui.input_path.text.return_value = "/tempZone/home/user"
    ui.input_path.setText = MagicMock()

    # Browser table
    ui.browser_table.currentRow.return_value = 0
    ui.browser_table.item.return_value = MagicMock()
    ui.browser_table.item.return_value.text.return_value = "file.txt"
    ui.browser_table.setRowCount = MagicMock()

    # Info tabs
    tab = MagicMock()
    tab.objectName.return_value = "metadata"
    ui.info_tabs.currentWidget.return_value = tab

    # Metadata widgets
    ui.meta_table.currentRow.return_value = 0
    ui.meta_table.item.return_value = MagicMock()
    ui.meta_table.item.return_value.text.return_value = "meta"

    ui.meta_key_field = MagicMock()
    ui.meta_value_field = MagicMock()
    ui.meta_units_field = MagicMock()

    ui.meta_key_field.text.return_value = "k"
    ui.meta_value_field.text.return_value = "v"
    ui.meta_units_field.text.return_value = "u"

    # ACL widgets
    ui.acl_table.currentRow.return_value = 0
    ui.acl_table.item.return_value = MagicMock()
    ui.acl_table.item.return_value.text.return_value = "user"

    ui.acl_user_field = MagicMock()
    ui.acl_zone_field = MagicMock()
    ui.acl_box = MagicMock()
    ui.recursive_box = MagicMock()

    ui.acl_user_field.text.return_value = "user"
    ui.acl_zone_field.text.return_value = "zone"
    ui.acl_box.currentText.return_value = "read"
    ui.recursive_box.currentText.return_value = "False"

    # Error label
    ui.error_label.setText = MagicMock()
    ui.error_label.clear = MagicMock()
    ui.error_label.setWordWrap = MagicMock()

    return ui


# -------------------------
# PATH FACTORY
# -------------------------

@pytest.fixture
def make_irods_path():
    def _make(path_str):
        p = MagicMock()
        p.session = MagicMock()
        p.__str__.return_value = path_str
        p.path = path_str
        return p
    return _make

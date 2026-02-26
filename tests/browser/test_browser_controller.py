import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QMessageBox
from ibridgesgui.browser_controller import BrowserController


@pytest.fixture
def ui():
    """Mock all UI elements used by BrowserController."""
    ui = MagicMock()

    # path input
    ui.input_path.text.return_value = "/tempZone/home/user"
    ui.input_path.setText = MagicMock()

    # browser table
    ui.browser_table.currentRow.return_value = 0
    ui.browser_table.item.return_value.text.return_value = "file.txt"

    # metadata table
    ui.meta_table.item.return_value.text.return_value = "meta"

    # ACL table
    ui.acl_table.item.return_value.text.return_value = "acl"

    return ui


@pytest.fixture
def service(make_irods_path):
    """Mock IrodsBrowserService."""
    service = MagicMock()
    service.home_path.return_value = make_irods_path("/tempZone/home/user")
    service.path_from_text.return_value = make_irods_path("/tempZone/home/user")
    service.parent_path.return_value = make_irods_path("/tempZone/home")
    service.list_table_rows.return_value = [["file.txt", "file.txt", "data"]]
    return service


@pytest.fixture
def controller(ui, service):
    with patch("ibridgesgui.browser_controller.IrodsBrowserService", return_value=service):
        return BrowserController(ui, session=MagicMock(), app_name="test")


def test_init_browser_calls_set_path(controller, ui):
    controller._set_path = MagicMock()
    controller.init_browser()
    controller._set_path.assert_called_once()


def test_set_path_updates_model_and_ui(controller, ui, make_irods_path):
    path = make_irods_path("/tempZone/home/user")
    controller._load_browser_table = MagicMock()

    controller._set_path(path)

    assert controller.model.current_path == path
    ui.input_path.setText.assert_called_with(str(path))
    controller._load_browser_table.assert_called_once()


def test_refresh_browser(controller, ui, service):
    controller._set_path = MagicMock()
    controller._refresh_browser()
    controller._set_path.assert_called_once_with(service.path_from_text.return_value)


def test_go_to_parent(controller, ui, service):
    controller._set_path = MagicMock()
    controller._go_to_parent()
    controller._set_path.assert_called_once_with(service.parent_path.return_value)


def test_load_browser_table_success(controller, ui, service):
    with patch("ibridgesgui.browser_controller.populate_table") as populate:
        controller._load_browser_table()
        populate.assert_called_once()


def test_load_browser_table_missing_collection(controller, ui):
    controller.model.current_path.collection_exists = lambda: False
    controller._load_browser_table()
    ui.error_label.setText.assert_called()


def test_open_selected_path(controller, ui):
    path = MagicMock()
    path.collection_exists.return_value = True
    controller._item_path = MagicMock(return_value=path)
    controller._set_path = MagicMock()

    controller._open_selected_path()
    controller._set_path.assert_called_once_with(path)


def test_delete_data_success(controller, ui):
    path = MagicMock()
    path.remove = MagicMock()
    controller._item_path = MagicMock(return_value=path)

    ui.browser_table.currentRow.return_value = 0

    with patch("PySide6.QtWidgets.QMessageBox.critical", return_value=QMessageBox.Yes):
        controller._refresh_browser = MagicMock()
        controller.delete_data()
        path.remove.assert_called_once()
        controller._refresh_browser.assert_called_once()


def test_metadata_edit_add(controller, ui, service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=make_irods_path("/tempZone/home/user/file.txt"))
    controller.model.metadata_cache = {}
    controller.model.updated_info_tabs = []

    ui.meta_key_field.text.return_value = "k"
    ui.meta_value_field.text.return_value = "v"
    ui.meta_units_field.text.return_value = "u"

    controller._fill_current_info_tab = MagicMock()

    controller._metadata_edits("add")
    service.add_metadata.assert_called_once()


def test_update_permission(controller, ui, service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=make_irods_path("/tempZone/home/user/file.txt"))

    ui.acl_user_field.text.return_value = "user"
    ui.acl_zone_field.text.return_value = "zone"
    ui.acl_box.currentText.return_value = "read"
    ui.recursive_box.currentText.return_value = "False"

    controller._fill_current_info_tab = MagicMock()

    controller._update_permission()
    service.set_acl.assert_called_once()


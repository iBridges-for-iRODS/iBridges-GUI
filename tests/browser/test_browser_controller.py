import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QMessageBox

from ibridgesgui.browsertab.browser_controller import BrowserController
from ibridges import IrodsPath



@pytest.fixture
def mock_service(make_irods_path):
    service = MagicMock()
    service.home_path.return_value = make_irods_path("/tempZone/home/user")
    service.path_from_text.return_value = make_irods_path("/tempZone/home/user")
    service.parent_path.return_value = make_irods_path("/tempZone/home")
    service.list_table_rows.return_value = [["C-", "file.txt", "data"]]
    service.get_metadata.return_value = [("k", "v", "u")]
    service.get_acls.return_value = [("u", "z", "read", "")]
    service.normalize_acls.return_value = [("u", "z", "read", "")]
    service.get_replicas.return_value = [("r1",)]
    service.compute_preview.return_value = ["line1", "line2"]
    return service


@pytest.fixture
def controller(ui, session, mock_service):
    with patch(
        "ibridgesgui.browsertab.browser_controller.IrodsBrowserService",
        return_value=mock_service,
    ):
        return BrowserController(ui, session, "test")

# --- init / navigation -------------------------------------------------------

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


def test_refresh_browser(controller, ui, mock_service):
    controller._set_path = MagicMock()
    controller._refresh_browser()
    controller._set_path.assert_called_once_with(mock_service.path_from_text.return_value)


def test_go_to_parent(controller, ui, mock_service):
    controller._set_path = MagicMock()
    controller._go_to_parent()
    controller._set_path.assert_called_once_with(mock_service.parent_path.return_value)


# --- browser table loading ---------------------------------------------------

def test_load_browser_table_success(controller, ui, mock_service):
    # Ensure the path is treated as a collection
    controller.model.current_path.collection_exists.return_value = True

    with patch("ibridgesgui.browsertab.browser_controller.populate_table") as populate:
        controller._load_browser_table()
        populate.assert_called_once()


def test_load_browser_table_non_collection(controller, ui, make_irods_path):
    path = make_irods_path("/x")
    path.collection_exists.return_value = False
    controller.model.current_path = path

    controller._load_browser_table()
    ui.browser_table.setRowCount.assert_called_with(0)
    ui.error_label.setText.assert_called()


def test_load_browser_table_exception(controller, ui, mock_service):
    mock_service.list_table_rows.side_effect = Exception("boom")
    controller._load_browser_table()
    ui.browser_table.setRowCount.assert_called_with(0)
    ui.error_label.setText.assert_called()


# --- selection helpers -------------------------------------------------------

def test_validate_selection_no_row(controller, ui):
    ui.browser_table.currentRow.return_value = -1
    assert controller._validate_selection() is False
    ui.error_label.setText.assert_called_once()


def test_item_path_invalid_row(controller, ui):
    assert controller._item_path(-1) is None


def test_item_path_missing_item(controller, ui):
    ui.browser_table.item.return_value = None
    assert controller._item_path(0) is None


# --- open selected path ------------------------------------------------------

def test_open_selected_path_no_selection(controller, ui):
    ui.browser_table.currentRow.return_value = -1
    controller._set_path = MagicMock()
    controller._open_selected_path()
    controller._set_path.assert_not_called()


def test_open_selected_path_not_collection(controller, ui):
    path = MagicMock()
    path.collection_exists.return_value = False
    controller._item_path = MagicMock(return_value=path)
    controller._set_path = MagicMock()
    controller._open_selected_path()
    controller._set_path.assert_not_called()


def test_open_selected_path_collection(controller, ui):
    path = MagicMock()
    path.collection_exists.return_value = True
    controller._item_path = MagicMock(return_value=path)
    controller._set_path = MagicMock()

    controller._open_selected_path()
    controller._set_path.assert_called_once_with(path)


# --- delete data -------------------------------------------------------------

def test_delete_data_success(controller, ui):
    path = MagicMock()
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=path)

    with patch("PySide6.QtWidgets.QMessageBox.critical", return_value=QMessageBox.Yes):
        controller._refresh_browser = MagicMock()
        controller.delete_data()
        path.remove.assert_called_once()
        controller._refresh_browser.assert_called_once()


def test_delete_data_user_declines(controller, ui):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock()
    with patch("PySide6.QtWidgets.QMessageBox.critical", return_value=QMessageBox.No):
        controller.delete_data()
        controller._item_path.return_value.remove.assert_not_called()


def test_delete_data_no_permission(controller, ui):
    from irods.exception import CAT_NO_ACCESS_PERMISSION
    controller._validate_selection = MagicMock(return_value=True)
    path = MagicMock()
    path.remove.side_effect = CAT_NO_ACCESS_PERMISSION()
    controller._item_path = MagicMock(return_value=path)

    with patch("PySide6.QtWidgets.QMessageBox.critical", return_value=QMessageBox.Yes):
        controller.delete_data()
        ui.error_label.setText.assert_called()


def test_delete_data_generic_exception(controller, ui):
    controller._validate_selection = MagicMock(return_value=True)
    path = MagicMock()
    path.remove.side_effect = Exception("boom")
    controller._item_path = MagicMock(return_value=path)

    with patch("PySide6.QtWidgets.QMessageBox.critical", return_value=QMessageBox.Yes):
        controller.delete_data()
        ui.error_label.setText.assert_called()


# --- fill current info tab / caching ----------------------------------------

def test_fill_current_info_tab_skips_when_no_selection(controller, ui):
    controller._validate_selection = MagicMock(return_value=False)
    controller._fill_tab = MagicMock()
    controller._fill_current_info_tab()
    controller._fill_tab.assert_not_called()


def test_fill_current_info_tab_calls_fill_tab_when_needed(controller, ui):
    controller._validate_selection = MagicMock(return_value=True)
    controller.model.needs_tab_update = MagicMock(return_value=True)
    controller._fill_tab = MagicMock()

    controller._fill_current_info_tab()
    controller._fill_tab.assert_called_once()


def test_fill_tab_metadata(controller, ui, mock_service):
    row = 0
    path = MagicMock()
    controller._item_path = MagicMock(return_value=path)
    controller.model.metadata_cache = {}

    controller._fill_tab("metadata")

    mock_service.get_metadata.assert_called_once_with(path)
    ui.render_metadata.assert_called_once()


def test_fill_tab_permissions(controller, ui, mock_service):
    row = 0
    path = MagicMock()
    controller._item_path = MagicMock(return_value=path)
    controller.model.acl_cache = {}

    controller._fill_tab("permissions")

    mock_service.get_acls.assert_called_once_with(path)
    mock_service.normalize_acls.assert_called_once()
    ui.render_acls.assert_called_once()


def test_fill_tab_replicas(controller, ui, mock_service):
    path = MagicMock()
    controller._item_path = MagicMock(return_value=path)
    controller.model.replica_cache = {}

    controller._fill_tab("replicas")

    mock_service.get_replicas.assert_called_once_with(path)
    ui.render_replicas.assert_called_once()


def test_fill_tab_preview(controller, ui, mock_service):
    path = MagicMock()
    controller._item_path = MagicMock(return_value=path)
    controller.model.preview_cache = {}

    controller._fill_tab("preview")

    mock_service.compute_preview.assert_called_once_with(path)
    ui.preview_browser.setText.assert_called_once()


# --- metadata edits ----------------------------------------------------------

def test_metadata_edit_add(controller, ui, mock_service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=make_irods_path("/x"))
    controller.model.invalidate_metadata = MagicMock()
    controller._fill_current_info_tab = MagicMock()

    ui.meta_key_field.text.return_value = "k"
    ui.meta_value_field.text.return_value = "v"
    ui.meta_units_field.text.return_value = "u"

    controller._metadata_edits("add")
    mock_service.add_metadata.assert_called_once()
    controller.model.invalidate_metadata.assert_called_once()
    controller._fill_current_info_tab.assert_called_once()


def test_metadata_edit_update(controller, ui, mock_service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=make_irods_path("/x"))
    controller.model.invalidate_metadata = MagicMock()
    controller._fill_current_info_tab = MagicMock()

    ui.meta_key_field.text.return_value = "newk"
    ui.meta_value_field.text.return_value = "newv"
    ui.meta_units_field.text.return_value = "newu"

    ui.meta_table.currentRow.return_value = 0
    ui.meta_table.item.side_effect = [
        MagicMock(text=lambda: "oldk"),
        MagicMock(text=lambda: "oldv"),
        MagicMock(text=lambda: "oldu"),
    ]

    controller._metadata_edits("update")
    mock_service.update_metadata.assert_called_once()
    controller.model.invalidate_metadata.assert_called_once()
    controller._fill_current_info_tab.assert_called_once()


def test_metadata_edit_delete(controller, ui, mock_service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=make_irods_path("/x"))
    controller.model.invalidate_metadata = MagicMock()
    controller._fill_current_info_tab = MagicMock()

    ui.meta_key_field.text.return_value = "k"
    ui.meta_value_field.text.return_value = "v"
    ui.meta_units_field.text.return_value = "u"

    controller._metadata_edits("delete")
    mock_service.delete_metadata.assert_called_once()
    controller.model.invalidate_metadata.assert_called_once()
    controller._fill_current_info_tab.assert_called_once()


def test_metadata_edit_invalid_selection(controller, ui):
    controller._validate_selection = MagicMock(return_value=False)
    controller._metadata_edits("add")
    ui.error_label.setText.assert_not_called()


def test_metadata_edit_exception(controller, ui, mock_service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=make_irods_path("/x"))
    mock_service.add_metadata.side_effect = Exception("fail")

    ui.meta_key_field.text.return_value = "k"
    ui.meta_value_field.text.return_value = "v"
    ui.meta_units_field.text.return_value = "u"

    controller._metadata_edits("add")
    ui.error_label.setText.assert_called()


# --- ACL updates -------------------------------------------------------------

def test_update_permission_success(controller, ui, mock_service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    path = make_irods_path("/x")
    controller._item_path = MagicMock(return_value=path)
    controller.model.invalidate_acls = MagicMock()
    controller._fill_current_info_tab = MagicMock()

    ui.acl_user_field.text.return_value = "user"
    ui.acl_zone_field.text.return_value = "zone"
    ui.acl_box.currentText.return_value = "read"
    ui.recursive_box.currentText.return_value = "True"

    controller._update_permission()

    mock_service.set_acl.assert_called_once()
    controller.model.invalidate_acls.assert_called_once()
    controller._fill_current_info_tab.assert_called_once()


def test_update_permission_inherit_on_dataobject(controller, ui, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    path = make_irods_path("/x")
    path.dataobject_exists.return_value = True
    controller._item_path = MagicMock(return_value=path)

    ui.acl_box.currentText.return_value = "Newly added items to collection will inherit permissions"

    controller._update_permission()
    ui.error_label.setText.assert_called()


def test_update_permission_missing_user(controller, ui, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    path = make_irods_path("/x")
    controller._item_path = MagicMock(return_value=path)

    ui.acl_user_field.text.return_value = ""
    ui.acl_box.currentText.return_value = "read"

    controller._update_permission()
    ui.error_label.setText.assert_called()


def test_update_permission_missing_access(controller, ui, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    path = make_irods_path("/x")
    controller._item_path = MagicMock(return_value=path)

    ui.acl_box.currentText.return_value = ""

    controller._update_permission()
    ui.error_label.setText.assert_called()


def test_update_permission_exception(controller, ui, mock_service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    path = make_irods_path("/x")
    controller._item_path = MagicMock(return_value=path)

    mock_service.set_acl.side_effect = Exception("boom")

    controller._update_permission()
    ui.error_label.setText.assert_called()


# --- row click ---------------------------------------------------------------

def test_on_row_clicked_updates_model_and_fills_tab(controller, ui):
    controller.model.on_row_clicked = MagicMock()
    controller._fill_current_info_tab = MagicMock()

    controller._on_row_clicked()

    controller.model.on_row_clicked.assert_called_once()
    controller._fill_current_info_tab.assert_called_once()

def test_invalidate_metadata(model):
    model.metadata_cache = {0: "x", 1: "y"}
    model.invalidate_metadata(row=0)
    assert 0 not in model.metadata_cache
    assert 1 in model.metadata_cache

def test_invalidate_acls(model):
    model.acl_cache = {0: "x", 1: "y"}
    model.invalidate_acls(row=0)
    assert 0 not in model.acl_cache
    assert 1 in model.acl_cache

def test_needs_tab_update_true(model):
    model.last_row = 0
    model.current_row = 1
    assert model.needs_tab_update("metadata") is True


def test_needs_tab_update_false(model):
    model.last_selected_row = 0
    model.current_selected_row = 0
    model.last_path = model.current_path
    model.updated_info_tabs.add("metadata")

    assert model.needs_tab_update("metadata") is False

def test_on_row_clicked(model):
    model.current_selected_row = -1
    model.last_selected_row = -1

    model.on_row_clicked(5)

    assert model.current_selected_row == 5
    assert model.last_selected_row == -1



import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QMessageBox
from ibridgesgui.browsertab.browser_controller import BrowserController


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

def test_load_browser_table_exception(controller, ui, service):
    service.list_table_rows.side_effect = Exception("boom")
    controller._load_browser_table()
    ui.browser_table.setRowCount.assert_called_with(0)
    ui.error_label.setText.assert_called()


# Selection validation in main table

def test_validate_selection_no_row(controller, ui):
    ui.browser_table.currentRow.return_value = -1
    assert controller._validate_selection() is False
    ui.error_label.setText.assert_called_once()

def test_item_path_invalid_row(controller, ui):
    assert controller._item_path(-1) is None

def test_item_path_missing_item(controller, ui):
    ui.browser_table.item.return_value = None
    assert controller._item_path(0) is None

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


def test_load_browser_table_exception(controller, ui, service):
    service.list_table_rows.side_effect = Exception("boom")
    controller._load_browser_table()
    ui.browser_table.setRowCount.assert_called_with(0)
    ui.error_label.setText.assert_called()


# Negative paths
def test_open_selected_path_no_selection(controller, ui):
    ui.browser_table.currentRow.return_value = -1
    controller._set_path = MagicMock()
    controller._open_selected_path()
    controller._set_path.assert_not_called()

def test_open_selected_path_not_a_collection(controller, ui):
    path = MagicMock()
    path.collection_exists.return_value = False
    controller._item_path = MagicMock(return_value=path)
    controller._set_path = MagicMock()
    controller._open_selected_path()
    controller._set_path.assert_not_called()

# Positive paths
def test_open_selected_path(controller, ui):
    path = MagicMock()
    path.collection_exists.return_value = True
    controller._item_path = MagicMock(return_value=path)
    controller._set_path = MagicMock()

    controller._open_selected_path()
    controller._set_path.assert_called_once_with(path)

# Delete functionality

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

# metadata

def test_fill_tab_metadata(controller, ui):
    controller.model.get_cached_metadata = MagicMock(return_value=[("k","v","u")])
    controller._render_metadata = MagicMock()
    controller._fill_tab("metadata", MagicMock(), 0)
    controller._render_metadata.assert_called_once()

def test_render_metadata_empty(controller, ui):
    controller._render_metadata([], MagicMock())
    ui.no_meta_label.setText.assert_called()

def test_load_metadata_item(controller, ui):
    index = MagicMock(row=lambda: 0)
    controller._load_metadata_item(index)
    ui.meta_key_field.setText.assert_called()



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

def test_metadata_edit_update(controller, ui, service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=make_irods_path("/x"))
    controller.model.metadata_cache = {}
    controller.model.updated_info_tabs = []

    ui.meta_key_field.text.return_value = "newk"
    ui.meta_value_field.text.return_value = "newv"
    ui.meta_units_field.text.return_value = "newu"

    ui.meta_table.currentRow.return_value = 0
    ui.meta_table.item.side_effect = [
        MagicMock(text=lambda: "oldk"),
        MagicMock(text=lambda: "oldv"),
        MagicMock(text=lambda: "oldu"),
    ]

    controller._fill_current_info_tab = MagicMock()

    controller._metadata_edits("update")
    service.update_metadata.assert_called_once()


def test_metadata_edit_delete(controller, ui, service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=make_irods_path("/x"))
    controller.model.metadata_cache = {}
    controller.model.updated_info_tabs = []

    ui.meta_key_field.text.return_value = "k"
    ui.meta_value_field.text.return_value = "v"
    ui.meta_units_field.text.return_value = "u"

    controller._fill_current_info_tab = MagicMock()

    controller._metadata_edits("delete")
    service.delete_metadata.assert_called_once()


def test_metadata_edit_invalid_selection(controller, ui):
    controller._validate_selection = MagicMock(return_value=False)
    controller._metadata_edits("add")
    ui.error_label.setText.assert_not_called()


def test_metadata_edit_exception(controller, ui, service, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    controller._item_path = MagicMock(return_value=make_irods_path("/x"))
    service.add_metadata.side_effect = Exception("fail")

    ui.meta_key_field.text.return_value = "k"
    ui.meta_value_field.text.return_value = "v"
    ui.meta_units_field.text.return_value = "u"

    controller._metadata_edits("add")
    ui.error_label.setText.assert_called()

# acls

def test_fill_tab_permissions(controller, ui, service):
    controller.model.get_cached_acls = MagicMock(return_value=[("u","z","read","")])
    controller._render_acls = MagicMock()
    controller._fill_tab("permissions", MagicMock(), 0)
    controller._render_acls.assert_called_once()

def test_render_acls(controller, ui):
    path = MagicMock()
    path.collection_exists.return_value = True
    with patch("ibridgesgui.browser_controller.get_irods_item") as get_item:
        get_item.return_value.owner_name = "owner"
        controller._render_acls([("u","z","read","")], path)
        ui.owner_label.setText.assert_called_with("owner")


def test_load_permission(controller, ui):
    index = MagicMock(row=lambda: 0)
    controller._load_permission(index)
    ui.acl_user_field.setText.assert_called()


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

def test_update_permission_missing_user(controller, ui):
    controller._validate_selection = MagicMock(return_value=True)
    ui.acl_user_field.text.return_value = ""
    ui.acl_box.currentText.return_value = "read"
    controller._update_permission()
    ui.error_label.setText.assert_called()

def test_update_permission_inherit_on_dataobject(controller, ui, make_irods_path):
    controller._validate_selection = MagicMock(return_value=True)
    path = make_irods_path("/x")
    path.dataobject_exists = lambda: True
    controller._item_path = MagicMock(return_value=path)

    ui.acl_user_field.text.return_value = "u"
    ui.acl_zone_field.text.return_value = "z"
    ui.acl_box.currentText.return_value = "Newly added items to collection will inherit permissions"
    ui.recursive_box.currentText.return_value = "False"

    controller._update_permission()
    ui.error_label.setText.assert_called()

def test_update_permission_invalid_user(controller, ui, service, make_irods_path):
    from irods.exception import CAT_INVALID_USER
    controller._validate_selection = MagicMock(return_value=True)
    path = make_irods_path("/x")
    controller._item_path = MagicMock(return_value=path)

    service.set_acl.side_effect = CAT_INVALID_USER()

    ui.acl_user_field.text.return_value = "u"
    ui.acl_zone_field.text.return_value = "z"
    ui.acl_box.currentText.return_value = "read"
    ui.recursive_box.currentText.return_value = "False"

    controller._update_permission()
    ui.error_label.setText.assert_called()

def test_update_permission_missing_access(controller, ui):
    controller._validate_selection = MagicMock(return_value=True)
    ui.acl_user_field.text.return_value = "u"
    ui.acl_box.currentText.return_value = ""
    controller._update_permission()
    ui.error_label.setText.assert_called()


# replicas

def test_fill_tab_replicas(controller, ui, service):
    controller.model.get_cached_replicas = MagicMock(return_value=[("r1",)])
    controller._render_replicas = MagicMock()
    controller._fill_tab("replicas", MagicMock(), 0)
    controller._render_replicas.assert_called_once()

def test_render_replicas_empty(controller, ui):
    controller._render_replicas([])
    ui.replica_table.setRowCount.assert_called_with(0)


# preview

def test_fill_tab_preview(controller, ui):
    controller.model.get_cached_preview = MagicMock(return_value=["content"])
    with patch("ibridgesgui.browser_controller.populate_textfield") as pop:
        controller._fill_tab("preview", MagicMock(), 0)
        pop.assert_called_once()

def test_compute_preview_collection(controller):
    path = MagicMock()
    path.collection_exists.return_value = True
    path.dataobject_exists.return_value = False

    # Create mocks for subcollections and data objects
    sc = MagicMock()
    sc.name = "sub"

    do = MagicMock()
    do.name = "obj"

    # Mock the service call
    controller.service.list_collection.return_value = ([sc], [do])

    out = controller._compute_preview(path)

    assert "Collections:" in out
    assert "sub" in out
    assert "DataObjects:" in out
    assert "obj" in out

def test_compute_preview_dataobject_success(controller, service):
    path = MagicMock()
    path.collection_exists.return_value = False
    path.dataobject_exists.return_value = True
    path.name = "file.txt"
    service.stream_obj.return_value = ["content"]
    out = controller._compute_preview(path)
    assert out == ["content"]

def test_compute_preview_dataobject_exception(controller, service):
    path = MagicMock()
    path.collection_exists.return_value = False
    path.dataobject_exists.return_value = True
    path.name = "file.txt"
    service.stream_obj.side_effect = Exception("fail")
    out = controller._compute_preview(path)
    assert "No Preview" in out[0]

def test_compute_preview_no_preview(controller):
    path = MagicMock()
    path.collection_exists.return_value = False
    path.dataobject_exists.return_value = False
    out = controller._compute_preview(path)
    assert "No Preview" in out[0]


# info tabs

def test_fill_current_info_tab_no_selection(controller, ui):
    controller._validate_selection = MagicMock(return_value=False)
    controller._fill_current_info_tab()
    ui.error_label.setText.assert_not_called()

def test_fill_current_info_tab_invalid_selection(controller, ui):
    controller._validate_selection = MagicMock(return_value=False)
    controller._fill_current_info_tab()
    ui.error_label.setText.assert_not_called()

def test_fill_current_info_tab_no_update_needed(controller, ui):
    controller._validate_selection = MagicMock(return_value=True)
    controller.model.needs_tab_update = MagicMock(return_value=False)
    controller._fill_tab = MagicMock()
    controller._fill_current_info_tab()
    controller._fill_tab.assert_not_called()

def test_fill_current_info_tab_exception(controller, ui):
    controller._validate_selection = MagicMock(return_value=True)
    controller.model.needs_tab_update = MagicMock(return_value=True)
    controller._fill_tab = MagicMock(side_effect=Exception("fail"))
    controller._fill_current_info_tab()
    ui.error_label.setText.assert_called()


# click rows in table

def test_on_row_clicked_negative_row(controller, ui):
    ui.browser_table.currentRow.return_value = -1
    controller._fill_current_info_tab = MagicMock()
    controller._on_row_clicked()
    controller._fill_current_info_tab.assert_not_called()

def test_on_row_clicked_valid(controller, ui):
    ui.browser_table.currentRow.return_value = 2
    controller.model.on_row_clicked = MagicMock()
    controller._fill_current_info_tab = MagicMock()
    controller._on_row_clicked()
    controller.model.on_row_clicked.assert_called_once_with(2)
    controller._fill_current_info_tab.assert_called_once()



# test calling widgets from top row buttons
def test_create_collection_calls_dialog_and_refresh(controller, ui):
    with patch("ibridgesgui.browser_controller.CreateCollection") as dlg:
        instance = dlg.return_value
        instance.exec = MagicMock()
        controller._set_path = MagicMock()

        controller.create_collection()

        dlg.assert_called_once()
        instance.exec.assert_called_once()
        controller._set_path.assert_called_once()

def test_rename_item_invalid_selection(controller, ui):
    controller._validate_selection = MagicMock(return_value=False)
    controller.rename_item()
    ui.error_label.setText.assert_not_called()

def test_download_data_invalid_selection(controller, ui):
    controller._validate_selection = MagicMock(return_value=False)
    controller.download_data()
    ui.error_label.setText.assert_not_called()

def test_upload_data_not_collection(controller, ui):
    controller.model.current_path.collection_exists = lambda: False
    controller.upload_data()
    ui.error_label.setText.assert_called()



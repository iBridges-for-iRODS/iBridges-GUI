from unittest.mock import MagicMock, patch
import PySide6

def test_delete_data_permission_error(controller, mock_ui, mock_service):
    # Mock table row selection
    mock_ui.browser_table.currentRow = MagicMock(return_value=0)

    # Mock table item
    item = MagicMock()
    item.text.return_value = "file.txt"
    mock_ui.browser_table.item = MagicMock(return_value=item)

    # Mock iRODS path
    path = MagicMock()
    path.__truediv__.return_value = path
    path.remove.side_effect = PermissionError()
    mock_service.path_from_text.return_value = path

    # Mock confirmation dialog
    with patch("PySide6.QtWidgets.QMessageBox.critical",
               return_value=PySide6.QtWidgets.QMessageBox.StandardButton.Yes):
        controller.delete_data()

    assert "No permissions" in mock_ui.error_label.text()


def test_add_metadata_calls_service(controller, mock_ui, mock_service):
    mock_ui.browser_table.currentRow = MagicMock(return_value=0)
    mock_ui.meta_key_field.setText("k")
    mock_ui.meta_value_field.setText("v")
    mock_ui.meta_units_field.setText("u")

    path = MagicMock()
    mock_service.path_from_text.return_value = path
    controller._get_item_path = MagicMock(return_value=path)

    controller._metadata_edits("add")

    mock_service.add_metadata.assert_called_once_with(path, "k", "v", "u")


def test_update_permission_invalid_user(controller, mock_ui, mock_service):
    mock_ui.browser_table.currentRow = MagicMock(return_value=0)
    path = MagicMock()
    path.dataobject_exists.return_value = False
    controller._get_item_path = MagicMock(return_value=path)

    mock_ui.acl_user_field.setText("")
    mock_ui.acl_box.currentText.return_value = "read"

    controller.update_permission()

    assert "Please provide a user" in mock_ui.error_label.text()


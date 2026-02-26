from unittest.mock import patch
from unittest.mock import MagicMock

def test_load_browser_table_nonexistent_collection(controller, mock_ui, mock_service):
    mock_service.path_from_text.return_value.collection_exists.return_value = False

    controller.load_browser_table()

    assert mock_ui.browser_table.rowCount() == 0
    assert "Collection does not exist" in mock_ui.error_label.text()


def test_load_browser_table_populates_table(controller, mock_ui, mock_service):
    path = MagicMock()
    path.collection_exists.return_value = True
    mock_service.path_from_text.return_value = path

    mock_service.list_table_rows.return_value = [
        ("col1", "collection"),
        ("file1", "dataobject"),
    ]

    with patch("ibridgesgui.browser_controller.populate_table") as populate:
        controller.load_browser_table()
        populate.assert_called_once()


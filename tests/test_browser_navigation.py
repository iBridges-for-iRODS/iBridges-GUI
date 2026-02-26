from unittest.mock import MagicMock

def test_init_browser_connects_signals(controller, mock_ui):
    # Replace connect() with MagicMocks
    mock_ui.input_path.returnPressed = MagicMock()
    mock_ui.refresh_button.clicked = MagicMock()
    mock_ui.home_button.clicked = MagicMock()
    mock_ui.parent_button.clicked = MagicMock()

    controller.init_browser()

    mock_ui.input_path.returnPressed.connect.assert_called_with(controller.refresh_browser)
    mock_ui.refresh_button.clicked.connect.assert_called_with(controller.refresh_browser)
    mock_ui.home_button.clicked.connect.assert_called_with(controller.set_input_path_to_home)
    mock_ui.parent_button.clicked.connect.assert_called_with(controller.set_input_path_to_parent)


def test_update_input_path_calls_model_and_loads_table(controller, mock_ui):
    controller.model.reset_selection_cache = MagicMock()
    controller.load_browser_table = MagicMock()

    controller.update_input_path("/temp")

    assert mock_ui.input_path.text() == "/temp"
    controller.model.reset_selection_cache.assert_called_once()
    controller.load_browser_table.assert_called_once()


def test_refresh_browser_calls_service_and_updates(controller, mock_service):
    controller.update_input_path = MagicMock()
    mock_service.path_from_text.return_value = "/abc"

    controller.refresh_browser()

    mock_service.path_from_text.assert_called_once()
    controller.update_input_path.assert_called_with("/abc")


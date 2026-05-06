import builtins
from unittest.mock import patch, MagicMock

import ibridgesgui.__main__ as main_module


def test_main_entry_point():
    # Mock QApplication and QStackedWidget so no GUI is created
    with patch("ibridgesgui.__main__.QApplication") as MockApp, \
         patch("ibridgesgui.__main__.QStackedWidget") as MockStack, \
         patch("ibridgesgui.__main__.ConfigManager") as MockConfig, \
         patch("ibridgesgui.__main__.config_module") as MockConfigModule, \
         patch("ibridgesgui.__main__.MainWindow") as MockMainWindow, \
         patch("ibridgesgui.__main__.setproctitle") as MockSetProc:

        mock_app = MagicMock()
        MockApp.return_value = mock_app

        mock_stack = MagicMock()
        MockStack.return_value = mock_stack

        mock_cfg = MagicMock()
        mock_cfg.get_log_level.return_value = "debug"
        MockConfig.return_value = mock_cfg

        # Run main()
        main_module.main(session=None)

        # Assertions
        MockSetProc.setproctitle.assert_called_once()
        MockConfig.assert_called_once()
        MockConfigModule.init_logger.assert_called_once()
        MockConfigModule.ensure_irods_location.assert_called_once()

        MockApp.assert_called_once()
        MockStack.assert_called_once()

        MockMainWindow.assert_called_once()

        # Ensure the window was added and shown
        mock_stack.addWidget.assert_called_once()
        mock_stack.show.assert_called_once()

        # Ensure the Qt event loop was started
        mock_app.exec.assert_called_once()


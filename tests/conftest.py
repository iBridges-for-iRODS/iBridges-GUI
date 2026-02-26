import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import (
    QLineEdit, QTableWidget, QLabel, QTabWidget, QWidget, QPushButton
)

from ibridgesgui.browser_controller import BrowserController


@pytest.fixture
def mock_ui(qtbot):
    ui = MagicMock()

    # Path input
    ui.input_path = QLineEdit()
    qtbot.addWidget(ui.input_path)

    # Buttons
    ui.refresh_button = QPushButton()
    ui.home_button = QPushButton()
    ui.parent_button = QPushButton()
    ui.upload_button = QPushButton()
    ui.download_button = QPushButton()
    ui.create_coll_button = QPushButton()
    ui.rename_button = QPushButton()
    ui.delete_button = QPushButton()
    ui.add_meta_button = QPushButton()
    ui.update_meta_button = QPushButton()
    ui.delete_meta_button = QPushButton()
    ui.add_acl_button = QPushButton()

    # Tables
    ui.browser_table = QTableWidget()
    ui.meta_table = QTableWidget()
    ui.acl_table = QTableWidget()
    ui.replica_table = QTableWidget()

    # Info tabs
    ui.info_tabs = QTabWidget()
    ui.info_tabs.addTab(QWidget(), "metadata")
    ui.info_tabs.addTab(QWidget(), "permissions")
    ui.info_tabs.addTab(QWidget(), "replicas")
    ui.info_tabs.addTab(QWidget(), "preview")

    # Other UI elements
    ui.error_label = QLabel()
    ui.preview_browser = QLabel()
    ui.no_meta_label = QLabel()
    ui.acl_user_field = QLineEdit()
    ui.acl_zone_field = QLineEdit()
    ui.acl_box = MagicMock()
    ui.recursive_box = MagicMock()
    ui.owner_label = QLabel()
    ui.meta_key_field = QLineEdit()
    ui.meta_value_field = QLineEdit()
    ui.meta_units_field = QLineEdit()

    return ui


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.home_path.return_value = "/home/irods"
    return service


@pytest.fixture
def controller(mock_ui, mock_service):
    with patch("ibridgesgui.browser_controller.IrodsBrowserService", return_value=mock_service):
        ctrl = BrowserController(mock_ui, session=None, app_name="test")
        return ctrl


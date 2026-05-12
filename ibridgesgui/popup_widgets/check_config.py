"""Dialog for creating, editing, and validating iRODS environment JSON."""

from __future__ import annotations

import json
from pathlib import Path

from ibridges.util import find_environment_provider, get_environment_providers
from PySide6 import QtCore, QtWidgets

from ibridgesgui.config import (
    _read_json,
    check_irods_config,
    save_irods_config,
)
from ibridgesgui.gui_utils import populate_textfield
from ibridgesgui.popup_widgets.base import UiDialogMixin
from ibridgesgui.ui_files.configCheck import Ui_configCheck


class CheckConfig(UiDialogMixin, QtWidgets.QDialog, Ui_configCheck):
    """Popup dialog to edit and validate an iRODS environment.json file."""

    ui_filename = "configCheck.ui"

    def __init__(self, logger, env_path: Path) -> None:
        """Init."""
        super().__init__()
        self._init_ui()

        self.logger = logger
        self.env_path = env_path
        self._busy = False

        self.setWindowTitle("Create, edit and inspect iRODS environment")

        providers = get_environment_providers()
        self.templates = {
            f"Template - {key} ({descr})": key
            for p in providers
            for key, descr in p.descriptions.items()
        }

        self._init_env_box()

        self.envbox.activated.connect(self.load)
        self.new_button.clicked.connect(self.create_env)
        self.check_button.clicked.connect(self.check_env)
        self.save_button.clicked.connect(self.save_env)
        self.save_as_button.clicked.connect(self.save_env_as)
        self.close_button.clicked.connect(self.close)

    def _init_env_box(self) -> None:
        """Populate the environment selection box."""
        self.envbox.clear()
        env_files = [""] + [p.name for p in self.env_path.glob("*.json")]
        self.envbox.addItems(env_files)
        self.envbox.addItems(self.templates.keys())
        self.envbox.setCurrentIndex(0)

    def _enable_buttons(self, enable: bool) -> None:
        """Enable or disable all action buttons safely."""
        buttons = [
            self.envbox,
            self.new_button,
            self.check_button,
            self.save_button,
            self.save_as_button,
            self.close_button,
        ]

        if not enable:
            # Disable immediately and block signals
            for btn in buttons:
                btn.blockSignals(True)
                btn.setEnabled(False)
            return

        # Re-enable AFTER the UI has finished updating
        def _reenable():
            for btn in buttons:
                btn.setEnabled(True)
                btn.blockSignals(False)

        QtCore.QTimer.singleShot(0, _reenable)

    def load(self) -> None:
        """Load either a template or an existing environment file."""
        selected = self.envbox.currentText()
        if selected.startswith("Template - "):
            self._load_template(self.templates[selected])
        else:
            self._load_env_file(self.env_path / selected)

    def _load_template(self, template_key: str) -> None:
        """Load a template environment JSON."""
        self.error_label.clear()
        provider = find_environment_provider(get_environment_providers(), template_key)
        env_json = provider.environment_json(
            template_key, *[q.upper() for q in provider.questions]
        ).split("\n")
        populate_textfield(self.env_field, env_json)
        self.error_label.setText("Please fill in your user name.")

    def _load_env_file(self, env_file: Path) -> None:
        """Load an existing environment JSON file."""
        self.error_label.clear()
        try:
            content = json.dumps(
                _read_json(env_file),
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
            )
            populate_textfield(self.env_field, content)
        except Exception as err:  # noqa: BLE001
            self.error_label.setText(str(err))

    def create_env(self) -> None:
        """Insert a default environment template."""
        self.error_label.clear()
        self.envbox.setCurrentIndex(0)
        env = {
            "irods_host": "<THE SERVER NAME OR IP ADDRESS>",
            "irods_port": 1247,
            "irods_home": "<A DEFAULT LOCATION ON THE IRODS SERVER AS YOUR HOME>",
            "irods_default_resource": "<A DEFAULT IRODS RESOURCE NAME>",
            "irods_user_name": "<YOUR IRODS USERNAME>",
            "irods_zone_name": "<THE IRODS ZONE NAME>",
            "irods_authentication_scheme": "pam",
            "irods_encryption_algorithm": "AES-256-CBC",
            "irods_encryption_key_size": 32,
            "irods_encryption_num_hash_rounds": 16,
            "irods_encryption_salt_size": 8,
            "irods_client_server_policy": "CS_NEG_REQUIRE",
            "irods_client_server_negotiation": "request_server_negotiation",
        }
        populate_textfield(
            self.env_field,
            json.dumps(env, sort_keys=True, indent=4, separators=(",", ": ")),
        )


    def check_env(self) -> None:
        """Validate the JSON in the text field."""
    
        if self._busy:
            return
        self._busy = True
    
        # Block signals on ALL interactive widgets
        widgets = [
            self.envbox,
            self.new_button,
            self.check_button,
            self.save_button,
            self.save_as_button,
            self.close_button,
        ]
        for w in widgets:
            w.blockSignals(True)
            w.setEnabled(False)
    
        self.error_label.clear()
    
        # Perform the validation
        try:
            msg = check_irods_config(json.loads(self.env_field.toPlainText()))
        except json.JSONDecodeError as err:
            msg = f"JSON decoding error: {err.msg} at position {err.pos}."
    
        self.error_label.setText(msg)
    
        # Re-enable AFTER the event loop has flushed
        def _reenable():
            for w in widgets:
                w.setEnabled(True)
                w.blockSignals(False)
            self._busy = False
    
        QtCore.QTimer.singleShot(1, _reenable)
    

    def save_env(self) -> None:
        """Save the JSON to the currently selected file."""
        self.error_label.clear()
        env_file = self.env_path / self.envbox.currentText()
        if not env_file.is_file():
            self.error_label.setText("Choose 'Save as' to save")
            return

        try:
            save_irods_config(env_file, json.loads(self.env_field.toPlainText()))
            self.error_label.setText(f"Configuration saved as {env_file}")
        except json.JSONDecodeError:
            self.error_label.setText("Incorrectly formatted. Click 'Check' for details.")

    def save_env_as(self) -> None:
        """Save the JSON to a new file."""
        self.error_label.clear()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save as File", str(self.env_path), "(*.json)"
        )
        if not file_path:
            return

        if not file_path.endswith(".json"):
            self.error_label.setText("ERROR: File must have .json extension.")
            return

        try:
            save_irods_config(file_path, json.loads(self.env_field.toPlainText()))
            self.error_label.setText(f"Configuration saved as {file_path}")
        except json.JSONDecodeError:
            self.error_label.setText("Incorrectly formatted. Click 'Check' for details.")

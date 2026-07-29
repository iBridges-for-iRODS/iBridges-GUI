"""Popup dialogs used throughout the iBridges GUI."""

from ibridgesgui.popup_widgets.check_config import CheckConfig
from ibridgesgui.popup_widgets.create_collection import CreateCollection
from ibridgesgui.popup_widgets.create_directory import CreateDirectory
from ibridgesgui.popup_widgets.download_data import DownloadData
from ibridgesgui.popup_widgets.rename_item import Rename
from ibridgesgui.popup_widgets.resc_tree import RescInfoDialog
from ibridgesgui.popup_widgets.upload_data import UploadData

__all__ = [
    "CreateCollection",
    "CreateDirectory",
    "Rename",
    "CheckConfig",
    "UploadData",
    "DownloadData",
    "RescInfoDialog"
]

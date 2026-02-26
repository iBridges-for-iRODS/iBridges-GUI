import logging
from typing import Iterable, Tuple, List

import irods.exception
from ibridges import IrodsPath
from ibridges.permissions import Permissions
from ibridges.util import obj_replicas

from ibridgesgui.gui_utils import get_irods_item


class IrodsBrowserService:
    """All iRODS-related operations used by the Browser tab."""

    def __init__(self, session, logger: logging.Logger):
        self.session = session
        self.logger = logger

    # -------- navigation / listing --------

    def path_from_text(self, text: str) -> IrodsPath:
        return IrodsPath(self.session, text)

    def home_path(self) -> IrodsPath:
        return IrodsPath(self.session)

    def parent_path(self, text: str) -> IrodsPath:
        return IrodsPath(self.session, text).parent

    def list_collection(
        self, path: IrodsPath
    ) -> Tuple[Iterable, Iterable]:
        """Return (subcollections, data_objects) for a collection."""
        coll = path.collection
        return coll.subcollections, coll.data_objects

    # -------- replicas --------

    def replicas_for(self, path: IrodsPath):
        if not path.dataobject_exists():
            return []
        obj = path.dataobject
        return obj_replicas(obj)

    # -------- metadata --------

    def metadata_for(self, path: IrodsPath):
        return list(path.meta)

    def add_metadata(self, path: IrodsPath, key: str, value: str, units: str):
        path.meta.add(key, value, units)

    def update_metadata(
        self,
        path: IrodsPath,
        old_key: str,
        old_value: str,
        old_units: str,
        new_key: str,
        new_value: str,
        new_units: str,
    ):
        # will be filled later
        pass

    def delete_metadata(self, path: IrodsPath, key: str, value: str, units: str):
        path.meta.delete(key, value, units)

    # -------- ACLs / permissions --------

    def permissions_for(self, path: IrodsPath):
        obj = get_irods_item(path)
        return Permissions(self.session, obj)

    # -------- destructive operations --------

    def delete_path(self, path: IrodsPath):
        path.remove()

    # -------- main browser table --------
    
    def list_table_rows(self, path: IrodsPath):
        """Return rows for the browser table (collections first, then data objects)."""
        coll = path.collection
    
        coll_rows = [
            (
                "C-",
                subcoll.name,
                "",
                "",
                subcoll.create_time.strftime("%d-%m-%Y"),
                subcoll.modify_time.strftime("%d-%m-%Y %H:%M"),
            )
            for subcoll in coll.subcollections
        ]
    
        obj_rows = [
            (
                max(repl[4] for repl in obj_replicas(obj)),
                obj.name,
                str(obj.size),
                obj.checksum,
                obj.create_time.strftime("%d-%m-%Y"),
                obj.modify_time.strftime("%d-%m-%Y %H:%M"),
            )
            for obj in coll.data_objects
        ]
    
        return coll_rows + obj_rows


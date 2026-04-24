"""iRODS functionality for browser."""

import logging
from typing import Iterable, Tuple

from ibridges import IrodsPath
from ibridges.permissions import Permissions
from ibridges.util import obj_replicas

from ibridgesgui.gui_utils import get_irods_item


class IrodsBrowserService:
    """All iRODS-related operations used by the Browser tab."""

    def __init__(self, session, logger: logging.Logger):
        """Init."""
        self.session = session
        self.logger = logger

    # -------- navigation / listing --------

    def path_from_text(self, text: str) -> IrodsPath:
        """Convert to IrodsPath."""
        return IrodsPath(self.session, text)

    def home_path(self) -> IrodsPath:
        """Get home path."""
        return IrodsPath(self.session)

    def parent_path(self, text: str) -> IrodsPath:
        """Determine parent."""
        return IrodsPath(self.session, text).parent

    def list_collection(self, path: IrodsPath) -> Tuple[Iterable, Iterable]:
        """Return (subcollections, data_objects) for a collection."""
        coll = path.collection
        return coll.subcollections, coll.data_objects

    def stream_obj(self, path: IrodsPath) -> str:
        """Stream the first chars of a data object."""
        with path.open("r") as stream:
            content = [stream.read(1024).decode("utf-8")]
        return content

    # -------- preview ---------

    def compute_preview(self, irods_path: IrodsPath):
        """Return preview content for a collection or data object."""
        # Collections: list subcollections + objects
        if irods_path.collection_exists():
            subcolls, objs = self.list_collection(irods_path)
            content = ["Collections:", "-----------------"]
            content.extend([sc.name for sc in subcolls])
            content.extend(["", "DataObjects:", "-----------------"])
            content.extend([do.name for do in objs])
            return content

        # Data objects: preview text-like files
        if irods_path.dataobject_exists():
            ext = irods_path.name.split(".")[-1] if "." in irods_path.name else ""
            if ext in ("txt", "json", "csv"):
                try:
                    return self.stream_obj(irods_path)
                except Exception as error:
                    return [
                        f"No Preview for: {irods_path}",
                        repr(error),
                        "Storage resource might be down.",
                    ]
            return [f"No Preview for: {irods_path}"]

        return [f"No Preview for: {irods_path}"]

    # -------- replicas --------

    def get_replicas(self, path: IrodsPath):
        """Retrieve replicas."""
        if not path.dataobject_exists():
            return []
        obj = path.dataobject
        return obj_replicas(obj)

    # -------- metadata --------

    def get_metadata(self, irods_path):
        """Return metadata as a list of (key, value, units) tuples."""
        try:
            return [(avu.name, avu.value, avu.units) for avu in irods_path.meta]
        except Exception as err:
            raise RuntimeError(f"Failed to load metadata for {irods_path}: {err}") from err

    def add_metadata(self, path: IrodsPath, key: str, value: str, units: str):
        """Add metadata to coll or obj."""
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
        """Update a single AVU on a path."""
        # Retrieve the specific AVU
        avu = path.meta[old_key, old_value, old_units]

        # Mutate it in place
        avu.key = new_key
        avu.value = new_value
        avu.units = new_units

    def delete_metadata(self, path: IrodsPath, key: str, value: str, units: str):
        """Delete metadata."""
        path.meta.delete(key, value, units)

    # -------- ACLs / permissions --------

    def normalize_acls(self, acls):
        """Normalize iRODS ACLs into UI-friendly form."""
        clean = []
        for user, zone, perm, status in acls:
            if perm == "read_object":
                perm = "read"
            elif perm == "modify_object":
                perm = "write"
            clean.append((user, zone, perm, status))
        return clean

    def get_acls(self, path: IrodsPath):
        """Return a list of (user_name, user_zone, access_name, inheritance_flag)."""
        obj = get_irods_item(path)
        perms = Permissions(self.session, obj)
        inheritance = ""

        if path.collection_exists():
            inheritance = f"{path.collection.inheritance}"

        return [(p.user_name, p.user_zone, p.access_name, inheritance) for p in perms]

    def set_acl(
        self,
        path: IrodsPath,
        user_name: str,
        user_zone: str,
        access: str,
        recursive: bool,
    ):
        """Apply an ACL change to a collection or data object."""
        obj = get_irods_item(path)
        perms = Permissions(self.session, obj)
        perms.set(
            perm=access,
            user=user_name,
            zone=user_zone,
            recursive=recursive,
        )

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

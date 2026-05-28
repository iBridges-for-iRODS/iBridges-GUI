"""iRODS functionality for browser."""

import logging
from typing import Iterable, Tuple
from irods.exception import CAT_NO_ACCESS_PERMISSION

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

    def is_text_bytes(self, data: bytes) -> bool:
        # Null bytes → definitely binary
        if b"\x00" in data:
            return False
    
        # Try common encodings
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                data.decode(enc)
                return True
            except UnicodeDecodeError:
                continue
    
        return False


    def compute_preview(self, irods_path: IrodsPath):
        """Return preview content for a collection or data object."""
    
        # Collections
        if irods_path.collection_exists():
            subcolls, objs = self.list_collection(irods_path)
            content = ["Collections:", "-----------------"]
            content.extend([sc.name for sc in subcolls])
            content.extend(["", "DataObjects:", "-----------------"])
            content.extend([do.name for do in objs])
            return content
    
        # Data objects
        if irods_path.dataobject_exists():
            try:
                # Read only the first few KB for sniffing
                with irods_path.open("r") as stream:
                    head = stream.read(4096)
            except Exception as error:
                return [
                    f"No Preview for: {irods_path}",
                    repr(error),
                    "Storage resource might be down.",
                ]
    
            # Decide based on content, not suffix
            if self.is_text_bytes(head):
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

    def find_irods_exception(self, exc):
        """Walk the exception chain to find the underlying iRODS exception."""
        
        # NOTE: Work around for ibridges #412
        seen = set()
        stack = [exc]

        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)

            # Found the real iRODS exception
            if isinstance(current, CAT_NO_ACCESS_PERMISSION):
                return current

            # Walk deeper
            if current.__cause__:
                stack.append(current.__cause__)
            if current.__context__:
                stack.append(current.__context__)

        return None


    def add_metadata(self, path: IrodsPath, key: str, value: str, units: str):
        """Add metadata to coll or obj."""
        try:
            path.meta.add(key, value, units)
        except Exception as err:
            # user has no permission to modify metadata
            irods_exc = self.find_irods_exception(err)
            if irods_exc:
                raise irods_exc
            raise err

    def _has_object_write_own(self, acls, username, zonename):
        WRITE_LEVEL = {"own", "write_object", "modify_object"}

        return any(
            acc.access_name in WRITE_LEVEL
            and acc.user_name == username
            and acc.user_zone == zonename
            for acc in acls
        )

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
        # NOTE: workraound for ibridgs 412 second part
        if path.collection_exists():
            acls = Permissions(self.session, path.collection)
        else:
            acls = Permissions(self.session, path.dataobject)
        if not self._has_object_write_own(acls, self.session.irods_session.username, self.session.irods_session.zone):
            raise CAT_NO_ACCESS_PERMISSION("You need object write permissions to update metadata.")

        try:
            # Retrieve the specific AVU
            avu = path.meta[old_key, old_value, old_units]

            # Mutate it in place
            avu.key = new_key
            avu.value = new_value
            avu.units = new_units
        except Exception as err:
            # user has no permission to modify metadata
            irods_exc = self.find_irods_exception(err)
            if irods_exc:
                raise irods_exc
            raise err

    def delete_metadata(self, path: IrodsPath, key: str, value: str, units: str):
        """Delete metadata."""
        try:
            path.meta.delete(key, value, units)
        except Exception as err:
            # user has no permission to modify metadata
            irods_exc = self.find_irods_exception(err)
            if irods_exc:
                raise irods_exc
            raise err

    # -------- ACLs / permissions --------

    def get_acl_strings(self):
        PERM_MAP = {
            "read_object": "read",
            "modify_object": "write",
            "null": "delete",
        }
        perm = Permissions(self.session, self.session.home)
        avail = [PERM_MAP.get(perm_str, perm_str) 
                        for (perm_str, _) in perm.available_permissions.items()]
        return avail

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

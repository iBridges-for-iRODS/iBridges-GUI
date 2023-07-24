"""Manipulate paths as strings behaving like pathlib Paths.

"""
import logging
import os
import pathlib
import shutil

import irods.path


def is_posix() -> bool:
    """Determine POSIXicity.

    Returns
    -------
    bool
        Whether or not this is a POSIX operating system.
    """
    return os.name == 'posix'


class PurePath(str):
    """A platform-dependent pure path without file system functionality
    based on the best of str and pathlib.

    """
    _path = None
    _posix = None

    def __new__(cls, *args):
        """Instantiate a PurePath from whole paths or segments of paths,
        absolute or logical.

        Returns
        -------
        PurePath
            Uninitialized instance.

        """
        if is_posix() or cls._posix:
            path = pathlib.PurePosixPath(*args)
        else:
            path = pathlib.PureWindowsPath(*args)
        return super().__new__(cls, path.__str__())

    def __init__(self, *args):
        """Initialize a PurePath.

        """
        self.args = normalize(*args, posix=self._posix)

    def __repr__(self) -> str:
        """Render Paths into a representation.

        Returns
        -------
        str
            Representation of the pathlib.Path.

        """
        return f'{self.__class__.__name__}("{self.path.__str__()}")'

    def __str__(self) -> str:
        """Render Paths into a string.

        Returns
        -------
        str
            String value of the pathlib.Path.

        """
        return self.path.__str__()

    @property
    def name(self) -> str:
        """The final path component, if any.

        Returns
        -------
        str
            Name of the Path.

        """
        return self.path.name

    @property
    def parent(self):
        """The logical parent of the path.

        Returns
        -------
        *Path
            Parent of the Path.

        """
        return type(self)(str(self.path.parent))

    @property
    def parts(self) -> tuple:
        """An object providing sequence-like access to the components
        in the filesystem path.

        Returns
        -------
        tuple
            Parts of the Path.

        """
        return self.path.parts

    @property
    def path(self) -> pathlib.PurePath:
        """A pathlib.Path instance providing extra functionality.

        Returns
        -------
        pathlib.PurePath
            Initialized from self.args.

        """
        if self._path is None:
            if is_posix() or self._posix:
                self._path = pathlib.PurePosixPath(*self.args)
            else:
                self._path = pathlib.PureWindowsPath(*self.args)
        return self._path

    @property
    def stem(self) -> str:
        """The final path component, minus its last suffix.

        Returns
        -------
        str
            Stem of the Path.

        """
        return self.path.stem

    @property
    def suffix(self) -> str:
        """The final component's last suffix, if any.  This includes
        the leading period. For example: '.txt'.

        Returns
        -------
        str
            Suffix of the path.

        """
        return self.path.suffix

    @property
    def suffixes(self) -> list:
        """A list of the final component's suffixes, if any.  These
        include the leading periods. For example: ['.tar', '.gz'].

        Returns
        -------
        list[str]
            Suffixes of the path.

        """
        return self.path.suffixes

    def joinpath(self, *args):
        """Combine this path with one or several arguments, and return
        a new path representing either a subpath (if all arguments are
        relative paths) or a totally different path (if one of the
        arguments is anchored).

        Returns
        -------
        *Path
            Joined Path.

        """
        return type(self)(
            str(self.path.joinpath(*normalize(*args, posix=self._posix))))

    def with_suffix(self, suffix: str):
        """Create a new path with the file `suffix` changed.  If the
        path has no `suffix`, add given `suffix`.  If the given
        `suffix` is an empty string, remove the `suffix` from the path.

        Parameters
        ----------
        suffix : str
            New extension for the file 'stem'.

        Returns
        -------
        *Path
            Suffix-updated Path.

        """
        return type(self)(str(self.path.with_suffix(suffix)))


class iRODSPath(PurePath, irods.path.iRODSPath):
    """A pure POSIX path without file system functionality based on the
    best of str, pathlib, and iRODSPath.  This path is normalized upon
    instantiation.

    """
    _posix = True

    def __new__(cls, *args):
        """Instantiate an iRODSPath.

        Returns
        -------
        iRODSPath
            Uninitialized instance.

        """
        path = pathlib.PurePosixPath(*args)
        return super().__new__(cls, path.__str__())


class LocalPath(PurePath):
    """A platform-dependent local path with file system functionality
    based on the best of str and pathlib.

    """

    def __new__(cls, *args, **kwargs):
        """Instantiate a LocalPath.

        Returns
        -------
        LocalPath
            Uninitialized instance.

        """
        if is_posix():
            path = pathlib.PosixPath(*args)
        else:
            path = pathlib.WindowsPath(*args)
        return super().__new__(cls, path.__str__())

    @property
    def path(self) -> pathlib.Path:
        """A pathlib.Path instance providing extra functionality.

        Returns
        -------
        pathlib.Path
            Initialized from self.args.

        """
        if self._path is None:
            if is_posix():
                self._path = pathlib.PosixPath(*self.args)
            else:
                self._path = pathlib.WindowsPath(*self.args)
        return self._path

    def absolute(self):
        """Determine an absolute version of this path, i.e., a path
        with a root or anchor.

        No normalization is done, i.e. all '.' and '..' will be kept
        along.  Use resolve() to get the canonical path to a file.

        Returns
        -------
        LocalPath
            Not normalized full path.

        """
        return type(self)(str(self.path.absolute()))

    def copy_path(self, target: str, squash: bool = False):
        """Copy this path to (not into) the target path, overwriting
        existing elements if that path exists and `squash` is True.

        The target path may be absolute or relative. Relative paths are
        interpreted relative to the current working directory, *not*
        the directory of the Path object.

        Parameters
        ----------
        target : str
            The path to replace.
        squash : bool
            Whether to overwrite path.

        """
        if self.is_file():
            shutil.copy(self, target, follow_symlinks = True)
            return
        options = {'symlinks': True}
        if squash:
            # This option works for Python 3.8+
            options['dirs_exist_ok'] = True
        try:
            shutil.copytree(self, target, **options)
        except FileExistsError as error:
            if squash:
                type(self)(target).rmdir(squash=True)
                shutil.copytree(self, target)
            else:
                logging.warning('Cannot copy to %s: %r', target, error)

    @classmethod
    def cwd(cls):
        """Give the current working directory.

        Returns
        -------
        LocalPath
            The current working directory path.

        """
        return cls(str(pathlib.Path.cwd()))

    def exists(self) -> bool:
        """Whether this path exists.

        Path.exists() sometimes raises an error prior to Python 3.8

        Returns
        -------
        bool
            Path exists or not.

        """
        try:
            return self.path.exists()
        except Exception as error:
            print(f'WARNING -- problem ({error}) determining if {self.path} exists')
            return False

    def expanduser(self):
        """Return a new path with expanded ~ and ~user constructs (as
        returned by os.path.expanduser)

        Returns
        -------
        LocalPath
            User-expanded Path.
        """
        try:
            return type(self)(str(self.path.expanduser()))
        except AttributeError:
            return type(self)(os.path.expanduser(self.path))

    def glob(self, pattern: str) -> iter:
        """Iterate over this subtree and yield all existing files (of
        any kind, including directories) matching the given relative
        `pattern`.

        Parameters
        ----------
        pattern : str
            Wildcard patter to match files.

        Returns
        -------
        iter
            Generator of matches.

        """
        return (type(self)(path) for path in self.path.glob(pattern=pattern))

    def is_dir(self) -> bool:
        """Whether this path is a directory.

        Path.is_dir() sometimes raises an error prior to Python 3.8

        Returns
        -------
        bool
            Is a directory (folder) or not.

        """
        try:
            return self.path.is_dir()
        except Exception as error:
            print(f'WARNING -- problem ({error}) determining if {self.path} is a directory')
            return False

    def is_file(self) -> bool:
        """Whether this path is a regular file (also True for symlinks
        pointing to regular files)

        Path.is_file() sometimes raises an error prior to Python 3.8

        Returns
        -------
        bool
            Is a regular file (symlink) or not.

        """
        try:
            return self.path.is_file()
        except Exception as error:
            print(f'WARNING -- problem ({error}) determining if {self.path} is a file')
            return False

    def mkdir(self, mode: int = 511, parents: bool = False, exist_ok: bool = False):
        """Create a new directory at this path.

        Parameters
        ----------
        mode : int
            Creation mode of the directory (folder).
        parents : bool
            Create the parents too?
        exist_ok : bool
            Okay if directory already exists?

        """
        try:
            self.path.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)
        except AttributeError:
            if not parents:
                if not self.path.exists():
                    os.mkdir(self.path, mode=mode)
            else:
                os.makedirs(self.path, mode=mode, exist_ok=exist_ok)

    def read_bytes(self) -> bytes:
        """Open the file in bytes mode, read it, and close the file.

        Returns
        -------
        bytes
            Bytes contents of the file.

        """
        return self.path.read_bytes()

    def read_text(self, encoding: str = None, errors: str = None) -> str:
        """Open the file in text mode, read it, and close the file.

        Parameters
        ----------
        encoding : str
            The name of the encoding used to decode or encode the file
            (see open()).
        errors : str
            Specifies how encoding errors are to be handled (see
            open()).

        Returns
        -------
        str
            String contents of the file.

        """
        return self.path.read_text(encoding=encoding, errors=errors)

    def rename_path(self, target: str):
        """Rename (move) this path to the target path.  `target` is not
        overwritten.  Use replace_path() if overwriting is desired.

        The target path may be absolute or relative. Relative paths are
        interpreted relative to the current working directory, *not*
        the directory of the Path object.

        Parameters
        ----------
        target : str
            The path to replace.

        Returns
        -------
        LocalPath
            The target path.

        """
        if not type(self)(target).exists():
            return type(self)(str(self.path.rename(target)))
        logging.warning('Cannot rename %s: directory exists', target)
        return self

    def replace_path(self, target: str, squash: bool = False):
        """Rename (move) this path to the target path, overwriting the
        directory if it exists, and overwriting any contents if `squash`
        is set.

        The target path may be absolute or relative. Relative paths are
        interpreted relative to the current working directory, *not*
        the directory of the Path object.

        Parameters
        ----------
        target : str
            The path to replace.
        squash : bool
            Whether to overwrite path.

        Returns
        -------
        LocalPath
            The target path if replaced, this path otherwise.

        """
        try:
            return type(self)(str(self.path.replace(target)))
        # Weird Windows PermissionError: [WinError 5] Access is denied:
        except PermissionError:
            if len(list(type(self)(target).glob('*'))) == 0:
                type(self)(target).rmdir(squash=True)
                return type(self)(str(self.path.replace(target)))
            if squash:
                type(self)(target).rmdir(squash=True)
                return type(self)(str(self.path.replace(target)))
            logging.warning('Cannot replace %s: directory not empty', target)
            return self
        # Directory not empty
        except OSError:
            if squash:
                type(self)(target).rmdir(squash=True)
                return type(self)(str(self.path.replace(target)))
            logging.warning('Cannot replace %s: directory not empty', target)
            return self

    def resolve(self):
        """Make the path absolute (full path with a root or anchor),
        resolving all symlinks on the way and also normalizing it (for
        example turning slashes into backslashes under Windows).

        Returns
        -------
        LocalPath
            Normalized full path with relative segments and symlinks
            resolved.

        """
        return type(self)(str(self.path.resolve()))

    def rmdir(self, squash: bool = False):
        """Remove this directory.  The directory must be empty unless
        `squash` is set.

        Parameters
        ----------
        squash : bool
            Whether to remove non-empty directory.
        """
        try:
            self.path.rmdir()
        # Weird Windows PermissionError: [WinError 5] Access is denied:
        except PermissionError:
            if len(list(self.glob('*'))) == 0:
                shutil.rmtree(self)
            else:
                if squash:
                    shutil.rmtree(self)
                else:
                    logging.warning('Cannot rmdir %s: directory not empty', self)
        # Directory not empty
        except OSError:
            if squash:
                shutil.rmtree(self)
            else:
                logging.warning('Cannot rmdir %s: directory not empty', self)

    def stat(self) -> os.stat_result:
        """Run os.stat() on this path.

        Returns
        -------
        os.stat_result
            Stat structure.

        """
        return self.path.stat()

    def unlink(self, missing_ok: bool = False):
        """Remove this file or link.  If the path is a directory, use
        rmdir() instead.

        Parameters
        ----------
        missing_ok : bool
            Ignore missing files/directories.

        """
        self.path.unlink(missing_ok=missing_ok)

    def write_bytes(self, data: bytes):
        """Open the file in bytes mode, write to it, and close the file.

        Parameters
        ----------
        data : bytes
            Information to write to file.

        """
        self.path.write_bytes(data=data)

    def write_text(self, data: str, encoding: str = None, errors: str = None):
        """

        Parameters
        ----------
        data : str
            Information to write to file.
        encoding : str
            The name of the encoding used to decode or encode the file
            (see open()).
        errors : str
            Specifies how encoding errors are to be handled (see
            open()).

        """
        self.path.write_text(data=data, encoding=encoding, errors=errors)


def normalize(*args, posix: bool) -> tuple:
    """Normalize (i.e. remove path separators) the incoming arguments
    and construct a sequence of path "parts".

    Parameters
    ----------
    posix : bool
        Does the output need to follow POSIX path conventions?

    Returns
    -------
    tuple
        Sequence of path "parts".

    """
    if args:
        if posix:
            argpath = pathlib.PurePosixPath(args[0])
        else:
            argpath = pathlib.PurePath(args[0])
        anchor = argpath.anchor
        drive = argpath.drive
        parts = []
        for arg in args:
            if isinstance(arg, (PurePath, pathlib.PurePath)):
                parts.extend(arg.parts)
            else:
                comps = arg.split('/')
                for comp in comps:
                    parts.extend(comp.split('\\'))
        if drive in parts:
            _ = parts.pop(parts.index(drive))
        if parts and parts[0] != anchor:
            parts.insert(0, anchor)
        return tuple(parts)
    return args

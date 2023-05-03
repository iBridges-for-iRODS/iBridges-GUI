"""Test iBridges Path.

"""
import pathlib
import sys

import utils


class TestPath:
    """

    """

    def test_is_posix(self):
        orig_platform = sys.platform
        sys.platform = 'win32'
        assert not utils.path.is_posix()
        sys.platform = 'linux'
        assert utils.path.is_posix()
        sys.platform = orig_platform

    def test_pure_path(self):
        path = utils.path.PurePath('.')
        assert isinstance(path.path, pathlib.PurePath)

    def test_irods_path(self):
        path = utils.path.IrodsPath('.')
        assert isinstance(path.path, pathlib.PurePath)
        not_norm = '/zone/./home/./user/../user'
        is_norm = '/zone/home/user'
        path = utils.path.IrodsPath(not_norm)
        norm_path = utils.path.IrodsPath(is_norm)
        assert path == norm_path

    def test_local_path(self):
        path = utils.path.LocalPath('.')
        assert isinstance(path.path, pathlib.Path)

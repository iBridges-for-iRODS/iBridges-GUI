"""Test iBridges utilities.

"""
import os
import sys

import utils


class TestUtils:
    """

    """

    def test_ensure_dir(self):
        dirname = 'ensure.dir'
        assert not os.path.isdir(dirname)
        assert utils.utils.ensure_dir(dirname)
        assert os.path.isdir(dirname)
        assert utils.utils.ensure_dir(dirname)
        os.rmdir(dirname)

    def test_get_local_size(self):
        size = 1024
        dirname = 'size.dir'
        filename = 'size.file'
        os.mkdir(dirname)
        with open(os.path.join(dirname, filename), 'w') as sizefd:
            sizefd.seek(size - 1)
            sizefd.write('\0')
        assert utils.utils.get_local_size([dirname]) == size
        os.unlink(os.path.join(dirname, filename))
        os.rmdir(dirname)

    def test_get_data_size(self):
        pass

    def test_get_coll_size(self):
        pass

    def test_can_connect(self):
        pass

    def test_get_coll_dict(self):
        pass

    def test_get_downloads_dir(self):
        if sys.platform not in ['win32', 'cygwin']:
            downname = os.path.expanduser('~/Downloads')
            assert utils.utils.get_downloads_dir() == downname

    def test_get_working_dir(self):
        pass

    def test_setup_logger(self):
        pass

    def test_bytes_to_str(self):
        value = 2**30
        assert utils.utils.bytes_to_str(value) == '1.074 GB'
        value = 2**40
        assert utils.utils.bytes_to_str(value) == '1.100 TB'

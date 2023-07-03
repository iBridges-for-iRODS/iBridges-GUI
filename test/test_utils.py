"""Test iBridges utilities.

"""
import os
import tempfile

import pytest

import utils

TEMP_DIR = tempfile.mkdtemp()


# iRODS mock classes
####################
class MockiRODSReplica:
    size = 1024
    status = '1'


class MockiRODSDataObject:
    name = 'data_object'
    path = '/zone/home/coll'
    replicas = [
        MockiRODSReplica(),
        MockiRODSReplica(),
    ]


class MockiRODSCollection:
    data_objects = [
        MockiRODSDataObject(),
        MockiRODSDataObject(),
        MockiRODSDataObject(),
        MockiRODSDataObject(),
    ]
    path = '/zone/home/coll'
    subcollections = []

    def walk(self, topdown: bool = True) -> tuple:
        """Method from PRC version 1.1.6.  Update as needed."""
        if topdown:
            yield self, self.subcollections, self.data_objects
        for subcollection in self.subcollections:
            new_root = subcollection
            for x in new_root.walk(topdown):
                yield x
        if not topdown:
            yield self, self.subcollections, self.data_objects


# pytest fixtures
#################
@pytest.fixture
def irods_collection() -> MockiRODSCollection:
    """Create a disconnected version of an iRODSCollection complete
    with pseudo iRODSDataObjects and a similar subcollection.

    Yields
    ------
    MockiRODSCollection
        A realistic collection instance

    """
    coll = MockiRODSCollection()
    subcoll = MockiRODSCollection()
    subcoll.path = f'{coll.path}/subcoll'
    coll.subcollections = [subcoll]
    yield coll


@pytest.fixture
def irods_data_object() -> MockiRODSDataObject:
    """Create a disconnected version of an iRODSDataObject complete
    with iRODSReplicas.

    Yields
    ------
    MockiRODSDataObject
        A realistic data object instance

    """
    yield MockiRODSDataObject()


# Tests
#######
def test_ensure_dir():
    """Check that the existence of a local directory is ensured.

    """
    dirname = f'{TEMP_DIR}/ensure.dir'
    assert not os.path.isdir(dirname)
    assert utils.utils.ensure_dir(dirname)
    assert os.path.isdir(dirname)
    assert utils.utils.ensure_dir(dirname)
    os.rmdir(dirname)


def test_get_local_size():
    """Check that the size of the files within a local directory is accurate.

    """
    size = 1024
    dirname = f'{TEMP_DIR}/size.dir'
    os.mkdir(dirname)
    filename1 = f'{TEMP_DIR}/size1.file'
    filename2 = f'{dirname}/size2.file'
    with open(filename1, 'w') as sizefd:
        sizefd.seek(1 * size - 1)
        sizefd.write('\0')
    with open(filename2, 'w') as sizefd:
        sizefd.seek(2 * size - 1)
        sizefd.write('\0')
    assert utils.utils.get_local_size([TEMP_DIR]) == 3 * size
    os.unlink(filename1)
    os.unlink(filename2)
    os.rmdir(dirname)


def test_get_data_size(irods_data_object):
    """Check getting the size of an iRODS data object.

    """
    assert utils.utils.get_data_size(irods_data_object) == 1024


def test_get_coll_size(irods_collection):
    """Check getting the recursive size of an iRODS collection.

    """
    assert utils.utils.get_coll_size(irods_collection) == 8192


def test_can_connect():
    """Check that a network connection test works properly.

    """
    pass


def test_get_coll_dict(irods_collection):
    """Test creation of recursive collection dictionary.

    """
    expected = {
        '/zone/home/coll':
            ['data_object', 'data_object', 'data_object', 'data_object'],
        '/zone/home/coll/subcoll':
            ['data_object', 'data_object', 'data_object', 'data_object'],
    }
    assert utils.utils.get_coll_dict(irods_collection) == expected


def test_get_downloads_dir():
    """Check (currently for POSIX only) if the correct Downloads
    directory is identified.

    """
    if os.name == 'posix':
        downname = os.path.expanduser('~/Downloads')
        assert utils.utils.get_downloads_dir() == downname


def test_get_working_dir():
    """Check that the executable directory is correctly identified.

    """
    pass


def test_bytes_to_str():
    """Test the conversion of the number of bytes to a string with
    units.

    """
    value = 2**30
    assert utils.utils.bytes_to_str(value) == '1.074 GB'
    value = 2**40
    assert utils.utils.bytes_to_str(value) == '1.100 TB'

"""Test iBridges Path.

"""
import glob
import os
import pathlib
import pytest
import tempfile

import utils

TEMP_DIR = tempfile.mkdtemp()


# pytest fixtures
#################
@pytest.fixture(scope='function')
def pure_path() -> utils.path.PurePath:
    """Create a PurePath instance.

    Yields
    ------
    utils.path.PurePath

    """
    yield utils.path.PurePath()


@pytest.fixture(scope='function')
def irods_path() -> utils.path.iRODSPath:
    """Create an iRODSPath instance.

    Yields
    ------
    utils.path.iRODSPath

    """
    yield utils.path.iRODSPath()


@pytest.fixture(scope='function')
def local_path() -> utils.path.LocalPath:
    """Create a LocalPath instance and clean up after yield.
    Unfortunately, the cleanup does not wait until after yield.

    Yields
    ------
    utils.path.iRODSPath

    """
    yield utils.path.LocalPath(TEMP_DIR)
    # pytest fixture finalization is not working for some reason
    # for item in glob.glob(f'{TEMP_DIR}/*'):
    #     if os.path.isdir(item):
    #         os.removedirs(item)
    #     else:
    #         os.remove(item)


# Tests
#######
def test_is_posix():
    """Test that the correct system type is identified.

    """
    orig_name = os.name
    os.name = 'nt'
    assert not utils.path.is_posix()
    os.name = 'posix'
    assert utils.path.is_posix()
    os.name = orig_name


def test_pure_path_new(pure_path):
    """Test the __new__() method provides the correct output.

    """
    assert pure_path._path is None
    assert pure_path._posix is None
    # Raw string (r'') does not work in this definition for some reason.
    # It requires an extra space, or it will escape the final "'".
    raw = r'.\ '
    orig_name = os.name
    os.name = 'nt'
    assert pure_path.__class__(raw) == ' '
    os.name = 'posix'
    # TODO understand why the normalization causes this for POSIX only
    # Must cast as str because of normalization (Why?)
    assert str(pure_path.__class__(raw)) == ' '
    os.name = orig_name
    assert pure_path.__class__('a', 'b', 'c') == os.path.join('a', 'b', 'c')


def test_pure_path_repr(pure_path):
    """Test the object representation output.

    """
    assert repr(pure_path) == 'PurePath(".")'


def test_pure_path_str(pure_path):
    """Test the string casting.

    """
    assert str(pure_path) == '.'


def test_pure_path_name(pure_path):
    """Check that the name attribute is correct.

    """
    assert pure_path.__class__('a', 'b', 'c').name == 'c'


def test_pure_path_parent(pure_path):
    """Check that the parent attribute is correct.

    """
    assert pure_path.__class__('a', 'b', 'c').parent.parent == 'a'


def test_pure_path_parts(pure_path):
    """Check that the parts attribute is correct.

    """
    assert pure_path.__class__('a', 'b', 'c').parts == ('a', 'b', 'c')


def test_pure_path_path(pure_path):
    """Check that the path property is correct.  It should depend on
    the type of system.

    """
    if os.name == 'nt':
        assert isinstance(pure_path.__class__().path, pathlib.PureWindowsPath)
    if os.name == 'posix':
        assert isinstance(pure_path.__class__().path, pathlib.PurePosixPath)


def test_pure_path_stem(pure_path):
    """Check that the stem attribute is correct.

    """
    assert pure_path.__class__('file.ext').stem == 'file'


def test_pure_path_suffix(pure_path):
    """Check that the suffix attribute is correct.

    """
    assert pure_path.__class__('file.ext').suffix == '.ext'


def test_pure_path_suffixes(pure_path):
    """Check that the suffixes attribute is correct.

    """
    assert pure_path.__class__('file.ext.txt').suffixes == ['.ext', '.txt']


def test_pure_path_joinpath(pure_path):
    """Test that the joinpath method does just that.

    """
    assert pure_path.joinpath('a').joinpath('b') == os.path.join('a', 'b')


def test_pure_path_with_suffix(pure_path):
    """Test that the with_suffix method works correctly.

    """
    assert pure_path.__class__('file.ext').with_suffix('') == 'file'
    assert pure_path.__class__('file').with_suffix('.txt') == 'file.txt'
    assert pure_path.__class__('file.ext').with_suffix('.txt') == 'file.txt'


def test_irods_path_new(irods_path):
    """Check that the __new__() method provides the correct output,
    particularly the path normalization.

    """
    assert irods_path._posix is True
    # Raw string (r'') does not work in this definition for some reason.
    # It requires an extra space, or it will escape the final "'".
    raw = r'.\ '
    orig_name = os.name
    os.name = 'nt'
    # Must cast as str because of normalization (Why?)
    assert str(irods_path.__class__(raw)) == ' '
    os.name = orig_name
    assert irods_path.__class__('/zone/./home/./user/../user', 'coll') == '/zone/home/user/coll'


def test_irods_path_repr(irods_path):
    """Check that the object representation is correct.

    """
    assert repr(irods_path) == 'iRODSPath(".")'


def test_irods_path_path(irods_path):
    """Check that the path property is correct.  It should NOT depend
    on the type of system.

    """
    orig_name = os.name
    os.name = 'nt'
    assert isinstance(irods_path.__class__().path, pathlib.PurePosixPath)
    os.name = orig_name


def test_irods_path_joinpath(pure_path, irods_path):
    src_path = irods_path.__class__('/a/b/c')
    rel_path = pure_path.__class__('d/e/f')
    rds_path = src_path.joinpath(rel_path)
    assert rds_path == irods_path.__class__('/a/b/c/d/e/f')


def test_local_path_new(local_path):
    """Check that the __new__() method provides the correct output.

    """
    assert local_path._posix is None
    # Raw string (r'') does not work in this definition for some reason.
    # It requires an extra space, or it will escape the final "'".
    raw = r'.\ '
    if os.name == 'nt':
        assert local_path.__class__(raw) == ' '
    if os.name == 'posix':
        # Must cast as str because of normalization (Why?)
        assert str(local_path.__class__(raw)) == ' '


def test_local_path_repr(local_path):
    """Check that the object representation is correct.

    """
    assert repr(local_path) == f'LocalPath("{TEMP_DIR}")'


def test_local_path_path(local_path):
    """Check that the path property is correct.  It should depend on
    the type of system.

    """
    if os.name == 'nt':
        assert isinstance(local_path.__class__().path, pathlib.WindowsPath)
    if os.name == 'posix':
        assert isinstance(local_path.__class__().path, pathlib.PosixPath)


def test_local_path_absolute(local_path):
    """Test the absolute method resolves the path correctly.

    """
    assert local_path.absolute().path == pathlib.Path(TEMP_DIR).absolute()


def test_local_path_copy_path(local_path):
    """Test the copy_path method copies correctly.

    """
    os.makedirs(f'{TEMP_DIR}/test1/test')
    local_path.joinpath('test1').copy_path(f'{TEMP_DIR}/test2')
    assert os.path.isdir(f'{TEMP_DIR}/test1/test')
    assert os.path.isdir(f'{TEMP_DIR}/test2/test')
    # pytest fixture finalization is not working for some reason
    for dirname in ['test1', 'test2']:
        if os.path.isdir(f'{TEMP_DIR}/{dirname}'):
            if os.path.isdir(f'{TEMP_DIR}/{dirname}/test'):
                os.rmdir(f'{TEMP_DIR}/{dirname}/test')
            os.rmdir(f'{TEMP_DIR}/{dirname}')


def test_local_path_cwd(local_path):
    """Test the cwd (current working directory) method give the correct
    value.

    """
    assert local_path.cwd().path == pathlib.Path().cwd()


def test_local_path_exists(local_path):
    """Test the exists method determines existence correctly.

    """
    assert local_path.exists() == os.path.exists(TEMP_DIR)


def test_local_path_expanduser(local_path):
    """Test the expanduser method resolves the user's home directory
    correctly.

    """
    assert local_path.__class__('~').expanduser() == os.path.expanduser('~')


def test_local_path_glob(local_path):
    """Test the glob method finds the correct listing.

    """
    for dirname in ['test1', 'test2', 'test3']:
        os.mkdir(f'{TEMP_DIR}/{dirname}')
    # Filenames/directories starting with '.' are ignored by
    # glog.glob(), so manually ignore them here as well.
    found = sorted([str(fname) for fname in local_path.glob("*")
                    if not fname.startswith(".")])
    assert found == sorted(glob.glob(f'{TEMP_DIR}/*'))
    # pytest fixture finalization is not working for some reason
    for dirname in ['test1', 'test2', 'test3']:
        os.rmdir(f'{TEMP_DIR}/{dirname}')


def test_local_path_is_dir(local_path):
    """Test the is_dir method correctly identifies directories.

    """
    assert local_path.is_dir() == os.path.isdir(TEMP_DIR)


def test_local_path_is_file(local_path):
    """Test the is_file method correctly identifies files.

    """
    assert local_path.is_file() == os.path.isfile(TEMP_DIR)


def test_local_path_mkdir(local_path):
    """Test the mkdir method correctly created a directory.

    """
    local_path.joinpath('test').mkdir()
    assert os.path.isdir(f'{TEMP_DIR}/test')
    # pytest fixture finalization is not working for some reason
    os.rmdir(f'{TEMP_DIR}/test')


def test_local_path_read_bytes(local_path):
    """Test the read_bytes method reads from a file correctly and in
    the correct format.

    """
    with open(f'{TEMP_DIR}/test.file', 'w') as testfd:
        testfd.write('test')
    assert local_path.joinpath('test.file').read_bytes() == b'test'
    # pytest fixture finalization is not working for some reason
    os.remove(f'{TEMP_DIR}/test.file')


def test_local_path_read_text(local_path):
    """Test the read_text method reads from a file correctly and in the
    correct format.

    """
    with open(f'{TEMP_DIR}/test.file', 'w') as testfd:
        testfd.write('test')
    assert local_path.joinpath('test.file').read_text() == 'test'
    # pytest fixture finalization is not working for some reason
    os.remove(f'{TEMP_DIR}/test.file')


def test_local_path_rename_path(local_path):
    """Test the rename_path method correctly renames its
    file/directory.

    """
    os.mkdir(f'{TEMP_DIR}/test1')
    local_path.joinpath('test1').rename_path(f'{TEMP_DIR}/test2')
    assert not os.path.isdir(f'{TEMP_DIR}/test1')
    assert os.path.isdir(f'{TEMP_DIR}/test2')
    os.mkdir(f'{TEMP_DIR}/test3')
    # TODO figure out how to test logging output
    local_path.joinpath('test2').rename_path(f'{TEMP_DIR}/test3')
    assert os.path.isdir(f'{TEMP_DIR}/test2')
    assert os.path.isdir(f'{TEMP_DIR}/test3')
    # pytest fixture finalization is not working for some reason
    for dirname in ['test1', 'test2', 'test3']:
        if os.path.isdir(f'{TEMP_DIR}/{dirname}'):
            os.rmdir(f'{TEMP_DIR}/{dirname}')


def test_local_path_replace_path(local_path):
    """Test the replace_path method correctly replaces its
    file/directory.

    """
    os.mkdir(f'{TEMP_DIR}/test1')
    os.mkdir(f'{TEMP_DIR}/test2')
    local_path.joinpath('test1').replace_path(f'{TEMP_DIR}/test2')
    assert not os.path.isdir(f'{TEMP_DIR}/test1')
    assert os.path.isdir(f'{TEMP_DIR}/test2')
    os.mkdir(f'{TEMP_DIR}/test3')
    os.mkdir(f'{TEMP_DIR}/test3/test')
    # TODO figure out how to test logging output
    local_path.joinpath('test2').replace_path(f'{TEMP_DIR}/test3')
    assert os.path.isdir(f'{TEMP_DIR}/test2')
    assert os.path.isdir(f'{TEMP_DIR}/test3')
    local_path.joinpath('test2').replace_path(f'{TEMP_DIR}/test3', squash=True)
    assert not os.path.isdir(f'{TEMP_DIR}/test2')
    assert os.path.isdir(f'{TEMP_DIR}/test3')
    # pytest fixture finalization is not working for some reason
    for dirname in ['test1', 'test2', 'test3']:
        if os.path.isdir(f'{TEMP_DIR}/{dirname}'):
            os.rmdir(f'{TEMP_DIR}/{dirname}')


def test_local_path_resolve(local_path):
    """Test the resolve method resolves the absolute path taking into
    account '.' and '..' references within.

    """
    assert local_path.resolve().path == pathlib.Path(TEMP_DIR).resolve()
    assert local_path.joinpath('../').resolve().path == pathlib.Path(
        f'{TEMP_DIR}/../').resolve()


def test_local_path_rmdir(local_path):
    """Test the rmdir method correctly removes a directory.

    """
    os.mkdir(f'{TEMP_DIR}/test')
    local_path.joinpath('test').rmdir()
    assert not os.path.isdir(f'{TEMP_DIR}/test')
    # pytest fixture finalization is not working for some reason
    if os.path.isdir(f'{TEMP_DIR}/test'):
        os.rmdir(f'{TEMP_DIR}/test')


def test_local_path_stat(local_path):
    """Test the stat method gives the correct output.

    """
    assert isinstance(local_path.stat(), os.stat_result)


def test_local_path_unlink(local_path):
    """Test the unlink method correctly removes a file.

    """
    with open(f'{TEMP_DIR}/test.file', 'w') as testfd:
        testfd.write('test')
    assert os.path.isfile(f'{TEMP_DIR}/test.file')
    local_path.joinpath('test.file').unlink()
    assert not os.path.isfile(f'{TEMP_DIR}/test.file')
    with pytest.raises(FileNotFoundError):
        local_path.joinpath('test.file').unlink()
    # pytest fixture finalization is not working for some reason
    if os.path.isfile(f'{TEMP_DIR}/test.file'):
        os.remove(f'{TEMP_DIR}/test.file')


def test_local_path_write_bytes(local_path):
    """Test the write_bytes method writes to a file correctly and in
    the correct format.

    """
    local_path.joinpath('test.file').write_bytes(b'test')
    with open(f'{TEMP_DIR}/test.file', 'rb') as testfd:
        assert testfd.read() == b'test'
    # pytest fixture finalization is not working for some reason
    os.remove(f'{TEMP_DIR}/test.file')


def test_local_path_write_text(local_path):
    """Test the write_text method writes to a file correctly and in the
    correct format.

    """
    local_path.joinpath('test.file').write_text('test')
    with open(f'{TEMP_DIR}/test.file', 'r') as testfd:
        assert testfd.read() == 'test'
    # pytest fixture finalization is not working for some reason
    os.remove(f'{TEMP_DIR}/test.file')

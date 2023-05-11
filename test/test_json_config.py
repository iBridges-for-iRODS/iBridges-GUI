"""Test iBridges JSONConfig.

"""
import json
import os
import pathlib
import pytest
import tempfile

import utils

CWD = tempfile.mkdtemp()
TEMPLATE = {
    'one': 1,
    'true': True,
    'list': [],
}


@pytest.fixture(scope='function')
def config_filepath() -> str:
    """Create then remove a test configuration file, yielding the
    filepath in between.

    Yields
    ------
    str
        Path and name of the newly created JSON file.

    """
    filepath = pathlib.Path(CWD, 'config.json')
    filepath.write_text(json.dumps(TEMPLATE))
    yield str(filepath)
    filepath.unlink(missing_ok=True)


def test_bool(config_filepath):
    """Check that the truthiness of the class reflects the truthiness
    of its config dictionary.

    Parameters
    ----------
    config_filepath : str
        A pytest fixture with function scope to provide the path to
        the pre-created configuration JSON file.

    """
    assert bool(utils.json_config.JSONConfig()) is bool({})
    assert bool(utils.json_config.JSONConfig(config_filepath)) is bool(TEMPLATE)


def test_repr():
    """Check that the representation is correctly formatted.

    """
    assert utils.json_config.JSONConfig().__repr__() == 'JSONConfig("{}")'


def test_config(config_filepath):
    """Check that the config property 'get's, 'set's, and 'del's as it
    should.

    Parameters
    ----------
    config_filepath : str
        A pytest fixture with function scope to provide the path to
        the pre-created configuration JSON file.

    """
    assert utils.json_config.JSONConfig().config == {}
    new_config = utils.json_config.JSONConfig(config_filepath)
    assert new_config.config == TEMPLATE
    del new_config.config
    assert new_config._config == {}
    # Reloads from file.
    assert new_config.config == TEMPLATE


def test_filepath(config_filepath):
    """Check that the filepath property 'get's and 'set's as it should.

    Parameters
    ----------
    config_filepath : str
        A pytest fixture with function scope to provide the path to
        the pre-created configuration JSON file.

    """
    new_config = utils.json_config.JSONConfig()
    assert isinstance(new_config.filepath, utils.path.LocalPath)
    assert new_config.filepath == '.'
    new_config.filepath = config_filepath
    assert isinstance(new_config.filepath, utils.path.LocalPath)
    assert new_config.filepath == config_filepath
    assert new_config.config == TEMPLATE


def test_clear(config_filepath):
    """Check that the config dictionary is cleared correctly.

    Parameters
    ----------
    config_filepath : str
        A pytest fixture with function scope to provide the path to
        the pre-created configuration JSON file.

    """
    new_config = utils.json_config.JSONConfig(config_filepath)
    assert new_config.filepath == config_filepath
    assert new_config.config != {}
    new_config.clear()
    assert new_config.filepath == config_filepath
    # If 'config' property is accessed here, the configuration will
    # only be reloaded.  We need to test the shadow variable.
    assert new_config._config == {}


def test_reset(config_filepath):
    """Check that the whole object (config and filepath) is reset to
    default values.

    Parameters
    ----------
    config_filepath : str
        A pytest fixture with function scope to provide the path to
        the pre-created configuration JSON file.

    """
    new_config = utils.json_config.JSONConfig(config_filepath)
    assert new_config.filepath == config_filepath
    assert new_config.config != {}
    new_config.reset()
    assert new_config.filepath == '.'
    assert new_config.config == {}


def test_save(config_filepath):
    """Check that any additions to the config dictionary are saved to
    the JSON file.

    Parameters
    ----------
    config_filepath : str
        A pytest fixture with function scope to provide the path to
        the pre-created configuration JSON file.

    """
    new_config = utils.json_config.JSONConfig(config_filepath)
    assert new_config.config == TEMPLATE
    new_config.config['two'] = 2
    new_config.save()
    assert json.loads(new_config.filepath.read_text())['two'] == 2

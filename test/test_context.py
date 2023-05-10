"""Test iBridges Context.

"""
import json
import os
import pytest
import tempfile

import utils

CONTEXT = utils.context.Context()
ENV = os.environ
HOME = tempfile.mkdtemp()
IBRIDGES_CONF_FILE = 'ibridges_config.json'
IRODS_ENV_FILE = 'irods_environment.json'
IRODS_AUTH_FILE = '.irodsA'
# Change global constants so as not to conflict with local environment.
utils.context.DEFAULT_IBRIDGES_CONF_FILE = os.path.join(
    HOME, IBRIDGES_CONF_FILE)
utils.context.IBRIDGES_DIR = HOME
utils.context.IRODS_DIR = HOME


@pytest.fixture(scope='function')
def reset_ibridges_configuration():
    """A pytest fixture to reset the ibridges_configuration property
    and remove the configuration file _after_ the 'yield'.

    """
    yield
    if CONTEXT.ibridges_conf_file.is_file():
        os.remove(CONTEXT.ibridges_conf_file)
    CONTEXT._ibridges_configuration = None
    CONTEXT.ibridges_conf_file = ''


@pytest.fixture(scope='function')
def reset_irods_environment():
    """A pytest fixture to reset the irods_environment property and
    remove the environment file _after_ the 'yield'.

    """
    yield
    if CONTEXT.irods_env_file.is_file():
        os.remove(CONTEXT.irods_env_file)
    CONTEXT._irods_environment = None
    CONTEXT.irods_env_file = ''


def test_context_is_singleton():
    """Check that the Context class only ever instantiates a single
    instance.

    """
    assert utils.context.Context() is CONTEXT


def test_ibridges_configuration(reset_ibridges_configuration):
    """Missing iBridges configuration file is given the default
    contents.  Check that the property does this and loads the
    configuration properly.

    Parameters
    ----------
    reset_ibridges_configuration : None
        A pytest fixture with function scope to reset to the pretest
        setup of the iBridges configuration.

    """
    assert CONTEXT._ibridges_configuration is None
    for key in utils.context.IBRIDGES_CONF_TEMPLATE:
        assert key in CONTEXT.ibridges_configuration.config
    assert CONTEXT.ibridges_conf_file == utils.context.DEFAULT_IBRIDGES_CONF_FILE


def test_irods_connector():
    """The IrodsConnector is manually set to a property prior to a new
    session.  Check that the property handles it correctly.

    """
    assert CONTEXT.irods_connector is None
    CONTEXT.irods_connector = 'IrodsConnector'
    assert CONTEXT.irods_connector == 'IrodsConnector'
    del CONTEXT.irods_connector
    assert CONTEXT.irods_connector is None


def test_irods_environment(reset_irods_environment):
    """The iRODS environment file is required to exist.  Check that the
    property loads it properly.

    Parameters
    ----------
    reset_irods_environment : None
        A pytest fixture with function scope to reset to the pretest
        setup of the iRODS environment.

    """
    assert CONTEXT._irods_environment is None
    CONTEXT.irods_env_file = os.path.join(utils.context.IRODS_DIR, IRODS_ENV_FILE)
    ienv_dict = {key: None for key in utils.context.MANDATORY_IRODS_ENV_KEYS}
    with open(CONTEXT.irods_env_file, 'w') as envfd:
        json.dump(ienv_dict, envfd)
    for key in utils.context.MANDATORY_IRODS_ENV_KEYS:
        assert key in CONTEXT.irods_environment.config


def test_ienv_is_complete(reset_irods_environment):
    """Check that the environment completeness methods works correctly.

    Parameters
    ----------
    reset_irods_environment : None
        A pytest fixture with function scope to reset to the pretest
        setup of the iRODS environment.

    """
    CONTEXT.irods_env_file = os.path.join(utils.context.IRODS_DIR, IRODS_ENV_FILE)
    with open(CONTEXT.irods_env_file, 'w') as envfd:
        json.dump({}, envfd)
    assert CONTEXT.irods_environment.config == {}
    assert not CONTEXT.ienv_is_complete()
    ienv_dict = {key: None for key in utils.context.MANDATORY_IRODS_ENV_KEYS}
    CONTEXT.irods_environment.config.update(ienv_dict)
    assert CONTEXT.ienv_is_complete()


def test_save_ibridges_configuration(reset_ibridges_configuration):
    """Check that the save method does that properly.

    Parameters
    ----------
    reset_ibridges_configuration : None
        A pytest fixture with function scope to reset to the pretest
        setup of the iBridges configuration.

    """
    CONTEXT.ibridges_conf_file = utils.context.DEFAULT_IBRIDGES_CONF_FILE
    conf_dict = utils.context.IBRIDGES_CONF_TEMPLATE.copy()
    with open(CONTEXT.ibridges_conf_file, 'w') as conffd:
        json.dump(conf_dict, conffd)
    with open(CONTEXT.ibridges_conf_file) as conffd:
        new_conf_dict = json.load(conffd)
    assert new_conf_dict == conf_dict
    conf_dict.update({'test_key': 'test_val'})
    CONTEXT.ibridges_configuration.config.update({'test_key': 'test_val'})
    CONTEXT.save_ibridges_configuration()
    with open(CONTEXT.ibridges_conf_file) as conffd:
        new_conf_dict = json.load(conffd)
    assert new_conf_dict == conf_dict


def test_save_irods_environment(reset_irods_environment):
    """Check that the save method does that properly.

    Parameters
    ----------
    reset_irods_environment : None
        A pytest fixture with function scope to reset to the pretest
        setup of the iRODS environment.

    """
    # setup
    CONTEXT.irods_env_file = os.path.join(utils.context.IRODS_DIR, IRODS_ENV_FILE)
    ienv_dict = {key: None for key in utils.context.MANDATORY_IRODS_ENV_KEYS}
    with open(CONTEXT.irods_env_file, 'w') as envfd:
        json.dump(ienv_dict, envfd)
    with open(CONTEXT.irods_env_file) as envfd:
        new_ienv_dict = json.load(envfd)
    assert new_ienv_dict == ienv_dict
    ienv_dict.update({'test_key': 'test_val'})
    CONTEXT.irods_environment.config['test_key'] = 'test_val'
    CONTEXT.save_irods_environment()
    with open(CONTEXT.irods_env_file) as envfd:
        new_ienv_dict = json.load(envfd)
    assert new_ienv_dict == ienv_dict


def test_reset(reset_ibridges_configuration, reset_irods_environment):
    """Check that the reset of the context resets what it should.

    Parameters
    ----------
    reset_ibridges_configuration : None
        A pytest fixture with function scope to reset to the pretest
        setup of the iBridges configuration.
    reset_irods_environment : None
        A pytest fixture with function scope to reset to the pretest
        setup of the iRODS environment.

    """
    CONTEXT.irods_connector = 'IrodsConnector'
    assert CONTEXT.irods_connector == 'IrodsConnector'
    CONTEXT.ibridges_conf_file = utils.context.DEFAULT_IBRIDGES_CONF_FILE
    conf_dict = utils.context.IBRIDGES_CONF_TEMPLATE.copy()
    conf_dict['extra_key'] = 'extra_val'
    with open(CONTEXT.ibridges_conf_file, 'w') as conffd:
        json.dump(conf_dict, conffd)
    assert CONTEXT.ibridges_configuration.config == conf_dict
    CONTEXT.ibridges_conf_file = ''
    CONTEXT.irods_env_file = os.path.join(utils.context.IRODS_DIR, IRODS_ENV_FILE)
    ienv_dict = {key: None for key in utils.context.MANDATORY_IRODS_ENV_KEYS}
    with open(CONTEXT.irods_env_file, 'w') as envfd:
        json.dump(ienv_dict, envfd)
    assert CONTEXT.irods_environment.config == ienv_dict
    CONTEXT.irods_env_file = ''
    CONTEXT.reset()
    assert CONTEXT.irods_connector is None
    assert CONTEXT.ibridges_configuration.config == utils.context.IBRIDGES_CONF_TEMPLATE
    assert CONTEXT.ibridges_configuration.filepath == CONTEXT.ibridges_conf_file
    assert CONTEXT.irods_environment.config == {}
    assert CONTEXT.irods_environment.filepath == '.'


def test_is_complete():
    """This is tested above, but a placeholder is left in case it
    becomes necessary to test this function directly.

    """
    pass


def test_context_container(reset_ibridges_configuration, reset_irods_environment):
    """The ContextContainer class is an abstract base class intended to
    allow inheritance of convenience methods accessing only specific
    parts of the Context class.  Check that this is the case.

    Parameters
    ----------
    reset_ibridges_configuration : None
        A pytest fixture with function scope to reset to the pretest
        setup of the iBridges configuration.
    reset_irods_environment : None
        A pytest fixture with function scope to reset to the pretest
        setup of the iRODS environment.

    """
    class TestClass(utils.context.ContextContainer):
        pass
    test_obj = TestClass()
    CONTEXT.irods_connector = 'IrodsConnector'
    CONTEXT.ibridges_conf_file = utils.context.DEFAULT_IBRIDGES_CONF_FILE
    conf_dict = utils.context.IBRIDGES_CONF_TEMPLATE.copy()
    with open(CONTEXT.ibridges_conf_file, 'w') as conffd:
        json.dump(conf_dict, conffd)
    CONTEXT.irods_env_file = os.path.join(utils.context.IRODS_DIR, IRODS_ENV_FILE)
    ienv_dict = {key: None for key in utils.context.MANDATORY_IRODS_ENV_KEYS}
    with open(CONTEXT.irods_env_file, 'w') as envfd:
        json.dump(ienv_dict, envfd)
    with pytest.raises(TypeError):
        _ = utils.context.ContextContainer()
    assert test_obj.context == CONTEXT
    assert test_obj.conf == CONTEXT.ibridges_configuration.config
    assert test_obj.conn == CONTEXT.irods_connector
    assert test_obj.ienv == CONTEXT.irods_environment.config

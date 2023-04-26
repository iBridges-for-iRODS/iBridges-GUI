""" session operations
"""
import logging
import os
import ssl

import irods.connection
import irods.exception
import irods.password_obfuscation
import irods.session

from . import keywords as kw
import utils


class Session(object):
    """Irods session operations """

    def __init__(self, context: utils.context.Context, password=None, greet=False):
        """ iRODS authentication with Python client.

        Parameters
        ----------
        password : str
            Plain text password.
        context : utils.context Context object containing valid
            irods environment and ibridges configuration 
        greet: bool
            Print some greeting and irods info to prompt

        The 'password' is autoloaded from its cache, but can be
        overridden by `password` argument.  The iRODS authentication
        file is expected in the standard location (~/.irods/.irodsA) or
        to be specified in the local environment with the
        IRODS_AUTHENTICATION_FILE variable.

        """
        self._password = password
        self._ienv = context.irods_environment.config
        self._conf = context.ibridges_configuration.config
        self._irods_env_file = context.irods_env_file
        self._irods_session = None

        if self._ienv == None:
            raise ValueError("ERROR SESSION: no irods environment")
        if self._conf == None:
            raise ValueError("ERROR SESSION: no ibridges configuration")

        self._irods_session = self._connect_to_irods()
        self._cache_password()
        if greet:
            self.greet()

    def greet(self):
        """Print irods server info to prompt.
        """

        print('Welcome to iRODS:')
        print(f'iRODS Zone: {self._irods_session.zone}')
        print(f'You are: {self._irods_session.username}')
        print(f'Default resource: {self.default_resc}')
        print('You have access to: \n')
        home_path = f'/{self._irods_session.zone}/home'
        if self._irods_session.collections.exists(home_path):
            colls = self._irods_session.collections.get(home_path).subcollections
            print('\n'.join([coll.path for coll in colls]))

    def _cache_password(self):
        given_pass = self._password
        cached_pass = self.read_cached_password
        if given_pass != cached_pass:
            self._write_password()

    def __del__(self):
        self.del_irods_session()

    @property
    def conf(self) -> dict:
        """iBridges configuration dictionary.

        Returns
        -------
        dict
            Configuration from JSON serialized string.

        """
        return self._conf

    @property
    def davrods(self) -> str:
        """DavRODS server URL.

        Returns
        -------
        str
            URL of the configured DavRODS server.

        """
        return self._conf.get('davrods_server', '')

    @property
    def default_resc(self) -> str:
        """Default resource name from iRODS environment.

        Returns
        -------
        str
            Resource name.

        """
        return self._ienv.get('irods_default_resource', '')

    @property
    def host(self) -> str:
        """Retrieve hostname of the iRODS server

        Returns
        -------
        str
            Hostname.

        """
        if self._irods_session:
            return self._irods_session.host
        return None

    @property
    def ienv(self) -> dict:
        """iRODS environment dictionary.

        Returns
        -------
        dict
            Environment from JSON serialized string.
        """
        return self._ienv

    @property
    def port(self) -> str:
        """Retrieve port of the iRODS server

        Returns
        -------
        str
            Port.

        """
        if self._irods_session:
            return str(self._irods_session.port)
        return None

    @property
    def username(self) -> str:
        """Retrieve username

        Returns
        -------
        str
            Username.

        """
        if self._irods_session:
            return self._irods_session.username
        return None

    @property
    def server_version(self) -> tuple:
        """Retrieve version of the iRODS server

        Returns
        -------
        tuple
            Server version: (major, minor, patch).

        """
        if self._irods_session:
            return self._irods_session.server_version
        return None

    @property
    def zone(self) -> str:
        """Retrieve the zone name

        Returns
        -------
        str
            Zone.

        """
        if self._irods_session:
            return self._irods_session.zone
        return None

    def read_cached_password(self) -> str:
        """iRODS password.

        Returns
        -------
        str
            iRODS password pre-set or decoded from iRODS authentication
            file. Can be a PAM negotiated password.

        """
        irods_auth_file = os.environ.get(
            'IRODS_AUTHENTICATION_FILE', None)
        if irods_auth_file is None:
            irods_auth_file = utils.path.LocalPath('~/.irods/.irodsA').expanduser()
        if irods_auth_file.exists():
            with open(irods_auth_file, encoding='utf-8') as authfd:
                self._password = irods.password_obfuscation.decode(authfd.read())
                return self._password

    @property
    def irods_session(self):
        if self._irods_session:
            return self._irods_session
        return None

    def del_irods_session(self):
        """Properly delete irods session.
        """
        if self._irods_session is not None:
            self._irods_session.cleanup()
            del self._irods_session
            self._irods_session = None

    def _connect_to_irods(self):
        """Run through different types of authentication methods and
        instantiate an iRODS session.

        Parameters
        ----------
        options : dict
            Initial iRODS settings for the session.

        Returns
        -------
        iRODSSession
            iRODS connection based on given environment and password.

        """
        if self._password == None:
            try:
                logging.info('iRODS AUTH FILE SESSION: reading .irodsA')
                irods_session = irods.session.iRODSSession(
                    irods_env_file=self._irods_env_file)
                _ = irods_session.server_version
                logging.info(
                        'IRODS LOGIN SUCCESS: %s, %s, %s', irods_session.username,
                        irods_session.zone, irods_session.host)
                return irods_session
            except Exception as error:
                logging.info('iRODS AUTH FILE SESSION LOGIN FAILED: {error!r}')
                raise error
        else:
            try:
                logging.info('iRODS SESSION: authentication with password')
                irods_session = irods.session.iRODSSession(password=self._password, **self._ienv)
                _ = irods_session.server_version
                logging.info(
                        'IRODS LOGIN SUCCESS: %s, %s, %s', irods_session.username,
                        irods_session.zone, irods_session.host)
                return irods_session
            except irods.connection.PlainTextPAMPasswordError as ptppe:
                print(f'{kw.RED}SOMETHING WRONG WITH THE ENVIRONMENT JSON? {ptppe!r}{kw.DEFAULT}')
                try: #standard SSL context 
                    ssl_context = ssl.create_default_context(
                        purpose=ssl.Purpose.SERVER_AUTH,
                        cafile=None, capath=None, cadata=None)
                    ssl_settings = {
                        'client_server_negotiation':
                            'request_server_negotiation',
                        'client_server_policy': 'CS_NEG_REQUIRE',
                        'encryption_algorithm': 'AES-256-CBC',
                        'encryption_key_size': 32,
                        'encryption_num_hash_rounds': 16,
                        'encryption_salt_size': 8,
                        'ssl_context': ssl_context,
                    }
                    options.update(ssl_settings)
                    logging.info('----RETRY WITH DEFAULT SSL SETTINGS')
                    irods_session = irods.session.iRODSSession(password=password, **options)
                    _ = irods_session.server_version
                    logging.info(
                            'IRODS LOGIN SUCCESS: %s, %s, %s', irods_session.username,
                            irods_session.zone, irods_session.host)
                    return irods_session
                except Exception as error:
                    logging.info('iRODS AUTH FILE SESSION LOGIN FAILED: {error!r}')
                    raise error
            except Exception as autherror:
                logging.info('AUTHENTICATION ERROR')
                raise autherror

    def _write_password(self):
        """Store the password in the iRODS
        authentication file in obfuscated form.

        """
        connection = self._irods_session.pool.get_connection()
        pam_passwords = self._irods_session.pam_pw_negotiated
        if len(pam_passwords):
            irods_auth_file = self._irods_session.get_irods_password_file()
            with open(irods_auth_file, 'w', encoding='utf-8') as authfd:
                authfd.write(
                    irods.password_obfuscation.encode(pam_passwords[0]))
        else:
            logging.info('WARNING -- unable to cache obfuscated password locally')
        connection.release()

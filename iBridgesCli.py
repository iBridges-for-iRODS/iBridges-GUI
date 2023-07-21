#!/usr/bin/env python3
"""
Commandline client to upload data to a storage service and double-link the storage location with a metadata store.

Implemented for:
    Storage types:
        iRODS
"""
from __future__ import annotations
import argparse
import getpass
import logging
import sys

import irods.exception

import irodsConnector
import irodsConnector.keywords as kw
import utils

THIS_APPLICATION = 'iBridgesCli'
parser = argparse.ArgumentParser(
    prog=f'python3 {THIS_APPLICATION}.py', description="", epilog="")


def plugin_hook(func):
    """Callable function for the plugin_hook decorator.

    """
    def wrapper(self, **kwargs):
        """Executes hooked functions pre and post the decorated
        function.

        """

        pre_fs = post_fs = []
        actions = [plugin['actions'] for plugin in self.plugins
                   if plugin['hook'] == func.__name__]
        if actions:
            pre_fs = [action['function'] for action in actions[0]
                      if action['slot'] == 'pre']
            post_fs = [action['function'] for action in actions[0]
                       if action['slot'] == 'post']

        for pre_f in pre_fs:
            pre_f(calling_class=self, **kwargs)

        func(self, **kwargs)

        for post_f in post_fs:
            post_f(calling_class=self, **kwargs)

    return wrapper


class iBridgesCli:
    """Class for up- and downloading to YODA/iRODS via the commandline.
    Includes option for writing metadata to Elab Journal.

    """
    conn = irodsConnector.manager.IrodsConnector()
    context = utils.context.Context()
    target_path = None
    download_finished = None
    upload_finished = None

    def __init__(self, irods_env_file: str, local_path: str,
                 irods_path: str, irods_resc: str, operation: str,
                 logdir: str, plugins: list[dict] = None):
        """Initialize logging, set arguments, and check dependencies.

        Parameters
        ----------
        irods_env_file : str
            iRODS environment file.
        local_path : str
            Local path of file or directory.
        irods_path : str
            Remote path of data object or collection.
        irods_resc : str
            Name of iRODS resource for uploading.
        operation : str
            Name of operation: upload or download.
        logdir : str
            Local path of iBridgesCli logging directory.
        plugins : list[dict]
            Plugin definitions.

        """
        utils.utils.init_logger(THIS_APPLICATION)
        utils.utils.set_log_level()
        # Load the iBridges configuration from file.
        self.conf = self.context.ibridges_configuration.config
        default_irods_env_file = utils.path.LocalPath(
            utils.context.DEFAULT_IRODS_ENV_FILE).expanduser()
        last_irods_env_file = ''
        if 'last_ienv' in self.conf:
            last_irods_env_file = utils.path.LocalPath(
                utils.context.IRODS_DIR, self.conf['last_ienv'])
        # CLI parameters override ibridges_config.json
        self.context.irods_env_file = (
                irods_env_file or
                last_irods_env_file or
                default_irods_env_file or
                self._clean_exit('need iRODS environment file', True)
        )
        logging.debug(
            'self.context.irods_env_file=%s', self.context.irods_env_file)
        # Now that the `irods_env_file` is set, load the iRODS
        # environment from file.
        self.ienv = self.context.irods_environment.config
        self.local_path = (
                utils.path.LocalPath(local_path).expanduser() or
                self._clean_exit('need local path', True)
        )
        logging.debug('self.local_path=%s', self.local_path)
        self.irods_path = (
                utils.path.iRODSPath(irods_path) or
                self._clean_exit('need iRODS path', True)
        )
        logging.debug('self.irods_path=%s', self.irods_path)
        # Read default irods_resc from env file if not specified.
        self.irods_resc = (
                irods_resc or
                self.ienv.get('irods_default_resource', '') or
                self._clean_exit('need an iRODS resource', True)
        )
        logging.debug('self.irods_resc=%s', self.irods_resc)
        self.operation = operation
        logging.debug('self.operation=%s', self.operation)
        logdir_path = utils.path.LocalPath(logdir)
        logging.debug('logdir_path=%s', logdir_path)
        self.plugins = self._cleanup_plugins(plugins)
        logging.debug('self.plugins=%s', self.plugins)
        # Check if paths actually exist.
        for path in [self.context.irods_env_file, self.local_path, logdir_path]:
            if not path.exists():
                self._clean_exit(f'{path} does not exist')

    @classmethod
    def _cleanup_plugins(cls, plugins: list[dict]) -> list[dict]:
        """Filter plugins based on remaining actions.

        Format:

            plugins = [
                {
                    'hook': 'upload',
                    'actions' : [
                        { 'slot': 'pre', 'function': function_before },
                        { 'slot': 'post', 'function': function_after }
                    ]
                }
            ]

        Returns
        -------
        list[dict]
            Active plugins.

        """
        # Filter plugins.
        plugins = [plugin for plugin in plugins
                   if 'hook' in plugin and 'actions' in plugin]
        # Filter plugins actions.
        for plugin in plugins:
            plugin['actions'] = [action for action in plugin['actions']
                                 if (
                                         'function' in action and
                                         callable(action['function']) and
                                         'slot' in action and
                                         action['slot'] in ['pre', 'post']
                                 )]
        # Filter plugins with remaining actions.
        return [plugin for plugin in plugins if len(plugin['actions']) > 0]

    def _clean_exit(self, message: str = None, show_help: bool = False,
                    exit_code: int = 1):
        """Exit program when something is wrong giving a message, help
        and/or an exit code.

        Parameters
        ----------
        message : str
            Error message.
        show_help : bool
            Whether to show the help.
        exit_code : int
            System return code.

        """
        if message:
            if exit_code == 0:
                logging.info(message)
            else:
                logging.error(message)
        if show_help:
            parser.print_help()
        if self.conn:
            self.conn.cleanup()
        sys.exit(exit_code)

    def connect_irods(self) -> bool:
        """Connect to iRODS instance after interactively asking for
        password.

        Returns
        -------
        bool
            If the iRODS session is successful.

        """
        attempts = 0
        while True:
            envname = self.context.irods_env_file.name
            secret = getpass.getpass(
                f'Password for {envname} (leave empty to use cached): ')
            try:
                if not self.context.ienv_is_complete():
                    self._clean_exit(
                        'iRODS environment file incomplete', True)
                self.conn.password = secret
                self.conn.connect()

                if self.conn.icommands.has_icommands:
                    in_var = input(
                        "Use icommands (Y/N, default Y): ").strip().lower()
                    if in_var in ['', 'y', 'yes']:
                        self.conn.use_icommands = True
                        self.conn.icommands.set_irods_env_file(
                            self.context.irods_env_file)

                assert self.conn.session.has_valid_irods_session(), "No session"
                break
            except AssertionError as error:
                logging.error('Failed to connect: %r', error)
                attempts += 1
                if attempts >= 3 or input('Try again (Y/n): ').lower() == 'n':
                    return False
        return True

    @plugin_hook
    def download(self) -> bool:
        """Download dataobject or collection from iRODS.

        Returns
        -------
        bool
            Whether operation is successful.

        """
        # status for the benefit of the plugin
        self.download_finished = False

        # checks if remote object exists and if it's an object or a collection
        if self.conn.collection_exists(self.irods_path):
            item = self.conn.get_collection(self.irods_path)
        elif self.conn.dataobject_exists(self.irods_path):
            item = self.conn.get_dataobject(self.irods_path)
        else:
            logging.error('iRODS path %s does not exist', self.irods_path)
            return False

        # get its size to check if there's enough space
        download_size = self.conn.get_irods_size([self.irods_path])
        logging.info(
            "Downloading '%s' (approx. %sGB)", self.irods_path,
            round(download_size * kw.MULTIPLIER, 2))

        # download
        self.conn.download_data(
            source=item, destination=self.local_path,
            size=download_size, force=False)

        self.download_finished = True

        logging.info('Download complete')
        return True

    @plugin_hook
    def upload(self) -> bool:
        """Uploads local file(s) to iRODS.

        Returns
        -------
        bool
            Whether operation is successful.

        """
        # status for the benefit of the plugin
        self.upload_finished = False

        # check if intended upload target exists
        try:
            self.conn.ensure_coll(self.target_path)
            logging.info('Uploading to %s', self.target_path)
        except (irods.exception.CollectionDoesNotExist,
                irods.exception.SYS_INVALID_INPUT_PARAM):
            logging.error('Collection path invalid: %s', self.target_path)
            return False

        # check if there's enough space left on the resource
        upload_size = utils.utils.get_local_size([self.local_path])

        free_space = int(self.conn.get_free_space(resc_name=self.irods_resc))
        if free_space-1000**3 < upload_size and \
                not self.conf.get('force_transfers', False):
            logging.error('Not enough space left on iRODS resource to upload.')
            return False

        self.conn.upload_data(
            source=self.local_path,
            destination=self.conn.get_collection(self.target_path),
            res_name=self.irods_resc,
            size=upload_size,
            force=True)

        self.upload_finished = True

        logging.info('Upload complete')
        return True

    def run(self):
        """Run the main process of the class instance.

        """
        self.connect_irods()

        if not self.conn.session.has_valid_irods_session():
            self._clean_exit("Connection failed")

        if self.operation == 'download':

            if not self.download():
                self._clean_exit()

        elif self.operation == 'upload':

            # try:
            #     _ = self.conn.resources.get(self.irods_resc)
            # except ResourceDoesNotExist:
            #     self._clean_exit(f"iRODS resource '{self.irods_resc}' not found")

            if self.irods_resc not in self.conn.resources:
                self._clean_exit(f"iRODS resource '{self.irods_resc}' not found")

            self.target_path = self.irods_path

            if not self.upload():
                self._clean_exit()

        else:
            logging.error('Unknown operation: %s', self.operation)

        self._clean_exit(message="Done", exit_code=0)


def from_arguments(**kwargs) -> iBridgesCli:
    """Create iBridgesCli instance from cli-arguments. optionally,
    functions to be triggered at hook-points can be specified.

    Returns
    -------
    iBridgesCli
        Instance initialized with arguments.

    """
    default_logdir = utils.path.LocalPath(utils.context.IBRIDGES_DIR).expanduser()
    parser.add_argument(
        '--local_path', '-l',
        help='local path to download to, or upload from', type=str)
    parser.add_argument(
        '--irods_path', '-i',
        help='irods path to upload to, or download from', type=str)
    parser.add_argument(
        '--operation', '-o', type=str, choices=['upload', 'download'],
        required=True)
    parser.add_argument(
        '--env', '-e', type=str,
        help='path to irods environment file (irods_environment.json).')
    parser.add_argument(
        '--irods_resc', '-r', type=str,
        help='irods resource. default is read from irods env file.')
    parser.add_argument(
        '--logdir', type=str,
        help=f'directory for logfile. default: {default_logdir}',
        default=default_logdir)
    args = parser.parse_args()
    return iBridgesCli(
        irods_env_file=args.env,
        local_path=args.local_path,
        irods_path=args.irods_path,
        irods_resc=args.irods_resc,
        operation=args.operation,
        logdir=args.logdir,
        plugins=kwargs.get('plugins')
    )


def main():
    """Main function to instantiate the main class and run the main
    process.

    """
    elab = utils.elab_plugin.ElabPlugin()
    cli = from_arguments(plugins=[
        {
            'hook': 'upload',
            'actions': [
                {'slot': 'pre', 'function': elab.setup},
                {'slot': 'post', 'function': elab.annotate}
            ]
        }
    ])
    cli.run()


if __name__ == '__main__':
    main()

""" rule operations
"""
import logging

import irods.exception
import irods.rule

from . import session


class Rules(object):
    """Irods Rule operations """

    def __init__(self, sess_man: session.Session):
        """ iRODS data operations initialization

            Parameters
            ----------
            sess_man : session.Session
                instance of the Session class

        """
        self.sess_man = sess_man

    def execute_rule(self, parameters: dict, rule_type: str = 'irods_rule_language') -> tuple:
        """Execute an iRODS rule.
        Works for rules on the server and with rule files

        Parameters
        ----------
        parameters : dict
            Rule arguments, passed as variable.
        rule_type : str
            changes between irods rule language and python rules.

        Returns
        -------
        tuple
            (stdout, stderr)

        rule file example:
        parameters = {
        'rule_file': 'filename.r',
        'output': 'ruleExecOut',
        'params': {  # extra quotes for string literals
            '*obj': '"/zone/home/user"',
            '*name': '"attr_name"',
            '*value': '"attr_value"'
        }
        }
        rule on server example:

        """
        try:
            rule = irods.rule.Rule(
                self.sess_man.irods_session,
                instance_name=f'irods_rule_engine_plugin-{rule_type}-instance', **parameters)
            out = rule.execute()
        except irods.exception.NetworkException as error:
            logging.info('Lost connection to iRODS server.')
            return '', repr(error)
        except irods.exception.SYS_HEADER_READ_LEN_ERR as error:
            logging.info('iRODS server hiccuped.  Check the results and try again.')
            return '', repr(error)
        except Exception as error:
            logging.info('RULE EXECUTION ERROR', exc_info=True)
            return '', repr(error)
        stdout, stderr = '', ''
        if len(out.MsParam_PI) > 0:
            buffers = out.MsParam_PI[0].inOutStruct
            stdout = (buffers.stdoutBuf.buf or b'').decode()
            # Remove garbage after terminal newline.
            stdout = '\n'.join(stdout.split('\n')[:-1])
            stderr = (buffers.stderrBuf.buf or b'').decode()
        return stdout, stderr

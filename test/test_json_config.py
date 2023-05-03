"""Test iBridges JSONConfig.

"""
import json
import os

import utils


class TestJSONConfig:
    """

    """

    def test_json_config(self):
        filename = './config.json'
        if os.path.exists(filename):
            os.remove(filename)
        config = utils.json_config.JsonConfig(filename)
        test_config = {'test_key': 'test_val'}
        config.config = test_config
        config.save()
        assert os.path.exists(filename)
        with open(filename) as confd:
            assert json.load(confd) == test_config

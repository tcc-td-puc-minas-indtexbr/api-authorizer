import json
import os
import sys

if __package__:
    current_path = os.path.abspath(os.path.dirname(__file__)).replace('/' + str(__package__), '', 1)
else:
    current_path = os.path.abspath(os.path.dirname(__file__))

if not current_path[-1] == '/':
    current_path += '/'

# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = current_path.replace('tests/', '')

_REGISTERED_PATHS = False


def register_paths():
    global _REGISTERED_PATHS
    if not _REGISTERED_PATHS:
        # path fixes, define the priority of the modules search
        sys.path.insert(0, ROOT_DIR)
        sys.path.insert(1, ROOT_DIR + 'chalicelib/')
        sys.path.insert(2, ROOT_DIR + 'vendor/')
        # print('registered paths')
        _REGISTERED_PATHS = True
    # else:
    # print('paths already registered')
    pass


register_paths()

# print(ROOT_DIR)
# print(ROOT_DIR + 'chalicelib/')

_LOADED = False


def load_env(env='dev', force=False):
    global _LOADED
    if not _LOADED or force:
        try:
            from chalicelib.logging import get_logger
            get_logger().info('Test - Loading env: {}'.format(env))
        except:
            print('load_env: Unable to load logger')

        chalice_config_path = ROOT_DIR + '.chalice/config.json'

        if os.path.isfile(chalice_config_path):
            file = open(chalice_config_path, 'r')
            data = file.read()
            configs = json.loads(data)
            env_vars = configs['stages'][env]['environment_variables']

            for k, v in env_vars.items():
                os.environ[k] = v
        else:
            exit('unable to load config')
        _LOADED = True
    else:
        pass


load_env()
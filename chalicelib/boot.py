import os
import sys
import json

if __package__:
    current_path = os.path.abspath(os.path.dirname(__file__)).replace('/' + str(__package__), '', 1)
else:
    current_path = os.path.abspath(os.path.dirname(__file__))

if not current_path[-1] == '/':
    current_path += '/'

ROOT_DIR = current_path


def load_env(env='dev', force=False):
    global _LOADED
    if not _LOADED or force:
        try:
            from chalicelib.logging import get_logger
            get_logger().info('Test - Loading env: {}'.format(env))
        except:
            print('load_env: Unable to load logger')

        chalice_config_path = current_path + '.chalice/config.json'

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


def register_vendor():
    vendor_path = current_path + "vendor"
    # print(vendor_path)
    if not os.path.isdir(vendor_path):
        vendor_path = current_path + "/vendor"
        # print(vendor_path)

    sys.path.insert(0, vendor_path)


def register_path(path):
    if os.path.isdir(path):
        sys.path.insert(0, path)


def print_env(app, logger):
    logger.info('Environment: %s' % os.getenv('APP_ENV'))
    # logger.info('Host: %s' % os.getenv('APP_HOST'))
    # logger.info('Port: %s' % os.getenv('APP_PORT'))
    # logger.info('Database: %s' % os.getenv('DB_HOST'))
    logger.info('Log Level: %s' % os.getenv('LOG_LEVEL'))
    logger.info('Debug: %s' % os.getenv('DEBUG'))
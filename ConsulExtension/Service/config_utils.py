import configparser
import os


def get_conf_value(section, key_name):
    """Function to return value from configuration
    File

    Args:
        key_name (str): Name of key
    """
    current_path = os.path.dirname(os.path.abspath(__file__))
    config = configparser.ConfigParser()
    config.read(''.join([current_path, '/config.cfg']))
    return config.get(section, key_name)

import configparser

def get_conf_value(section, key_name):
    """Funtion to return value from configuration
    File

    Args:
        key_name (str): Name of key
    """
    config = configparser.ConfigParser()
    config.read('config.cfg')
    return config.get(section, key_name)
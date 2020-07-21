import os
from Service.tests.utils import parse_json_file


def get_absolue_path(input_file):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    file_path = r'/'.join([dir_path, input_file])
    return file_path


def get_data(file_name):
    return parse_json_file(get_absolue_path(file_name))

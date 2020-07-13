"""Utilities for test cases"""

import json
import os


class DummyClass:
    """Dummy class for any dummy object"""
    pass


def get_absolue_path(input_file):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    print('Dir path : {}'.format(dir_path))
    file_path = r''.join([dir_path,
                          input_file])
    print('Absolute file path {} '.format(file_path))
    return file_path


def parse_json_file(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return data

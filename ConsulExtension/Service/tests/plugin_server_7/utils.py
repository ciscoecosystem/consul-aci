import json
import os


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


def generate_dummy_new_mapping_data(input_file):
    def dummy_get_new_mapping(tenant, datacenter):
        file_path = get_absolue_path(input_file)
        x = parse_json_file(file_path)
        print('=== {}'.format(x))
        return x
    return dummy_get_new_mapping


def generate_dummy_db_output(format_required, formator, expected_file):
    def dummy_select_query(self, connection, table_name, primary_key={}):
        file_path = get_absolue_path(expected_file)
        x = parse_json_file(file_path)
        print('=== {}'.format(x))
        if format_required:
            format(x)
        else:
            return x


def generate_dummy_exception_new_mapping_data():
    def dummy_get_new_mapping(tenant, datacenter):
        raise Exception
    return dummy_get_new_mapping


def compare_obj_list(actual_output, expected_output):
    if actual_output == expected_output:
        return True
    else:
        flag = False
        for act in actual_output:
            for exp in expected_output:
                for k, v in exp.items():
                    if act[k] == v:
                        flag = True
                    else:
                        flag = False
                        break
                if not flag:
                    break
            if not flag:
                break
        return flag


def verify_mapping(actual_output, expected_file):
    file = get_absolue_path(expected_file)
    expected_json = parse_json_file(file)
    actual_output = ''.join(actual_output)
    actual_output = json.loads(actual_output)
    print('==== {}'.format(actual_output))
    print('==== {}'.format(expected_json))
    if actual_output == expected_json:
        return True
    else:
        return False


def verify_change_key(actual_output, expected_file):
    file = get_absolue_path(expected_file)
    expected_output = parse_json_file(file)
    return compare_obj_list(actual_output, expected_output)

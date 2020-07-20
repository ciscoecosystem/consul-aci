from Service.tests.utils import get_absolue_path
from Service.tests.utils import parse_json_file
import json


def generate_dummy_new_mapping_data(input_file):
    def dummy_get_new_mapping(tenant, datacenter):
        file_path = get_absolue_path(input_file)
        x = parse_json_file(file_path)
        print('=== {}'.format(x))
        return x
    return dummy_get_new_mapping


def generate_dummy_db_output(formator, expected_file):
    def dummy_select_query(self, connection, table_name, primary_key={}):
        file_path = get_absolue_path(expected_file)
        x = parse_json_file(file_path)
        print('=== {}'.format(x))
        if formator:
            format(x)
        else:
            return x
    return dummy_select_query


def generate_multiple_dummy_db_output(formator, expected_files):
    db_outputs = []
    for file in expected_files:
        file_path = get_absolue_path(file)
        x = parse_json_file(file_path)
        # print('=== {}'.format(x))
        if formator:
            db_outputs.append(formator(x))
        else:
            db_outputs.append(x)
    cnt = 0
    print('=== {}'.format(db_outputs))
    while cnt < len(db_outputs):
        yield db_outputs[cnt]
        cnt = cnt + 1


def dummy_db_select_exception():
    def dummy_select_query(self, connection, table_name, primary_key={}):
        raise Exception()
    return dummy_select_query


def generate_dummy_exception_new_mapping_data():
    def dummy_get_new_mapping(tenant, datacenter):
        raise Exception
    return dummy_get_new_mapping


def compare_dicts(actual, expected):
    shared_items = {k: expected[k] for k in expected if k in actual and expected[k] == actual[k]}
    return len(shared_items.keys()) == len(expected.keys()) == len(actual.keys())


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


def verify_agent_status(actual_output, expected_file):
    file = get_absolue_path(expected_file)
    expected_output = parse_json_file(file)
    print('======== {} {} '.format(actual_output, expected_output))
    return compare_dicts(actual_output, expected_output)


def get_data_json(file_name):
    return parse_json_file(get_absolue_path(file_name))


def get_data_str(file_name):
    return json.dumps(parse_json_file(get_absolue_path(file_name)))

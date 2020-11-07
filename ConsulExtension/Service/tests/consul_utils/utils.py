import json
import os


class DummyResponse:
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


def create_dummy_session_get_status_code(response_code):
    def dummy_session(self, url, timeout=0):
        response = DummyResponse()
        response.status_code = int(response_code)
        return response
    return dummy_session


def create_dummy_session_get(input_file):
    file_path = get_absolue_path(input_file)

    def dummy_session(self, url, timeout=0):
        response = DummyResponse()
        with open(file_path) as f:
            response.content = ''.join(f)
        return response
    return dummy_session


def create_dummy_session_with_error_get(input_file):
    file_path = get_absolue_path(input_file)

    def dummy_session(self, url, timeout=0):
        response = DummyResponse()
        with open(file_path) as f:
            response.content = ''.join(f)
            response.status_code = 404
        return response
    return dummy_session


def verify_nodelist_against_catalog(actual_output, output_file):
    output_file = get_absolue_path(output_file)
    data = parse_json_file(output_file)
    flag = False
    for expected_node in data:
        flag = any(
            expected_node['node_id'] == each['node_id']
            and expected_node['node_ip'] == each['node_ip'] for each in actual_output
        )
    if data == actual_output:
        flag = True
    return flag


def verify_nodes_services(actual_output, output_file):
    output_file = get_absolue_path(output_file)
    data = parse_json_file(output_file)
    flag = False
    for expected_node in data:
        flag = any(
            expected_node['service_id'] == each['service_id']
            and set(expected_node['service_address']) == set(each['service_address']) for each in actual_output
        )
    if data == actual_output:
        flag = True
    return flag


def verify_node_and_service_checks(actual_output, output_file):
    output_file = get_absolue_path(output_file)
    data = parse_json_file(output_file)
    if data == actual_output:
        return True
    else:
        shared_items = {k: data[k] for k in data if k in actual_output and data[k] == actual_output[k]}
        return len(shared_items.keys()) == len(data.keys()) == len(actual_output.keys())


def verify_service_info(actual_output, expected_output):
    if (
        actual_output[0] == expected_output[0]
        and actual_output[1] == expected_output[1]
        and actual_output[2] == expected_output[2]
    ):
        return True
    else:
        return False


def verify_datacenter(actual_output, expected_output):
    if actual_output == expected_output:
        return True
    else:
        return False


def verify_detailed_service_check(actual_output, output_file):
    return True

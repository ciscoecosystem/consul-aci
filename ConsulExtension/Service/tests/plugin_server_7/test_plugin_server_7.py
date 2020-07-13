import pytest
from Service import plugin_server
from Service.tests.plugin_server_7.utils import (
                                    generate_dummy_new_mapping_data,
                                    verify_mapping,
                                    generate_dummy_exception_new_mapping_data,
                                    verify_change_key,
                                    get_absolue_path,
                                    parse_json_file)


@pytest.mark.parametrize("test_input, expected",
                         [('/data/1_mapping_initial_input.json',
                          {'output': '/data/1_mapping_initial_output.json',
                           'method': verify_mapping}),
                           ('/data/3_mapping_empty_input.json',
                          {'output': '/data/3_mapping_empty_output.json',
                           'method': verify_mapping})])
def test_mapping(test_input, expected):
    plugin_server.get_new_mapping = generate_dummy_new_mapping_data(test_input)
    actual_output = plugin_server.mapping('', '')
    verifier = expected['method']
    assert verifier(actual_output, expected['output'])


@pytest.mark.parametrize("test_input, expected",
                         [('/data/3_mapping_empty_input.json',
                          {'output': '/data/2_mapping_exception_output.json',
                           'method': verify_mapping})])
def test_mapping_exception(test_input, expected):
    plugin_server.get_new_mapping = generate_dummy_exception_new_mapping_data()
    actual_output = plugin_server.mapping('', '')
    verifier = expected['method']
    assert verifier(actual_output, expected['output'])


@pytest.mark.parametrize('input, expected',
                         [(100, ('200', 'Polling Interval Set!')),
                          (3, ('200', 'Polling Interval Set!'))])
def test_set_polling_interval(input, expected):
    assert plugin_server.set_polling_interval(input), expected


@pytest.mark.parametrize('input, expected',
                         [('/data/change_key/1_initial_input.json', '/data/change_key/1_initial_output.json'),
                          ('/data/change_key/1_empty_input.json', '/data/change_key/1_empty_output.json'),
                          (None, [])])
def test_change_key(input, expected):
    services = None
    if input:
        input_file = get_absolue_path(input)
        services = parse_json_file(input_file)
        actual_output = plugin_server.change_key(services)
        assert verify_change_key(actual_output, expected)
    else:
        actual_output = plugin_server.change_key(services)
        assert actual_output == []

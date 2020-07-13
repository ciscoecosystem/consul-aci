import requests
import Service.consul_utils
from Service.tests.consul_utils.utils import (create_dummy_session_get_status_code,
                                              verify_nodelist_against_catalog,
                                              verify_nodes_services,
                                              create_dummy_session_get,
                                              verify_node_and_service_checks,
                                              verify_service_info,
                                              verify_datacenter,
                                              verify_detailed_service_check)
import pytest


@pytest.mark.parametrize("test_input,expected",
                         [("200", (True, None)),
                          ("403", (False, '403: Authentication failed!')),
                          ("500", (False, '500: Consul Server Error!'))])
def test_check_connection(test_input, expected):
    requests.Session.get = create_dummy_session_get_status_code(test_input)
    consul = Service.consul_utils.Consul('', '', '', '')
    connection, message = consul.check_connection()
    assert connection == expected[0] and message == expected[1]


@pytest.mark.parametrize("test_input,expected",
                         [("/data/node_data/1_initial_test_input.json",
                           {'method': verify_nodelist_against_catalog,
                            'output_file':
                            '/data/node_data/1_initial_test_output.json'}),
                          ("/data/node_data/2_same_node_diff_ips_input.json",
                           {'method': verify_nodelist_against_catalog,
                            'output_file':
                            '/data/node_data/2_same_node_diff_ips_output.json'}),
                          ("/data/node_data/3_empty_node_input.json",
                           {'method': verify_nodelist_against_catalog,
                            'output_file':
                            '/data/node_data/3_empty_node_output.json'})
                          ])
def test_nodes(test_input, expected):
    requests.Session.get = create_dummy_session_get(test_input)
    consul = Service.consul_utils.Consul('', '', '', '')
    actual_output = consul.nodes()
    verifier = expected['method']
    assert verifier(actual_output, expected['output_file'])


@pytest.mark.parametrize("test_input,expected",
                         [(("nodename18", "/data/nodes_services/1_initial_node_service_input.json"),
                           {'method': verify_nodes_services,
                            'output_file':
                            '/data/nodes_services/1_initial_node_service_output.json'}),
                          (("nodename19", "/data/nodes_services/2_blank_ip_node_service_input.json"),
                           {'method': verify_nodes_services,
                            'output_file':
                            '/data/nodes_services/2_blank_ip_node_service_output.json'}),
                          (("nodename10", "/data/nodes_services/3_empty_node_service_input.json"),
                           {'method': verify_nodes_services,
                            'output_file':
                            '/data/nodes_services/3_empty_node_service_ouput.json'})
                          ])
def test_nodes_services(test_input, expected):
    requests.Session.get = create_dummy_session_get(test_input[1])
    consul = Service.consul_utils.Consul('', '', '', '')
    actual_output = consul.nodes_services(test_input[0])
    verifier = expected['method']
    assert verifier(actual_output, expected['output_file'])


@pytest.mark.parametrize("test_input,expected",
                         [(("servicename12",
                            "/data/service_check/1_initial_service_check.json"),
                           {'method': verify_node_and_service_checks,
                            'output_file':
                            '/data/service_check/1_initial_service_check_output.json'}),
                          (("servicename12",
                            "/data/service_check/2_empty_service_check.json"),
                           {'method': verify_node_and_service_checks,
                            'output_file':
                            '/data/service_check/2_empty_service_check_output.json'}),
                          (("servicename12",
                            "/data/service_check/3_passing_service_check_input.json"),
                           {'method': verify_node_and_service_checks,
                            'output_file':
                            '/data/service_check/3_passing_service_check_output.json'}),
                          (("servicename12",
                            "/data/service_check/4_exception_service_check_intput.json"),
                           {'method': verify_node_and_service_checks,
                            'output_file':
                            '/data/service_check/4_exception_service_check_output.json'})
                          ])
def test_service_checks(test_input, expected):
    requests.Session.get = create_dummy_session_get(test_input[1])
    consul = Service.consul_utils.Consul('', '', '', '')
    actual_output = consul.service_checks(test_input[0])

    verifier = expected['method']
    assert verifier(actual_output, expected['output_file'])


@pytest.mark.parametrize("test_input,expected", [
    ((
        "nodename1", "/data/node_check/1_initial_node_check_input.json"), {
        'method': verify_node_and_service_checks,
        'output_file': '/data/node_check/1_initial_node_check_output.json'
    }),
    ((
        "nodename1", "/data/node_check/2_empty_node_check_intput.json"), {
        'method': verify_node_and_service_checks,
        'output_file': '/data/node_check/2_empty_node_check_output.json'}),
    ((
        "nodename1", "/data/node_check/3_exception_node_check_input.json"), {
        'method': verify_node_and_service_checks,
        'output_file': '/data/node_check/3_exception_node_check_output.json'})
])
def test_node_checks(test_input, expected):
    requests.Session.get = create_dummy_session_get(test_input[1])
    consul = Service.consul_utils.Consul('', '', '', '')
    actual_output = consul.service_checks(test_input[0])

    verifier = expected['method']
    assert verifier(actual_output, expected['output_file'])


@pytest.mark.parametrize("test_input,expected", [
    (("nodename1", "/data/service_info/1_initial_service_info.json"), {
        'method': verify_service_info,
        'output': (['cache', 'global'], 'servicekind10', 'namespace10')
    }),
    (("nodename1", "/data/service_info/2_empty_service_info.json"), {
        'method': verify_service_info,
        'output': ([], "", "")
    }),
    (("nodename1", "/data/service_info/3_wrong_name_service_info.json"), {
        'method': verify_service_info,
        'output': ([], '', '')
    })
])
def test_service_info(test_input, expected):
    requests.Session.get = create_dummy_session_get(test_input[1])
    consul = Service.consul_utils.Consul('', '', '', '')
    actual_output = consul.service_info(test_input[0])

    verifier = expected['method']
    assert verifier(actual_output, expected['output'])


@pytest.mark.parametrize("test_input,expected", [
    (("/data/datacenter/1_initial_datacenter.json"), {
        'method': verify_datacenter,
        'output': 'dc1'
    }),
    (("/data/datacenter/2_empty_datacenter.json"), {
        'method': verify_datacenter,
        'output': '-'
    }),
    (("/data/datacenter/3_exception_datacenter.json"), {
        'method': verify_datacenter,
        'output': '-'
    })
])
def test_datacenter(test_input, expected):
    requests.Session.get = create_dummy_session_get(test_input)
    consul = Service.consul_utils.Consul('', '', '', '')
    actual_output = consul.datacenter()
    verifier = expected['method']
    assert verifier(actual_output, expected['output'])


@pytest.mark.parametrize("test_input,expected", [
    (("servicename12",
      "serviceid12",
      "/data/detailed_service_check/1_initial_detailed_service_check_input.json"), {
          'method': verify_detailed_service_check,
          'output_file': '/data/detailed_service_check/1_initial_detailed_service_check_output.json'
    }),
    (("servicename12",
      "serviceid12",
      "/data/detailed_service_check/2_empty_detailed_service_check_input.json"), {
          'method': verify_detailed_service_check,
          'output_file': '/data/detailed_service_check/2_empty_detailed_service_check_output.json'
    })
])
def test_detailed_service_check(test_input, expected):
    requests.Session.get = create_dummy_session_get(test_input[2])
    consul = Service.consul_utils.Consul('', '', '', '')
    actual_output = consul.detailed_service_check(test_input[0], test_input[1])

    verifier = expected['method']
    assert verifier(actual_output, expected['output_file'])


@pytest.mark.parametrize("test_input,expected", [
    (("nodename1",
      "/data/detailed_node_check/1_initial_detailed_node_check_input.json"), {
          'method': verify_detailed_service_check,
          'output_file': '/data/detailed_node_check/1_initial_detailed_node_check_output.json'
    })
])
def test_detailed_node_check(test_input, expected):
    requests.Session.get = create_dummy_session_get(test_input[1])
    consul = Service.consul_utils.Consul('', '', '', '')
    actual_output = consul.detailed_node_check(test_input[0])

    verifier = expected['method']
    assert verifier(actual_output, expected['output_file'])

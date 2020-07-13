import pytest
from Service import data_fetch
from Service import consul_utils
from Service import threading_util


def nodes(self):
    response = [
        {
            "node_id": "test_node_id"
        },
        {
            "node_id": "test_node_id2"
        }
    ]
    return response


class DummyConsul:
    def nodes_services(self, node_name):
        response = [
            {
                "service_id": "service_id1",
                "service_address": "service_address1",
                "service_port": "service_port1",
                "service_ip": "service_ip1",
                "service_name": "service_name1"
            },
            {
                "service_id": "service_id2",
                "service_address": "service_address2",
                "service_port": "service_port2",
                "service_ip": "service_ip2",
                "service_name": "service_name2"
            }
        ]
        return response

    def detailed_node_check(self, node_name):
        response = [
            {
                "CheckID": "test_CheckID1"
            },
            {
                "CheckID": "test_CheckID2"
            }
        ]
        return response

    def service_info(self, service_name):
        return [
            "test_service_tags",
            "test_service_kind",
            "test_service_namespace"
        ]

    def detailed_service_check(self, service_name, service_id):
        response = [
            {
                "CheckID": "test_CheckID1"
            },
            {
                "CheckID": "test_CheckID2"
            }
        ]
        return response


def test_get_nodes():
    consul_utils.Consul.nodes = nodes
    nodes_dict = threading_util.ThreadSafeDict()
    agent = {
        "ip": "test_ip",
        "port": "test_port",
        "token": "test_token",
        "protocol": "test_protocol"
    }
    expected = threading_util.ThreadSafeDict()
    expected['test_node_id'] = {
        'agent_addr': ['test_ip:test_port'],
        'node_id': 'test_node_id',
        'agent_consul_obj': None
    }
    expected['test_node_id2'] = {
        'agent_addr': ['test_ip:test_port'],
        'node_id': 'test_node_id2',
        'agent_consul_obj': None
    }
    data_fetch.get_nodes(nodes_dict, agent)
    assert nodes_dict.keys() == expected.keys()
    for key in nodes_dict:
        assert nodes_dict[key].keys() == expected[key].keys()
        for each in expected[key]:
            if each != 'agent_consul_obj':
                assert nodes_dict[key][each] == expected[key][each]


def test_get_services():
    dummy_consul_obj = DummyConsul()
    node = {
        "node_name": "node_name",
        "agent_consul_obj": dummy_consul_obj,
        "node_name": "node_name",
        "node_id": "node_id",
        "agent_addr": "agent_addr"
    }
    expected = threading_util.ThreadSafeDict()
    expected["service_id1{}".format("node_id")] = {
        "service_id": "service_id1",
        "service_address": "service_address1",
        "service_port": "service_port1",
        "service_ip": "service_ip1",
        "service_name": "service_name1",
        "agent_consul_obj": dummy_consul_obj,
        "node_id": "node_id",
        "agent_addr": "agent_addr"
    }
    expected["service_id2{}".format("node_id")] = {
        "service_id": "service_id2",
        "service_address": "service_address2",
        "service_port": "service_port2",
        "service_ip": "service_ip2",
        "service_name": "service_name2",
        "agent_consul_obj": dummy_consul_obj,
        "node_id": "node_id",
        "agent_addr": "agent_addr"
    }

    services_dict = threading_util.ThreadSafeDict()
    data_fetch.get_services(services_dict, node)
    assert services_dict == expected


def test_get_node_checks():
    dummy_consul_obj = DummyConsul()
    node_checks_dict = threading_util.ThreadSafeDict()
    node = {
        "node_name": "node_name",
        "agent_consul_obj": dummy_consul_obj,
        "node_name": "node_name",
        "node_id": "node_id",
        "agent_addr": "agent_addr"
    }
    expected = threading_util.ThreadSafeDict()
    expected["test_CheckID1node_id"] = {
        "node_id": "node_id",
        "node_name": "node_name",
        "agent_addr": "agent_addr",
        "CheckID": "test_CheckID1"
    }
    expected["test_CheckID2node_id"] = {
        "node_id": "node_id",
        "node_name": "node_name",
        "agent_addr": "agent_addr",
        "CheckID": "test_CheckID2"
    }
    data_fetch.get_node_checks(node_checks_dict, node)
    assert expected == node_checks_dict


def test_get_service_info():
    dummy_consul_obj = DummyConsul()
    service = {
        "service_name": "service_name1",
        "agent_consul_obj": dummy_consul_obj
    }
    expected = {
        "service_name": "service_name1",
        "agent_consul_obj": dummy_consul_obj,
        "service_tags": "test_service_tags",
        "service_kind": "test_service_kind",
        "service_namespace": "test_service_namespace"
    }
    data_fetch.get_service_info(service)
    assert expected == service


def test_get_service_checks():
    dummy_consul_obj = DummyConsul()
    service_checks_dict = threading_util.ThreadSafeDict()
    service = {
        "service_name": "service_name",
        "agent_consul_obj": dummy_consul_obj,
        "service_id": "service_id",
        "agent_addr": "agent_addr"
    }
    expected = threading_util.ThreadSafeDict()
    expected["test_CheckID1service_id"] = {
        "service_id": "service_id",
        "agent_addr": "agent_addr",
        "CheckID": "test_CheckID1"
    }
    expected["test_CheckID2service_id"] = {
        "service_id": "service_id",
        "agent_addr": "agent_addr",
        "CheckID": "test_CheckID2"
    }
    data_fetch.get_service_checks(service_checks_dict, service)
    assert expected == service_checks_dict

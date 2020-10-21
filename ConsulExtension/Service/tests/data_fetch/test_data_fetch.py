from Service import data_fetch
from Service import consul_utils
from Service import threading_util
from Service import alchemy_core
import pytest
import json
import os


def clear_db():
    try:
        os.remove("/home/app/data/ConsulDatabase.db")
    except Exception:
        pass


def reader(filename):
    return json.load(open('./tests/data_fetch/data/{}'.format(filename), 'r'))


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


@pytest.mark.parametrize("case", ["initial", True, False])
def test_change_data_fetch_status(case):

    def dummy_insert_and_update(self, connection, table_name, new_record, field_arg_dict={}):
        assert table_name == expected_table_name
        assert new_record == expected_new_record
        assert field_arg_dict == expected_field_arg_dict

    def dummy_select_from_table(self, connection, table_name):
        ls = ["dummy"]
        if case == "initial":
            ls = []
        return ls

    insert_and_update = alchemy_core.Database.insert_and_update
    alchemy_core.Database.insert_and_update = dummy_insert_and_update
    select_from_table = alchemy_core.Database.select_from_table
    alchemy_core.Database.select_from_table = dummy_select_from_table

    expected_table_name = alchemy_core.Database.DATA_FETCH_TABLE_NAME
    if case != "initial":
        expected_field_arg_dict = {
            'running': not case
        }
        expected_new_record = [case]
        data_fetch.change_data_fetch_status(case)

    if case == "initial":
        expected_field_arg_dict = {}
        expected_new_record = [True]
        data_fetch.change_data_fetch_status(True)

    alchemy_core.Database.insert_and_update = insert_and_update
    alchemy_core.Database.select_from_table = select_from_table


def test_get_agents_from_db():

    def dummy_select_from_table(self, connection, table_name):
        return reader("get_agents_from_db/input.json")

    expected = reader("get_agents_from_db/output.json")

    select_from_table = alchemy_core.Database.select_from_table
    alchemy_core.Database.select_from_table = dummy_select_from_table

    response = data_fetch.get_agents_from_db()
    assert expected == response

    alchemy_core.Database.select_from_table = select_from_table


def test_fetch_and_save_nodes():
    pass

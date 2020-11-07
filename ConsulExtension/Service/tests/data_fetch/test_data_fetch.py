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


def test_change_data_fetch_status():
    clear_db()
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.DATA_FETCH_TABLE_NAME)
    connection.close()
    assert data == []

    data_fetch.change_data_fetch_status(True)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.DATA_FETCH_TABLE_NAME, {}, ['running'])
    connection.close()
    assert data[0][0] is True

    data_fetch.change_data_fetch_status(False)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.DATA_FETCH_TABLE_NAME, {}, ['running'])
    connection.close()
    assert data[0][0] is False
    clear_db()


def test_change_agent_edit_status():
    clear_db()
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.DATA_FETCH_TABLE_NAME)
    connection.close()
    assert data == []

    data_fetch.change_agent_edit_status(True)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.DATA_FETCH_TABLE_NAME, {}, ['edited'])
    connection.close()
    assert data[0][0] is True

    data_fetch.change_agent_edit_status(False)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.DATA_FETCH_TABLE_NAME, {}, ['edited'])
    connection.close()
    assert data[0][0] is False
    clear_db()


@pytest.mark.parametrize("case", [True, False])
def test_get_agent_edit_status(case):
    clear_db()
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    connection = db_obj.engine.connect()
    with connection.begin():
        db_obj.insert_and_update(
            connection,
            db_obj.DATA_FETCH_TABLE_NAME,
            [True, case]
        )
    connection.close()

    status = data_fetch.get_agent_edit_status()

    assert status == case


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

    def dummy_get_nodes(nodes_dict, agent):
        nodes_dict.update(reader('fetch_and_save_nodes/nodes_dict.json'))

    get_nodes = data_fetch.get_nodes
    data_fetch.get_nodes = dummy_get_nodes

    datacenter = 'dc1'
    agents = ['dummy_agent']
    nodes_dict = threading_util.ThreadSafeDict()
    consul_ip_list, nodes_key = data_fetch.fetch_and_save_nodes(datacenter, agents, nodes_dict)

    expected = reader('fetch_and_save_nodes/output.json')
    assert set(expected[0]) == consul_ip_list
    assert set(expected[1]) == nodes_key

    data_fetch.get_nodes = get_nodes


@pytest.mark.parametrize("input_data", reader('remove_unused_nodes/input.json'))
def test_remove_unused_nodes(input_data):
    clear_db()
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    agent_addr_list = input_data["agent_addr_list"]
    nodes_key = set(input_data["nodes_key"])

    connection = db_obj.engine.connect()
    with connection.begin():
        db_obj.insert_and_update(
            connection,
            db_obj.NODE_TABLE_NAME,
            input_data["input"]
        )
    connection.close()

    data_fetch.remove_unused_nodes(agent_addr_list, nodes_key)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.NODE_TABLE_NAME)
    connection.close()

    if data:
        assert list(data[0][:-3]) == input_data["output"]
    else:
        assert data == input_data["output"]
    clear_db()


def test_fetch_and_save_services():

    def dummy_get_services(service_dict, node):
        service_dict.update(reader('fetch_and_save_services/services_dict.json'))

    def dummy_get_service_info(service):
        service.update(reader('fetch_and_save_services/service_info.json'))

    get_services = data_fetch.get_services
    get_service_info = data_fetch.get_service_info
    data_fetch.get_services = dummy_get_services
    data_fetch.get_service_info = dummy_get_service_info

    datacenter = 'dc1'
    nodes_dict = reader('fetch_and_save_services/nodes_dict.json')
    services_dict = threading_util.ThreadSafeDict()
    consul_ip_list, services_key = data_fetch.fetch_and_save_services(datacenter, nodes_dict, services_dict)

    expected = reader('fetch_and_save_services/output.json')
    assert set(expected[0]) == consul_ip_list
    assert set(map(tuple, expected[1])) == services_key

    data_fetch.get_services = get_services
    data_fetch.get_service_info = get_service_info


@pytest.mark.parametrize("input_data", reader('remove_unused_services/input.json'))
def test_remove_unused_services(input_data):
    clear_db()
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    agent_addr_list = input_data["agent_addr_list"]
    services_key = set(input_data["services_key"])

    connection = db_obj.engine.connect()
    with connection.begin():
        db_obj.insert_and_update(
            connection,
            db_obj.SERVICE_TABLE_NAME,
            input_data["input"]
        )
    connection.close()

    data_fetch.remove_unused_services(agent_addr_list, services_key)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.SERVICE_TABLE_NAME)
    connection.close()

    if data:
        assert list(data[0][:-3]) == input_data["output"]
    else:
        assert data == input_data["output"]
    clear_db()


def test_fetch_and_save_nodechecks():

    def dummy_get_node_checks(node_checks_dict, agent):
        node_checks_dict.update(reader('fetch_and_save_nodechecks/node_checks_dict.json'))

    get_node_checks = data_fetch.get_node_checks
    data_fetch.get_node_checks = dummy_get_node_checks

    nodes_dict = reader('fetch_and_save_nodechecks/nodes_dict.json')
    node_checks_dict = threading_util.ThreadSafeDict()
    node_checks_key = data_fetch.fetch_and_save_nodechecks(nodes_dict, node_checks_dict)

    expected = reader('fetch_and_save_nodechecks/output.json')
    assert set(map(tuple, expected)) == node_checks_key

    data_fetch.get_node_checks = get_node_checks


@pytest.mark.parametrize("input_data", reader('remove_unused_nodechecks/input.json'))
def test_remove_unused_nodechecks(input_data):
    clear_db()
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    agent_addr_list = input_data["agent_addr_list"]
    node_checks_key = set(input_data["node_checks_key"])

    connection = db_obj.engine.connect()
    with connection.begin():
        db_obj.insert_and_update(
            connection,
            db_obj.NODECHECKS_TABLE_NAME,
            input_data["input"]
        )
    connection.close()

    data_fetch.remove_unused_nodechecks(agent_addr_list, node_checks_key)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.NODECHECKS_TABLE_NAME)
    connection.close()

    if data:
        assert list(data[0][:-3]) == input_data["output"]
    else:
        assert data == input_data["output"]
    clear_db()


def test_fetch_and_save_servicechecks():

    def dummy_get_service_checks(service_checks_dict, agent):
        service_checks_dict.update(reader('fetch_and_save_servicechecks/service_checks_dict.json'))

    get_service_checks = data_fetch.get_service_checks
    data_fetch.get_service_checks = dummy_get_service_checks

    services_dict = reader('fetch_and_save_servicechecks/services_dict.json')
    service_checks_dict = threading_util.ThreadSafeDict()
    service_checks_key = data_fetch.fetch_and_save_servicechecks(services_dict, service_checks_dict)

    expected = reader('fetch_and_save_servicechecks/output.json')
    assert set(map(tuple, expected)) == service_checks_key

    data_fetch.get_service_checks = get_service_checks


@pytest.mark.parametrize("input_data", reader('remove_unused_servicechecks/input.json'))
def test_remove_unused_servicechecks(input_data):
    clear_db()
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    agent_addr_list = input_data["agent_addr_list"]
    service_checks_key = set(input_data["service_checks_key"])

    connection = db_obj.engine.connect()
    with connection.begin():
        db_obj.insert_and_update(
            connection,
            db_obj.SERVICECHECKS_TABLE_NAME,
            input_data["input"]
        )
    connection.close()

    data_fetch.remove_unused_servicechecks(agent_addr_list, service_checks_key)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.SERVICECHECKS_TABLE_NAME)
    connection.close()

    if data:
        assert list(data[0][:-3]) == input_data["output"]
    else:
        assert data == input_data["output"]
    clear_db()


def test_fetch_and_save_eps():
    ep_data = reader('fetch_and_save_eps/ep_data.json')

    ep_key = data_fetch.fetch_and_save_eps(ep_data)

    expected = set(map(tuple, reader('fetch_and_save_eps/output.json')))

    assert expected == ep_key


@pytest.mark.parametrize("input_data", reader('remove_unused_eps/input.json'))
def test_remove_unused_eps(input_data):
    clear_db()
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    tenant = input_data["tenant"]
    ep_key = set(input_data["ep_key"])

    connection = db_obj.engine.connect()
    with connection.begin():
        db_obj.insert_and_update(
            connection,
            db_obj.EP_TABLE_NAME,
            input_data["input"]
        )
    connection.close()

    data_fetch.remove_unused_eps(tenant, ep_key)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.EP_TABLE_NAME)
    connection.close()

    if data:
        assert list(data[0][:-3]) == input_data["output"]
    else:
        assert data == input_data["output"]
    clear_db()


def test_fetch_and_save_epgs():
    epg_data = reader('fetch_and_save_epgs/epg_data.json')

    epg_key = data_fetch.fetch_and_save_epgs(epg_data)

    expected = set(reader('fetch_and_save_epgs/output.json'))

    assert expected == epg_key


@pytest.mark.parametrize("input_data", reader('remove_unused_epgs/input.json'))
def test_remove_unused_epgs(input_data):
    clear_db()
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    tenant = input_data["tenant"]
    epg_key = set(input_data["epg_key"])

    connection = db_obj.engine.connect()
    with connection.begin():
        db_obj.insert_and_update(
            connection,
            db_obj.EPG_TABLE_NAME,
            input_data["input"]
        )
    connection.close()

    data_fetch.remove_unused_epgs(tenant, epg_key)

    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(connection, db_obj.EPG_TABLE_NAME)
    connection.close()

    if data:
        assert list(data[0][:-3]) == input_data["output"]
    else:
        assert data == input_data["output"]
    clear_db()


@pytest.mark.parametrize("input_data", reader('get_polling_interval/input.json'))
def test_get_polling_interval(input_data):

    def dummy_select_from_table(self, connection, table_name, field_arg_dict={}, required_fields=[]):
        data = input_data["select"]
        if data is None:
            raise Exception('unit testing get_polling_interval')
        return data

    select_from_table = alchemy_core.Database.select_from_table
    alchemy_core.Database.select_from_table = dummy_select_from_table

    polling_interval = data_fetch.get_polling_interval()

    assert input_data["response"] == polling_interval

    alchemy_core.Database.select_from_table = select_from_table
    clear_db()

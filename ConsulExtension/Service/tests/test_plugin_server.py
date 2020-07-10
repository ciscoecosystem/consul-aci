import json
import os
import pytest
import sys
from mock import Mock

sys.modules['cobra'] = 'cobra'
sys.modules['cobra.model'] = 'cobra.model'
sys.modules['cobra.model.pol'] = Mock(name='Uni')
sys.modules['cobra.model.aaa'] = Mock(name='UserEp')

from Service import plugin_server
from Service import alchemy_core
from Service import consul_utils


def get_data(file_name):
    with open('./tests/plugin_server/{}'.format(file_name), 'r') as fp:
        data = json.load(fp)
        return data


def mapping_key_maker(data, obj_type, datacenter):
    dc = dict()
    if obj_type == 'dc':
        for each in data:
            st = ""
            st += each.get("ip")
            st += each.get("dn")
            st += datacenter
            st += "1" if each.get("enabled") else "0"
            st += each.get("ap")
            st += each.get("bd")
            st += each.get("vrf")
            st += each.get("tenant")
            dc[st] = True
    else:
        for each in data:
            st = ""
            st += each[0]
            st += each[1]
            st += each[2]
            st += "1" if each[3] else "0"
            st += each[4]
            st += each[5]
            st += each[6]
            st += each[7]
            dc[st] = True
    return dc


def check_saved_mapping(db_saved_data, data, datacenter):
    data = mapping_key_maker(data, 'dc', datacenter)
    db_saved_data = mapping_key_maker(db_saved_data, 'db', datacenter)
    for each in db_saved_data:
        if each not in data:
            return False
    return True


def read_creds_checker(response, db_data):
    response = response.get("payload")[0]
    db_data = db_data[0]
    if response.get("ip") != db_data[0]:
        return False
    if response.get("port") != db_data[1]:
        return False
    if response.get("protocol") != db_data[2]:
        return False
    if response.get("token") != db_data[3]:
        return False
    if response.get("status") != bool(db_data[4]):
        return False
    if response.get("datacenter") != db_data[5]:
        return False
    return True


def check_connection(self):
    return True, "message"


def datacenter(self):
    return "-"


consul_utils.Consul.check_connection = check_connection
consul_utils.Consul.datacenter = datacenter
'''
Case 1: Dangeling node
Case 2: Node to EP mapping
Case 3: Service and Node has same ip but not mapped with any EP
Case 4: Service and Node has same ip and mapped with any EP
Case 5: Service and Node has different ip but Service mapped with any EP
Case 6: Service and Node has different ip and Service, Node not mapped with any EP
Case 7: Service and Node has different ip and Service and Node mapped with different EPs
Case 8: Service and Node has different ip and Node mapped with any EP
Case 9: Service without any ip address
'''
get_new_mapping_cases = [1, 2, 3, 4, 5, 6, 7, 8, 9]
mapping_data = get_data('saved_mapping.json')
read_creds_cases = get_data('read_creds.json')
epg_alias_data = get_data('get_epg_alias.json')


@pytest.mark.parametrize("case", get_new_mapping_cases)
def test_get_new_mapping(case):
    tenant = 'tn0'
    datacenter = 'dc1'

    try:
        os.system(
            'cp ./tests/plugin_server/{}.db ./ConsulDatabase.db'.format(case)
        )
    except Exception:
        assert False

    new_mapping = plugin_server.get_new_mapping(tenant, datacenter)
    original_mapping = get_data('{}.json'.format(case))
    os.remove('./ConsulDatabase.db')
    assert new_mapping == original_mapping


@pytest.mark.parametrize("mapped_data", mapping_data)
def test_save_mapping(mapped_data):
    db_obj = alchemy_core.Database()
    db_obj.create_tables()
    tenant = 'tn0'
    datacenter = 'dc1'
    passed_response = {
        "payload": "Saved Mappings",
        "status_code": "200",
        "message": "OK"
    }
    failed_response = {
        "payload": {},
        "status_code": "300",
        "message": "Could not save mappings to the database."
    }
    if mapped_data != "fail":
        mapped_data = [mapped_data]
        response = json.loads(plugin_server.save_mapping(
            tenant,
            datacenter,
            json.dumps(mapped_data)
        ))
        assert response == passed_response
        connection = db_obj.engine.connect()
        db_saved_data = db_obj.select_from_table(
            connection,
            db_obj.MAPPING_TABLE_NAME
        )
        connection.close()
        assert check_saved_mapping(db_saved_data, mapped_data, datacenter)
    else:
        response = json.loads(plugin_server.save_mapping(
            tenant,
            datacenter,
            {}
        ))
        assert response == failed_response

    os.remove('./ConsulDatabase.db')


@pytest.mark.parametrize("case", read_creds_cases)
def test_read_creds(case):
    db_obj = alchemy_core.Database()
    db_obj.create_tables()
    empty_agent_response = {
        'payload': [],
        'status_code': '301',
        'message': 'Agents not found'
    }
    if case == "empty_agents":
        response = json.loads(plugin_server.read_creds())
        assert response == empty_agent_response
    else:
        data = case
        connection = db_obj.engine.connect()
        db_obj.insert_and_update(
            connection,
            db_obj.LOGIN_TABLE_NAME,
            data,
            {
                'agent_ip': data[0],
                'port': data[1]
            }
        )
        connection.close()
        response = json.loads(plugin_server.read_creds())
        connection = db_obj.engine.connect()
        db_data = db_obj.select_from_table(connection, db_obj.LOGIN_TABLE_NAME)
        connection.close()
        assert read_creds_checker(response, db_data)
    os.remove('./ConsulDatabase.db')


@pytest.mark.parametrize("case", epg_alias_data)
def test_get_epg_alias(case):
    arg = case.get("dn")
    expected = case.get("expected")
    db_obj = alchemy_core.Database()
    db_obj.create_tables()
    connection = db_obj.engine.connect()
    db_obj.insert_and_update(
        connection,
        db_obj.EPG_TABLE_NAME,
        [
            "dn",
            "tenant",
            "EPG",
            "BD",
            "contracts",
            "vrf",
            "epg_health",
            "app_profile",
            expected
        ],
        {
            "dn": arg
        }
    )
    connection.close()
    response = plugin_server.get_epg_alias(arg)
    assert response == expected
    os.remove('./ConsulDatabase.db')

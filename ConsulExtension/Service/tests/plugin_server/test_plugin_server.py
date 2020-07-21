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
from Service.apic_utils import AciUtils
from Service.tests.plugin_server.utils import (
    generate_dummy_new_mapping_data,
    verify_mapping,
    generate_dummy_exception_new_mapping_data,
    generate_dummy_db_output,
    verify_change_key,
    get_absolue_path,
    parse_json_file,
    verify_agent_status,
    dummy_db_select_exception,
    get_data_json,
    get_data_str
)


def get_data(file_name):
    with open('./tests/plugin_server/data/{}'.format(file_name), 'r') as fp:
        data = json.load(fp)
        return data


def clear_db():
    os.remove("./ConsulDatabase.db")


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
            st += each.get("epg")
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
            st += each[8]
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
    try:
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
    except Exception:
        return [] == db_data
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
get_new_mapping_cases = [
    "dangling",
    "node_to_ep",
    "service_node_with_same_ip_to_none",
    "service_node_with_same_ip_to_ep",
    "service_node_with_diff_ip_service_to_ep",
    "service_node_with_diff_ip_both_to_none",
    "service_node_with_diff_ip_both_to_diff_ep",
    "service_node_with_diff_ip_node_to_ep",
    "service_without_ip"
]

mapping_data = get_data('saved_mapping.json')
read_creds_cases = get_data('read_creds.json')
epg_alias_data = get_data('get_epg_alias.json')


@pytest.mark.parametrize("case", get_new_mapping_cases)
def test_get_new_mapping(case):
    tenant = 'tn0'
    datacenter = 'dc1'

    try:
        os.system(
            'cp ./tests/plugin_server/data/{}.db ./ConsulDatabase.db'.format(case)
        )
    except Exception:
        assert False

    new_mapping = plugin_server.get_new_mapping(tenant, datacenter)
    original_mapping = get_data('{}.json'.format(case))
    assert new_mapping == original_mapping
    clear_db()


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

    clear_db()


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
        response = json.loads(plugin_server.read_creds("tn0"))
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
        response = json.loads(plugin_server.read_creds("tn0"))
        connection = db_obj.engine.connect()
        db_data = db_obj.select_from_table(connection, db_obj.LOGIN_TABLE_NAME)
        connection.close()
        assert read_creds_checker(response, db_data)
    clear_db()


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
            "epg_alias"
        ],
        {
            "dn": arg
        }
    )
    connection.close()
    response = plugin_server.get_epg_alias(arg)
    assert response == expected
    clear_db()


@pytest.mark.parametrize("data, expected", [
    ("/plugin_server/data/get_faults/get_faults_input.json",
     "/plugin_server/data/get_faults/get_faults_output.json"),
    ("/plugin_server/data/get_faults/empty_input.json",
     "/plugin_server/data/get_faults/empty_output.json")
])
def test_get_faults(data, expected):

    # Mock apic_util login

    def dummy_login(self):
        return "dummy-token"

    def dummy_get_ap_epg_faults(self, dn):
        return get_data_json(data)

    AciUtils.login = dummy_login
    AciUtils.get_ap_epg_faults = dummy_get_ap_epg_faults

    response = plugin_server.get_faults("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg")

    assert response == get_data_str(expected)


@pytest.mark.parametrize("data, expected", [
    ("/plugin_server/data/get_events/get_events_input.json",
     "/plugin_server/data/get_events/get_events_output.json"),
    ("/plugin_server/data/get_events/empty_input.json",
     "/plugin_server/data/get_events/empty_output.json")
])
def test_get_events(data, expected):

    def dummy_get_ap_epg_events(self, dn):
        return get_data_json(data)

    AciUtils.get_ap_epg_events = dummy_get_ap_epg_events

    response = plugin_server.get_events("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg")

    assert response == get_data_str(expected)


@pytest.mark.parametrize("data, expected", [
    ("/plugin_server/data/get_audit_logs/get_audit_logs_input.json",
     "/plugin_server/data/get_audit_logs/get_audit_logs_output.json"),
    ("/plugin_server/data/get_audit_logs/empty_input.json",
     "/plugin_server/data/get_audit_logs/empty_output.json")
])
def test_get_audit_logs(data, expected):

    def dummy_get_ap_epg_audit_logs(self, dn):
        return get_data_json(data)

    AciUtils.get_ap_epg_audit_logs = dummy_get_ap_epg_audit_logs

    response = plugin_server.get_audit_logs("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg")

    assert response == get_data_str(expected)


@pytest.mark.parametrize("data, expected", [
    ("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", "DummyTn/DummyAp/DummyEpg"),
    ("uni//ap-DummyAp/epg-DummyEpg", "/DummyAp/DummyEpg"),
    ("uni/tn-DummyTn//epg-DummyEpg", "DummyTn//DummyEpg"),
    ("uni/a-a/a-a/a-a", "/a/a"),
    ("dummy-string", "//"),
])
def test_get_to_epg(data, expected):

    response = plugin_server.get_to_epg(data)

    assert response == expected


@pytest.mark.parametrize("data, expected", [
    ("/plugin_server/data/get_ingress_egress/ingress_egress_input.json",
     ("11", "22")),
    ("/plugin_server/data/get_ingress_egress/empty_input.json",
     ("0", "0"))
])
def test_get_ingress_egress(data, expected):

    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return get_data_json(data)

    def dummy_login(self):
        return "dummy-token"

    AciUtils.login = dummy_login
    AciUtils.get_mo_related_item = dummy_get_mo_related_item

    obj = AciUtils()
    response = plugin_server.get_ingress_egress(
        "uni/tn-DummyTn/ap-DummyAp/epg-DummyToEpg",
        "uni/tn-DummyTn/ap-DummyAp/epg-DummyFromEpg",
        "subj",
        "flt",
        obj
    )

    assert response == expected


@pytest.mark.parametrize("data, expected", [
    ("/plugin_server/data/get_filter_list/1_input.json",
     "/plugin_server/data/get_filter_list/1_output.json"),
    ("/plugin_server/data/get_filter_list/2_input.json",
     "/plugin_server/data/get_filter_list/2_output.json"),
    ("/plugin_server/data/get_filter_list/3_input.json",
     "/plugin_server/data/get_filter_list/3_output.json"),
    ("/plugin_server/data/get_filter_list/4_input.json",
     "/plugin_server/data/get_filter_list/4_output.json"),
    ("/plugin_server/data/get_filter_list/5_input.json",
     "/plugin_server/data/get_filter_list/5_output.json"),
    ("/plugin_server/data/get_filter_list/6_input.json",
     "/plugin_server/data/get_filter_list/6_output.json"),
    ("/plugin_server/data/get_filter_list/7_input.json",
     "/plugin_server/data/get_filter_list/7_output.json"),
])
def test_get_filter_list(data, expected):

    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return get_data_json(data)

    def dummy_login(self):
        return "dummy-token"

    AciUtils.login = dummy_login
    AciUtils.get_mo_related_item = dummy_get_mo_related_item

    obj = AciUtils()
    response = plugin_server.get_filter_list("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", obj)

    assert response == get_data_json(expected)


@pytest.mark.parametrize("data, dn, mo_type, mac_list,ip_list, ip, expected", [
    ("/plugin_server/data/get_children_ep_info/fvcep_input.json",
     "", "ep", "00:00:00:00:00:AA", "",
     "/plugin_server/data/get_children_ep_info/fvcep_ip.json",
     "/plugin_server/data/get_children_ep_info/fvcep_output.json"),
    ("/plugin_server/data/get_children_ep_info/fvip_input.json",
     "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", "epg", "", "",
     "/plugin_server/data/get_children_ep_info/fvip_ip.json",
     "/plugin_server/data/get_children_ep_info/fvip_output.json")
])
def test_get_children_ep_info(data, dn, mo_type, mac_list, ip_list, ip, expected):

    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return get_data_json(data)

    def dummy_login(self):
        return "dummy-token"

    def dummy_get_ep_info(self, ep_attr):
        return get_data_json("/plugin_server/data/get_children_ep_info/get_ep_info.json")

    AciUtils.login = dummy_login
    AciUtils.get_ep_info = dummy_get_ep_info
    AciUtils.get_mo_related_item = dummy_get_mo_related_item

    response = plugin_server.get_children_ep_info(dn, mo_type, mac_list, ip_list, get_data_json(ip))

    assert json.loads(response) == get_data_json(expected)


@pytest.mark.parametrize("data, expected", [
    ("/plugin_server/data/get_configured_access_policies/get_configured_access_policies_input.json",
     "/plugin_server/data/get_configured_access_policies/get_configured_access_policies_output.json")
])
def test_get_configured_access_policies(data, expected):

    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return get_data_json(data)

    def dummy_login(self):
        return "dummy-token"

    AciUtils.login = dummy_login
    AciUtils.get_mo_related_item = dummy_get_mo_related_item

    response = plugin_server.get_configured_access_policies("DummyTn", "DummyAp", "DummyEpg")

    assert json.loads(response) == get_data_json(expected)


@pytest.mark.parametrize("data, expected", [
    ("/plugin_server/data/get_to_epg_traffic/get_to_epg_traffic_input.json",
     "/plugin_server/data/get_to_epg_traffic/get_to_epg_traffic_output.json")
])
def test_get_to_epg_traffic(data, expected):

    def dummy_get_all_mo_instances(self, mo_dn, item_query_string):
        return get_data_json(data)

    def dummy_login(self):
        return "dummy-token"

    def dummy_get_filter_list(flt_attr_tdn, aci_util_obj):
        return ["flt1", "flt1"]

    def dummy_get_ingress_egress(from_epg_dn, to_epg_dn, subj_dn, flt_name, aci_util_obj):
        return ("1", "1")

    def dummy_get_epg_alias(dn):
        return "DummyAlias"

    def dummy_get_to_epg(dn):
        return "DummyTn/DummyAp/DummyEpg"

    AciUtils.login = dummy_login
    AciUtils.get_to_epg = dummy_get_to_epg
    AciUtils.get_all_mo_instances = dummy_get_all_mo_instances
    plugin_server.get_filter_list = dummy_get_filter_list
    plugin_server.get_ingress_egress = dummy_get_ingress_egress
    plugin_server.get_epg_alias = dummy_get_epg_alias

    response = plugin_server.get_to_epg_traffic("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg")

    assert json.loads(response) == get_data_json(expected)


@pytest.mark.parametrize("test_input, expected",
                         [('/plugin_server/data/mapping/1_mapping_initial_input.json',
                          {'output': '/plugin_server/data/mapping/1_mapping_initial_output.json',
                           'method': verify_mapping}), ('/plugin_server/data/mapping/3_mapping_empty_input.json',
                          {'output': '/plugin_server/data/mapping/3_mapping_empty_output.json',
                           'method': verify_mapping})])
def test_mapping(test_input, expected):
    plugin_server.get_new_mapping = generate_dummy_new_mapping_data(test_input)
    actual_output = plugin_server.mapping('', '')
    verifier = expected['method']
    assert verifier(actual_output, expected['output'])


@pytest.mark.parametrize("test_input, expected",
                         [('/plugin_server/data/mapping/3_mapping_empty_input.json',
                          {'output': '/plugin_server/data/mapping/2_mapping_exception_output.json',
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


@pytest.mark.parametrize(
    'input, expected',
    [
        ('/plugin_server/data/change_key/1_initial_input.json', '/plugin_server/data/change_key/1_initial_output.json'),
        ('/plugin_server/data/change_key/1_empty_input.json', '/plugin_server/data/change_key/1_empty_output.json'),
        (None, [])
    ]
)
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


@pytest.mark.parametrize(
    'input, expected',
    [
        (
            '/plugin_server/data/agent_status/1_initial_input.json',
            '/plugin_server/data/agent_status/1_initial_output.json'
        ),
        (
            '/plugin_server/data/agent_status/2_different_dc_input.json',
            '/plugin_server/data/agent_status/2_different_dc_output.json'
        ),
        (None, [])
    ]
)
def test_get_agent_status(input, expected):
    if input:
        original_select = alchemy_core.Database.select_from_table
        alchemy_core.Database.select_from_table = generate_dummy_db_output(None, input)
        actual_output = plugin_server.get_agent_status('tn0', 'dc1')
        alchemy_core.Database.select_from_table  = original_select
        assert verify_agent_status(actual_output, expected)
    else:
        original_select = alchemy_core.Database.select_from_table
        alchemy_core.Database.select_from_table = dummy_db_select_exception()
        with pytest.raises(Exception):
            assert plugin_server.get_agent_status('tn0', 'dc1')
        alchemy_core.Database.select_from_table  = original_select


@pytest.mark.parametrize("interval", [2, 2.2, "fail"])
def test_set_polling_interval(interval):
    try:
        clear_db()
    except Exception:
        pass
    passed_response = {
        "status_code": "200",
        "message": "Polling Interval Set!"
    }
    failed_response = {
        'status_code': '300',
        'message': 'Some error occurred, could not set polling interval'
    }
    dummy_db = alchemy_core.Database()
    dummy_db.create_tables()
    connection = dummy_db.engine.connect()
    ls = dummy_db.select_from_table(
        connection,
        dummy_db.POLLING_TABLE_NAME
    )
    connection.close()

    assert len(ls) == 0

    if interval != "fail":
        response = plugin_server.set_polling_interval(interval)
        assert json.loads(response) == passed_response

        connection = dummy_db.engine.connect()
        db_interval = dummy_db.select_from_table(
            connection,
            dummy_db.POLLING_TABLE_NAME,
            {'pkey': 'interval'},
            ['interval']
        )[0][0]
        connection.close()
        assert interval == db_interval
        clear_db()
    else:
        clear_db()
        response = plugin_server.set_polling_interval(interval)
        assert json.loads(response) == failed_response
        clear_db()


@pytest.mark.parametrize("interval", [2, 2.2, "fail"])
def test_get_polling_interval(interval):
    try:
        clear_db()
    except Exception:
        pass
    dummy_db = alchemy_core.Database()
    dummy_db.create_tables()
    passed_response = json.dumps({
        "status_code": "200",
        "message": "Ok",
        "payload": {
            "interval": interval
        }
    })
    failed_response = json.dumps({
        "status_code": "300",
        "message": "Could not get polling interval",
        "payload": []
    })
    plugin_server.set_polling_interval(interval)
    if interval != "fail":
        response = plugin_server.get_polling_interval()
        assert response == passed_response
        clear_db()
    else:
        plugin_server_db_obj = plugin_server.db_obj
        plugin_server.db_obj = None
        response = plugin_server.get_polling_interval()
        plugin_server.db_obj = plugin_server_db_obj
        assert response == failed_response
        clear_db()

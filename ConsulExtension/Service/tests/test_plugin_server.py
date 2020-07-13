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
            "epg_alias"
        ],
        {
            "dn": arg
        }
    )
    connection.close()
    response = plugin_server.get_epg_alias(arg)
    assert response == expected
    os.remove('./ConsulDatabase.db')


@pytest.mark.parametrize("data, expected", [
    ({
        "faultRecords": [{
            "faultRecord": {
                "attributes": {
                    "code": "F000",
                    "affected": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA/ip-[1.1.1.1]",
                    "descr": "For Tenant DummyTn, application EPG DummyEpg, ACI has detected some fault. Context: 0000.",
                    "cause": "dummy-error",
                    "severity": "cleared",
                    "created": "1970-1-1T00:00:00.000-01:00",
                }
            }
        }]
    }, json.dumps({
        "status_code": "200",
        "message": "OK",
        "payload": [{
            "code": "F000",
            "affected": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA/ip-[1.1.1.1]",
            "descr": "For Tenant DummyTn, application EPG DummyEpg, ACI has detected some fault. Context: 0000.",
            "cause": "dummy-error",
            "severity": "cleared",
            "created": "1970-1-1T00:00:00.000-01:00",
        }]
    })),
    ([], json.dumps({
        "status_code": "300",
        "message": "Error while fetching Fault details.",
        "payload": []}))
])
def test_get_faults(data, expected):

    # Mock apic_util login

    def dummy_login(self):
        return "dummy-token"

    def dummy_get_ap_epg_faults(self, dn):
        return data

    AciUtils.login = dummy_login
    AciUtils.get_ap_epg_faults = dummy_get_ap_epg_faults

    response = plugin_server.get_faults("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg")

    assert response == expected


@pytest.mark.parametrize("data, expected", [
    ({
        "eventRecords": [{
            "eventRecord": {
                "attributes": {
                    "code": "F000",
                    "affected": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA/ip-[1.1.1.1]",
                    "descr": "For Tenant DummyTn, application EPG DummyEpg, ACI has detected some fault. Context: 0000.",
                    "cause": "dummy-error",
                    "severity": "cleared",
                    "created": "1970-1-1T00:00:00.000-01:00",
                }
            }
        }]
    }, json.dumps({
        "status_code": "200",
        "message": "OK",
        "payload": [{
            "code": "F000",
            "affected": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA/ip-[1.1.1.1]",
            "descr": "For Tenant DummyTn, application EPG DummyEpg, ACI has detected some fault. Context: 0000.",
            "cause": "dummy-error",
            "severity": "cleared",
            "created": "1970-1-1T00:00:00.000-01:00",
        }]
    })),
    ([], json.dumps({
        "status_code": "300",
        "message": "Error while fetching Event details.",
        "payload": []}))
])
def test_get_events(data, expected):

    def dummy_get_ap_epg_events(self, dn):
        return data

    AciUtils.get_ap_epg_events = dummy_get_ap_epg_events

    response = plugin_server.get_events("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg")

    assert response == expected


@pytest.mark.parametrize("data, expected", [
    ({
        "auditLogRecords": [{
            "aaaModLR": {
                "attributes": {
                    "affected": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA/ip-[1.1.1.1]",
                    "descr": "For Tenant DummyTn, application EPG DummyEpg, ACI has detected some fault. Context: 0000.",
                    "created": "1970-1-1T00:00:00.000-01:00",
                    "id": "ID000",
                    "ind": "dummy-action",
                    "user": "dummy-user",
                }
            }
        }]
    }, json.dumps({
        "status_code": "200",
        "message": "OK",
        "payload": [{
            "affected": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA/ip-[1.1.1.1]",
            "descr": "For Tenant DummyTn, application EPG DummyEpg, ACI has detected some fault. Context: 0000.",
            "created": "1970-1-1T00:00:00.000-01:00",
            "id": "ID000",
            "action": "dummy-action",
            "user": "dummy-user",
        }]
    })),
    ([], json.dumps({
        "status_code": "300",
        "message": "Error while fetching Audit log details.",
        "payload": []}))
])
def test_get_audit_logs(data, expected):

    def dummy_get_ap_epg_audit_logs(self, dn):
        return data

    AciUtils.get_ap_epg_audit_logs = dummy_get_ap_epg_audit_logs

    response = plugin_server.get_audit_logs("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg")

    assert response == expected


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
    ([{
        "actrlRuleHitAg15min": {
            "attributes": {
                "ingrPktsCum": "11",
                "egrPktsCum": "22",
            }
        }
    }], ("11", "22")),
    ([], ("0", "0"))
])
def test_get_ingress_egress(data, expected):

    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return data

    def dummy_login(self):
        return "dummy-token"

    AciUtils.login = dummy_login
    AciUtils.get_mo_related_item = dummy_get_mo_related_item

    obj = AciUtils()
    response = plugin_server.get_ingress_egress("uni/tn-DummyTn/ap-DummyAp/epg-DummyToEpg", "uni/tn-DummyTn/ap-DummyAp/epg-DummyFromEpg", "subj", "flt", obj)

    assert response == expected


@pytest.mark.parametrize("data, expected", [
    ([{"vzRFltE": {"attributes": {"etherT": "unspecified"}}}], ["*"]),
    ([{
        "vzRFltE": {
            "attributes": {
                "etherT": "dummy",
                "prot": "unspecified",
                "sFromPort": "unspecified",
                "sToPort": "unspecified",
                "dFromPort": "unspecified",
                "dToPort": "unspecified"
            }
        }
    }], ["dummy:*:* to *"]),
    ([{
        "vzRFltE": {
            "attributes": {
                "etherT": "dummy",
                "prot": "dummy",
                "sFromPort": "unspecified",
                "sToPort": "unspecified",
                "dFromPort": "unspecified",
                "dToPort": "unspecified"
            }
        }
    }], ["dummy:dummy:* to *"]),
    ([{
        "vzRFltE": {
            "attributes": {
                "etherT": "dummy",
                "prot": "dummy",
                "sFromPort": "dummy",
                "sToPort": "unspecified",
                "dFromPort": "unspecified",
                "dToPort": "unspecified"
            }
        }
    }], ["dummy:dummy:* to *"]),
    ([{
        "vzRFltE": {
            "attributes": {
                "etherT": "dummy",
                "prot": "dummy",
                "sFromPort": "dummy",
                "sToPort": "dummy",
                "dFromPort": "unspecified",
                "dToPort": "unspecified"
            }
        }
    }], ["dummy:dummy:dummy-dummy to *"]),
    ([{
        "vzRFltE": {
            "attributes": {
                "etherT": "dummy",
                "prot": "dummy",
                "sFromPort": "unspecified",
                "sToPort": "unspecified",
                "dFromPort": "dummy",
                "dToPort": "unspecified"
            }
        }
    }], ["dummy:dummy:* to *"]),
    ([{
        "vzRFltE": {
            "attributes": {
                "etherT": "dummy",
                "prot": "dummy",
                "sFromPort": "unspecified",
                "sToPort": "unspecified",
                "dFromPort": "dummy",
                "dToPort": "dummy"
            }
        }
    }], ["dummy:dummy:* to dummy-dummy"]),
])
def test_get_filter_list(data, expected):

    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return data

    def dummy_login(self):
        return "dummy-token"

    AciUtils.login = dummy_login
    AciUtils.get_mo_related_item = dummy_get_mo_related_item

    obj = AciUtils()
    response = plugin_server.get_filter_list("uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", obj)

    assert response == expected


@pytest.mark.parametrize("data, dn, mo_type, mac_list, ip, expected", [
    ([{
        "fvCEp": {
            "attributes": {
                "encap": "dummy-encap",
                "mac": "00:00:00:00:00:AA",
                "mcastAddr": "not-applicable",
                "lcC": "dummy-lcc",
            },
            "children": []
        }
    }], "", "ep", "00:00:00:00:00:AA", "1.1.1.1", json.dumps({
        "status_code": "200",
        "message": "OK",
        "payload": [{
            "ip": "1.1.1.1",
            "mac": "00:00:00:00:00:AA",
            "mcast_addr": "---",
            "learning_source": "dummy-lcc",
            "encap": "dummy-encap",
            "ep_name": "dummy-vm-name",
            "hosting_server_name": "1.1.1.1",
            "iface_name": ["Pod-0/Node-111/eth0/0"],
            "ctrlr_name": "hyper000"
        }]
    })),
    ([{
        "fvCEp": {
            "attributes": {
                "encap": "dummy-encap",
                "mac": "00:00:00:00:00:AA",
                "mcastAddr": "not-applicable",
                "lcC": "dummy-lcc",
                "ip": "2.2.2.2"
            },
            "children": [{
                "fvIp": {
                    "attributes": {
                        "addr": "2.2.2.2",
                    }
                }
            }]
        }
    }], "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", "epg", "", "", json.dumps({
        "status_code": "200",
        "message": "OK",
        "payload": [{
            "ip": "2.2.2.2",
            "mac": "00:00:00:00:00:AA",
            "mcast_addr": "---",
            "learning_source": "dummy-lcc",
            "encap": "dummy-encap",
            "ep_name": "dummy-vm-name",
            "hosting_server_name": "1.1.1.1",
            "iface_name": ["Pod-0/Node-111/eth0/0"],
            "ctrlr_name": "hyper000"
        }]
    }))
])
def test_get_children_ep_info(data, dn, mo_type, mac_list, ip, expected):

    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return data

    def dummy_login(self):
        return "dummy-token"

    def dummy_get_ep_info(self, ep_attr):
        return {
            "controller": "hyper000",
            "hosting_servername": "1.1.1.1",
            "interfaces": ["Pod-0/Node-111/eth0/0"],
            "vm_name": "dummy-vm-name",
            "vmm_domain": "DUMMY0-leaf000"
        }

    AciUtils.login = dummy_login
    AciUtils.get_ep_info = dummy_get_ep_info
    AciUtils.get_mo_related_item = dummy_get_mo_related_item

    response = plugin_server.get_children_ep_info(dn, mo_type, mac_list, ip)

    assert response == expected


def test_get_configured_access_policies():

    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return [{
            "syntheticAccessPolicyInfo": {
                "attributes": {
                    "domain": "uni/vmmp-DummyHost/dom-DummyDom",
                    "accBndlGrp": "uni/dummy/dummy/accportgrp-Dummy-Group",
                    "vLanPool": "uni/dummy/dummy/from-[dummy-lan1]-to-[dummy-lan2]",
                    "accPortP": "uni/dummy/accportprof-Dummy-Profile",
                    "attEntityP": "uni/dummy/attentp-Dummy-AttEntryP",
                    "nodeP": "uni/dummy/nprof-Dummy-Switch",
                    "pathEp": "topology/pod-1/paths-111/pathep-[dummy-path]",
                }
            }
        }]

    def dummy_login(self):
        return "dummy-token"

    AciUtils.login = dummy_login
    AciUtils.get_mo_related_item = dummy_get_mo_related_item

    response = plugin_server.get_configured_access_policies("DummyTn", "DummyAp", "DummyEpg")

    assert response == json.dumps({
        "status_code": "200",
        "message": "Ok",
        "payload": [{
            "domain": "DummyHost/DummyDom",
            "switch_prof": "Dummy-Switch",
            "aep": "Dummy-AttEntryP",
            "iface_prof": "Dummy-Profile",
            "pc_vpc": "Dummy-Group",
            "node": "111",
            "path_ep": "dummy-path",
            "vlan_pool": "[dummy-lan1]-to-[dummy-lan2]"
        }]
    })


def test_get_to_epg_traffic():

    def dummy_get_all_mo_instances(self, mo_dn, item_query_string):
        return [{
            "vzFromEPg": {
                "children": [{
                    "vzToEPg": {
                        "attributes": {
                            "epgDefDn": "uni/tn-DummyTn/brc-DummyBrc/dummy/cons-dummy",
                            "epgDn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg"
                        },
                        "children": [{
                            "vzRsRFltAtt": {
                                "attributes": {
                                    "tDn": "uni/tn-common/fp-default",
                                },
                                "children": [{
                                    "vzCreatedBy": {
                                        "attributes": {
                                            "ownerDn": "uni/tn-DummyTn/brc-DummyBrc/subj-DummySubj/rssubjFiltAtt-DummyFilt"
                                        }
                                    }
                                }]
                            }
                        }]
                    }
                }]
            }
        }]

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

    assert response == json.dumps({
        "status_code": "200",
        "message": "",
        "payload": [{
            "to_epg": "DummyTn/DummyAp/DummyEpg",
            "contract_subj": "DummyTn/DummyBrc/DummySubj",
            "filter_list": ["flt1", "flt1"],
            "ingr_pkts": "1",
            "egr_pkts": "1",
            "alias": "DummyAlias",
            "contract_type": "",
            "type": "Consumer"
        }]
    })

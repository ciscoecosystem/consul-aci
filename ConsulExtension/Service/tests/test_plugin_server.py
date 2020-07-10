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
from Service import apic_utils
from Service.apic_utils import AciUtils


def get_data(file_name):
    with open('./tests/plugin_server/{}'.format(file_name), 'r') as fp:
        data = json.load(fp)
        return data


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
cases = [1, 2, 3, 4, 5, 6, 7, 8, 9]


@pytest.mark.parametrize("case", cases)
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

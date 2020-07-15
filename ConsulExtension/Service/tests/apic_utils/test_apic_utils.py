import pytest
from requests import Session
from Service import apic_utils
from Service.apic_utils import AciUtils
from Service.tests.utils import DummyClass
from Service.tests.apic_utils.utils import get_data


aci_get_cases = [(200, {'dummy_key': 'dummy_val'}), (400, None)]


@pytest.mark.parametrize("status,expected", aci_get_cases)
def test_aci_get(status, expected):
    """Test aci get function"""

    # Mock session's get
    def json():
        return {'dummy_key': 'dummy_val'}

    def dummy_get(self, url, cookies, timeout, verify):
        obj = DummyClass()
        obj.status_code = status
        if status == 200:
            obj.json = json
        return obj

    Session.get = dummy_get

    # Mock apic_util login
    def dummy_login(self):
        return "dummy-token"

    AciUtils.login = dummy_login

    # Test the function
    obj = AciUtils()
    response = obj.aci_get("http://dummy.apic.url")

    assert response == expected


@pytest.mark.parametrize("aci_get_data, data", [
    ("data/get_vm_domain_and_name_cases/domain_and_name_get_data.json",
     "data/get_vm_domain_and_name_cases/domain_and_name_input.json")
])
def test_get_vm_domain_and_name(aci_get_data, data):
    """Test the VM Domain and Name"""

    def dummy_aci_get(self, url):
        return get_data(aci_get_data)

    AciUtils.aci_get = dummy_aci_get

    # Test the function
    obj = AciUtils()
    response = obj.get_vm_domain_and_name(get_data(data))

    assert response == ('DUMMY0-leaf000', 'dummy-vm-name')


@pytest.mark.parametrize("interface, expected", [
    ("topology/pod-1/pathdummy-xxx", ""),
    ("topology/pod-1/pathgrp-[1.1.1.1]", "[1.1.1.1]"),
    ("topology/pod-0/paths-111/pathep-[eth0/0]", "111"),
    ("topology/pod-0/protpaths-111-222/pathep-[FI-A-PG]", "-111-222"),
    (["topology/pod-0/protpaths-111-222/pathep-[FI-A-PG]",
      "topology/pod-0/paths-111/pathep-[eth0/0]"], "-111-222, 111"),
])
def test_get_node_from_interface(interface, expected):

    # Test the function
    response = AciUtils.get_node_from_interface(interface)

    assert response == expected


@pytest.mark.parametrize("data, node, expected", [
    ("data/get_interface_cases/paths_input.json",
     "data/get_interface_cases/paths_node.json",
     "data/get_interface_cases/paths_output.json"
     ),
    ("data/get_interface_cases/protpaths_input.json",
     "data/get_interface_cases/protpaths_node.json",
     "data/get_interface_cases/protpaths_output.json"
     ),
    ("data/get_interface_cases/pathgrp_input.json",
     "data/get_interface_cases/pathgrp_node.json",
     "data/get_interface_cases/pathgrp_output.json"
     )
])
def test_get_interface(data, node, expected):

    # Mock apic_util get_node_from_interface
    def dummy_get_node_from_interface(self, interface):
        return get_data(node)

    AciUtils.get_node_from_interface = dummy_get_node_from_interface

    # Test the function
    obj = AciUtils()
    response = obj.get_interface(get_data(data))

    assert response == get_data(expected)


@pytest.mark.parametrize("data,mo_instance_data,expected", [
    ("data/get_controller_and_hosting_server/with_ip_host_input.json",
     "data/get_controller_and_hosting_server/with_ip_host_mo_instance.json",
     ('hyper000', '1.1.1.1')),
    ("data/get_controller_and_hosting_server/with_host_input.json",
     "data/get_controller_and_hosting_server/with_host_mo_instance.json",
     ('hyper000', '')),
    ("data/get_controller_and_hosting_server/without_ip_host_input.json",
     "data/get_controller_and_hosting_server/without_ip_host_mo_instance.json",
     ('', ''))
])
def test_get_controller_and_hosting_server(data, mo_instance_data, expected):

    def dummy_get_all_mo_instances(self, mo_class, query_string=""):
        return get_data(mo_instance_data)

    AciUtils.get_all_mo_instances = dummy_get_all_mo_instances

    # Test the function
    obj = AciUtils()
    response = obj.get_controller_and_hosting_server(get_data(data))

    assert response == expected


@pytest.mark.parametrize("data, expected", [
    ("data/get_all_mo_instances_cases/get_instance_input.json",
     "data/get_all_mo_instances_cases/get_instance_output.json")
])
def test_get_all_mo_instances(data, expected):

    def dummy_aci_get(self, url):
        return get_data(data)

    AciUtils.aci_get = dummy_aci_get

    # Test the function
    obj = AciUtils()
    response = obj.get_all_mo_instances("dummy-class", "dummy-query")

    assert response == get_data(expected)


def test_get_dict_records():

    response = AciUtils.get_dict_records([1, 2, 3], 'key')

    assert response == {'key': [1, 2, 3]}


@pytest.mark.parametrize('data,expected', [
    ("data/get_ip_mac_list_cases/cep_input.json",
     "data/get_ip_mac_list_cases/cep_output.json"),
    ("data/get_ip_mac_list_cases/no_ip_input.json",
     "data/get_ip_mac_list_cases/no_ip_output.json"),
    ("data/get_ip_mac_list_cases/fvip_input.json",
     "data/get_ip_mac_list_cases/fvip_output.json"),
    ("data/get_ip_mac_list_cases/same_cep_fvip_input.json",
     "data/get_ip_mac_list_cases/same_cep_fvip_output.json"),
    ("data/get_ip_mac_list_cases/2_fvip_input.json",
     "data/get_ip_mac_list_cases/2_fvip_output.json"),
    ("data/get_ip_mac_list_cases/diff_cep_fvip_input.json",
     "data/get_ip_mac_list_cases/diff_cep_fvip_output.json")
])
def test_get_ip_mac_list(data, expected):

    response = AciUtils.get_ip_mac_list(get_data(data))

    assert response == get_data(expected)


@pytest.mark.parametrize("data, expected", [
    ("data/get_ep_info_cases/ep_input.json",
     "data/get_ep_info_cases/ep_output.json")
])
def test_get_ep_info(data, expected):

    # Mock AciUtils functions
    def dummy_get_controller_and_hosting_server(self, ep_child):
        return ("hyper000", "1.1.1.1")

    def dummy_get_interface(self, ep_child):
        return "Pod-0/Node-111/eth0/0"

    def dummy_get_vm_domain_and_name(self, ep_child):
        return ('DUMMY0-leaf000', 'dummy-vm-name')

    AciUtils.get_controller_and_hosting_server = dummy_get_controller_and_hosting_server
    AciUtils.get_interface = dummy_get_interface
    AciUtils.get_vm_domain_and_name = dummy_get_vm_domain_and_name

    # Test the function
    obj = AciUtils()
    response = obj.get_ep_info(get_data(data))

    assert response == get_data(expected)


@pytest.mark.parametrize("data, ep_data, expected", [
    ("data/parse_and_return_ep_data_cases/ep_input.json",
     "data/parse_and_return_ep_data_cases/get_ep_input.json",
     "data/parse_and_return_ep_data_cases/ep_output.json")
])
def test_parse_and_return_ep_data(data, ep_data, expected):

    # Mock AciUtils functions
    def dummy_get_ep_info(self, ep_attr):
        return get_data(data)

    def dummy_get_ip_mac_list(ep_child):
        return [["2.2.2.2", True], ["1.1.1.1", False]]

    AciUtils.get_ep_info = dummy_get_ep_info
    get_ip_mac_list = dummy_get_ip_mac_list

    # Test the function
    obj = AciUtils()
    response = obj.parse_and_return_ep_data(get_data(data))

    assert response == get_data(expected)


@pytest.mark.parametrize("data, ep_data, expected", [
    ("data/parse_ep_data_cases/ep_input.json",
     "data/parse_ep_data_cases/get_ep_input.json",
     "data/parse_ep_data_cases/ep_output.json")
])
def test_parse_ep_data(data, ep_data, expected):

    def dummy_parse_and_return_ep_data(self, ep_data):
        return get_data(ep_data)

    AciUtils.parse_and_return_ep_data = dummy_parse_and_return_ep_data

    obj = AciUtils()
    response = obj.parse_ep_data(get_data(data))

    assert response == get_data(expected)


def test_apic_fetch_ep_data():

    resp_data = [{"key": "val"}, {"key": "val"}]

    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return {"imdata": [{}]}

    def dummy_parse_ep_data(self, data):
        return resp_data

    AciUtils.aci_get = dummy_aci_get
    AciUtils.parse_ep_data = dummy_parse_ep_data
    AciUtils.epg_url = "dummy-epg-url"

    obj = AciUtils()
    response = obj.apic_fetch_ep_data('DummyTn')

    assert response == resp_data


def test_apic_fetch_epg_data():

    resp_data = [{"key": "val"}, {"key": "val"}]

    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return {"imdata": [{}]}

    def dummy_parse_epg_data(self, data):
        return resp_data

    AciUtils.aci_get = dummy_aci_get
    AciUtils.parse_epg_data = dummy_parse_epg_data
    AciUtils.epg_url = "dummy-epg-url"

    obj = AciUtils()
    response = obj.apic_fetch_epg_data('DummyTn')

    assert response == resp_data


@pytest.mark.parametrize('data, dn, expected', [
    ("data/apic_fetch_bd_cases/bd_input.json", "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", "Dummy-BD0"),
    ("data/apic_fetch_bd_cases/empty_input.json", "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", None)
])
def test_apic_fetch_bd(data, dn, expected):

    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return get_data(data)

    AciUtils.aci_get = dummy_aci_get
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.apic_fetch_bd(dn)

    assert response == expected


@pytest.mark.parametrize('data, dn, expected', [
    ("data/apic_fetch_vrf_cases/vrf_input.json",
     "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg",
     "data/apic_fetch_vrf_cases/vrf_output.json",),
    ("data/apic_fetch_vrf_cases/empty_input.json",
     "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg",
     "data/apic_fetch_vrf_cases/empty_output.json",)
])
def test_apic_fetch_vrf(data, dn, expected):

    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return get_data(data)

    AciUtils.aci_get = dummy_aci_get
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.apic_fetch_vrf(dn)

    assert response == get_data(expected)


@pytest.mark.parametrize('data, dn, expected', [
    ("data/apic_fetch_contract_cases/all_contracts_input.json",
     "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg",
     "data/apic_fetch_contract_cases/all_contracts_output.json"),
    ("data/apic_fetch_contract_cases/no_contracts_input.json",
     "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg",
     "data/apic_fetch_contract_cases/no_contracts_output.json")
])
def test_apic_fetch_contract(data, dn, expected):
    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return get_data(data)

    AciUtils.aci_get = dummy_aci_get
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.apic_fetch_contract(dn)

    assert response == get_data(expected)


@pytest.mark.parametrize('data, dn, expected', [
    ("data/get_epg_health_cases/epg_health_input.json",
     "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg",
     "data/get_epg_health_cases/epg_health_output.json"),
    ("data/get_epg_health_cases/empty_input.json",
     "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg",
     "data/get_epg_health_cases/empty_output.json")
])
def test_get_epg_health(data, dn, expected):
    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return get_data(data)

    AciUtils.aci_get = dummy_aci_get
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.get_epg_health(dn)

    assert response == get_data(expected)


def test_get_ap_epg_faults():
    # Mock AciUtils methods
    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return ['data1', 'data2']

    AciUtils.get_mo_related_item = dummy_get_mo_related_item
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.get_ap_epg_faults('dummy-dn')

    assert response == {'faultRecords': ['data1', 'data2']}


def test_get_ap_epg_events():
    # Mock AciUtils methods
    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return ['data1', 'data2']

    AciUtils.get_mo_related_item = dummy_get_mo_related_item
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.get_ap_epg_events('dummy-dn')

    assert response == {'eventRecords': ['data1', 'data2']}


def test_get_ap_epg_audit_logs():
    # Mock AciUtils methods
    def dummy_get_mo_related_item(self, mo_dn, item_query_string, item_type):
        return ['data1', 'data2']

    AciUtils.get_mo_related_item = dummy_get_mo_related_item
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.get_ap_epg_audit_logs('dummy-dn')

    assert response == {'auditLogRecords': ['data1', 'data2']}


@pytest.mark.parametrize('data, mo_dn, item_query_string, item_type, expected', [
    ({"imdata": ['data1', 'data2']}, 'dummy-dn', 'dummy-url', '', ['data1', 'data2']),
    ({"imdata": ['data1', 'data2']}, '', 'dummy-url', "other_url", ['data1', 'data2'])
])
def test_get_mo_related_item(data, mo_dn, item_query_string, item_type, expected):

    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return data

    AciUtils.aci_get = dummy_aci_get
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.get_mo_related_item(mo_dn, item_query_string, item_type)

    assert response == expected


@pytest.mark.parametrize('data, contract, expected', [
    ("data/parse_and_return_epg_data_cases/epg_data_input.json",
     "data/parse_and_return_epg_data_cases/epg_data_contract.json",
     "data/parse_and_return_epg_data_cases/epg_data_output.json")
])
def test_parse_and_return_epg_data(data, contract, expected):

    # Mock AciUtils methods
    def dummy_apic_fetch_bd(self, url):
        return "Dummy-BD0"

    def dummy_apic_fetch_vrf(self, url):
        return "Dummy-VRF"

    def dummy_apic_fetch_contract(self, url):
        return get_data(contract)

    def dummy_get_epg_health(self, url):
        return "96"

    AciUtils.apic_fetch_bd = dummy_apic_fetch_bd
    AciUtils.apic_fetch_vrf = dummy_apic_fetch_vrf
    AciUtils.apic_fetch_contract = dummy_apic_fetch_contract
    AciUtils.get_epg_health = dummy_get_epg_health

    obj = AciUtils()
    response = obj.parse_and_return_epg_data(get_data(data))

    assert response == get_data(expected)


def test_parse_epg_data():

    # Mock AciUtils methods
    def dummy_parse_and_return_epg_data(self, url):
        return {"dummy-key": "dummy-val"}

    AciUtils.parse_and_return_epg_data = dummy_parse_and_return_epg_data

    obj = AciUtils()
    response = obj.parse_and_return_epg_data([{"fvAEPg": {}}])

    assert response == {"dummy-key": "dummy-val"}


def test_login():

    def dummy_create_cert_session():
        obj = DummyClass()
        obj.dn = 'dummy-dn'
        return (obj, 'dummy-key')

    def json():
        return {'imdata': [{'aaaLogin': {'attributes': {'token': 'dummy-token'}}}]}

    def dummy_post(self, url, data, headers, timeout, verify):
        obj = DummyClass()
        obj.status_code = 200
        obj.json = json
        return obj

    Session.get = dummy_post

    apic_utils.create_cert_session = dummy_create_cert_session

    obj = AciUtils()
    response = obj.login()

    assert response == 'dummy-token'

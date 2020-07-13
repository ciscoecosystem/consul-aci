import pytest
import time
from requests import Session
from Service import apic_utils
from Service.apic_utils import AciUtils
from Service.tests.utils import DummyClass


aci_get_cases = [(200, {'dummy_key': 'dummy_val'}), (400, None)]

get_interface_cases = [
    ({
        "fvRsCEpToPathEp": {
            "attributes": {
                "tDn": "topology/pod-0/paths-111/pathep-[eth0/0]",
            }
        }
    }, "111", "Pod-0/Node-111/eth0/0"),
    ({
        "fvRsCEpToPathEp": {
            "attributes": {
                "tDn": "topology/pod-0/protpaths-111-222/pathep-[FI-A-PG]",
            }
        }
    }, "-111-222", "Pod-0/Node--111-222/FI-A-PG"),
    ({
        "fvRsCEpToPathEp": {
            "attributes": {
                "tDn": "topology/pod-1/pathgrp-[1.1.1.1]",
            }
        }
    }, "[1.1.1.1]", "Pod-1/Node-[1.1.1.1]/1.1.1.1(vmm)")
]

get_node_from_interface_cases = [
    ("topology/pod-1/pathdummy-xxx", ""),
    ("topology/pod-1/pathgrp-[1.1.1.1]", "[1.1.1.1]"),
    ("topology/pod-0/paths-111/pathep-[eth0/0]", "111"),
    ("topology/pod-0/protpaths-111-222/pathep-[FI-A-PG]", "-111-222"),
    (["topology/pod-0/protpaths-111-222/pathep-[FI-A-PG]", "topology/pod-0/paths-111/pathep-[eth0/0]"], "-111-222, 111"),
]

get_controller_and_hosting_server = [
    ({
        "fvRsHyper": {
            "attributes": {
                "tDn": "comp/prov-dummy/ctrlr-[DUMMY0-leaf000]-hyper000/hv-host-00"
            }
        }
    }, [{
        "compHv": {
            "attributes": {
                "name": "1.1.1.1"
            }
        }
    }], ("hyper000", "1.1.1.1")),
    ({
        "fvRsHyper": {
            "attributes": {
                "tDn": "comp/prov-dummy/ctrlr-[DUMMY0-leaf000]-hyper000/hv-host-00"
            }
        }
    }, [], ("hyper000", "")),
    ({}, [{
        "compHv": {
            "attributes": {
                "name": "1.1.1.1"
            }
        }
    }], ("", ""))
]

get_ip_mac_list_cases = [
    ({
        "fvCEp": {
            "attributes": {
                "ip": "1.1.1.1",
                "mac": "00:00:00:00:00:AA",
            },
            "children": [
                {
                    "fvRsCEpToPathEp": {},
                },
                {
                    "fvRsHyper": {},
                },
                {
                    "fvRsToVm": {}
                }
            ]
        }
    }, [["1.1.1.1", True]]),
    ({
        "fvCEp": {
            "attributes": {
                "ip": "0.0.0.0",
                "mac": "00:00:00:00:00:AA",
            },
            "children": [
                {
                    "fvRsCEpToPathEp": {},
                },
                {
                    "fvRsHyper": {},
                },
                {
                    "fvRsToVm": {}
                }
            ]
        }
    }, [["00:00:00:00:00:aa", False]]),
    ({
        "fvCEp": {
            "attributes": {
                "ip": "0.0.0.0",
                "mac": "00:00:00:00:00:AA",
            },
            "children": [
                {
                    "fvIp": {
                        "attributes": {
                            "addr": "1.1.1.1",
                        }
                    },
                },
                {
                    "fvRsCEpToPathEp": {},
                },
                {
                    "fvRsHyper": {},
                },
                {
                    "fvRsToVm": {}
                }
            ]
        }
    }, [["1.1.1.1", False]]),
    ({
        "fvCEp": {
            "attributes": {
                "ip": "1.1.1.1",
                "mac": "00:00:00:00:00:AA",
            },
            "children": [
                {
                    "fvIp": {
                        "attributes": {
                            "addr": "1.1.1.1",
                        }
                    },
                },
                {
                    "fvRsCEpToPathEp": {},
                },
                {
                    "fvRsHyper": {},
                },
                {
                    "fvRsToVm": {}
                }
            ]
        }
    }, [["1.1.1.1", False]]),
    ({
        "fvCEp": {
            "attributes": {
                "ip": "0.0.0.0",
                "mac": "00:00:00:00:00:AA",
            },
            "children": [
                {
                    "fvIp": {
                        "attributes": {
                            "addr": "1.1.1.1",
                        }
                    },
                },
                {
                    "fvIp": {
                        "attributes": {
                            "addr": "2.2.2.2",
                        }
                    },
                },
                {
                    "fvRsCEpToPathEp": {},
                },
                {
                    "fvRsHyper": {},
                },
                {
                    "fvRsToVm": {}
                }
            ]
        }
    }, [["1.1.1.1", False], ["2.2.2.2", False]]),
    ({
        "fvCEp": {
            "attributes": {
                "ip": "1.1.1.1",
                "mac": "00:00:00:00:00:AA",
            },
            "children": [
                {
                    "fvIp": {
                        "attributes": {
                            "addr": "2.2.2.2",
                        }
                    },
                },
                {
                    "fvRsCEpToPathEp": {},
                },
                {
                    "fvRsHyper": {},
                },
                {
                    "fvRsToVm": {}
                }
            ]
        }
    }, [["2.2.2.2", False], ["1.1.1.1", True]])
]

apic_fetch_bd_cases = [
    ({
        "imdata": [{
            "fvRsBd": {
                "attributes": {
                    "tnFvBDName": "Dummy-BD0",
                }
            }}]
    }, "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", "Dummy-BD0"),
    ({}, "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", None)
]

apic_fetch_vrf_cases = [
    ({
        "imdata": [{
            "fvRsCtx": {
                "attributes": {
                    "tnFvCtxName": "Dummy-VRF",
                }
            }}]
    }, "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", "Dummy-VRF"),
    ({}, "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", '')
]

apic_fetch_contract_cases = [
    ({"imdata": [
        {
            "fvRsProv": {
                "attributes": {
                    "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/rsprov-dummy1",
                }
            }
        },
        {
            "fvRsProv": {
                "attributes": {
                    "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/rsprov-dummy2",
                }
            }
        },
        {
            "fvRsCons": {
                "attributes": {
                    "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/rscons-dummy1",
                }
            }
        },
        {
            "fvRsCons": {
                "attributes": {
                    "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/rscons-dummy2",
                }
            }
        },
        {
            "fvRsIntraEpg": {
                "attributes": {
                    "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/rscons-dummy0",
                }
            }
        },
        {
            "fvRsConsIf": {
                "attributes": {
                    "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/rscons-dummy0",
                }
            }
        },
        {
            "fvRsProtBy": {
                "attributes": {
                    "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/rscons-dummy0",
                }
            }
        }
    ]
    }, "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", {
        "Consumer": ["dummy1", "dummy2"],
        "Intra EPG": ["dummy0"],
        "Provider": ["dummy1", "dummy2"],
        "Consumer Interface": ["dummy0"],
        "Taboo": ["dummy0"]
    }),
    ({}, "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", {})
]

get_epg_health_cases = [
    ({
        "imdata": [{
            "healthInst": {
                "attributes": {
                    "cur": "96",
                }
            }
        }, {
            "healthNodeInst": {}
        }, {
            "healthNodeInst": {}
        }]
    }, "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", "96"),
    ({}, "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg", '')
]

get_mo_related_item_cases = [
    ({"imdata": ['data1', 'data2']}, 'dummy-dn', 'dummy-url', '', ['data1', 'data2']),
    ({"imdata": ['data1', 'data2']}, '', 'dummy-url', "other_url", ['data1', 'data2'])
]


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


def test_get_vm_domain_and_name():
    """Test the VM Domain and Name"""

    def dummy_aci_get(self, url):
        return {
            "totalCount": "1",
            "imdata": [
                {
                    "compVm": {
                        "attributes": {
                            "name": "dummy-vm-name",
                        }
                    }
                }
            ]
        }

    AciUtils.aci_get = dummy_aci_get

    # Test the function
    obj = AciUtils()
    response = obj.get_vm_domain_and_name({
        "fvRsToVm": {
            "attributes": {
                "tDn": "comp/prov-dummy/ctrlr-[DUMMY0-leaf000]-dummy/vm-vm-000",
            }
        }
    })

    assert response == ('DUMMY0-leaf000', 'dummy-vm-name')


@pytest.mark.parametrize("interface, expected", get_node_from_interface_cases)
def test_get_node_from_interface(interface, expected):

    # Test the function
    response = AciUtils.get_node_from_interface(interface)

    assert response == expected


@pytest.mark.parametrize("data, node, expected", get_interface_cases)
def test_get_interface(data, node, expected):

    # Mock apic_util get_node_from_interface
    def dummy_get_node_from_interface(self, interface):
        return node

    AciUtils.get_node_from_interface = dummy_get_node_from_interface

    # Test the function
    obj = AciUtils()
    response = obj.get_interface(data)

    assert response == expected


@pytest.mark.parametrize("data,mo_instance_data,expected", get_controller_and_hosting_server)
def test_get_controller_and_hosting_server(data, mo_instance_data, expected):

    def dummy_get_all_mo_instances(self, mo_class, query_string=""):
        return mo_instance_data

    AciUtils.get_all_mo_instances = dummy_get_all_mo_instances

    # Test the function
    obj = AciUtils()
    response = obj.get_controller_and_hosting_server(data)

    assert response == expected


def test_get_all_mo_instances():

    def dummy_aci_get(self, url):
        return {
            "totalCount": "1",
            "imdata": [
                {
                    "compHv": {
                        "attributes": {
                            "name": "1.1.1.1"
                        }
                    }
                }
            ]
        }

    AciUtils.aci_get = dummy_aci_get

    # Test the function
    obj = AciUtils()
    response = obj.get_all_mo_instances("dummy-class", "dummy-query")

    assert response == [{"compHv": {"attributes": {"name": "1.1.1.1"}}}]


def test_get_dict_records():

    response = AciUtils.get_dict_records([1, 2, 3], 'key')

    assert response == {'key': [1, 2, 3]}


@pytest.mark.parametrize('data,expected', get_ip_mac_list_cases)
def test_get_ip_mac_list(data, expected):

    response = AciUtils.get_ip_mac_list(data)

    assert response == expected


def test_get_ep_info():

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
    response = obj.get_ep_info([
        {
            "fvRsCEpToPathEp": {
                "attributes": {
                    "tDn": "topology/pod-0/paths-111/pathep-[eth0/0]",
                }
            }
        },
        {
            "fvRsHyper": {
                "attributes": {
                    "tDn": "comp/prov-dummy/ctrlr-[DUMMY0-leaf000]-hyper000/hv-host-00"
                }
            }
        },
        {
            "fvRsToVm": {
                "attributes": {
                    "tDn": "comp/prov-dummy/ctrlr-[DUMMY0-leaf000]-dummy/vm-vm-000",
                }
            }
        }
    ])

    assert response == {
        "controller": "hyper000",
        "hosting_servername": "1.1.1.1",
        "interfaces": ["Pod-0/Node-111/eth0/0"],
        "vm_name": 'dummy-vm-name',
        "vmm_domain": 'DUMMY0-leaf000'
    }


def test_parse_and_return_ep_data():

    # Mock AciUtils functions
    def dummy_get_ep_info(self, ep_attr):
        return {
            "controller": "hyper000",
            "hosting_servername": "1.1.1.1",
            "interfaces": ["Pod-0/Node-111/eth0/0"],
            "vm_name": 'dummy-vm-name',
            "vmm_domain": 'DUMMY0-leaf000'
        }

    def dummy_get_ip_mac_list(ep_child):
        return [["2.2.2.2", True], ["1.1.1.1", False]]

    AciUtils.get_ep_info = dummy_get_ep_info
    get_ip_mac_list = dummy_get_ip_mac_list

    # Test the function
    obj = AciUtils()
    response = obj.parse_and_return_ep_data({
        "fvCEp": {
            "attributes": {
                "ip": "2.2.2.2",
                "mac": "00:00:00:00:00:AA",
                "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
                "lcC": "dummy-vmm",
                "encap": "dummy-lan-111",
                "mcastAddr": "not-applicable"
            },
            "children": [
                {
                    "fvIp": {
                        "attributes": {
                            "addr": "1.1.1.1",
                        }
                    },
                },
                {
                    "fvRsCEpToPathEp": {},
                },
                {
                    "fvRsHyper": {},
                },
                {
                    "fvRsToVm": {}
                }
            ]
        }
    })

    assert response == [{
        "controller": "hyper000",
        "hosting_servername": "1.1.1.1",
        "interfaces": ["Pod-0/Node-111/eth0/0"],
        "vm_name": 'dummy-vm-name',
        "vmm_domain": 'DUMMY0-leaf000',
        "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
        "learning_src": "dummy-vmm",
        "tenant": "DummyTn",
        "mac": "00:00:00:00:00:AA",
        "encap": "dummy-lan-111",
        "multi_cast_addr": "---",
        "ip": "1.1.1.1",
        "is_cep": False
    }, {
        "controller": "hyper000",
        "hosting_servername": "1.1.1.1",
        "interfaces": ["Pod-0/Node-111/eth0/0"],
        "vm_name": 'dummy-vm-name',
        "vmm_domain": 'DUMMY0-leaf000',
        "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
        "learning_src": "dummy-vmm",
        "tenant": "DummyTn",
        "mac": "00:00:00:00:00:AA",
        "encap": "dummy-lan-111",
        "multi_cast_addr": "---",
        "ip": "2.2.2.2",
        "is_cep": True
    }]


def test_parse_ep_data():

    def dummy_parse_and_return_ep_data(self, ep_data):
        return [
            {
                "controller": "hyper000",
                "hosting_servername": "1.1.1.1",
                "interfaces": ["Pod-0/Node-111/eth0/0"],
                "vm_name": 'dummy-vm-name',
                "vmm_domain": 'DUMMY0-leaf000',
                "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
                "learning_src": "dummy-vmm",
                "tenant": "DummyTn",
                "mac": "00:00:00:00:00:AA",
                "encap": "dummy-lan-111",
                "multi_cast_addr": "---",
                "ip": "1.1.1.1",
                "is_cep": False
            }, {
                "controller": "hyper000",
                "hosting_servername": "1.1.1.1",
                "interfaces": ["Pod-0/Node-111/eth0/0"],
                "vm_name": 'dummy-vm-name',
                "vmm_domain": 'DUMMY0-leaf000',
                "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
                "learning_src": "dummy-vmm",
                "tenant": "DummyTn",
                "mac": "00:00:00:00:00:AA",
                "encap": "dummy-lan-111",
                "multi_cast_addr": "---",
                "ip": "2.2.2.2",
                "is_cep": True
            }]

    AciUtils.parse_and_return_ep_data = dummy_parse_and_return_ep_data

    obj = AciUtils()
    response = obj.parse_ep_data([{
        "fvCEp": {
            "attributes": {
                "ip": "2.2.2.2",
                "mac": "00:00:00:00:00:AA",
                "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
                "lcC": "dummy-vmm",
                "encap": "dummy-lan-111",
                "mcastAddr": "not-applicable"
            },
            "children": [
                {
                    "fvIp": {
                        "attributes": {
                            "addr": "1.1.1.1",
                        }
                    },
                },
                {
                    "fvRsCEpToPathEp": {},
                },
                {
                    "fvRsHyper": {},
                },
                {
                    "fvRsToVm": {}
                }
            ]
        }
    }, {
        "fvCEp": {
            "attributes": {
                "ip": "2.2.2.2",
                "mac": "00:00:00:00:00:AA",
                "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
                "lcC": "dummy-vmm",
                "encap": "dummy-lan-111",
                "mcastAddr": "not-applicable"
            },
            "children": [
                {
                    "fvIp": {
                        "attributes": {
                            "addr": "1.1.1.1",
                        }
                    },
                },
                {
                    "fvRsCEpToPathEp": {},
                },
                {
                    "fvRsHyper": {},
                },
                {
                    "fvRsToVm": {}
                }
            ]
        }
    }])

    assert response == [{
        "controller": "hyper000",
        "hosting_servername": "1.1.1.1",
        "interfaces": ["Pod-0/Node-111/eth0/0"],
        "vm_name": 'dummy-vm-name',
        "vmm_domain": 'DUMMY0-leaf000',
        "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
        "learning_src": "dummy-vmm",
        "tenant": "DummyTn",
        "mac": "00:00:00:00:00:AA",
        "encap": "dummy-lan-111",
        "multi_cast_addr": "---",
        "ip": "1.1.1.1",
        "is_cep": False
    }, {
        "controller": "hyper000",
        "hosting_servername": "1.1.1.1",
        "interfaces": ["Pod-0/Node-111/eth0/0"],
        "vm_name": 'dummy-vm-name',
        "vmm_domain": 'DUMMY0-leaf000',
        "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
        "learning_src": "dummy-vmm",
        "tenant": "DummyTn",
        "mac": "00:00:00:00:00:AA",
        "encap": "dummy-lan-111",
        "multi_cast_addr": "---",
        "ip": "2.2.2.2",
        "is_cep": True
    }, {
        "controller": "hyper000",
        "hosting_servername": "1.1.1.1",
        "interfaces": ["Pod-0/Node-111/eth0/0"],
        "vm_name": 'dummy-vm-name',
        "vmm_domain": 'DUMMY0-leaf000',
        "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
        "learning_src": "dummy-vmm",
        "tenant": "DummyTn",
        "mac": "00:00:00:00:00:AA",
        "encap": "dummy-lan-111",
        "multi_cast_addr": "---",
        "ip": "1.1.1.1",
        "is_cep": False
    }, {
        "controller": "hyper000",
        "hosting_servername": "1.1.1.1",
        "interfaces": ["Pod-0/Node-111/eth0/0"],
        "vm_name": 'dummy-vm-name',
        "vmm_domain": 'DUMMY0-leaf000',
        "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg/cep-00:00:00:00:00:AA",
        "learning_src": "dummy-vmm",
        "tenant": "DummyTn",
        "mac": "00:00:00:00:00:AA",
        "encap": "dummy-lan-111",
        "multi_cast_addr": "---",
        "ip": "2.2.2.2",
        "is_cep": True
    }]


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


@pytest.mark.parametrize('data, dn, expected', apic_fetch_bd_cases)
def test_apic_fetch_bd(data, dn, expected):

    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return data

    AciUtils.aci_get = dummy_aci_get
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.apic_fetch_bd(dn)

    assert response == expected


@pytest.mark.parametrize('data, dn, expected', apic_fetch_vrf_cases)
def test_apic_fetch_vrf(data, dn, expected):

    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return data

    AciUtils.aci_get = dummy_aci_get
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.apic_fetch_vrf(dn)

    assert response == expected


@pytest.mark.parametrize('data, dn, expected', apic_fetch_contract_cases)
def test_apic_fetch_contract(data, dn, expected):
    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return data

    AciUtils.aci_get = dummy_aci_get
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.apic_fetch_contract(dn)

    assert response == expected


@pytest.mark.parametrize('data, dn, expected', get_epg_health_cases)
def test_get_epg_health(data, dn, expected):
    # Mock AciUtils methods
    def dummy_aci_get(self, url):
        return data

    AciUtils.aci_get = dummy_aci_get
    AciUtils.proto = "http://"
    AciUtils.apic_ip = "dummy-apic-ip"

    obj = AciUtils()
    response = obj.get_epg_health(dn)

    assert response == expected


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


@pytest.mark.parametrize('data, mo_dn, item_query_string, item_type, expected', get_mo_related_item_cases)
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


def test_parse_and_return_epg_data():

    # Mock AciUtils methods
    def dummy_apic_fetch_bd(self, url):
        return "Dummy-BD0"

    def dummy_apic_fetch_vrf(self, url):
        return "Dummy-VRF"

    def dummy_apic_fetch_contract(self, url):
        return {
            "Consumer": ["dummy1", "dummy2"],
            "Intra EPG": ["dummy0"],
            "Provider": ["dummy1", "dummy2"],
            "Consumer Interface": ["dummy0"],
            "Taboo": ["dummy0"]
        }

    def dummy_get_epg_health(self, url):
        return "96"

    AciUtils.apic_fetch_bd = dummy_apic_fetch_bd
    AciUtils.apic_fetch_vrf = dummy_apic_fetch_vrf
    AciUtils.apic_fetch_contract = dummy_apic_fetch_contract
    AciUtils.get_epg_health = dummy_get_epg_health

    obj = AciUtils()
    response = obj.parse_and_return_epg_data({
        "fvAEPg": {
            "attributes": {
                "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg",
                "name": "DummyEpg",
                "nameAlias": "DummyAliasName",
            }
        }
    })

    assert response == {
        "dn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg",
        "tenant": "DummyTn",
        "bd": "Dummy-BD0",
        "app_profile": "DummyAp",
        "epg": "DummyEpg",
        "epg_alias": "DummyAliasName",
        "vrf": "DummyTn/Dummy-VRF",
        "contracts": {
            "Consumer": ["dummy1", "dummy2"],
            "Intra EPG": ["dummy0"],
            "Provider": ["dummy1", "dummy2"],
            "Consumer Interface": ["dummy0"],
            "Taboo": ["dummy0"]
        },
        "epg_health": "96"
    }


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

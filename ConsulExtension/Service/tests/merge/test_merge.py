import json
import pytest
from Service import merge
from copy import deepcopy


def get_data(case, file_name):
    with open('./tests/merge/data/{}/{}'.format(case, file_name), 'r') as fp:
        data = json.load(fp)
        return data


'''
Case1: Dangeling node
Case2: All the data having ipv6 addresses
Case3: Service with different ip as that of Node which mappes to Some EP
Case4: Service with different ip as that of Node which DOES NOT map to any EP
Case5: Service with no ip
Case6: All above combinations
'''
cases_merge_aci_consul = [
    "dangling",
    "ipv6",
    "service_to_ep",
    "service_to_none",
    "service_without_ip",
    "random_combination"
]
cases_custom_copy = get_data("custom_copy", "custom_copy_input.json")


def gen_keys_ls(data):
    ls = []
    for each in data:
        ls.append("{}{}".format(
            each.get("dn", ""),
            each.get("IP", "")
        ))
    return ls


def get_final_output(original_response, generated_response):
    for each in generated_response:
        if each not in original_response:
            return False
    return True


def verifier_consul_data_formatter(copy_consul_data, consul_data, mapping_ips):
    flag = True
    for i, node in enumerate(copy_consul_data):
        for key in node.keys():
            if key == "node_services":
                for service in node['node_services']:
                    if (
                        (
                            service.get('service_ip') == ""
                            or service.get('service_ip')
                            in node.get('node_ips', [])
                        )
                        and not
                        (
                            service.get('service_ip') != ""
                            and service.get('service_ip') not in mapping_ips
                        )
                        and service not in consul_data[i]["node_services_copy"]
                    ):
                        assert service is False
                        flag = False
                        break
                    if (
                        (
                            service.get('service_ip') != ""
                            and service.get('service_ip') not in mapping_ips
                        )
                        and service in consul_data[i]["node_services"]
                    ):
                        flag = False
                        break
                else:
                    break
            else:
                if node[key] != consul_data[i][key]:
                    flag = False
                    break
        else:
            break
    return flag


@pytest.mark.parametrize("case", cases_merge_aci_consul)
def test_merge_aci_consul(case):
    tenant = 'tn0'
    aci_data = get_data(case, 'aci_data.json')
    consul_data = get_data(case, 'consul_data.json')
    aci_consul_mappings = get_data(case, 'aci_consul_mappings.json')
    original_response = get_data(case, 'final_list.json')
    generated_response = merge.merge_aci_consul(
        tenant,
        aci_data,
        consul_data,
        aci_consul_mappings
    )
    original_response = gen_keys_ls(original_response)
    generated_response = gen_keys_ls(generated_response[0])
    assert get_final_output(original_response, generated_response)


@pytest.mark.parametrize("case", cases_custom_copy)
def test_custom_copy(case):
    case_copy = merge.custom_copy(case)
    assert case_copy == case
    case = None
    assert case_copy != case


@pytest.mark.parametrize("case", cases_merge_aci_consul)
def test_aci_consul_mappings_formatter(case):
    data = get_data(case, "aci_consul_mappings.json")
    output = merge.aci_consul_mappings_formatter(data)
    flag = True
    for each in data:
        ip = each.get('ip')
        if ip:
            dn = each.get('dn')
            key = (dn, ip)
            if each != output[key]:
                flag = False
                break
    assert flag


@pytest.mark.parametrize("case", cases_merge_aci_consul)
def test_mapped_consul_nodes_formatter(case):
    data = get_data(case, "consul_data.json")
    output = merge.mapped_consul_nodes_formatter(data)
    flag = True
    for node in data:
        for ip in node.get('node_ips', []):
            if node not in output[ip]:
                flag = False
                break
        else:
            break
    assert flag


@pytest.mark.parametrize("case", cases_merge_aci_consul)
def test_consul_data_formatter(case):
    aci_consul_mappings = get_data(case, "aci_consul_mappings.json")
    mappings = [node for node in aci_consul_mappings if node.get('enabled')]
    mapping_ips = dict()
    for each in mappings:
        mapping_ips[each.get('ip')] = True
    consul_data = get_data(case, "consul_data.json")
    copy_consul_data = deepcopy(consul_data)
    merge.consul_data_formatter(consul_data, mapping_ips)
    assert verifier_consul_data_formatter(copy_consul_data, consul_data, mapping_ips)

import json
import pytest
from Service import merge


def get_data(case, file_name):
    with open('./tests/merge/{}/{}'.format(case, file_name), 'r') as fp:
        data = json.load(fp)
        return data


'''
Dangeling node 									                            dangling
All the data having ipv6 addresses                                          ipv6
Service with different ip as that of Node which mappes to Some EP	    	nodeservicetoep
Service with different ip as that of Node which DOES NOT map to any EP		notnodeservicetoep
Service with no ip								                            servicewithoutip
All above combinations								                        general20
'''
cases = ['dangling', 'ipv6', 'nodeservicetoep', 'notnodeservicetoep', 'servicewithoutip', 'general20']


@pytest.mark.parametrize("case", cases)
def test_merge_aci_consul(case):
    tenant = 'tn0'
    aci_data = get_data(case, 'aci_data.json')
    consul_data = get_data(case, 'consul_data.json')
    aci_consul_mappings = get_data(case, 'aci_consul_mappings.json')
    original_response = get_data(case, 'final_list.json')
    generated_response = merge.merge_aci_consul(tenant,
                                                aci_data,
                                                consul_data,
                                                aci_consul_mappings
                                                )
    assert original_response == generated_response

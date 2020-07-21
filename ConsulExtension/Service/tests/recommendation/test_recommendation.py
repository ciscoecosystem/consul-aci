from Service.recommend_utils import (determine_recommendation,
                                     recommended_eps)
from Service.plugin_server import get_apic_data

import pytest
import sys
from mock import Mock

sys.modules['cobra'] = 'cobra'
sys.modules['cobra.model'] = 'cobra.model'
sys.modules['cobra.model.pol'] = Mock(name='Uni')
sys.modules['cobra.model.aaa'] = Mock(name='UserEp')

import os
import configparser
from Service import custom_logger
logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")

DOMAIN_LIST = ['uni/tn-tn0/ap-ap0/epg-epg1',
               'uni/tn-tn0/ap-ap0/epg-epg2',
               'uni/tn-tn0/ap-ap1/epg-epg1']

IP_LIST = []
STATIC_IP_KEY = 'RECOMMENDATION_TEST_IP'


class FileCopyException(Exception):
    pass


def get_conf_value(section, key_name):
    """Function to return value from configuration
    File

    Args:
        key_name (str): Name of key
    """

    dir_path = os.path.dirname(os.path.abspath(__file__))
    print('Dir path : {}'.format(dir_path))
    file_path = r''.join([dir_path,
                          '/data/recommendation_config.cfg'])

    config = configparser.ConfigParser()

    config.read(file_path)
    return config.get(section, key_name)


@pytest.fixture(scope="module", autouse=True)
def pre_test_setup(request):
    # factory will only be invoked once per session -
    try:
        os_cmd = os.system(
            'cp ./tests/recommendation/data/ConsulDatabase.db ./ConsulDatabase.db')
        if os_cmd != 0:
            raise FileCopyException('Unable to execute copy command')
        print('Test DB successfully copied')
    except FileCopyException as e:
        print('Exception {}'.format(e))

    IP_LIST.append(get_conf_value('IP', STATIC_IP_KEY))

    def delete_db():
        os.remove('./ConsulDatabase.db')
    request.addfinalizer(delete_db)


@pytest.fixture(scope='class')
def cef_ip_and_fvip_data():
    extract_ap_epgs = {'ap2': {'epg3': 2, 'epg0': 1, 'epg1': 2, 'epg4': 2},
                       'ap0': {'epg2': 2, 'epg0': 1, 'epg1': 2, 'epg4': 1},
                       'ap1': {'epg2': 2, 'epg1': 1, 'epg4': 2}}

    common_eps = []
    common_eps.append({'dn': DOMAIN_LIST[0],
                       'IP': IP_LIST[0], 'cep_ip': True})
    common_eps.append({'dn': DOMAIN_LIST[1],
                       'IP': IP_LIST[0], 'cep_ip': False})
    common_eps.append({'dn': DOMAIN_LIST[2],
                       'IP': IP_LIST[0], 'cep_ip': True})
    apic_data = get_apic_data('tn0')
    return extract_ap_epgs, common_eps, apic_data


@pytest.fixture(scope='class')
def vrf_data():
    extract_ap_epgs = {'ap2': {'epg3': 2, 'epg0': 1, 'epg1': 2, 'epg4': 2},
                       'ap0': {'epg2': 2, 'epg0': 1, 'epg1': 2, 'epg4': 1},
                       'ap1': {'epg2': 2, 'epg1': 1, 'epg4': 2}}
    common_eps = []
    common_eps.append({'dn': DOMAIN_LIST[0],
                       'IP': IP_LIST[0], 'cep_ip': False})
    common_eps.append({'dn': DOMAIN_LIST[1],
                       'IP': IP_LIST[0], 'cep_ip': False})
    common_eps.append({'dn': DOMAIN_LIST[2],
                       'IP': IP_LIST[0], 'cep_ip': False})
    apic_data = get_apic_data('tn0')
    return extract_ap_epgs, common_eps, apic_data


@pytest.fixture(scope='class')
def ap_data():
    extract_ap_epgs = {'ap2': {'epg3': 2, 'epg0': 1, 'epg1': 2, 'epg4': 2},
                       'ap0': {'epg2': 2, 'epg0': 1, 'epg1': 2, 'epg4': 1},
                       'ap1': {'epg2': 2, 'epg1': 5, 'epg4': 2, }}
    common_eps = []
    common_eps.append({'dn': DOMAIN_LIST[0],
                       'IP': IP_LIST[0], 'cep_ip': False})
    common_eps.append({'dn': DOMAIN_LIST[1],
                       'IP': IP_LIST[0], 'cep_ip': False})
    common_eps.append({'dn': DOMAIN_LIST[2],
                       'IP': IP_LIST[0], 'cep_ip': False})
    apic_data = get_apic_data('tn0')
    return extract_ap_epgs, common_eps, apic_data


@pytest.fixture(scope='class')
def ap_same_count_data(scope='class'):
    extract_ap_epgs = {'ap2': {'epg3': 2, 'epg0': 1, 'epg1': 2, 'epg4': 2},
                       'ap0': {'epg2': 2, 'epg0': 1, 'epg1': 2, 'epg4': 1},
                       'ap1': {'epg2': 2, 'epg0': 1, 'epg1': 2, 'epg4': 1}}
    common_eps = []
    common_eps.append({'dn': DOMAIN_LIST[0],
                       'IP': IP_LIST[0], 'cep_ip': False})
    common_eps.append({'dn': DOMAIN_LIST[1],
                       'IP': IP_LIST[0], 'cep_ip': False})
    common_eps.append({'dn': DOMAIN_LIST[2],
                       'IP': IP_LIST[0], 'cep_ip': False})
    apic_data = get_apic_data('tn0')
    return extract_ap_epgs, common_eps, apic_data


def test_recommended_eps():
    source_ip_list = []
    parsed_eps = []
    apic_data = []
    actual_eps = recommended_eps(source_ip_list,
                                 parsed_eps, apic_data)
    assert actual_eps == []


def test_determine_recommendation_cef_fvip(cef_ip_and_fvip_data):
    source_ip_list, parsed_eps, apic_data = cef_ip_and_fvip_data
    expected_eps = []
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[0], 'No', 'IP'])
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[2], 'No', 'IP'])
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[1], 'Yes', 'IP'])
    actual_eps = determine_recommendation(source_ip_list,
                                          parsed_eps, apic_data)

    assert len(actual_eps) == len(expected_eps)
    assert all(item in actual_eps for item in expected_eps)


def test_determine_recommendation_vrf(vrf_data):
    source_ip_list, parsed_eps, apic_data = vrf_data
    expected_eps = []
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[0], 'No', 'IP'])
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[2], 'No', 'IP'])
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[1], 'Yes', 'IP'])
    actual_eps = determine_recommendation(source_ip_list,
                                          parsed_eps, apic_data)
    assert len(actual_eps) == len(expected_eps)
    assert all(item in actual_eps for item in expected_eps)


def test_determine_recommendation_ap(ap_data):
    source_ip_list, parsed_eps, apic_data = ap_data
    expected_eps = []
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[0], 'No', 'IP'])
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[2], 'No', 'IP'])
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[1], 'Yes', 'IP'])
    actual_eps = determine_recommendation(source_ip_list,
                                          parsed_eps, apic_data)

    print('expected {}'.format(expected_eps))
    print('expected {}'.format(actual_eps))

    assert len(actual_eps) == len(expected_eps)
    assert all(item in actual_eps for item in expected_eps)


def test_determine_recommendation_same_ap_count(ap_same_count_data):
    source_ip_list, parsed_eps, apic_data = ap_same_count_data
    expected_eps = []
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[0], 'No', 'IP'])
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[2], 'Yes', 'IP'])
    expected_eps.append([IP_LIST[0],
                         DOMAIN_LIST[1], 'Yes', 'IP'])
    actual_eps = determine_recommendation(source_ip_list,
                                          parsed_eps, apic_data)
    assert len(actual_eps) == len(expected_eps)
    assert all(item in actual_eps for item in expected_eps)

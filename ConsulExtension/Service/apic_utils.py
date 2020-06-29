import re
import json
import copy
import base64
import requests
from collections import defaultdict
import concurrent.futures

import urls
from decorator import time_it
from custom_logger import CustomLogger
from config_utils import get_conf_value

from cobra.model.pol import Uni as PolUni
from cobra.model.aaa import UserEp as AaaUserEp
from cobra.model.aaa import AppUser as AaaAppUser
from cobra.model.aaa import UserCert as AaaUserCert
try:
    from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, sign
except Exception as e:
    print("=== could not import openssl crypto ===")


logger = CustomLogger.get_logger("/home/app/log/app.log")

APIC_IP = get_conf_value('APIC', 'APIC_IP')
STATIC_IP = get_conf_value('APIC', 'STATIC_IP')
APIC_THREAD_POOL = int(get_conf_value('APIC', 'APIC_THREAD_POOL'))


def create_cert_session():
    """
    Create user certificate and session.
    """

    cert_user = 'CiscoHashiCorp_ConsulExtensionforACI'  # Name of Application, used for token generation
    # static generated upon install
    plugin_key_file = '/home/app/credentials/plugin.key'
    pol_uni = PolUni('')
    aaa_user_ep = AaaUserEp(pol_uni)
    aaa_app_user = AaaAppUser(aaa_user_ep, cert_user)
    aaa_user_cert = AaaUserCert(aaa_app_user, cert_user)

    with open(plugin_key_file, "r") as file:
        plugin_key = file.read()

    return (aaa_user_cert, plugin_key)


class AciUtils(object):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(AciUtils, cls).__new__(cls)
            cls.apic_ip = APIC_IP
            cls.session = requests.Session()
            cls.proto = 'https://'
            cls.apic_token = cls.__instance.login()

            if not cls.apic_token:
                logger.warning(
                    'Connection to APIC failed. Trying http instead...')
                cls.proto = 'http://'
                logger.info(cls.proto)
                logger.info(cls.apic_ip)
                cls.apic_token = cls.__instance.login()

            if cls.apic_token:
                cls.ep_url = urls.FVEP_URL.format(cls.proto, cls.apic_ip)
                cls.ip_url = urls.FVIP_URL.format(cls.proto, cls.apic_ip)
                cls.epg_url = urls.FVAEPG_URL.format(cls.proto, cls.apic_ip)
            else:
                logger.error(
                    'Could not connect to APIC. Please verify your APIC connection.')
        return cls.__instance

    @time_it
    def login(self):
        """
        Login into APIC using certificate and plugin key

        Returns:
            auth_token -- Authentication token from Cisco APIC API
        """
        user_cert, plugin_key = create_cert_session()
        app_token_payload = {"aaaAppToken": {
            "attributes": {"appName": "CiscoHashiCorp_ConsulExtensionforACI"}}}
        data = json.dumps(app_token_payload)
        pay_load = "POST" + urls.LOGIN_URL_SUFFIX + data
        private_key = load_privatekey(FILETYPE_PEM, plugin_key)
        signed_digest = sign(private_key, pay_load.encode(), 'sha256')
        signature = base64.b64encode(signed_digest).decode()

        token = "APIC-Request-Signature=" + signature + ";"
        token += "APIC-Certificate-Algorithm=v1.0;"
        token += "APIC-Certificate-Fingerprint=fingerprint;"
        token += "APIC-Certificate-DN=" + str(user_cert.dn)
        try:
            response = self.session.post(urls.LOGIN_URL.format(
                self.proto, self.apic_ip), data=data, headers={'Cookie': token}, timeout=10, verify=False)
            status_code = response.status_code
            if status_code == 200 or status_code == 201:
                auth = response.json()
                auth_token = auth['imdata'][0]['aaaLogin']['attributes']['token']
                self.apic_token = auth_token
                return auth_token
            else:
                logger.error(
                    "Login Failed for APIC. Status code {}".format(status_code))
                self.apic_token = None
                return None
        except Exception as e:
            logger.exception('Unable to connect with APIC. Exception: {}'.format(str(e)))
            self.apic_token = None

    @time_it
    def aci_get(self, url, retry=1):
        """Function to  make API call to APIC API
        with provided URL

        Arguments:
            url str -- URL of API to make request
            retry int -- retry count to retry if API fails in first call

        Returns:
            response dict -- JSON response from APIC API call
        """
        try:
            response = self.session.get(
                url, cookies={'APIC-Cookie': self.apic_token}, timeout=90, verify=False)
            status_code = response.status_code
            if status_code == 200 or status_code == 201:
                logger.info('API call success: ' + str(url))
                return response.json()
            elif status_code == 403:
                self.login()
                if retry == 1:
                    self.aci_get(url, 2)
            else:
                logger.info('API call status code: ' + str(status_code))
        except Exception as e:
            logger.exception(
                'ACI call exception: {}, URL: {}'.format(str(e), str(url)))
            return None

    @time_it
    def apic_fetch_ep_data(self, tenant):
        """Function to fetch and parse ep data and return list
        of parsed data.

        Arguments:
            tenant {str} -- Name of tenant to fetch EP data

        Returns:
            list -- list of parsed EP data
        """
        try:
            url = urls.FETCH_EP_DATA_URL.format(self.epg_url, str(tenant))
            response_json = self.aci_get(url)
            if response_json and response_json.get("imdata"):
                data = response_json.get("imdata")
                logger.debug(
                    'Total EPs fetched for Tenant: {} - {} EPs'.format(str(tenant), str(len(data))))
                parsed_ep_data = self.parse_ep_data(data)
                return parsed_ep_data
            return []
        except Exception as e:
            logger.exception(
                'Exception in EP Data API call, Error: {}'.format(str(e)))
            return []

    def parse_ep_data(self, ep_resp):
        """Function to iterate over EP data response using threading

        Arguments:
            ep_resp {list} -- List of EP response from API

        Returns:
            list -- list of dictionary with parsed EP data
        """
        try:
            logger.info('Parsing APIC EP Data!')
            ep_list = []
            future_list = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=APIC_THREAD_POOL) as executor:
                for item in ep_resp:
                    future = executor.submit(
                        self.parse_and_return_ep_data, item)
                    future_list.append(future)
                for future in concurrent.futures.as_completed(future_list):
                    data = future.result()
                    ep_list.extend(data)
            return ep_list
        except Exception as e:
            logger.exception(
                'Exception in Parsing EP Data API call, Error: {}'.format(str(e)))
            return []

    def parse_and_return_ep_data(self, item):
        """Function to Parse data of EP

        Arguments:
            item {dict} -- Single response of EP data

        Returns:
            dict -- Parsed EP data
        """
        data_list = []
        data = {}
        ep_attr = item.get('fvCEp').get('attributes')
        data['dn'] = ep_attr.get('dn')
        data['learning_src'] = ep_attr.get("lcC")
        data['tenant'] = data['dn'].split('tn-')[1].split('/')[0]
        data['mac'] = ep_attr.get("mac")
        data['encap'] = ep_attr.get("encap")
        data['multi_cast_addr'] = ep_attr.get("mcastAddr")
        if data['multi_cast_addr'] == "not-applicable":
            data['multi_cast_addr'] = "---"
        ep_child_attr = item.get('fvCEp').get('children')
        ep_info = self.get_ep_info(ep_child_attr)

        for each in AciUtils.get_ip_mac_list(item):
            data['ip'], data['is_cep'] = each  # TODO: if mac, then add ''
            data.update(ep_info)
            data_list.append(copy.deepcopy(data))
        return data_list

    def get_ep_info(self, ep_children_list):

        ep_info = {
            "controller": "",
            "hosting_servername": "",
            "interfaces": "",
            "vm_name": "",
            "vmm_domain": ""
        }

        interface_list = []
        for ep_child in ep_children_list:
            if "fvRsHyper" in ep_child:
                ep_info["controller"], ep_info["hosting_servername"] = self.get_controller_and_hosting_server(
                    ep_child)

            if "fvRsCEpToPathEp" in ep_child:
                interface = self.get_interface(ep_child)
                interface_list.append(interface)
                ep_info.update({"interfaces": interface_list})

            if "fvRsToVm" in ep_child:
                ep_info['vmm_domain'], ep_info['vm_name'] = self.get_vm_domain_and_name(
                    ep_child)

        return ep_info

    def get_vm_domain_and_name(self, ep_child):
        """Function to ger VM name and VM domain fro EP response

        Arguments:
            ep_child {dict} -- Children of EP API response

        Returns:
            str -- VM name and VM domain name
        """
        tdn_dom = str(ep_child['fvRsToVm']['attributes']['tDn'])
        vmm_dom = str(tdn_dom.split("ctrlr-[")[1].split(']-')[0])
        tdn = str(ep_child['fvRsToVm']['attributes']['tDn'])
        vm_url = self.proto + self.apic_ip + '/api/mo/' + tdn + '.json'
        vm_response = self.aci_get(vm_url)
        vm_response = vm_response.get('imdata')[0]
        vm_name = vm_response['compVm']['attributes']['name']
        if not vm_name:
            vm_name = '---'
        return (vmm_dom, vm_name)

    def get_interface(self, ep_child):
        """Function to get interface for EP

        Arguments:
            ep_child {dict} -- Children of EP API response

        Returns:
            str -- Interface name
        """
        interface = ep_child["fvRsCEpToPathEp"]["attributes"]["tDn"]
        if re.match('topology\/pod-+\d+\/pathgrp-.*', interface):
            pod_number = interface.split("/pod-")[1].split("/")[0]
            node_number = self.get_node_from_interface(interface)
            # The ethernet name is NOT available
            eth_name = str(interface.split(
                "/pathgrp-[")[1].split("]")[0]) + "(vmm)"
            iface_name = "Pod-" + pod_number + "/Node-" + \
                str(node_number) + "/" + eth_name
            return iface_name
        elif re.match('topology\/pod-+\d+\/paths(-\d+)+?\/pathep-.*', interface) or \
                re.match('topology\/pod-+\d+\/protpaths(-\d+)+?\/pathep-.*', interface):
            pod_number = interface.split("/pod-")[1].split("/")[0]
            node_number = self.get_node_from_interface(interface)
            eth_name = interface.split("/pathep-[")[1][0:-1]
            iface_name = "Pod-" + pod_number + "/Node-" + \
                str(node_number) + "/" + eth_name
            return iface_name
        else:
            logger.error(
                "Different format of interface is found: {}".format(interface))
            return interface

    def get_controller_and_hosting_server(self, ep_child):
        """Function to get controller and hosting server from EP response

        Arguments:
            ep_child {dict} -- Children of EP API response

        Returns:
            str -- Controller name and Hosting server name
        """

        ctrlr_name = ""
        hyper_name = ""
        hyper_dn = ep_child.get("fvRsHyper", {}).get(
            "attributes", {}).get("tDn", "")
        try:
            ctrlr_name = re.compile(
                "\/ctrlr-\[.*\]-").split(hyper_dn)[1].split("/")[0]
            hyper_query_string = 'query-target-filter=eq(compHv.dn,"' + \
                hyper_dn + '")'
            hyper_resp = self.get_all_mo_instances(
                "compHv", hyper_query_string)
            if len(hyper_resp) > 0:
                hyper_resp = hyper_resp[0]
                hyper_name = hyper_resp.get("compHv", {}).get(
                    "attributes", {}).get("name", "")
            else:
                logger.error(
                    "Could not get Hosting Server Name using Hypervisor info")

        except Exception as e:
            logger.exception(
                "Exception in get controller and hosting server: " + str(e))

        return (ctrlr_name, hyper_name)

    def get_all_mo_instances(self, mo_class, query_string=""):
        """Function to return All mo instances

        Arguments:
            mo_class {str} -- Name of Mo class
            query_string {str} -- Query String

        Returns:
            dict -- API response of MO Instance API
        """
        try:
            instance_list = []
            url = urls.MO_INSTANCE_URL.format(
                self.proto, self.apic_ip, mo_class)
            if query_string:
                url += "?" + query_string
            response_json = self.aci_get(url)
            if response_json and response_json['imdata']:
                instance_list = response_json['imdata']
            return instance_list
        except Exception as ex:
            logger.exception('Exception while fetching MO: {}, Error: {}'.format(mo_class, str(ex)))
            return []

    @staticmethod
    def get_node_from_interface(interfaces):
        """Function to return node number from interface

        Arguments:
            interfaces {list or str} -- List of interface or interface string

        Returns:
            str -- node number
        """
        node_number = ''
        protpaths = "/protpaths"
        paths = "/paths-"
        pathgrp = "/pathgrp-"
        if isinstance(interfaces, list):
            for interface in interfaces:
                if (interface.find(protpaths) != -1):
                    node_number += str(interface.split(protpaths)
                                       [1].split("/")[0]) + ', '
                elif(interface.find(paths) != -1):
                    node_number += str(interface.split(paths)
                                       [1].split("/")[0]) + ', '
                elif(interface.find(pathgrp) != -1):
                    node_number += str(interface.split(pathgrp)
                                       [1].split("/")[0]) + ', '
                else:
                    logger.error(
                        "Different value of interface found {}".format(interface))
            node_number = node_number[:-2]
        elif isinstance(interfaces, str) or isinstance(interfaces, unicode):
            if (interfaces.find(protpaths) != -1):
                node_number += str(interfaces.split(protpaths)
                                   [1].split("/")[0])
            elif(interfaces.find(paths) != -1):
                node_number += str(interfaces.split(paths)[1].split("/")[0])
            elif(interfaces.find(pathgrp) != -1):
                node_number += str(interfaces.split(pathgrp)[1].split("/")[0])
            else:
                logger.error(
                    "Different value of interface found {}".format(interfaces))
        return node_number

    @time_it
    def apic_fetch_epg_data(self, tenant):
        """Function to fetch EPGs data from APIC API

        Arguments:
            tenant str -- tenant name for which we want to fetch EPGs data

        Returns:
            dict -- data of EPGs from APIC API call
        """
        try:
            url = urls.FETCH_EPG_DATA_URL.format(self.epg_url, str(tenant))
            response_json = self.aci_get(url)
            if response_json and response_json.get("imdata"):
                data = response_json.get("imdata")
                logger.debug('Total EPGs fetched for Tenant: {} - {} EPGs'.format(str(tenant), str(len(data))))
                parsed_data = self.parse_epg_data(data)
                return parsed_data
            return None
        except Exception as e:
            logger.exception(
                'Exception in EPG Data API call, Error: {}'.format(str(e)))
            return None

    @time_it
    def apic_fetch_bd(self, dn):
        """Function to fetch BD data

        Arguments:
            dn {str} -- dn string

        Returns:
            str -- bd_data from response of FETCH_BD_URL
        """
        try:
            url = urls.FETCH_BD_URL.format(self.proto, self.apic_ip, dn)
            response_json = self.aci_get(url)
            if response_json and response_json.get("imdata"):
                data = response_json.get("imdata")
                bd_data = data[0]['fvRsBd']['attributes']['tnFvBDName']
                return bd_data
            return None
        except Exception as e:
            logger.exception(
                'Exception in BD API call, Error: {}'.format(str(e)))
            return None

    @time_it
    def apic_fetch_vrf(self, dn):
        """Function to fetch VRF detail from dn

        Arguments:
            dn {str} -- dn string

        Returns:
            str -- Vrf data from Response of FETCH_VRF_URL
        """
        try:
            url = urls.FETCH_VRF_URL.format(self.proto, self.apic_ip, dn)
            response_json = self.aci_get(url)
            if response_json and response_json.get("imdata"):
                data = response_json.get("imdata")
                vrf_data = data[0]['fvRsCtx']['attributes']['tnFvCtxName']
                return vrf_data
            return ''
        except Exception as e:
            logger.exception(
                'Exception in VRF API call, Error: {}'.format(str(e)))
            return ''

    @time_it
    def apic_fetch_contract(self, dn):
        """Fetch Contracts for EPG from dn

        Arguments:
            dn {str} -- dn string

        Returns:
            dict -- contract's dictionary
        """
        try:
            url = urls.FETCH_CONTRACT_URL.format(self.proto, self.apic_ip, dn)
            response_json = self.aci_get(url)
            contract_list = []
            mapping_dict = {
                'fvRsCons': "Consumer",
                'fvRsIntraEpg': "IntraEpg",
                'fvRsProv': "Provider",
                'fvRsConsIf': "Consumer Interface",
                'fvRsProtBy': "Taboo"
            }
            if response_json and response_json.get("imdata"):
                data = response_json.get("imdata")
                for child in data:
                    keys = child.keys()
                    if len(keys) > 0:
                        ct_name = child[keys[0]]['attributes']['dn'].split(
                            "/", 4)[4].split("-")[1]
                    else:
                        continue

                    key = str(keys[0])
                    if key in mapping_dict:
                        contract_list.append({mapping_dict.get(key): ct_name})

            contracts_dict = defaultdict(list)
            for contract in contract_list:
                for contract_key, contract_value in contract.iteritems():
                    contracts_dict[contract_key].append(contract_value)

            return contracts_dict
        except Exception as e:
            logger.exception(
                'Exception in Contracts API call,  Error: {}'.format(str(e)))
            return {}

    def get_epg_health(self, dn):
        """Function to get health of EPG from dn

        Arguments:
            dn {str} -- dn string

        Returns:
            str -- Health of EPG
        """
        try:
            url = urls.EPG_HEALTH_URL.format(self.proto, self.apic_ip, dn)
            response = self.aci_get(url)
            health = response['imdata']
            for each in health:
                for key, value in each.iteritems():
                    if str(key) == 'healthInst':
                        return value['attributes']['cur']
            return ''
        except Exception as e:
            logger.exception(
                'Exception in EPG health API call,  Error: {}'.format(str(e)))
            return ''

    def parse_epg_data(self, epg_resp):
        """Function to iterate over API response of EPG data
        using multithreading.

        Arguments:
            epg_resp {list} -- List of EPG data from API

        Returns:
            list -- List of dictionary of parsed EPG data
        """
        logger.info('Stared Parsing APIC EPG Data!')
        parsed_data = []
        future_list = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=APIC_THREAD_POOL) as executor:
            for item in epg_resp:
                future = executor.submit(self.parse_and_return_epg_data, item)
                future_list.append(future)
            for future in concurrent.futures.as_completed(future_list):
                data = future.result()
                parsed_data.append(data)
        return parsed_data

    def parse_and_return_epg_data(self, item):
        """Function to Parse EPG data

        Arguments:
            item {dict} -- EPG data from API

        Returns:
            dict -- Parsed EPG response
        """
        data = {}
        epg_attr = item.get('fvAEPg', {}).get('attributes', {})
        data['dn'] = epg_attr.get('dn')
        data['tenant'] = data['dn'].split('tn-')[1].split('/')[0]
        data['bd'] = self.apic_fetch_bd(data['dn'])
        data['app_profile'] = data['dn'].split('ap-')[1].split('/')[0]
        data['epg'] = epg_attr.get("name")
        data['epg_alias'] = epg_attr.get("nameAlias")
        dn_split = data['dn'].split("/", 4)
        vrf_str = dn_split[0] + '/' + dn_split[1] + '/BD-' + data['bd']
        vrf_data = self.apic_fetch_vrf(vrf_str)
        data['vrf'] = data['tenant'] + "/" + vrf_data
        data['contracts'] = self.apic_fetch_contract(data['dn'])
        data['epg_health'] = self.get_epg_health(data['dn'])
        return data

    @staticmethod
    def get_ip_mac_list(item):
        """Return IP and MAC list from data of EP

        Arguments:
            item {dict} -- data of EP

        Returns:
            list -- list of IP and MAC
        """
        is_cep = False
        is_ip_list = False
        ip_set = []
        is_cep_list = []
        response = []
        for eachip in item.get('fvCEp').get('children'):
            # If first key is 'fvIp' than add IP to list otherwise add mac address
            if eachip.keys()[0] == 'fvIp':
                is_ip_list = True
                ip_set.append(str(eachip.get('fvIp').get('attributes').get('addr')).lower())
                is_cep_list.append(is_cep)

        # Below if condition adds all valid ip and mac to the list
        cep_ip = str(item.get('fvCEp').get('attributes').get('ip')).lower()
        if cep_ip != STATIC_IP:
            is_cep = True
            ip_set.append(cep_ip)
            is_cep_list.append(is_cep)
        elif not is_ip_list:
            ip_set.append(item.get('fvCEp').get('attributes').get('mac').lower())
            is_cep_list.append(is_cep)
        
        for i, value in enumerate(ip_set):
            if value not in ip_set[:i]:
                response.append([value, is_cep_list[i]])
        return response

    @time_it
    def get_ap_epg_faults(self, dn):
        """
        Get Faults from rest API.
        """
        faults_dict = None
        try:
            faults_list = self.get_mo_related_item(dn, urls.FAULTS_QUERY, "")
            faults_dict = AciUtils.get_dict_records(faults_list, "faultRecords")
        except Exception as ex:
            logger.info("Exception while processing Faults : {}".format(ex))
        return faults_dict

    @time_it
    def get_ap_epg_events(self, dn):
        """
        Get Events from rest API.
        """
        events_dict = None
        try:
            events_list = self.get_mo_related_item(dn, urls.EVENTS_QUERY, "")
            events_dict = AciUtils.get_dict_records(events_list, "eventRecords")
        except Exception as ex:
            logger.info("Exception while processing Events : {}".format(ex))
        return events_dict

    @time_it
    def get_ap_epg_audit_logs(self, dn):
        """
        Get Audit logs from rest API.
        """
        audit_logs_dict = None
        try:
            audit_logs_list = self.get_mo_related_item(dn, urls.AUDIT_LOGS_QUERY, "")
            audit_logs_dict = AciUtils.get_dict_records(audit_logs_list, "auditLogRecords")
        except Exception as ex:
            logger.info("Exception while processing Audit logs : " + str(ex))
        return audit_logs_dict

    @time_it
    def get_mo_related_item(self, mo_dn, item_query_string, item_type):
        """
        Common method to get MO related data based on item_type value
        """
        try:
            if item_type == "":
                url = urls.MO_URL.format(self.proto, self.apic_ip, mo_dn, item_query_string)
            elif item_type == "other_url":
                url = "{0}{1}{2}".format(self.proto, self.apic_ip, item_query_string)
            elif item_type == "HealthRecords":
                url = urls.MO_HEALTH_URL.format(self.proto, self.apic_ip, mo_dn)
            elif item_type == "ifConnRecords":
                url = urls.MO_OTHER_URL.format(self.proto, self.apic_ip, mo_dn, item_query_string)

            item_list = []
            response_json = self.aci_get(url)
            if response_json and response_json.get("imdata"):
                item_list = response_json.get("imdata")
            else:
                response_json = self.aci_get(url)
                if response_json and response_json.get("imdata"):
                    item_list = response_json.get("imdata")
            # logger.debug("get mo returns: {}".format(str(item_list)))
            return item_list
        except Exception as ex:
            logger.exception('Exception while fetching EPG item with query string: {} ,\nError: {}'.format(item_query_string, ex))
            logger.exception('Epg Item Url : {}'.format(url))
            return []

    @staticmethod
    def get_dict_records(list_of_records, key):
        records_dict = dict()
        records_dict[key] = list_of_records
        return records_dict

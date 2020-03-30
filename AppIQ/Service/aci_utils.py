__author__ = 'nilayshah'

import requests
import json, base64
import datetime
import urls
from cobra.model.pol import Uni as PolUni
from cobra.model.aaa import UserEp as AaaUserEp
from cobra.model.aaa import AppUser as AaaAppUser
from cobra.model.aaa import UserCert as AaaUserCert
from custom_logger import CustomLogger

try:
    from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, sign
except:
    print "=== could not import openssl crypto ==="

logger = CustomLogger.get_logger("/home/app/log/app.log")

def create_cert_session():
    """
    Create user certificate and session.
    """
    start_time = datetime.datetime.now()
    cert_user = 'Cisco_AppIQ'  # vendor_appname
    plugin_key_file = '/home/app/credentials/plugin.key'  # static generated upon install
    pol_uni = PolUni('')
    aaa_user_ep = AaaUserEp(pol_uni)
    aaa_app_user = AaaAppUser(aaa_user_ep, cert_user)
    aaa_user_cert = AaaUserCert(aaa_app_user, cert_user)

    with open(plugin_key_file, "r") as file:
        plugin_key = file.read()

    end_time =  datetime.datetime.now()
    logger.info("Time for create_cert_session: " + str(end_time - start_time))

    return (aaa_user_cert, plugin_key)


class ACI_Utils(object):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(ACI_Utils, cls).__new__(cls)
            cls.apic_ip = '172.17.0.1'
            cls.session = requests.Session()
            cls.proto = 'https://'
            cls.apic_token = cls.__instance.login()
        
            if not cls.apic_token:
                logger.warning('Connection to APIC failed. Trying http instead...')
                cls.proto = 'http://'
                logger.info(cls.proto)
                logger.info(cls.apic_ip)
                cls.apic_token = cls.__instance.login()
                
            if cls.apic_token:
                cls.ep_url = urls.FVEP_URL.format(cls.proto, cls.apic_ip)
                cls.ip_url = urls.FVIP_URL.format(cls.proto, cls.apic_ip)
                cls.epg_url = urls.FVAEPG_URL.format(cls.proto, cls.apic_ip)
            else:
                logger.error('Could not connect to APIC. Please verify your APIC connection.')
        return cls.__instance


    def login(self):
        """
        Login into APIC using certificate and plugin key
        """
        start_time = datetime.datetime.now()
        global auth_token
        user_cert, plugin_key = create_cert_session()
        app_token_payload = {"aaaAppToken": {"attributes": {"appName": "Cisco_AppIQ"}}}
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
            response = self.session.post(urls.LOGIN_URL.format(self.proto, self.apic_ip), data=data, headers={'Cookie': token},timeout=10, verify=False)
            status_code = response.status_code
            if status_code == 200 or status_code == 201:
                auth = json.loads(response.text)
                auth_token = auth['imdata'][0]['aaaLogin']['attributes']['token']
                return auth_token
            else:
                return None
        except Exception as e:
            logger.exception('Unable to connect with APIC. Exception: '+str(e))
            return None
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for ACI login: " + str(end_time - start_time))


    def ACI_get(self, url, cookie=None):
        """
        Common method to get data from ACI.
        """
        start_time = datetime.datetime.now()
        try:
            response = self.session.get(url, cookies=cookie, verify=False)
            status_code = response.status_code
            if status_code == 200 or status_code == 201:
                return response
            else:
                apic_token = self.login()
                response = self.session.get(url,cookies={'APIC-Cookie': apic_token}, verify=False)
                status_code = response.status_code
                if status_code == 200 or status_code == 201:
                    logger.info('API call success: '+str(url))
                    return response
        except Exception as e:
            logger.exception('ACI call Exception:'+str(e)+', URL:'+str(url))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: Could not connect to APIC database. Error: "+str(e)})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for ACI_get: " + str(end_time - start_time))


    def get_mo_related_item(self, mo_dn, item_query_string, item_type):
        """
        Common method to get MO related data based on item_type value
        """
        start_time = datetime.datetime.now()
        try:
            if item_type == "":
                url = urls.MO_URL.format(self.proto, self.apic_ip, mo_dn, item_query_string)
            elif item_type == "other_url":
                url = "{0}{1}{2}".format(self.proto, self.apic_ip, item_query_string)
            elif item_type == "HealthRecords":
                url = urls.MO_HEALTH_URL.format(self.proto, self.apic_ip, mo_dn)
            elif item_type == "ifConnRecords":
                url = urls.MO_OTHER_URL.format(self.proto, self.apic_ip, mo_dn, item_query_string)

            response = self.ACI_get(url, cookie = {'APIC-Cookie': self.apic_token})
            item_list = ((json.loads(response.text)['imdata']))
            return item_list
        except Exception as ex:
            logger.exception('Exception while fetching EPG item with query string: ' + item_query_string + ',\nError:' + str(ex))
            logger.exception('Epg Item Url : =>' + url)
            return []
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_mo_related_item: " + str(end_time - start_time))


    def get_all_mo_instances(self, mo_class, query_string = ""):
        start_time = datetime.datetime.now()
        try:
            url = urls.MO_INSTANCE_URL.format(self.proto, self.apic_ip, mo_class)
            if (query_string != ""):
                url += "?" + query_string
            response = self.ACI_get(url, cookie = {'APIC-Cookie': self.apic_token})
            instance_list = ((json.loads(response.text)['imdata']))
            return {"status": True, "payload": instance_list}
        except Exception as ex:
            logger.exception('Exception while fetching MO: ' + mo_class + ', Error:' + str(ex))
            return {"status": False, "payload": []}
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_all_mo_instances: " + str(end_time - start_time))


    def get_epg_health(self, tenant, app_profile, epg_name, apic_token=None):
        start_time = datetime.datetime.now()
        try:
            url = urls.EPG_HEALTH_URL.format(self.proto, self.apic_ip, str(tenant), app_profile, epg_name)
            response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            health = ((json.loads(response.text)['imdata']))
            for each in health:
                for key,value in each.iteritems():
                    if str(key) == 'healthInst':
                        return value['attributes']['cur']
        except Exception as e:
            logger.exception('Exception in EPG health API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve EPG Health. Error: "+str(e)})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_epg_health: " + str(end_time - start_time))


    def apic_fetchEPData(self, tenant, apic_token=None):
        start_time = datetime.datetime.now()
        try:
            url = urls.FETCH_EP_DATA_URL.format(self.ip_url, str(tenant))
            response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            response_json = json.loads(response.text)
            data = response_json.get("imdata")
            if data:
                logger.debug('Total EPs fetched for Tenant: '+str(tenant)+' - '+str(len(data))+ 'EPs')
                return data
            return []
        except Exception as e:
            logger.exception('Exception in EP/IP Data API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve EP data. Error: "+str(e)})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for apic_fetchEPData: " + str(end_time - start_time))


    def apic_fetchEPGData(self, tenant, apic_token=None):
        start_time = datetime.datetime.now()
        try:
            url = urls.FETCH_EPG_DATA_URL.format(self.epg_url, str(tenant))
            response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            response_json = json.loads(response.text)
            data = response_json.get("imdata")
            if data:
                logger.debug('Total EPGs fetched for Tenant: '+str(tenant)+' - '+str(len(data))+ 'EPGs')
                return data
            return []
        except Exception as e:
            logger.exception('Exception in EPG Data API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve EPG data. Error: "+str(e)})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for apic_fetchEPGData: " + str(end_time - start_time))


    def apic_fetchBD(self, dn, apic_token=None):
        start_time = datetime.datetime.now()
        try:
            url = urls.FETCH_BD_URL.format(self.proto, self.apic_ip, dn)
            response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            response_json = json.loads(response.text)
            data = response_json.get("imdata")
            if data:
                bd_data = data[0]['fvRsBd']['attributes']['tnFvBDName']
                return bd_data
            return ""
        except Exception as e:
            logger.exception('Exception in BD API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could retrieve BD data. Error: "+str(e)})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for apic_fetchBD: " + str(end_time - start_time))


    def apic_fetchVRF(self, dn, apic_token=None):
        start_time = datetime.datetime.now()
        try:
            url = urls.FETCH_VRF_URL.format(self.proto, self.apic_ip, dn)
            response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            response_json = json.loads(response.text)
            data = response_json.get("imdata")
            if data:
                vrf_data = data[0]['fvRsCtx']['attributes']['tnFvCtxName']
                return vrf_data
            return ""
        except Exception as e:
            logger.exception('Exception in VRF API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve VRF data. Error: "+str(e)})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for apic_fetchVRF: " + str(end_time - start_time))


    def extractCtxName(self, dn):
        """
        Extract ctx name from dn string
        """
        # Example of dn
        # "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-test/cep-00:50:56:92:BA:4A/ip-[20.20.20.10]"
        split_dn = dn.split("/", 4)[4].split("-")
        return split_dn[1]


    def apic_fetchContract(self, dn, apic_token=None):
        start_time = datetime.datetime.now()
        try:
            url = urls.FETCH_CONTRACT_URL.format(self.proto, self.apic_ip, dn)
            response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            response_json = json.loads(response.text)
            data = response_json.get("imdata")
            contract_list = []
            if data:
                for child in data:
                    keys = child.keys()
                    if len(keys) > 0:
                        ct_name = str(self.extractCtxName(child[keys[0]]['attributes']['dn']))
                    else:
                        continue
                    
                    key = str(keys[0])
                    if key == 'fvRsCons':
                        contract_list.append({'Consumer': ct_name})
                    elif key == 'fvRsIntraEpg':
                        contract_list.append({'IntraEpg': ct_name})
                    elif key == 'fvRsProv':
                        contract_list.append({'Provider': ct_name})
                    elif key == 'fvRsConsIf':
                        contract_list.append({'Consumer Interface': ct_name})
                    elif key == 'fvRsProtBy':
                        contract_list.append({'Taboo': ct_name})
                return contract_list
        except Exception as e:
            logger.exception('Exception in Contracts API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve Contracts. Error: "+str(e)})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for apic_fetchContract: " + str(end_time - start_time))


    def parseEPs(self, data, tenant):
        """
        Reads dn, ip and tenant for an fvIp and returns a list of those dictionaries
        """
        response = []
        tenant_str = str(tenant)
        for each in data:
            val = {'dn': str(each['fvIp']['attributes']['dn']), 'IP': str(each['fvIp']['attributes']['addr']),
                   'tenant': tenant_str}
            response.append(val)
        return response


    def apic_parseData(self, ep_resp, apic_token=None):
        start_time = datetime.datetime.now()
        try:
            logger.info('Parsing APIC Data!')
            ep_list = []

            for ep in ep_resp:
                ep_attr = ep['fvCEp']['attributes']
                fviplist = []
                is_ip_list = False
                for eachip in ep['fvCEp']['children']:
                    # If first key is 'fvIp' than add IP to list otherwise add mac address
                    if eachip.keys()[0] == 'fvIp':
                        is_ip_list = True
                        fviplist.append(str(eachip['fvIp']['attributes']['addr']))

                if not is_ip_list:
                    fviplist.append(str(ep['fvCEp']['attributes']['mac']))

                if fviplist: 
                    dn_str = str(ep_attr['dn'])
                    dn_split = dn_str.split("/", 5)
                    bd_str = dn_split[0] + '/' + dn_split[1] + '/' + dn_split[2] + '/' + dn_split[3]
                    bd_data = self.apic_fetchBD(bd_str, apic_token=apic_token)
                    vrf_str = dn_split[0] + '/' + dn_split[1] + '/BD-' + bd_data
                    vrf_data = self.apic_fetchVRF(vrf_str, apic_token=apic_token)
                    vrf_name =  dn_split[1].split('-')[1] + "/" + vrf_data
                    ct_data_list = self.apic_fetchContract(bd_str, apic_token=apic_token)

                    for ip in fviplist:
                        
                        ep_dict = {"AppProfile": '', 'EPG': '', 'CEP-Mac': '', 'IP': '', 'Interfaces': [], 'VM-Name': '', 'BD': '',
                            'VMM-Domain': '', 'Contracts': [], 'VRF':'','dn': '/'.join((dn_str.split('/', 4)[0:4]))}

                        ep_dict.update({'VRF': str(vrf_name)})
                        ep_dict.update({'Contracts': ct_data_list})
                        ep_dict.update({'BD': str(bd_data)})
                        splitString = dn_str.split("/")
                        if "." in ip:
                            ep_dict.update({"IP": str(ip)})
                        for eachSplit in splitString:
                            if "-" in eachSplit:
                                epSplit = eachSplit.split("-", 1)
                                if epSplit[0] == "ap":
                                    ep_dict.update({"AppProfile": str(epSplit[1])})
                                elif epSplit[0] == "epg":
                                    ep_dict.update({"EPG": str(epSplit[1])})
                                elif epSplit[0] == "cep":
                                    ep_dict.update({"CEP-Mac": str(epSplit[1])})
                        # ep_dict.update({'IP': str(ep_attr['ip'])})
                        ep_child_attr = ep['fvCEp']['children']
                        path_list = []
                        for child in ep_child_attr:
                            if str(child.keys()[0]) == 'fvRsCEpToPathEp':
                                path_list.append(str(child['fvRsCEpToPathEp']['attributes']['tDn']))
                            
                            if str(child.keys()[0]) == 'fvRsToVm':
                                tDn_dom = str(child['fvRsToVm']['attributes']['tDn'])
                                vmmDom = str(tDn_dom.split("ctrlr-[")[1].split(']-')[0])
                                
                                ep_dict.update({'VMM-Domain': vmmDom})
                                tDn = str(child['fvRsToVm']['attributes']['tDn'])
                                vm_url = self.proto + self.apic_ip + '/api/mo/' + tDn + '.json'
                                vm_response = self.ACI_get(vm_url,cookie={'APIC-Cookie': apic_token})

                                vm_name = json.loads(vm_response.text)['imdata'][0]['compVm']['attributes']['name']

                                if not vm_name:
                                    vm_name = 'EP-'+str(ep['fvCEp']['attributes']['name'])
                                ep_dict.update({'VM-Name': str(vm_name)})
                            else:
                                ep_dict.update({'VMM-Domain':'None'})
                                ep_dict.update({'VM-Name':'EP-'+str(ep['fvCEp']['attributes']['name'])})
                            ep_dict.update({'Interfaces': path_list})
                        ep_list.append(ep_dict)
            return ep_list
        except Exception as e:
            logger.exception('Exeption in ACI Parsing Data, Error: '+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not parse APIC data. Error: "+str(e)})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for apic_parseData: " + str(end_time - start_time))


    def check_unicast_routing(self, bd):
        """
        Get unicast routing value for given bd. It returns "Yes" if enabled.
        """
        url = urls.CHECK_UNICAST_URL.format(self.proto, self.apic_ip, str(bd))
        response = self.ACI_get(url, cookie = {'APIC-Cookie': self.apic_token})
        unicast_route = ""
        try:
            if json.loads(response.text):
                for fvcep in json.loads(response.text)['imdata']:
                    unicast_route = fvcep["fvBD"]["attributes"]["unicastRoute"]
            return unicast_route
        except Exception as e:
            logger.exception("Exception occured while checking unicast routing:"+str(e))
            return ""


    def fetch_ep_for_mac(self, mac):
        """
        Fetach ep value for given mac
        """
        url = urls.FETCH_EP_MAC_URL.format(self.proto, self.apic_ip, mac)
        response = self.ACI_get(url, cookie = {'APIC-Cookie': self.apic_token})
        return_val = ""
        try:
            if json.loads(response.text):
                for fvcep in json.loads(response.text)['imdata']:
                    dn = fvcep["fvCEp"]["attributes"]["dn"]
                    dn_final = dn.split("/")[0:-1]
                    counter = 0
                    for dn_split in dn_final:
                        if counter == 0:
                            return_val += str(dn_split)
                            counter += 1
                        else:
                            return_val += "/"+str(dn_split)
        except Exception as e:
            logger.exception("Exception occured while fetching ep for mac:"+str(e))
        return return_val


    def get_unicast_routing(self, mac):
        """
        Get unicast routing value for given mac.
        If unicast routing is enabled then return true and dn.
        Else return False and None.
        """
        try:
            apic_token = self.apic_token
            dn = self.fetch_ep_for_mac(mac)
            bd = self.apic_fetchBD(dn, apic_token)
            check = self.check_unicast_routing(bd)
            if check == "yes":
                return True, dn
        except Exception as e:
            logger.exception("Exception occured while get unicast routing:"+str(e))
        return False, None


    def main(self, tenant):
        start_time = datetime.datetime.now()
        try:
            auth_token = self.login()
            logger.info('APIC Login success!')
            epg_data = self.apic_fetchEPGData(tenant, apic_token=auth_token)
            parse_data = self.apic_parseData(epg_data,apic_token=auth_token)
            return parse_data
        except Exception as e:
            logger.exception('Exception in ACI Local Main, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve ACI objects. Error: "+str(e)})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for ACI MAIN: " + str(end_time - start_time))


    def get_dict_records(self, list_of_records, key):
        records_dict = dict()
        records_dict[key] = list_of_records
        return records_dict


    def get_ap_epg_audit_logs(self, timeStamp, dn):
        """
        Get Audit logs from rest API.
        """
        start_time = datetime.datetime.now()
        audit_logs_dict = None
        try:
            audit_logs_list = self.get_mo_related_item(dn, urls.AUDIT_LOGS_QUERY, "")
            audit_logs_dict = self.get_dict_records(audit_logs_list, "auditLogRecords")
        except Exception as ex:
            logger.info("Exception while processing Audit logs : " + str(ex))
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time taken for get_ap_epg_audit_logs: " + str(end_time - start_time))
        return audit_logs_dict


    def get_ap_epg_events(self, timeStamp, dn):
        """
        Get Events from rest API.
        """
        start_time = datetime.datetime.now()
        events_dict = None
        try:
            events_list = self.get_mo_related_item(dn, urls.EVENTS_QUERY, "")
            events_dict = self.get_dict_records(events_list, "eventRecords")
        except Exception as ex:
            logger.info("Exception while processing Events : " + str(ex))
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time taken for get_ap_epg_events: " + str(end_time - start_time))
        return events_dict


    def get_ap_epg_faults(self, timeStamp, dn):
        """
        Get Faults from rest API.
        """
        start_time = datetime.datetime.now()
        faults_dict = None
        try:
            faults_list = self.get_mo_related_item(dn, urls.FAULTS_QUERY, "")
            faults_dict = self.get_dict_records(faults_list, "faultRecords")
        except Exception as ex:
            logger.info("Exception while processing Faults : " + str(ex))
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time taken for get_ap_epg_faults: " + str(end_time - start_time))
        return faults_dict

__author__ = 'nilayshah'

import json, time, os
import socket
import re
import datetime
import aci_utils
import appd_utils
import alchemy as database
import consul_generate_d3 as d3
import RecommendedDNObjects as Recommend
from flask import Flask
from multiprocessing import Process, Value
from custom_logger import CustomLogger
import consul_merge # TODO: 
import requests

app = Flask(__name__, template_folder="../UIAssets", static_folder="../UIAssets/public")
app.debug = True

logger = CustomLogger.get_logger("/home/app/log/app.log")

database_object = database.Database()
d3Object = d3.generateD3Dict()
credintial_file_path = '/home/app/data/credentials.json'


def get_instance_name():
    """
    Get instance name from file.
    """
    file_exists = os.path.isfile(credintial_file_path)
    instance_name = "N/A"
    if file_exists:
        try:
            with open(credintial_file_path, 'r') as creds:
                creds = json.load(creds)
                instance_name = str(str(creds['appd_ip']).split('//')[1])
        except:
            instance_name = "N/A"
    else:
        instance_name = "N/A"
    return instance_name


@app.route('/check.json', methods=['GET', 'POST'])
def checkFile():
    start_time = datetime.datetime.now()
    logger.info('Checking if File Exists')
    file_exists = os.path.isfile(credintial_file_path)
    if file_exists:
        try:
            with open(credintial_file_path, 'r') as creds:
                app_creds = json.load(creds)
                appd_ip = app_creds.get("appd_ip")
                appd_port = app_creds.get("appd_port")
                appd_user = app_creds.get("appd_user")
                appd_account = app_creds.get("appd_account")
                appd_pw = app_creds.get("appd_pw")
            appd_object = appd_utils.AppD(appd_ip, appd_port, appd_user, appd_account, appd_pw)
            status = appd_object.check_connection()
            if status == 200 or status == 201:
                return json.dumps({"payload": "Signed in", "status_code": "200", "message": "OK"})
            else:
                return json.dumps({"payload": "Not signed in", "status_code": str(status),
                                   "message": "Exited with code: " + str(
                                       status) + ". Please verify AppDynamics connection"})
        except Exception as e:
            logger.exception("Error while check file! Error:" + str(e))
            return json.dumps({"payload": "Not logged in", "status_code": "300",
                               "message": "Please re-configure AppDynamics Controller!"})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for checkFile: " + str(end_time - start_time))
    else:
        end_time =  datetime.datetime.now()
        logger.error("Time for checkFile File NOT found: " + str(end_time - start_time))
        
        return json.dumps({"payload": "File does not exists", "status_code": "300",
                           "message": "AppDynamics is not configured. Please login!"})    


def parse_host(host):
    """
    Returns ip for host.
    """
    try:
        parsed_host = socket.gethostbyname(host)
        if parsed_host:
            return host
    except:
        return ""


@app.route('/login.json', methods=['GET', 'POST'])
def login(appd_creds):
    start_time = datetime.datetime.now()
    logger.info('Entered Login')
    host = str(appd_creds.get("appd_ip"))
    appd_port = str(appd_creds.get("appd_port"))
    appd_user = str(appd_creds.get("appd_user"))
    appd_account = str(appd_creds.get("appd_account"))
    appd_pw = str(appd_creds.get("appd_pw"))
    if 'http://' in host or 'https://' in host:
        parsed_ip = host.split('://')[1]
        if '/' in parsed_ip:
            ip = parsed_ip.split('/')[0]
        else:
            ip = parsed_ip
        valid_ip = parse_host(ip)
        proto = host.split('://')[0]
        appd_ip = proto + "://"+valid_ip
    else:
        appd_ip = "https://"+parse_host(host)

    appd_object = appd_utils.AppD(appd_ip, appd_port, appd_user, appd_account, appd_pw)
    try:
        login_status = appd_object.check_connection()

        if login_status == 200 or login_status == 201:
            credentials = {'appd_ip': appd_ip, 'appd_port': appd_port, 'appd_user': appd_user, 'appd_account': appd_account,
                        'appd_pw': appd_pw, 'polling_interval': '1'}

            # This is the main process being started.
            Process(target=appd_object.main).start()
            
            with open(credintial_file_path, 'w+') as creds:
                creds.seek(0)
                creds.truncate()
                json.dump(credentials, creds)
                creds.close()
            logger.info('Login Successful!')

            return json.dumps({"payload": "Connection Successful", "status_code": "200",
                               "message": "Credentials Saved!"})  # login_resp
        else:
            logger.error("login failed:"+str(login_status))
            return json.dumps({"payload": "Login to AppDynamics Failed", "status_code": str(login_status),
                                "message": "Login to AppDynamics failed, exited with code: " + str(
                                    login_status) + ". Please verify AppDynamics connection"})

    except Exception as e:
        logger.exception("Error while login! Error:" + str(e))
        return json.dumps({"payload": "Not signed in", "status_code": "300",
                           "message": "An error occured while saving AppDynamics Credentials. Please try again!"})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for LOGIN to APP: " + str(end_time - start_time))


def set_polling_interval(interval):
    """
    Sets the polling interval in AppDynamics config file
    """

    start_time = datetime.datetime.now()
    try:
        if os.path.isfile(credintial_file_path):
            with open(credintial_file_path, "r+") as creds:
                config_data = json.load(creds)
                config_data["polling_interval"] = str(interval)

                creds.seek(0)
                creds.truncate()
                json.dump(config_data, creds)
            
            return "200", "Polling Interval Set!"
        else:
            return "300", "Could not find Configuration File"
    except Exception as err:
        err_msg = "Exception while setting polling Interval : " + str(err)
        logger.error(err_msg)
        return "300", err_msg
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for set_polling_interval: " + str(end_time - start_time))


def get_agent_list():
    agent_list = [
        {
            "ip": "10.23.239.14",
            "port" : "8500",
            "token": ""
        }
    ]
    return agent_list


def apps(tenant):
    start_time = datetime.datetime.now()
    try:
        logger.info("UI Action app.json started")
        
        agent_list = get_agent_list()
        datacenter_dict = {}
        datacenter_set = set()
        datacenter_list = []
        if agent_list:
            for agent in agent_list:
                agent_datacenters = consul_agents_datacenter(agent['ip'], agent['port'], agent['token'])
                for datacenter in agent_datacenters: datacenter_set.add(datacenter)
            logger.info("datacenters : {}".format(datacenter_set))

        for datacenter in datacenter_set:
            datacenter_list.append({"datacenterName" : datacenter, "isViewEnabled" : True})
        datacenter_dict['datacenters'] = datacenter_list

        
        logger.info("UI Action app.json ended")
        return json.dumps({"agentIP":"10.23.239.14", "payload": datacenter_dict, "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Could not fetch applications from databse. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not fetch applications from databse."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for APPS: " + str(end_time - start_time))


def consul_agents_datacenter(agent_ip, agent_port, agent_token):
    """This will return all the datacenters of an agent"""
    try:
        agent_resp = requests.get('http://{}:{}/v1/catalog/datacenters'.format(agent_ip, agent_port))
        datacenter_list = json.loads(agent_resp.content)
        return datacenter_list
    except Exception as e:
        logger.info("Error in loading datacenter list. " + e)
        return []


def get_mapping_dict_target_cluster(mapped_objects):
    """
    return mapping dict from recommended objects
    """
    target = []
    for map_object in mapped_objects:
        for entry in map_object.get('domains'):
            if entry.get('recommended') == True:
                if 'ipaddress' in map_object:
                    logger.debug("Mapping found with ipaddress for "+str(map_object))
                    target.append({'domainName': entry.get('domainName'), 'ipaddress': map_object.get('ipaddress'), 'disabled': False})
                elif 'macaddress' in map_object:
                    logger.debug("Mapping found with macaddress for "+str(map_object))
                    target.append({'domainName': entry.get('domainName'), 'macaddress': map_object.get('macaddress').upper(), 'disabled': False})
    return target

@app.route('/mapping.json', methods=['GET'])
def mapping(tenant, appDId):
    """
    Create mapping dict to display on UI at mapping tab. 
    Source will display at left on UI.
    Traget will display at Right on UI.
    """
    start_time = datetime.datetime.now()
    try:
        appId = str(appDId) + str(tenant)
        mapping_dict = {"source_cluster": [], "target_cluster": []}
        
        # returns the mapping from Mapping Table
        already_mapped_data = database_object.return_mapping(appId)
        rec_object = Recommend.Recommend()
        mapped_objects = rec_object.correlate_aci_appd(tenant, appDId)        

        if not mapped_objects:
            logger.info('Empty Mapping dict for appDId:'+str(appDId))
            return json.dumps({"instanceName":get_instance_name(),"payload": mapping_dict, 
                               "status_code": "200","message": "OK"})

        # Get new mapping based on recommendation which may have new nodes
        current_mapping = get_mapping_dict_target_cluster(mapped_objects)

        if already_mapped_data != None:
            logger.info('Mapping to target cluster already exists')

            #current mapping -> new mapping between aci and appd
            for new_map in current_mapping:
                #already_mapped_data from database right side
                for each_already_mapped in already_mapped_data:
                    key = 'ipaddress'
                    if 'ipaddress' not in each_already_mapped:
                        key = 'macaddress'
                        
                    # Find node which is same as based on recommendation
                    if each_already_mapped.get(key) == new_map.get(key) and each_already_mapped.get('domainName') == new_map.get('domainName'):
                        # If disabled node found in recommended and saved mapping then it should be disabled
                        if each_already_mapped.get('disabled') == True:
                            new_map['disabled'] = True
                        break

        database_object.check_if_exists_and_update('Mapping', [appId, current_mapping])
        mapping_dict['target_cluster'] = [node for node in current_mapping if node.get('disabled') == False]

        for new_object in mapped_objects:
            mapping_dict['source_cluster'].append(new_object)

        return json.dumps({"instanceName":get_instance_name(),
                           "payload": mapping_dict, # {"source_cluster": mapped_objects, "target_cluster": {{dn:IP},{dn:IP}}}
                           "status_code": "200",
                           "message": "OK"})
    except Exception as e:
        logger.exception('Exception in Mapping, Error:'+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not fetch mappings from the database."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for MAPPING: " + str(end_time - start_time))


def parse_mapping_before_save(already_mapped_data, data_list):
    """
    Set disabled value true if user has disabled particular node manually.
    """
    for previous_mapping in already_mapped_data:
        is_node_exist = False
        for current_mapping in data_list:
            key = 'ipaddress'
            if 'ipaddress' not in current_mapping:
                key = 'macaddress'
            if current_mapping.get(key) == previous_mapping.get(key) and current_mapping.get('domainName') == previous_mapping.get('domainName'):
                is_node_exist = True
                break
        
        # Append removed node by user as disabled 
        if not is_node_exist:
            previous_mapping['disabled'] = True
            data_list.append(previous_mapping)

    return data_list
            

@app.route('/saveMapping.json', methods=['POST'])
def save_mapping(appDId, tenant, mappedData):
    """
    Save mapping to database.
    """
    start_time = datetime.datetime.now()
    try:
        appId = str(appDId) + str(tenant)
        logger.info('Saving Mappings for app:'+str(appId))
        mappedData_dict = json.loads(
            (str(mappedData).strip("'<>() ").replace('\'', '\"')))  # new implementation for GraphQL
        data_list = []

        already_mapped_data = database_object.return_mapping(appId)
        for mapping in mappedData_dict:
            if mapping.get('ipaddress') != "":
                data_list.append({'ipaddress': mapping.get('ipaddress'), 'domainName': mapping['domains'][0]['domainName'], 'disabled': False})
            elif mapping.get('macaddress') != "":
                data_list.append({'macaddress': mapping.get('macaddress'), 'domainName': mapping['domains'][0]['domainName'], 'disabled': False})

        if not data_list:
            database_object.delete_entry('Mapping', appId)
            #enable_view(appDId, False)
        else:
            data_list = parse_mapping_before_save(already_mapped_data, data_list)
            database_object.delete_entry('Mapping', appId)
            database_object.check_if_exists_and_update('Mapping', [appId, data_list])
            enable_view(appDId, True)
        database_object.commit_session()
        return json.dumps({"payload": "Saved Mappings", "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Could not save mappings to the database. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not save mappings to the database."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for saveMapping: " + str(end_time - start_time))


def get_faults(dn):
    """
    Get List of Faults from APIC related to the given Modular object.
    """
    start_time = datetime.datetime.utcnow()
    aci_util_obj = aci_utils.ACI_Utils()
    faults_resp = aci_util_obj.get_ap_epg_faults(start_time, dn)

    if faults_resp:
        faults_payload = []
        faults_list = faults_resp.get("faultRecords")
        for fault in faults_list:
            fault_attr = fault.get("faultRecord").get("attributes")
            fault_dict = {
                "code" : fault_attr.get("code"),
                "severity" : fault_attr.get("severity"),
                "affected" : fault_attr.get("affected"),
                "descr" : fault_attr.get("descr"),
                "created" : fault_attr.get("created")
            }
            faults_payload.append(fault_dict)
        return json.dumps({
            "status_code": "200",
            "message": "OK",
            "payload": faults_payload
        })
    else:
        logger.error("Error in fetching Fault List!")
        return json.dumps({
            "status_code": "300",
            "message": "Error while fetching Fault details.",
            "payload": []
        })

def get_events(dn):
    """
    Get List of Events related to the given MO.
    """
    start_time = datetime.datetime.utcnow()
    aci_util_obj = aci_utils.ACI_Utils()
    events_resp = aci_util_obj.get_ap_epg_events(start_time, dn)

    if events_resp:
        events_payload = []
        events_list = events_resp.get("eventRecords")
        for event in events_list:
            event_attr = event.get("eventRecord").get("attributes")
            event_dict = {
                "code" : event_attr.get("code"),
                "severity" : event_attr.get("severity"),
                "affected" : event_attr.get("affected"),
                "descr" : event_attr.get("descr"),
                "created" : event_attr.get("created"),
                "cause" : event_attr.get("cause")
            }
            events_payload.append(event_dict)
        return json.dumps({
            "status_code": "200",
            "message": "OK",
            "payload": events_payload
        })
    else:
        logger.error("Error in fetching Event List!")
        return json.dumps({
            "status_code": "300",
            "message": "Error while fetching Event details.",
            "payload": []
        })

def get_audit_logs(dn):
    """
    Get List of Audit Log Records related to the given MO.
    """

    start_time = datetime.datetime.utcnow()
    aci_util_obj = aci_utils.ACI_Utils()
    audit_logs_resp = aci_util_obj.get_ap_epg_audit_logs(start_time, dn)

    if audit_logs_resp:
        audit_logs_payload = []
        audit_logs_list = audit_logs_resp.get("auditLogRecords")
        for audit_log in audit_logs_list:
            audit_log_attr = audit_log.get("aaaModLR").get("attributes")
            audit_log_dict = {
                "affected" : audit_log_attr.get("affected"),
                "descr" : audit_log_attr.get("descr"),
                "created" : audit_log_attr.get("created"),
                "id" : audit_log_attr.get("id"),
                "action" : audit_log_attr.get("ind"),
                "user" : audit_log_attr.get("user")
            }
            audit_logs_payload.append(audit_log_dict)
        return json.dumps({
            "status_code": "200",
            "message": "OK",
            "payload": audit_logs_payload
        })
    else:
        logger.error("Error in fetching Audit Logs List!")
        return json.dumps({
            "status_code": "300",
            "message": "Error while fetching Audit log details.",
            "payload": []
        })

def get_childrenEp_info(dn, mo_type, ip_list):
    start_time = datetime.datetime.now()
    aci_util_obj = aci_utils.ACI_Utils()
    if mo_type == "ep":
        ip_list = ip_list.split(",")
        ip_query_filter_list = []
        for ip in ip_list:
            ip_query_filter_list.append('eq(fvCEp.ip,"' + ip + '")')
        ip_query_filter = ",".join(ip_query_filter_list)

        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&query-target-filter=or(' + ip_query_filter +')&rsp-subtree=children&rsp-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsVm'
    elif mo_type == "epg":
        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&rsp-subtree=children&rsp-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsVm'

    ep_list = aci_util_obj.get_mo_related_item(dn, ep_info_query_string, "")
    ep_info_list = []
    try:
        for ep in ep_list:
            ep_info_dict = dict()

            ep_children = ep.get("fvCEp").get("children")
            ep_info = get_ep_info(ep_children, aci_util_obj)
            ep_attr = ep.get("fvCEp").get("attributes")

            mcast_addr = ep_attr.get("mcastAddr")
            if mcast_addr == "not-applicable":
                mcast_addr = "---"

            ep_info_dict = {
                "ip" : ep_attr.get("ip"),
                "mac" : ep_attr.get("mac"),
                "mcast_addr" : mcast_addr,
                "learning_source" : ep_attr.get("lcC"),
                "encap" : ep_attr.get("encap"),
                "ep_name" : ep_info.get("ep_name"),
                "hosting_server_name" : ep_info.get("hosting_server_name"),
                "iface_name" : ep_info.get("iface_name"),
                "ctrlr_name" : ep_info.get("ctrlr_name")
            }
            ep_info_list.append(ep_info_dict)
        return json.dumps({
            "status_code": "200",
            "message": "OK",
            "payload": ep_info_list
        })
    except Exception as e:
        logger.exception("Exception while getting Children Ep Info : " + str(e))
        return json.dumps({
            "status_code": "300",
            "message": {'errors':str(e)},
            "payload": []
        })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for get_childrenEp_info: " + str(end_time - start_time))
    

def get_ep_info(ep_children_list, aci_util_obj):

    ep_info = {
        "ctrlr_name" : "",
        "hosting_server_name" : "",
        "iface_name" : "",
        "ep_name" : ""
    }
    
    for ep_child in ep_children_list:
        for child_name in ep_child:
            if child_name == "fvRsHyper":
                hyperDn = ep_child["fvRsHyper"]["attributes"]["tDn"]
                try:
                    ctrlr_name = re.compile("\/ctrlr-\[.*\]-").split(hyperDn)[1].split("/")[0]
                except Exception as e:
                    logger.exception("Exception in EpInfo: " + str(e))
                    ctrlr_name = ""

                hyper_query_string = 'query-target-filter=eq(compHv.dn,"' + hyperDn + '")'
                hyper_resp = aci_util_obj.get_all_mo_instances("compHv", hyper_query_string)

                if hyper_resp.get("status"):
                    if hyper_resp.get("payload"):
                        hyper_name = hyper_resp["payload"][0]["compHv"]["attributes"]["name"]
                    else:
                        logger.error("Could not get Hosting Server Name using Hypervisor info")
                        hyper_name = ""
                else:
                    hyper_name = ""
                ep_info["ctrlr_name"] = ctrlr_name
                ep_info["hosting_server_name"] = hyper_name

            elif child_name == "fvRsCEpToPathEp":
                name = ep_child["fvRsCEpToPathEp"]["attributes"]["tDn"]
                if re.match('topology\/pod-+\d+\/pathgrp-.*',name):
                    pod_number = name.split("/pod-")[1].split("/")[0]
                    node_number = get_node_from_interface(name)
                    #The ethernet name is NOT available
                    eth_name = str(name.split("/pathgrp-[")[1].split("]")[0]) + "(vmm)"
                    iface_name = eth_name
                    ep_info["iface_name"] = iface_name
                elif re.match('topology\/pod-+\d+\/paths(-\d+)+?\/pathep-.*',name):
                    pod_number = name.split("/pod-")[1].split("/")[0]
                    node_number = get_node_from_interface(name)
                    eth_name = name.split("/pathep-[")[1][0:-1]
                    iface_name = "Pod-" + pod_number + "/Node-" + str(node_number) + "/" + eth_name
                    ep_info["iface_name"] = iface_name
                elif re.match('topology\/pod-+\d+\/protpaths(-\d+)+?\/pathep-.*',name):
                    pod_number = name.split("/pod-")[1].split("/")[0]
                    node_number = get_node_from_interface(name)
                    eth_name = name.split("/pathep-[")[1][0:-1]
                    iface_name = "Pod-" + pod_number + "/Node-" + str(node_number) + "/" + eth_name
                    ep_info["iface_name"] = iface_name
                else:
                    logger.error("Different format of interface is found: {}".format(name))
                    raise Exception("Different format of interface is found: {}".format(name))

            elif child_name == "fvRsVm":
                vm_dn = ep_child["fvRsVm"]["attributes"]["tDn"]

                vm_query_string = 'query-target-filter=eq(compVm.dn,"' + vm_dn + '")'
                vm_resp = aci_util_obj.get_all_mo_instances("compVm", vm_query_string)

                if vm_resp.get("status"):
                    if vm_resp.get("payload"):
                        vm_name = vm_resp["payload"][0]["compVm"]["attributes"]["name"]
                    else:
                        logger.error("Could not get Name of EP using VM info")
                        vm_name = ""
                else:
                    vm_name = ""
                ep_info["ep_name"] = vm_name
        
    return ep_info


def get_configured_access_policies(tn, ap, epg):
    start_time = datetime.datetime.now()
    aci_util_obj = aci_utils.ACI_Utils()
    cap_url = "/mqapi2/deployment.query.json?mode=epgtoipg&tn=" + tn + "&ap=" + ap + "&epg=" + epg
    cap_resp = aci_util_obj.get_mo_related_item("", cap_url, "other_url")
    cap_list = []
    try:
        for cap in cap_resp:
            cap_dict = {
                "domain" : "",
                "switch_prof" : "",
                "aep" : "",
                "iface_prof" : "",
                "pc_vpc" : "",
                "node" : "",
                "path_ep" : "",
                "vlan_pool" : ""
            }
            cap_attr = cap["syntheticAccessPolicyInfo"]["attributes"]
            if re.search("/vmmp-",cap_attr["domain"]):
                # Get Domain Name of Configure Access Policy
                cap_vmm_prof = cap_attr["domain"].split("/vmmp-")[1].split("/")[0]
            else:
                logger.error("Attribute {} not found".format("domain"))
                raise Exception("Attribute {} not found".format("domain"))
            if re.search("/dom-",cap_attr["domain"]):
                cap_domain_name = cap_attr["domain"].split("/dom-")[1]
            else:
                logger.error("Attribute {} not found".format("domain"))
                raise Exception("Attribute {} not found".format("domain"))
            cap_dict["domain"] = cap_vmm_prof + "/" + cap_domain_name
            if re.search("/nprof-",cap_attr["nodeP"]):
                cap_dict["switch_prof"] = cap_attr["nodeP"].split("/nprof-")[1]
            else:
                logger.error("Attribute {} not found".format("nodeP"))
                raise Exception("Attribute {} not found".format("nodeP"))
            if re.search("/attentp-",cap_attr["attEntityP"]):
                cap_dict["aep"] = cap_attr["attEntityP"].split("/attentp-")[1]
            else:
                logger.error("Attribute {} not found".format("attEntityP"))
                raise Exception("Attribute {} not found".format("attEntityP"))
            if re.search("/accportprof-",cap_attr["accPortP"]):
                cap_dict["iface_prof"] = cap_attr["accPortP"].split("/accportprof-")[1]
            else:
                logger.error("Attribute {} not found".format("accPortP"))
                raise Exception("Attribute {} not found".format("accPortP"))
            if re.search("/accportgrp-",cap_attr["accBndlGrp"]):
                cap_dict["pc_vpc"] = cap_attr["accBndlGrp"].split("/accportgrp-")[1]
            elif re.search("/accbundle-",cap_attr["accBndlGrp"]):
                cap_dict["pc_vpc"] = cap_attr["accBndlGrp"].split("/accbundle-")[1]
            pc_pvc = re.search('\w+\/\w+\/\w+\/\w+-(.*)',cap_attr["accBndlGrp"])
            if pc_pvc:
                cap_dict["pc_vpc"] = pc_pvc.groups()[0]
            else:
                logger.error("Attribute {} not found".format("accBndlGrp"))
                raise Exception("Attribute {} not found".format("accBndlGrp"))
            cap_dict["node"] = get_node_from_interface(cap_attr["pathEp"])
            if not cap_dict["node"]:
                logger.error("Attribute {} not found".format("node"))
                raise Exception("attribute node not found")
            if re.search("/pathep-",cap_attr["pathEp"]):
                cap_dict["path_ep"] = cap_attr["pathEp"].split("/pathep-")[1][1:-1]
            else:
                logger.error("Attribute {} not found".format("pathEP"))
                raise Exception("Attribute {} not found".format("pathEp"))
            if re.search("/from-",cap_attr["vLanPool"]):
                cap_dict["vlan_pool"] = cap_attr["vLanPool"].split("/from-")[1]
            else:
                logger.error("Attribute {} not found".format("vLanpool"))
                raise Exception("Attribute {} not found".format("vLanpool"))
            cap_list.append(cap_dict)
        
        return json.dumps({
            "status_code": "200",
            "message": "",
            "payload": cap_list
        })
    except Exception as ex:
        return json.dumps({
            "status_code": "300",
            "message": {'errors':str(ex)},
            "payload": []
        })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for get_configured_access_policies: " + str(end_time - start_time))


def get_subnets(dn):
    """
    Gets the Subnets Information for an EPG
    """
    start_time = datetime.datetime.now()
    aci_util_obj = aci_utils.ACI_Utils()
    subnet_query_string = "query-target=children&target-subtree-class=fvSubnet"
    subnet_resp = aci_util_obj.get_mo_related_item(dn, subnet_query_string, "")
    subnet_list = []
    try:
        for subnet in subnet_resp:
            subnet_dict = {
                "ip" : "",
                "to_epg" : "",
                "epg_alias" : ""
            }
            subnet_attr = subnet.get("fvSubnet").get("attributes")
            subnet_dict["ip"] = subnet_attr["ip"]
            subnet_list.append(subnet_dict)
        
        return json.dumps({
            "status_code": "200",
            "message": "",
            "payload": subnet_list
        })
    except Exception as ex:
        return json.dumps({
            "status_code": "300",
            "message": str(ex),
            "payload": []
        })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for one: " + str(end_time - start_time))


def get_to_Epg_traffic(epg_dn):
    """
    Gets the Traffic Details from the given EPG to other EPGs
    """

    start_time = datetime.datetime.now()
    aci_util_obj = aci_utils.ACI_Utils()
    epg_traffic_query_string = 'query-target-filter=eq(vzFromEPg.epgDn,"' + epg_dn + '")&rsp-subtree=full&rsp-subtree-class=vzToEPg,vzRsRFltAtt,vzCreatedBy&rsp-subtree-include=required'
    epg_traffic_resp = aci_util_obj.get_all_mo_instances("vzFromEPg", epg_traffic_query_string)
    if epg_traffic_resp["status"]:
        epg_traffic_resp = epg_traffic_resp["payload"]

        from_epg_dn = epg_dn
        
        to_epg_traffic_list = []
        to_epg_traffic_set = set()
        
        try:
            for epg_traffic in epg_traffic_resp:
                to_epg_children = epg_traffic["vzFromEPg"]["children"]

                for to_epg_child in to_epg_children:

                    vz_to_epg_child = to_epg_child["vzToEPg"]

                    to_epg_dn = vz_to_epg_child["attributes"]["epgDn"]
                    if re.search("/tn-",to_epg_dn):
                        tn = to_epg_dn.split("/tn-")[1].split("/")[0]
                    else :
                        logger.error("attribute 'tn' not found in epgDn")
                        raise Exception("attribute 'tn' not found in epgDn")
                    if re.search("/ap-",to_epg_dn):
                        ap = to_epg_dn.split("/ap-")[1].split("/")[0]
                    elif re.match('(\w+|-)\/(\w+|-)+\/\w+-(.*)',to_epg_dn):
                        full_ap = to_epg_dn.split('/')[2] 
                        ap = re.split('\w+-(.*)',full_ap)[1]
                    else :
                        logger.error("attribute 'ap' not found in epgDn")
                        raise Exception("attribute 'ap' not found in epgDn")
                    if re.search("/epg-",to_epg_dn):
                        epg = to_epg_dn.split("/epg-")[1]
                    elif re.match('(\w+|-)\/(\w+|-)+\/\w+-(.*)',to_epg_dn):
                        full_epg = to_epg_dn.split('/')[3] 
                        epg = re.split('\w+-(.*)',full_epg)[1]
                    else :
                        logger.error("attribute 'epg' not found in epgDn")
                        raise Exception("attribute 'epg' not found in epgDn")
                    parsed_to_epg_dn = tn + "/" + ap + "/" + epg

                    flt_attr_children = vz_to_epg_child["children"]

                    for flt_attr in flt_attr_children:
                        to_epg_traffic_dict = {
                            "to_epg" : "",
                            "contract_subj" : "",
                            "filter_list" : [],
                            "ingr_pkts" : "",
                            "egr_pkts" : "",
                            "epg_alias" : "",
                            "contract_type" : ""
                        }

                        to_epg_traffic_dict["to_epg"] = parsed_to_epg_dn

                        flt_attr_child = flt_attr["vzRsRFltAtt"]
                        flt_attr_tdn = flt_attr_child["attributes"]["tDn"]

                        traffic_id = parsed_to_epg_dn + "||" + flt_attr_tdn

                        # Check if we have already encountered the filter for a particular destination EPG
                        if traffic_id in to_epg_traffic_set:
                            to_epg_traffic_set.add(traffic_id)
                            continue
                        if re.search("/fp-",flt_attr_tdn):
                            flt_name = flt_attr_tdn.split("/fp-")[1]
                        else:
                            logger.error("filter not found")
                            raise Exception("filter not found")
                        flt_attr_subj_dn = flt_attr_child["children"][0]["vzCreatedBy"]["attributes"]["ownerDn"]
                        if re.search("/rssubjFiltAtt-",flt_attr_subj_dn):
                            subj_dn = flt_attr_subj_dn.split("/rssubjFiltAtt-")[0]
                        else:
                            logger.error("filter attribute subject not found")
                            raise Exception("filter attribute subject not found")
                        if re.search("/tn-",flt_attr_subj_dn):
                            subj_tn = flt_attr_subj_dn.split("/tn-")[1].split("/")[0]
                        else:
                            logger.error("filter attribute subject dn not found")
                            raise Exception("filter attribute subject dn not found")
                        
                        if re.search("/brc-",flt_attr_subj_dn):
                            subj_ctrlr = flt_attr_subj_dn.split("/brc-")[1].split("/")[0]
                        else:
                            logger.error("filter attribute ctrlr not found")
                            raise Exception("filter attribute ctrlr not found")
                        if re.search("/subj-",flt_attr_subj_dn):
                            subj_name = flt_attr_subj_dn.split("/subj-")[1].split("/")[0]
                        else:
                            logger.error("filter attribute subj_name not found")
                            raise Exception("filter attribute subj_name not found")
                        
                        contract_subject = subj_tn + "/" + subj_ctrlr + "/" + subj_name
                        flt_list = get_filter_list(flt_attr_tdn, aci_util_obj)
                        ingr_pkts, egr_pkts = getIngressEgress(from_epg_dn, to_epg_dn, subj_dn, flt_name, aci_util_obj)
                                            
                        to_epg_traffic_dict["contract_subj"] = contract_subject
                        to_epg_traffic_dict["filter_list"] = flt_list
                        to_epg_traffic_dict["ingr_pkts"] = ingr_pkts
                        to_epg_traffic_dict["egr_pkts"] = egr_pkts

                        to_epg_traffic_set.add(traffic_id)
                        to_epg_traffic_list.append(to_epg_traffic_dict)

            return json.dumps({
                "status_code": "200",
                "message": "",
                "payload": to_epg_traffic_list
            })

        except Exception as ex:
            logger.exception("Exception while fetching To EPG Traffic List : \n" + str(ex))
            
            return json.dumps({
                "status_code": "300",
                "message": {'errors':str(ex)},
                "payload": []
            })
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_to_Epg_traffic: " + str(end_time - start_time))
    else:
        logger.error("Could not get Traffic Data related to EPG")
        end_time =  datetime.datetime.now()
        logger.info("Time for get_to_Epg_traffic: " + str(end_time - start_time))
        return json.dumps({
            "status_code": "300",
            "message": "Exception while fetching Traffic Data related to EPG",
            "payload": []
        })


def getIngressEgress(from_epg_dn, to_epg_dn, subj_dn, flt_name, aci_util_obj):
    """
    Returns the Cumulative Ingress and Egress packets information for the last 15 minutes
    """
    start_time = datetime.datetime.now()
    cur_aggr_stats_query_url = "/api/node/mo/" + from_epg_dn + "/to-[" + to_epg_dn + "]-subj-[" + subj_dn + "]-flt-" + flt_name + "/CDactrlRuleHitAg15min.json"
    cur_aggr_stats_list = aci_util_obj.get_mo_related_item("", cur_aggr_stats_query_url, "other_url")

    if cur_aggr_stats_list:
        cur_ag_stat_attr = cur_aggr_stats_list[0]["actrlRuleHitAg15min"]["attributes"]
        ingr_pkts = cur_ag_stat_attr.get("ingrPktsCum")
        egr_pkts = cur_ag_stat_attr.get("egrPktsCum")
        end_time =  datetime.datetime.now()
        logger.info("Time for getIngressEgress: " + str(end_time - start_time))
        return ingr_pkts, egr_pkts
    else:
        end_time =  datetime.datetime.now()
        logger.info("Time for getIngressEgress: " + str(end_time - start_time))
        return "0", "0"


def get_filter_list(flt_dn, aci_util_obj):
    """
    Returns the list of filters for a given destination EPG
    """
    start_time = datetime.datetime.now()
    flt_list = []
    flt_entry_query_string = "query-target=children&target-subtree-class=vzRFltE"
    flt_entries = aci_util_obj.get_mo_related_item(flt_dn, flt_entry_query_string, "")

    for flt_entry in flt_entries:
        flt_attr = flt_entry["vzRFltE"]["attributes"]
        
        ether_type = flt_attr["etherT"]

        if ether_type == "unspecified":
            flt_list.append("*")
            continue
        
        protocol = flt_attr["prot"] if flt_attr["prot"] != "unspecified" else "*"
        src_from_port = flt_attr["sFromPort"]
        src_to_port = flt_attr["sToPort"]
        dest_from_port = flt_attr["dFromPort"]
        dest_to_port = flt_attr["dToPort"]

        # If Source From Port or Source To port is unspecified, set value of source to "*"
        if src_from_port == "unspecified" or src_to_port == "unspecified":
            src_str = "*"
        else:
            src_str = src_from_port + "-" + src_to_port
        
        # If Destination From Port or Destination To port is unspecified, set value of destination to "*"
        if dest_from_port == "unspecified" or dest_to_port == "unspecified":
            dest_str = "*"
        else:
            dest_str = dest_from_port + "-" + dest_to_port

        flt_str = ether_type + ":" + protocol + ":" + src_str + " to " +dest_str

        flt_list.append(flt_str)

    
    end_time =  datetime.datetime.now()
    logger.info("Time for get_filter_list: " + str(end_time - start_time))
    return flt_list


# This will be called from the UI - after the Mappings are completed
@app.route('/enableView.json')
def enable_view(appid, bool):
    try:
        return database_object.enable_view_update(appid, bool)
    except Exception as e:
        logger.exception("Error while enabling view for app:" + str(appid) + ". Error:" + str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not enable the view."})


@app.route('/run.json')
def tree(tenant, appId):
    """
    Get tree view of nodes.
    """
    try:
        start_time = datetime.datetime.now()
        logger.info('UI Action TREE started')
        aci_util_obj = aci_utils.ACI_Utils()
        mapping(tenant, appId)
        merged_data = consul_merge.merge_aci_consul(tenant, 'data_centre', aci_util_obj)
        response = json.dumps(d3Object.generate_d3_compatible_dict(merged_data))
        return json.dumps({"agentIP":"10.23.239.14","payload": response, "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Error while building tree from run.json for app:" + str(appId) + ". Error:" + str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the View."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for TREE: " + str(end_time - start_time))


def merge_aci_appd(tenant, appDId, aci_util_obj):
    """
    Merge Aci data with App dynamics data fetched from DB
    """
    start_time = datetime.datetime.now()
    logger.info('Merging objects for Tenant:'+str(tenant)+', app_id'+str(appDId))
    try:
        aci_data = aci_util_obj.main(tenant)

        merge_list = []
        merged_eps = []
        total_epg_count = {}
        merged_epg_count = {}
        non_merged_ep_dict = {}

        appId = str(appDId) + str(tenant)
        mappings = database_object.return_mapping(appId)

        logger.debug("ACI Data: {}".format(str(aci_data)))
        logger.debug("Mapping Data: {}".format(str(mappings)))

        for aci in aci_data:
            if aci['EPG'] not in total_epg_count.keys():
                total_epg_count[aci['EPG']] = 1
            else:
                total_epg_count[aci['EPG']] += 1

            if mappings:
                mappings = [node for node in mappings if node.get('disabled') == False]
                for each in mappings:
                    # Check with IP or Mac 
                    mapping_key = 'ipaddress'
                    aci_key = 'IP'
                    if 'macaddress' in each:
                        mapping_key = 'macaddress'
                        aci_key = 'CEP-Mac'
                    
                    if aci.get(aci_key) and each.get(mapping_key) and aci.get(aci_key).upper() == each.get(mapping_key).upper() and each['domainName'] == str(aci['dn']):
                        # Change based on IP and Mac
                        appd_data = get_appD(appDId, aci.get(aci_key).upper())
                        if appd_data:
                            for each in appd_data:
                                each.update(aci)
                                if aci_key == 'CEP-Mac':
                                    each.update({'Machine Agent Enabled': 'True'})
                                merge_list.append(each)
                                if aci[aci_key] not in merged_eps:
                                    merged_eps.append(aci[aci_key])
                                    if aci['EPG'] not in merged_epg_count:
                                        merged_epg_count[aci['EPG']] = [aci[aci_key]]
                                    else:
                                        merged_epg_count[aci['EPG']].append(aci[aci_key])

        for aci in aci_data:
            if aci['IP'] in merged_eps or aci['CEP-Mac'] in merged_eps:
                continue
            else:
                if aci['EPG'] not in non_merged_ep_dict:
                    non_merged_ep_dict[aci['EPG']] = {aci['CEP-Mac']: str(aci['IP'])}
                else:
                    # TODO: Check below if conditions
                    if not non_merged_ep_dict[aci['EPG']]:
                        non_merged_ep_dict[aci['EPG']] = {}

                    if aci['CEP-Mac'] in non_merged_ep_dict[aci['EPG']].keys():
                        multipleips = non_merged_ep_dict[aci['EPG']][aci['CEP-Mac']]+", " + str(aci['IP'])
                        non_merged_ep_dict[aci['EPG']].update({aci['CEP-Mac']: multipleips})
                    else:
                        non_merged_ep_dict[aci['EPG']].update({aci['CEP-Mac']: str(aci['IP'])})

        final_non_merged = {}
        if non_merged_ep_dict:
            for key,value in non_merged_ep_dict.items():
                if not value:
                    continue
                final_non_merged[key] = value

        fractions = {}
        if total_epg_count:
            for epg in total_epg_count.keys():
                #fractions[epg] = str(len(merged_epg_count.get(epg, [])))+"/"+str(total_epg_count.get(epg, []))
                un_map_eps = int(total_epg_count.get(epg, [])) - len(merged_epg_count.get(epg, []))
                fractions[epg] = int(un_map_eps)
                logger.info('Total Unmapped Eps (Inactive):'+str(un_map_eps)+" - "+str(epg))

        updated_merged_list = []
        if fractions:
            for key, value in fractions.iteritems():
                for each in merge_list:
                    if key == each['EPG']:
                        each['fraction'] = value
                        each['Non_IPs'] = final_non_merged.get(key, {})
                        updated_merged_list.append(each)

        final_list = []
        for each in updated_merged_list:
            if 'fraction' not in each.keys():
                each['fraction'] = '0'
                each['Non_IPs'] = {}
            final_list.append(each)
        logger.info('Merge complete. Total objects correlated: ' + str(len(final_list)))

        return final_list #updated_merged_list#,total_epg_count # TBD for returning values
    except Exception as e:
        logger.exception("Error while merge_aci_data : "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the Merge ACI and AppDynamics objects."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for merge_aci_appd: " + str(end_time - start_time))


def get_appD(appId, ep):
    """
    Get application data from App dynamics for given application Id
    """
    start_time = datetime.datetime.now()
    try:
        app = database_object.return_application('appId', appId)
        tiers = database_object.return_tiers('appId', appId)
        appd_list = []

        for application in app:
            hev = database_object.return_health_violations('appId', application.appId)
            for tier in tiers:
                seps = database_object.return_service_endpoints('tierId', tier.tierId)
                sepList = []
                for sep in seps:
                    if isinstance(sep.sep, dict):
                        sepList.append(sep.sep)
                hevList = []
                hevs = database_object.return_health_violations('tierId', tier.tierId)
                for hev in hevs:
                    if (int(hev.violationId) >= 0):
                        hevList.append(
                            {
                                "Violation Id": (hev.violationId),
                                "Start Time": str(hev.startTime),
                                'Affected Object': str(hev.businessTransaction),
                                'Description': str(hev.description),
                                'Severity': str(hev.severity),
                                'End Time': str(hev.endTime),
                                'Status': str(hev.status),
                                'Evaluation States': hev.evaluationStates["evaluationStates"]
                            }
                        )
                nodes = database_object.return_nodes('tierId', tier.tierId)
                for node in nodes:
                    if ep in node.ipAddress:
                        appd_list.append(
                                { 
                                    'appId': application.appId, 
                                    'appName': str(application.appName), 
                                    'appHealth': str(application.appMetrics['data'][0]['severitySummary']['performanceState']),
                                    'tierId': tier.tierId, 'tierName': str(tier.tierName),
                                    'tierHealth': str(tier.tierHealth),
                                    'nodeId': node.nodeId,
                                    'nodeName': str(node.nodeName),
                                    'nodeHealth': str(node.nodeHealth),
                                    'ipAddressList': node.ipAddress,
                                    'serviceEndpoints': sepList, 
                                    'tierViolations': hevList 
                                })
                    elif ep in node.macAddress:
                        appd_list.append(
                                { 
                                    'appId': application.appId, 
                                    'appName': str(application.appName), 
                                    'appHealth': str(application.appMetrics['data'][0]['severitySummary']['performanceState']),
                                    'tierId': tier.tierId, 'tierName': str(tier.tierName),
                                    'tierHealth': str(tier.tierHealth),
                                    'nodeId': node.nodeId,
                                    'nodeName': str(node.nodeName),
                                    'nodeHealth': str(node.nodeHealth),
                                    'macAddressList': node.macAddress,
                                    'serviceEndpoints': sepList, 
                                    'tierViolations': hevList
                                })                        
        return appd_list
    except Exception as e:
        logger.exception("Could not load the View. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the View."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for get_appD: " + str(end_time - start_time))


@app.route('/details.json')  # Will take tenantname and appId as arguments
def get_details(tenant, appId):
    try:
        start_time = datetime.datetime.now()
        logger.info("UI Action details.json started")
        
        # consul_details can be merged with this function,
        # or put in a parsing/ class
        details_list = consul_details(tenant)
        logger.info("UI Action details.json ended: " + str(details_list))
        # details = [dict(t) for t in set([tuple(d.items()) for d in details_list])]
        return json.dumps({"agentIP":"10.23.239.14","payload": details_list, "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Could not load the Details. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the Details."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for GET_DETAILS: " + str(end_time - start_time))


def get_node_from_interface(interfaces):
    """
    This function extracts the node number from interface
    """
    node_number = ''
    if isinstance(interfaces, list):
        node_number = ''
        for interface in interfaces:
            if (interface.find("/protpaths") != -1):
                if node_number != '':
                    node_number += str(', ' + interface.split("/protpaths-")[1].split("/")[0])
                else:
                    node_number += str(interface.split("/protpaths-")[1].split("/")[0])
            elif(interface.find("/paths-") != -1):
                if node_number != '':
                    node_number += str(', ' + interface.split("/paths-")[1].split("/")[0])
                else:
                    node_number += str(interface.split("/paths-")[1].split("/")[0])
            elif(interface.find("/pathgrp-") != -1):
                if node_number != '':
                    node_number += str(', ' + interface.split("/pathgrp-")[1].split("/")[0])
                else:
                    node_number += str(interface.split("/pathgrp-")[1].split("/")[0])
            else:
                try:
                    if re.search(r'\/[a-zA-Z]*path[a-zA-Z]*-(.*)',interface):
                        if node_number != '':
                            node_number += str(',' + re.search(r'\/[a-zA-Z]*path[a-zA-Z]*-(.*)',interface))
                        else:
                            node_number += str(re.search(r'\/[a-zA-Z]*path[a-zA-Z]*-(.*)',interface))
                    else:
                        raise Exception("interface" + str(interface))
                except Exception as e:
                    node_number += ''
                    logger.exception("Exception in get_node_from_interface:"+str(e))
    elif isinstance(interfaces, str) or isinstance(interfaces, unicode):
        node_number = ''
        if (interfaces.find("/protpaths") != -1):
            node_number += str(interfaces.split("/protpaths-")[1].split("/")[0])
        elif(interfaces.find("/paths-") != -1):
            node_number += str(interfaces.split("/paths-")[1].split("/")[0])
        elif(interfaces.find("/pathgrp-") != -1):
            node_number += str(interfaces.split("/pathgrp-")[1].split("/")[0])
        else:
            try:
                if re.search(r'\/[a-zA-Z]*path[a-zA-Z]*-(.*)',interfaces):
                    node_number += str(re.search(r'\/[a-zA-Z]*path[a-zA-Z]*-(.*)',interfaces))
                else:
                    raise Exception("interface" + str(interfaces))
            except Exception as e:
                node_number += ''
                logger.exception("Exception in get_node_from_interface:"+str(e))
    return node_number


def get_all_interfaces(interfaces):
    interface_list = ''
    for interface in interfaces:
        if re.search("/pathep-\[",interface):
            if interface_list != '':
                interface_list += (', ' + str(interface.split("/pathep-")[1][1:-1]))
            else:
                interface_list +=str(interface.split("/pathep-")[1][1:-1])
        elif re.search("/pathgrp-",interface):
            if interface_list != '':
                interface_list += (', ' + str(interface.split("/pathgrp-")[1][1:-1])+"(vmm)")
            else:
                interface_list += str(interface.split("/pathgrp-")[1][1:-1]+"(vmm)")
        else:
            logger.error("Incompetible format of Interfaces found")
            raise Exception("Incompetible format of Interfaces found")
    return interface_list


def consul_details(tenant):
    try:
        logger.info("Consul Details start")

        aci_util_obj = aci_utils.ACI_Utils()
        details_list = []
        merged_data = consul_merge.merge_aci_consul(tenant, 'data_centre', aci_util_obj)
        for each in merged_data:
            epg_health = aci_util_obj.get_epg_health(str(tenant), str(each['AppProfile']), str(each['EPG']))
            ep_info = get_eps_info(each.get('dn'), each.get('IP'))
            details_list.append({
                    'interface': ep_info.get('interface'),
                    'endPointName': each.get('VM-Name'),
                    'ip': each.get('IP'),
                    'mac': each.get('CEP-Mac'),
                    'learningSource': ep_info.get('learningSource'),
                    'hostingServer': ep_info.get('hostingServer'),
                    'reportingController': ep_info.get('reportingController'),
                    'vrf': each.get('VRF'),
                    'bd': each.get('BD'),
                    'ap': each.get('AppProfile'),
                    'epgName': each.get('EPG'),
                    'epgHealth': epg_health,
                    'consulNode': each.get('nodeName'),
                    'nodeChecks': each.get('nodeCheck'),
                    'services': each.get('services')
                })
        return details_list
    except Exception as e:
        logger.exception("Error in consul_details: "+str(e))
        return []


def get_eps_info(dn, ip):

    try:
        aci_util_obj = aci_utils.ACI_Utils()
        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&query-target-filter=or(eq(fvCEp.ip,"'+ip+'"))&rsp-subtree=children&rsp-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsVm'
        ep = aci_util_obj.get_mo_related_item(dn, ep_info_query_string, "")
        ep_info = get_ep_info(ep[0].get("fvCEp").get("children"), aci_util_obj)
        ep_attr = ep[0].get("fvCEp").get("attributes")

        return {
            'interface': ep_info.get('iface_name'),
            'learningSource':ep_attr.get("lcC"),
            'hostingServer': ep_info.get('hosting_server_name'),
            'reportingController': ep_info.get('ctrlr_name')
        }

    except Exception as e:
        logger.exception("Error in get_eps_info: "+str(e))


def get_service_check(service_name, service_id):
    try:
        service_checks = consul_merge.consul_detailed_service_check(service_name, service_id)
        return service_checks
    except Exception as e:
        logger.exception("Error in get_service_check: "+ str(e))
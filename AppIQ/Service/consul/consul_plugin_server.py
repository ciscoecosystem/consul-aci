import os
import re
import json
import time
import socket
import datetime
from flask import Flask


from . import consul_merge
from . import recommend_utils
from . import consul_tree_parser
from consul_utils import Cosnul

import aci_utils
import custom_logger


app = Flask(__name__, template_folder="../UIAssets", static_folder="../UIAssets/public")
app.secret_key = "consul_key"
app.debug = True  # See use

logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")
consul_credential_file_path = "/home/app/data/consulCredentials.json"
mapppings_file_path = "/home/app/data/mappings.json"


def set_polling_interval(interval):
    """Sets the polling interval in AppDynamics config file
    
    TODO: see if needed or not
    """

    return "200", "Polling Interval Set!"


def get_agent_list(data_center):
    """Returns list of all the agents
    
    TODO: should not be static, should be from Alchemy
    """
    try:
        start_time = datetime.datetime.now()
        logger.info("Reading agent for datacenter " + str(data_center))
        file_exists = os.path.isfile(consul_credential_file_path)
        agent_list = []

        if file_exists:
            with open(consul_credential_file_path, 'r') as fread:
                creds = json.load(fread)
            
            for agent in creds:
                if agent.get('datacenter') == data_center:
                    agent_list.append(agent)
                    return agent_list
        else:
            return []
    except Exception as e:
        logger.exception("Could not fetch agent list for datacenter {}, Error: {}".format(data_center, str(e)))
        return []
    finally:
        end_time = datetime.datetime.now()
        logger.info("time for get agent list : " + str(end_time - start_time))


def mapping(tenant, datacenter):
    """
    TODO: return valid dict
    """
    start_time = datetime.datetime.now()
    try:

        mapping_dict = {"source_cluster": [], "target_cluster": []}

        aci_obj = aci_utils.ACI_Utils()
        end_points = aci_obj.apic_fetchEPGData(tenant) # TODO: handle this apis failure returned
        parsed_eps = aci_obj.parse_ep(end_points,tenant) # TODO: handle this apis failure returned

        agent = get_agent_list(datacenter)[0]
        consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol')) # TODO: all the 3 keys expected
        consul_data = consul_obj.get_consul_data()
        ip_list = []
        for node in consul_data:
            ip_list += node.get('node_ips', [])
            # For fetching ips of services.
            for service in node.get('node_services', []):
                # check ip is not empty string
                if service.get('service_ip', ''):
                    ip_list.append(service.get('service_ip'))

        aci_consul_mappings = recommend_utils.recommanded_eps(list(set(ip_list)), parsed_eps) # TODO: handle empty response

        if not aci_consul_mappings:
            logger.info("Empty ACI and Consul mappings.")
            return json.dumps({
                "agentIP": agent.get('ip'), # TODO: what to return here
                "payload": mapping_dict,
                "status_code": "200",
                "message": "OK"
                })

        current_mapping = get_mapping_dict_target_cluster(aci_consul_mappings)
        all_datacenter_mapping = {}
        already_mapped_data = []

        file_exists = os.path.isfile(mapppings_file_path)
        if file_exists:
            with open(mapppings_file_path, 'r') as fread:
                file_data = fread.read()
                if file_data:
                    all_datacenter_mapping = json.loads(file_data)
                    already_mapped_data = all_datacenter_mapping.get(datacenter)

            if already_mapped_data:
                # current_mapping is new mapping between aci and consul
                for new_map in current_mapping:
                    # already_mapped_data is previously stored mapping by user
                    for each_already_mapped in already_mapped_data:
                        if each_already_mapped.get('ipaddress') == new_map.get('ipaddress') and each_already_mapped.get('domainName') == new_map.get('domainName'):
                            # if node is already disabled then disable it from new mappings also
                            if each_already_mapped.get('disabled') == True:
                                new_map['disabled'] = True
                            break

        all_datacenter_mapping[datacenter] = current_mapping

        with open(mapppings_file_path, 'w') as fwrite:
            json.dump(all_datacenter_mapping, fwrite)        

        mapping_dict['target_cluster'] = [node for node in current_mapping if node.get('disabled') == False]
        
        for new_object in aci_consul_mappings:
            mapping_dict['source_cluster'].append(new_object)
    
        return json.dumps({
            "agentIP": agent.get('ip'), # TODO: what to return here
            "payload": mapping_dict,
            "status_code": "200",
            "message": "OK"
            })
    except Exception as e:
        logger.exception("Could not load mapping, Error: {}".format(str(e)))
        return json.dumps({
            "payload": {}, 
            "status_code": "300", 
            "message": "Could not load mapping"
            })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for Mapping: " + str(end_time - start_time))


def save_mapping(tenant, datacenter, mapped_data):
    """Save mapping to database.
    
    TODO: complete
    """
    start_time = datetime.datetime.now()
    try:        
        logger.info("Saving mappings for datacenter : " + str(datacenter))
        logger.debug("Mapped Data : " + mapped_data)
        mapped_data = mapped_data.replace("'", '"')
        mapped_data_dict = json.loads(mapped_data)

        data_list = []
        all_datacenter_mapping = {}
        already_mapped_data = []

        file_exists = os.path.isfile(mapppings_file_path)
        if file_exists:
            with open(mapppings_file_path, 'r') as fread:
                file_data = fread.read()
                if file_data:
                    all_datacenter_mapping = json.loads(file_data)
                    already_mapped_data = all_datacenter_mapping.get(datacenter)

        for mapping in mapped_data_dict:
            if mapping.get('ipaddress') != "":
                data_list.append({'ipaddress': mapping.get('ipaddress'), 'domainName': mapping['domains'][0]['domainName'], 'disabled': False})
        
        if not data_list:
            all_datacenter_mapping.pop(datacenter)
        else:
            data_list = parse_mapping_before_save(already_mapped_data, data_list)
            all_datacenter_mapping[datacenter] = data_list

        with open(mapppings_file_path, 'w') as fwrite:
            json.dump(all_datacenter_mapping, fwrite)

        return json.dumps({"payload": "Saved Mappings", "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Could not save mappings to the database. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not save mappings to the database."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for saveMapping: " + str(end_time - start_time))
    

def parse_mapping_before_save(already_mapped_data, data_list):
    """
    Set disabled value true if user has disabled particular node manually.
    """
    for previous_mapping in already_mapped_data:
        is_node_exist = False
        for current_mapping in data_list:
            if current_mapping.get('ipaddress') == previous_mapping.get('ipaddress') and current_mapping.get('domainName') == previous_mapping.get('domainName'):
                is_node_exist = True
                break
        
        # Append removed node by user as disabled 
        if not is_node_exist:
            previous_mapping['disabled'] = True
            data_list.append(previous_mapping)

    return data_list
    


def tree(tenant, datacenter):
    """Get correltated Tree view data.
    
    return: {
        agentIP: string
        payload: list of tree(dict)/{}
        status_code: string: 200/300 
        message: string
    }
    """

    logger.info("Tree view for tenant: {}".format(tenant))
    start_time = datetime.datetime.now()
    try:
        mapping(tenant, datacenter)
        all_datacenter_mapping = {}

        file_exists = os.path.isfile(mapppings_file_path)
        if file_exists:
            with open(mapppings_file_path, 'r') as fread:
                file_data = fread.read()
                if file_data:
                    all_datacenter_mapping = json.loads(file_data)
                    aci_consul_mappings = all_datacenter_mapping.get(datacenter)
        aci_obj = aci_utils.ACI_Utils()
        aci_data = aci_obj.main(tenant)
        agent = get_agent_list(datacenter)[0]
        consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
        consul_data = consul_obj.get_consul_data()

        merged_data = consul_merge.merge_aci_consul(tenant, aci_data, consul_data, aci_consul_mappings)

        logger.debug("ACI Consul mapped data: {}".format(merged_data))

        response = json.dumps(consul_tree_parser.consul_tree_dict(merged_data))
        logger.debug("Final Tree data: {}".format(response))

        return json.dumps({
            "agentIP": agent.get('ip'), # TODO: send valid ip
            "payload": response,
            "status_code": "200",
            "message": "OK"
            })
    except Exception as e:
        logger.exception("Error while building tree, Error: {}".format(str(e)))
        return json.dumps({
            "payload": {},
            "status_code": "300",
            "message": "Could not load the View."
            })
    finally:
        end_time =  datetime.datetime.now()
        logger.debug("Time for TREE: " + str(end_time - start_time))


def details(tenant, datacenter):
    """Get correlated Details view data
    
    return: {
        agentIP: string
        payload: list of dict/{}
        status_code: string: 200/300 
        message: string
    }
    """

    logger.info("Details view for tenant: {}".format(tenant))
    start_time = datetime.datetime.now()
    try:
        mapping(tenant, datacenter)
        all_datacenter_mapping = {}

        file_exists = os.path.isfile(mapppings_file_path)
        if file_exists:
            with open(mapppings_file_path, 'r') as fread:
                file_data = fread.read()
                if file_data:
                    all_datacenter_mapping = json.loads(file_data)
                    aci_consul_mappings = all_datacenter_mapping.get(datacenter)
        aci_obj = aci_utils.ACI_Utils()
        aci_data = aci_obj.main(tenant)
        agent = get_agent_list(datacenter)[0]
        consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
        consul_data = consul_obj.get_consul_data()

        merged_data = consul_merge.merge_aci_consul(tenant, aci_data, consul_data, aci_consul_mappings)

        details_list = []
        for each in merged_data:
            epg_health = aci_obj.get_epg_health(str(tenant), str(each['AppProfile']), str(each['EPG']))
            # ep_info = get_eps_info(each.get('dn'), each.get('IP'))
            details_list.append({
                    'interface': each.get('Interfaces'),
                    'endPointName': each.get('VM-Name'),
                    'ip': each.get('IP'),
                    'mac': each.get('CEP-Mac'),
                    'learningSource': each.get('learningSource'),
                    'hostingServer': each.get('hostingServerName'),
                    'reportingController': each.get('controllerName'),
                    'vrf': each.get('VRF'),
                    'bd': each.get('BD'),
                    'ap': each.get('AppProfile'),
                    'epgName': each.get('EPG'),
                    'epgHealth': epg_health,
                    'consulNode': each.get('node_name'),
                    'nodeChecks': each.get('node_check'),
                    'services': change_key(each.get('node_services'))
                })
        logger.debug("Details final data ended: " + str(details_list))
        
        # TODO: details = [dict(t) for t in set([tuple(d.items()) for d in details_list])]
        return json.dumps({
            "agentIP": agent.get('ip'),
            "payload": details_list,
            "status_code": "200",
            "message": "OK"
            })
    except Exception as e:
        logger.exception("Could not load the Details. Error: {}".format(str(e)))
        return json.dumps({
            "payload": {},
            "status_code": "300",
            "message": "Could not load the Details."
            })
    finally:
        end_time =  datetime.datetime.now()
        logger.debug("Time for DETAILS: " + str(end_time - start_time))


def get_mapping_dict_target_cluster(mapped_objects):
    """
    return mapping dict from recommended objects


    TODO: this can be handled in tree and Details or get proper mapping from db
    """
    target = []
    for map_object in mapped_objects:
        for entry in map_object.get('domains'):
            if entry.get('recommended') == True:
                logger.debug("Mapping found with ipaddress for "+str(map_object))
                target.append({'domainName': entry.get('domainName'), 'ipaddress': map_object.get('ipaddress'), 'disabled': False})
    return target


def change_key(services):
    final_list = []
    if services:
        for service in services:
            final_list.append({
                'service': service.get('service_name'),
                'serviceInstance': service.get('service_id'),
                'port': service.get('service_port'),
                'serviceTags': service.get('service_tags'),
                'serviceKind': service.get('service_kind'),
                'serviceChecks': service.get('service_checks')
            })
    return final_list


def get_service_check(service_name, service_id, datacenter):
    """Service checks with all detailed info
    
    return: {
        agentIP: string
        payload: list of dict/[]
        status_code: string: 200/300 
        message: string
    } 
    """
    
    logger.info("Service Check for service: {}, {}".format(service_name, service_id))
    start_time = datetime.datetime.now()
    try:
        agent = get_agent_list(datacenter)[0]
        consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
        response = consul_obj.detailed_service_check(service_name, service_id)
        logger.debug('Response of Service chceck: {}'.format(response))

        return json.dumps({
            "agentIP": agent.get('ip'),
            "payload": response,
            "status_code": "200",
            "message": "OK"
            })
    except Exception as e:
        logger.exception("Error in get_service_check: "+ str(e))
        return json.dumps({
            "payload": [],
            "status_code": "300",
            "message": "Could not load service checks."
            })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for get_service_check: " + str(end_time - start_time))


def get_node_checks(node_name, datacenter):
    """Node checks with all detailed info
    
    return: {
        agentIP: string
        payload: list of dict/[]
        status_code: string: 200/300 
        message: string
    } 
    """

    logger.info("Node Check for node: {}".format(node_name))
    start_time = datetime.datetime.now()
    try:
        agent = get_agent_list(datacenter)[0]
        consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
        response = consul_obj.detailed_node_check(node_name)
        logger.debug('Response of Service chceck: {}'.format(response))

        return json.dumps({
            "agentIP": agent.get('ip'),
            "payload": response,
            "status_code": "200",
            "message": "OK"
            })
    except Exception as e:
        logger.exception("Error in get_node_check: " + str(e))
        return json.dumps({
            "payload": [],
            "status_code": "300",
            "message": "Could not load node checks."
            })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for get_health_check: " + str(end_time - start_time))


def get_service_check_ep(service_list, datacenter):
    """Service checks with all detailed info of multiple service
    
    return: {
        agentIP: string
        payload: list of dict/[]
        status_code: string: 200/300 
        message: string
    } 
    """
    
    logger.info("Service Checks for services: {}".format(service_list))
    start_time = datetime.datetime.now()
    response = []
    try:
        agent = get_agent_list(datacenter)[0]
        consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
        service_list = json.loads(service_list)

        for service_dict in service_list:
            service_name = service_dict["Service"]
            service_id = service_dict["ServiceID"]
            
            response += consul_obj.detailed_service_check(service_name, service_id)
        
        return json.dumps({
            "agentIP": agent.get('ip'),
            "payload": response,
            "status_code": "200",
            "message": "OK"
            })
    except Exception as e:
        logger.exception("Error in get_node_check: " + str(e))
        return json.dumps({
            "payload": [],
            "status_code": "300",
            "message": "Could not load service checks."
            })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for get_service_check_ep: " + str(end_time - start_time))


def get_node_check_epg(node_list, datacenter):
    """Node checks with all detailed info of multiple Node
    
    return: {
        agentIP: string
        payload: list of dict/[]
        status_code: string: 200/300 
        message: string
    } 
    """

    logger.info("Node Checks for nodes: {}".format(node_list))
    start_time = datetime.datetime.now()
    response = []
    try:
        agent = get_agent_list(datacenter)[0]
        consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
        node_list = json.loads(node_list)

        for node_name in node_list:
            response += consul_obj.detailed_node_check(node_name)

        return json.dumps({
            "agentIP": agent.get('ip'),
            "payload": response,
            "status_code": "200",
            "message": "OK"
            })
    except Exception as e:
        logger.exception("Error in get_node_check_epg: " + str(e))
        return json.dumps({
            "payload": [],
            "status_code": "300",
            "message": "Could not load node checks."
            })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for get_service_check_ep: " + str(end_time - start_time))


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
                "created" : fault_attr.get("created"),
                "cause" : fault_attr.get("cause")
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


def get_children_ep_info(dn, mo_type, mac_list):
    start_time = datetime.datetime.now()
    aci_util_obj = aci_utils.ACI_Utils()
    if mo_type == "ep":
        mac_list = mac_list.split(",")
        mac_query_filter_list = []
        for mac in mac_list:
            mac_query_filter_list.append('eq(fvCEp.mac,"' + mac + '")')
        mac_query_filter = ",".join(mac_query_filter_list)

        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&query-target-filter=or(' + mac_query_filter +')&rsp-subtree=children&rsp-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsVm'
    elif mo_type == "epg":
        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&rsp-subtree=children&rsp-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsToVm'

    ep_list = aci_util_obj.get_mo_related_item(dn, ep_info_query_string, "")
    ep_info_list = []
    try:
        for ep in ep_list:
            ep_info_dict = dict()

            ep_children = ep.get("fvCEp").get("children")
            ep_info = aci_util_obj.get_ep_info(ep_children)
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
                "ep_name" : ep_info.get("VM-Name"),
                "hosting_server_name" : ep_info.get("hostingServerName"),
                "iface_name" : ep_info.get("Interfaces"),
                "ctrlr_name" : ep_info.get("controllerName")
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
        logger.info("Time for get_children_ep_info: " + str(end_time - start_time))
    

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
            cap_dict["node"] = aci_util_obj.get_node_from_interface(cap_attr["pathEp"])
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


def get_to_epg_traffic(epg_dn):
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
                        ingr_pkts, egr_pkts = get_ingress_egress(from_epg_dn, to_epg_dn, subj_dn, flt_name, aci_util_obj)
                                            
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
            logger.info("Time for get_to_epg_traffic: " + str(end_time - start_time))
    else:
        logger.error("Could not get Traffic Data related to EPG")
        end_time =  datetime.datetime.now()
        logger.info("Time for get_to_epg_traffic: " + str(end_time - start_time))
        return json.dumps({
            "status_code": "300",
            "message": "Exception while fetching Traffic Data related to EPG",
            "payload": []
        })


def get_ingress_egress(from_epg_dn, to_epg_dn, subj_dn, flt_name, aci_util_obj):
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
        logger.info("Time for get_ingress_egress: " + str(end_time - start_time))
        return ingr_pkts, egr_pkts
    else:
        end_time =  datetime.datetime.now()
        logger.info("Time for get_ingress_egress: " + str(end_time - start_time))
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


def read_creds():
    try:
        start_time = datetime.datetime.now()
        logger.info("Reading agents.")
        file_exists = os.path.isfile(consul_credential_file_path)
        
        if file_exists:
            with open(consul_credential_file_path, 'r') as fread:
                creds = []
                creds_string = fread.read()
                if creds_string:
                    creds = json.loads(creds_string)

                for agent in creds:
                    consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
                    status, message = consul_obj.check_connection()
                    agent['status'] = status
                    if status:
                        datacenter_name = consul_obj.datacenter()
                        if datacenter_name:
                            agent['datacenter'] = datacenter_name
                        else:
                            agent['datacenter'] = "-"
                    else:
                        agent['datacenter'] = "-"
            
            with open(consul_credential_file_path, 'w') as fwrite:
                json.dump(creds, fwrite)
                creds.sort(key = lambda x: x['timestamp'], reverse=True)
                    
                logger.debug("agent data: " + str(creds))
                return json.dumps({"payload": creds, "status_code": "200", "message": "OK"})
        else:
            logger.debug("credential file not found.")
            return json.dumps({"payload": [], "status_code": "500", "message": "Internal Server Error"})
    except Exception as e:
        logger.exception("Error in read credentials: " + str(e))
        return json.dumps({"payload": [], "status_code": "300", "message": "Could not load the credentials."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for read_creds: " + str(end_time - start_time))


def write_creds(agent_list):
    try:
        start_time = datetime.datetime.now()
        logger.info("Writing agents: " + str(agent_list))
        agent_list = json.loads(agent_list)
        file_exists = os.path.isfile(consul_credential_file_path)
        creds = []

        if file_exists:
            with open(consul_credential_file_path, 'r') as fread:
                creds_string = fread.read()
                if creds_string:
                    creds = json.loads(creds_string)
        
        logger.debug("credentials file content: " + str(creds))
        
        for agent in agent_list:
            agent['timestamp'] = int(time.time())
            consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
            status, message = consul_obj.check_connection()
            agent['status'] = status
            if status:
                datacenter_name = consul_obj.datacenter()
                if datacenter_name:
                    agent['datacenter'] = datacenter_name
                else:
                    agent['datacenter'] = "-"
            else:
                agent['datacenter'] = "-"
                agent['message'] = message

        logger.debug("New agent data: " + str(agent_list))

        ip_port_list = [(agent.get('ip'), agent.get('port')) for agent in creds]

        new_agent_list = [agent for agent in agent_list if (agent.get('ip'), agent.get('port')) not in ip_port_list]
        if new_agent_list:
            creds += new_agent_list

            with open(consul_credential_file_path, 'w') as fwrite:
                json.dump(creds, fwrite)

            if not [x.get('message', '') for x in new_agent_list if x.get('message', '')]:
                return json.dumps({"payload": new_agent_list, "status_code": "200", "message": "OK"})
            else:
                return json.dumps({"payload": new_agent_list, "status_code": "300", "message": str(new_agent_list[0].get('message', ''))})

        else:
            logger.error("Agent " + agent_list[0].get('ip') + ":" + str(agent_list[0].get('port')) + " already exists.")
            return json.dumps({"payload": new_agent_list, "status_code": "300", "message": "Agent " + agent_list[0].get('ip') + ":" + str(agent_list[0].get('port')) + " already exists."})
    except Exception as e:
        logger.exception("Error in write credentials: " + str(e))
        return json.dumps({"payload": [], "status_code": "300", "message": "Could not write the credentials."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for write_creds: " + str(end_time - start_time))


def update_creds(update_input):
    try:
        start_time = datetime.datetime.now()
        update_input = json.loads(update_input)
        logger.info("Updating agents.")
        old_data = update_input.get('oldData')
        logger.info("Old Data: " + str(old_data))
        new_data = update_input.get('newData')
        logger.info("New Data: " + str(new_data))
        file_exists = os.path.isfile(consul_credential_file_path)
        creds = []
        if file_exists:
            with open(consul_credential_file_path, 'r') as fread:
                creds_string = fread.read()
                if creds_string:
                    creds = json.loads(creds_string)
        
            
        logger.debug("credentials file content: " + str(creds))
        response = {}

        ip_port_list = [(agent.get('ip'), agent.get('port')) for agent in creds]
        ip_port_list.remove((old_data.get('ip'), old_data.get('port')))

        message = None
        if (new_data.get('ip'), new_data.get('port')) not in ip_port_list:
            for agent in creds:
                if old_data.get("protocol") == agent.get("protocol") and old_data.get("ip") == agent.get("ip") and old_data.get("port") == agent.get("port"):
                    agent["protocol"] = new_data.get("protocol")
                    agent["ip"] = new_data.get("ip")
                    agent["port"] = new_data.get("port")
                    agent["token"] = new_data.get("token")
                    agent['timestamp'] = int(time.time())
                    response.update(agent)
                    consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
                    status, message = consul_obj.check_connection()
                    response["status"] = status
                    if status:
                        datacenter_name = consul_obj.datacenter()
                        if datacenter_name:
                            response['datacenter'] = datacenter_name
                            agent["datacenter"] = datacenter_name
                        else:
                            response['datacenter'] = "-"
                            agent['datacenter'] = "-"
                    else:
                        response['datacenter'] = "-"
                        agent['datacenter'] = "-"
                    break        
            logger.debug("new file content: " + str(creds))
            logger.debug("response: " + str(response))

            with open(consul_credential_file_path, 'w') as fwrite:
                json.dump(creds, fwrite)

            if not message:
                return json.dumps({"payload": response, "status_code": "200", "message": "OK"})
            else:
                return json.dumps({"payload": response, "status_code": "300", "message": message})

        else:
            logger.error("Agent with " + new_data.get('ip') + ":" + str(new_data.get('port')) + " already exists.")
            return json.dumps({"payload": response, "status_code": "300", "message": "Agent " + new_data.get('ip') + ":" + str(new_data.get('port')) + " already exists."})
    except Exception as e:
        logger.exception("Error in update credentials: " + str(e))
        return json.dumps({"payload": [], "status_code": "300", "message": "Could not update the credentials."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for update_creds: " + str(end_time - start_time))


def delete_creds(agent_data):
    try:
        start_time = datetime.datetime.now()
        logger.info("deleting agents: " + str(agent_data))
        agent_data = json.loads(agent_data)
        file_exists = os.path.isfile(consul_credential_file_path)
        creds = []
        if file_exists:
            with open(consul_credential_file_path, 'r') as fread:
                creds_string = fread.read()
                if creds_string:
                    creds = json.loads(creds_string)
            
        logger.debug("credential file content before delete: " + str(creds))

        for agent in creds:
            if agent_data.get("protocol") == agent.get("protocol") and agent_data.get("ip") == agent.get("ip") and agent_data.get("port") == agent.get("port") and agent_data.get("token") == agent.get("token"):
                creds.remove(agent)
                break
        logger.debug("credential file content after delete: " + str(creds))

        with open(consul_credential_file_path, 'w') as fwrite:
            json.dump(creds, fwrite)
        return json.dumps({"status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Error in delete credentials: " + str(e))
        return json.dumps({"payload": [], "status_code": "300", "message": "Could not delete the credentials."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for delete_creds: " + str(end_time - start_time))

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
consul_credential_file_path = "/home/app/log/consulCredentials.json"

session = {}

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


def get_datacenter_list():
    """Returns all the datacenters
    
    return: {
        agentIP: string
        payload: { # TODO This should be list, not a dict of a list
            datacenters: string list
        } or {}
        status_code: string: 200/300 
        message: string
    }
    """
    
    logger.info('Get Datacenter List')
    start_time = datetime.datetime.now()
    datacenter_set = set()
    datacenter_list = []

    try:        
        # get list of all agents
        agent_list = get_agent_list('all')

        for agent in agent_list:
            consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol')) # TODO: all the 3 keys expected
            
            agent_datacenters = consul_obj.datacenters()
            for datacenter in agent_datacenters:
                datacenter_set.add(datacenter)
        logger.debug("Final datacenters set : {}".format(datacenter_set))

        datacenter_list = [{"datacenterName" : dc, "isViewEnabled" : True} for dc in datacenter_set]

        return json.dumps({
            "agentIP":"10.23.239.14", # TODO: what to return here
            "payload": { # TODO This should be list, not a dict of a list
                'datacenters': datacenter_list
            },
            "status_code": "200", 
            "message": "OK"
            })
    except Exception as e:
        logger.exception("Could not fetch datacenter list, Error: {}".format(str(e)))
        return json.dumps({
            "payload": {}, 
            "status_code": "300", 
            "message": "Could not fetch datacenter list"
            })
    finally:
        end_time =  datetime.datetime.now()
        logger.debug("Time for get_datacenter_list: " + str(end_time - start_time))


def mapping(tenant, datacenter):
    """
    TODO: return valid dict
    """

    try:

        mapping_dict = {"source_cluster": [], "target_cluster": []}

        aci_obj = aci_utils.ACI_Utils()
        end_points = aci_obj.apic_fetchEPData(tenant) # TODO: handle this apis failure returned
        parsed_eps = aci_obj.parseEPs(end_points,tenant) # TODO: handle this apis failure returned

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

        aci_consul_mappings = recommend_utils.recommanded_eps(tenant, list(set(ip_list)), parsed_eps) # TODO: handle empty response
        current_mapping = get_mapping_dict_target_cluster(aci_consul_mappings)

        mapping_dict['target_cluster'] = [node for node in current_mapping if node.get('disabled') == False]
        
        for new_object in aci_consul_mappings:
            mapping_dict['source_cluster'].append(new_object)
    
        return json.dumps({
            "agentIP":"10.23.239.14", # TODO: what to return here
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


def save_mapping(appDId, tenant, mappedData):
    """Save mapping to database.
    
    TODO: complete
    """

    return json.dumps({"payload": "Saved Mappings", "status_code": "200", "message": "OK"})


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
        aci_obj = aci_utils.ACI_Utils()
        end_points = aci_obj.apic_fetchEPData(tenant) # TODO: handle this apis failure returned
        parsed_eps = aci_obj.parseEPs(end_points,tenant) # TODO: handle this apis failure returned

        agent = get_agent_list(datacenter)[0]
        consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol')) # TODO: all the 3 keys expected
        session["consulObject"] = consul_obj
        
        consul_data = consul_obj.get_consul_data()
        ip_list = []
        for node in consul_data:
            ip_list += node.get('node_ips', [])
            # For fetching ips of services.
            for service in node.get('node_services', []):
                # check ip is not empty string
                if service.get('service_ip', ''):
                    ip_list.append(service.get('service_ip'))

        aci_consul_mappings = recommend_utils.recommanded_eps(tenant, list(set(ip_list)), parsed_eps) # TODO: handle empty response
        aci_consul_mappings = get_mapping_dict_target_cluster(aci_consul_mappings)

        aci_data = aci_obj.main(tenant)

        merged_data = consul_merge.merge_aci_consul(tenant, aci_data, consul_data, aci_consul_mappings)

        # parse interface data
        for ep_data in merged_data:
            interface_list = [ get_iface_name(iface_name) for iface_name in ep_data['Interfaces']]
            ep_data['Interfaces'] = interface_list

        logger.debug("ACI Consul mapped data: {}".format(merged_data))

        response = json.dumps(consul_tree_parser.consul_tree_dict(merged_data))
        logger.debug("Final Tree data: {}".format(response))

        return json.dumps({
            "agentIP":"10.23.239.14", # TODO: send valid ip
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
        aci_obj = aci_utils.ACI_Utils()
        end_points = aci_obj.apic_fetchEPData(tenant) # TODO: handle this apis failure returned
        parsed_eps = aci_obj.parseEPs(end_points,tenant) # TODO: handle this apis failure returned

        agent = get_agent_list(datacenter)[0] # TODO: for now first agent
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

        aci_consul_mappings = recommend_utils.recommanded_eps(tenant, list(set(ip_list)), parsed_eps) # TODO: handle empty response
        aci_consul_mappings = get_mapping_dict_target_cluster(aci_consul_mappings)

        aci_data = aci_obj.main(tenant)

        merged_data = consul_merge.merge_aci_consul(tenant, aci_data, consul_data, aci_consul_mappings)

        details_list = []
        for each in merged_data:
            epg_health = aci_obj.get_epg_health(str(tenant), str(each['AppProfile']), str(each['EPG']))
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
                    'consulNode': each.get('node_name'),
                    'nodeChecks': each.get('node_check'),
                    'services': change_key(each.get('node_services'))
                })
        logger.debug("Details final data ended: " + str(details_list))
        
        # TODO: details = [dict(t) for t in set([tuple(d.items()) for d in details_list])]
        return json.dumps({
            "agentIP":"10.23.239.14",
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


def get_eps_info(dn, ip):
    """Returns individual CEp's data
    
    TODO: this should go in APIC layer

    return: {
            interface: string
            learningSource: string
            hostingServer: string
            reportingController: string
        }
    """

    logger.info("EP detailed info for: {}, {}".format(dn, ip))
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
            "agentIP":"10.23.239.14",
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
            "agentIP":"10.23.239.14",
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
            "agentIP":"10.23.239.14",
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
            "agentIP":"10.23.239.14",
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


def get_childrenEp_info(dn, mo_type, mac_list):
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


def get_iface_name(name):
    if re.match('topology\/pod-+\d+\/pathgrp-.*',name):
        pod_number = name.split("/pod-")[1].split("/")[0]
        node_number = get_node_from_interface(name)
        #The ethernet name is NOT available
        eth_name = str(name.split("/pathgrp-[")[1].split("]")[0]) + "(vmm)"
        iface_name = eth_name
        return iface_name
    elif re.match('topology\/pod-+\d+\/paths(-\d+)+?\/pathep-.*',name):
        pod_number = name.split("/pod-")[1].split("/")[0]
        node_number = get_node_from_interface(name)
        eth_name = name.split("/pathep-[")[1][0:-1]
        iface_name = "Pod-" + pod_number + "/Node-" + str(node_number) + "/" + eth_name
        return iface_name
    elif re.match('topology\/pod-+\d+\/protpaths(-\d+)+?\/pathep-.*',name):
        pod_number = name.split("/pod-")[1].split("/")[0]
        node_number = get_node_from_interface(name)
        eth_name = name.split("/pathep-[")[1][0:-1]
        iface_name = "Pod-" + pod_number + "/Node-" + str(node_number) + "/" + eth_name
        return iface_name
    else:
        logger.error("Different format of interface is found: {}".format(name))
        raise Exception("Different format of interface is found: {}".format(name))

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
                    status = consul_obj.check_connection()
                    agent['status'] = status
                    if status:
                        datacenter_list = consul_obj.datacenters()
                        if datacenter_list:
                            agent['datacenter'] = datacenter_list[0]
                        else:
                            agent['datacenter'] = "-"
                    else:
                        agent['datacenter'] = "-"
            
            with open(consul_credential_file_path, 'w') as fwrite:
                json.dump(creds, fwrite)
                    
                logger.debug("agent data: " + str(creds))
                return json.dumps({"agentIP":"10.23.239.14","payload": creds, "status_code": "200", "message": "OK"})
        else:
            logger.debug("credential file not found.")
            return json.dumps({"agentIP":"10.23.239.14", "payload": [], "status_code": "200", "message": "OK"})
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
            consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
            status = consul_obj.check_connection()
            agent['status'] = status
            if status:
                datacenter_list = consul_obj.datacenters()
                if datacenter_list:
                    agent['datacenter'] = datacenter_list[0]
                else:
                    agent['datacenter'] = "-"
            else:
                agent['datacenter'] = "-"
        logger.debug("New agent data: " + str(agent_list))

        creds += agent_list
        with open(consul_credential_file_path, 'w') as fwrite:
            json.dump(creds, fwrite)

        return json.dumps({"agentIP":"10.23.239.14", "payload": agent_list, "status_code": "200", "message": "OK"})
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

        for agent in creds:
            if old_data.get("protocol") == agent.get("protocol") and old_data.get("ip") == agent.get("ip") and old_data.get("port") == agent.get("port"):
                agent["protocol"] = new_data.get("protocol")
                agent["ip"] = new_data.get("ip")
                agent["port"] = new_data.get("port")
                agent["token"] = new_data.get("token")
                response.update(agent)
                consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
                status = consul_obj.check_connection()
                response["status"] = status
                if status:
                    datacenter_list = consul_obj.datacenters()
                    if datacenter_list:
                        response['datacenter'] = datacenter_list[0]
                        agent["datacenter"] = datacenter_list[0]
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
        return json.dumps({"agentIP":"10.23.239.14", "payload": response, "status_code": "200", "message": "OK"})
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
        return json.dumps({"agentIP":"10.23.239.14", "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Error in delete credentials: " + str(e))
        return json.dumps({"payload": [], "status_code": "300", "message": "Could not delete the credentials."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for delete_creds: " + str(end_time - start_time))

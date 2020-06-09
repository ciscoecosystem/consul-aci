import os
import re
import json
import time
import socket
import datetime
import base64
from flask import Flask


import merge
import recommend_utils
import tree_parser
from consul_utils import Consul
from decorator import time_it

import apic_utils
import alchemy_core
import custom_logger


app = Flask(__name__, template_folder="../UIAssets",
            static_folder="../UIAssets/public")
app.secret_key = "consul_key"
app.debug = True

logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")

db_obj = alchemy_core.Database()
db_obj.create_tables()


def set_polling_interval(interval):
    """Sets the polling interval for data fetch

    TODO: to be implemented
    """

    return "200", "Polling Interval Set!"


def get_new_mapping(tenant, datacenter):
    try:
        # Get APIC data
        ep_data = list(db_obj.select_from_table(db_obj.EP_TABLE_NAME))
        parsed_eps = []
        for ep in ep_data:
            cep_ip = int(ep[12])
            if cep_ip == 1:
                cep_ip = True
            else:
                cep_ip = False
            parsed_eps.append(
                {
                    'dn': ep[3],
                    'IP': ep[1],
                    'cep_ip': cep_ip,
                }
            )

        # Get consul data
        consul_data = get_consul_data(datacenter)
        ip_list = []
        for node in consul_data:
            ip_list += node.get('node_ips', [])
            # For fetching ips of services.
            for service in node.get('node_services', []):
                # check ip is not empty string
                if service.get('service_ip', ''):
                    ip_list.append(service.get('service_ip'))

        aci_consul_mappings = recommend_utils.recommanded_eps(
            list(set(ip_list)), parsed_eps)

        if not aci_consul_mappings:
            logger.info("Empty ACI and Consul mappings.")
            return []

        current_mapping = []
        for map_object in aci_consul_mappings:
            for entry in map_object.get('domains'):
                    logger.debug("Mapping found with ipaddress for "+str(map_object))
                    current_mapping.append({
                        'dn': entry.get('domainName'), 
                        'ip': map_object.get('ipaddress'), 
                        'recommended': entry.get('recommended'),
                        'enabled': entry.get('recommended') # Initially only the recommended are true
                    })

        apic_data = get_apic_data(tenant)
        for maped_obj in current_mapping:
            for ep in apic_data:
                if ep.get('dn') == maped_obj.get('dn'):
                    maped_obj.update({
                        'vrf': ep.get('VRF'),
                        'bd': ep.get('BD'),
                        'ap': ep.get('AppProfile'),
                        'tenant': tenant,
                        'epg': ep.get('EPG')
                    })

        logger.info('New mapping: {}'.format(str(current_mapping)))

        already_mapped_data = list(db_obj.select_from_table(db_obj.MAPPING_TABLE_NAME))

        logger.info('Mapping in db mapping: {}'.format(str(already_mapped_data)))
        logger.info('Mapping in db mapping: {}'.format(str(already_mapped_data)))

        new_map_list = []

        # current_mapping is new mapping between aci and consul
        # already_mapped_data is previously stored mapping by user
        # if node is already disabled then disable it from new mappings also
        for new_map in current_mapping:
            for db_map in already_mapped_data:
                if db_map[0] == new_map.get('ip') and db_map[1] == new_map.get('dn') and db_map[2] == datacenter:
                    new_map['enabled'] = db_map[3] # replace the enabled value with the one in db
                    break

            db_obj.insert_and_update(db_obj.MAPPING_TABLE_NAME,
                (
                    new_map.get('ip'),
                    new_map.get('dn'),
                    datacenter,
                    new_map.get('enabled'),
                    new_map.get('ap'),
                    new_map.get('bd'),
                    new_map.get('epg'),
                    new_map.get('vrf'),
                    tenant
                ),
                {
                    'ip': new_map.get('ip'),
                    'dn': new_map.get('dn'),
                    'datacenter': datacenter
                })

            new_map_list.append((new_map.get('ip'), new_map.get('dn')))

        for mapping in already_mapped_data:
            if mapping[2] == datacenter and (mapping[0], mapping[1]) not in new_map_list:
                db_obj.delete_from_table(db_obj.MAPPING_TABLE_NAME, {
                    'ip': mapping[0],
                    'dn': mapping[1],
                    'datacenter': mapping[2]
                })


        return current_mapping
    except Exception as e:
        logger.exception("Could not load mapping, Error: {}".format(str(e)))
        return []



def mapping(tenant, datacenter):
    """Returns mapping to UI and saves recommanded mapping to db"""

    try:
        current_mapping = get_new_mapping(tenant, datacenter)
        
        return json.dumps({
            "agentIP": ' ',  # TODO: what to return here
            "payload": current_mapping, # REturn current mapping
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

@time_it
def save_mapping(tenant, datacenter, mapped_data):
    """Save mapping to database"""

    try:
        logger.info("Saving mappings for datacenter : " + str(datacenter))
        logger.debug("Mapped Data : " + mapped_data)
        mapped_data = mapped_data.replace("'", '"')
        mapped_data_dict = json.loads(mapped_data)

        for mapping in mapped_data_dict:
            db_obj.insert_and_update(db_obj.MAPPING_TABLE_NAME,
                (
                    mapping.get('ip'),
                    mapping.get('dn'),
                    datacenter,
                    mapping.get('enabled'),
                    mapping.get('ap'),
                    mapping.get('bd'),
                    mapping.get('vrf'),
                    tenant
                ),
                {
                    'ip': mapping.get('ip'),
                    'dn': mapping.get('dn'),
                    'datacenter': datacenter
                })

        return json.dumps({"payload": "Saved Mappings", "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Could not save mappings to the database. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not save mappings to the database."})


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

@time_it
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
    try:
        aci_consul_mappings = get_new_mapping(tenant, datacenter)

        apic_data = get_apic_data(tenant)
        consul_data = get_consul_data(datacenter)
        merged_data = merge.merge_aci_consul(tenant, apic_data, consul_data, aci_consul_mappings)

        logger.debug("ACI Consul mapped data: {}".format(merged_data))

        response = json.dumps(tree_parser.consul_tree_dict(merged_data))
        logger.debug("Final Tree data: {}".format(response))

        return json.dumps({
            "agentIP": '',  # TODO: send valid ip
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
                'serviceChecks': service.get('service_checks'),
                'serviceNamespace': service.get('service_namespace')
            })
    return final_list


@time_it
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
    try:
        response = []
        service_checks_data = list(db_obj.select_from_table(db_obj.SERVICECHECKS_TABLE_NAME))
        for check in service_checks_data:
            if check[1] == service_id and check[2] == service_name:
                response.append({
                    'ServiceName': check[2],
                    'CheckID': check[0],
                    'Type': check[4],
                    'Notes': check[5],
                    'Output': check[6],
                    'Name': check[3],
                    'Status': check[7]
                })

        logger.debug('Response of Service chceck: {}'.format(response))

        return json.dumps({
            "agentIP": '',
            "payload": response,
            "status_code": "200",
            "message": "OK"
        })
    except Exception as e:
        logger.exception("Error in get_service_check: " + str(e))
        return json.dumps({
            "payload": [],
            "status_code": "300",
            "message": "Could not load service checks."
        })


@time_it
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
    try:
        response = []
        node_checks_data = list(db_obj.select_from_table(db_obj.NODECHECKS_TABLE_NAME))
        for check in node_checks_data:
            if check[2] == node_name:
                response.append({
                    'NodeName': node_name,
                    'Name': check[3],
                    'ServiceName': check[4],
                    'CheckID': check[0],
                    'Type': check[5],
                    'Notes': check[6],
                    'Output': check[7],
                    'Status': check[8]
                })

        logger.debug('Response of Node chceck: {}'.format(response))

        return json.dumps({
            "agentIP": '',
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


@time_it
def get_multi_service_check(service_list, datacenter):
    """Service checks with all detailed info of multiple service

    return: {
        agentIP: string
        payload: list of dict/[]
        status_code: string: 200/300 
        message: string
    } 
    """

    logger.info("Service Checks for services: {}".format(service_list))
    response = []
    try:
        service_list = json.loads(service_list)
        response = []
        service_checks_data = list(db_obj.select_from_table(db_obj.SERVICECHECKS_TABLE_NAME))
        

        for service_dict in service_list:
            service_name = service_dict["Service"]
            service_id = service_dict["ServiceID"]
            for check in service_checks_data:
                if check[1] == service_id and check[2] == service_name:
                    response.append({
                        'ServiceName': check[2],
                        'CheckID': check[0],
                        'Type': check[4],
                        'Notes': check[5],
                        'Output': check[6],
                        'Name': check[3],
                        'Status': check[7]
                    })

        return json.dumps({
            "agentIP": '',
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


@time_it
def get_multi_node_check(node_list, datacenter):
    """Node checks with all detailed info of multiple Node

    return: {
        agentIP: string
        payload: list of dict/[]
        status_code: string: 200/300 
        message: string
    } 
    """

    logger.info("Node Checks for nodes: {}".format(node_list))
    response = []
    try:
        node_checks_data = list(db_obj.select_from_table(db_obj.NODECHECKS_TABLE_NAME))

        node_list = json.loads(node_list)

        for node_name in node_list:
            for check in node_checks_data:
                if check[2] == node_name:
                    response.append({
                        'NodeName': node_name,
                        'Name': check[3],
                        'ServiceName': check[4],
                        'CheckID': check[0],
                        'Type': check[5],
                        'Notes': check[6],
                        'Output': check[7],
                        'Status': check[8]
                    })

        return json.dumps({
            "agentIP": '',
            "payload": response,
            "status_code": "200",
            "message": "OK"
        })
    except Exception as e:
        logger.exception("Error in get_multi_node_check: " + str(e))
        return json.dumps({
            "payload": [],
            "status_code": "300",
            "message": "Could not load node checks."
        })


@time_it
def get_faults(dn):
    """
    Get List of Faults from APIC related to the given Modular object.
    """
    aci_util_obj = apic_utils.AciUtils()
    faults_resp = aci_util_obj.get_ap_epg_faults(dn)

    if faults_resp:
        faults_payload = []
        faults_list = faults_resp.get("faultRecords")
        for fault in faults_list:
            fault_attr = fault.get("faultRecord").get("attributes")
            fault_dict = {
                "code": fault_attr.get("code"),
                "severity": fault_attr.get("severity"),
                "affected": fault_attr.get("affected"),
                "descr": fault_attr.get("descr"),
                "created": fault_attr.get("created"),
                "cause": fault_attr.get("cause")
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


@time_it
def get_events(dn):
    """
    Get List of Events related to the given MO.
    """
    aci_util_obj = apic_utils.AciUtils()
    events_resp = aci_util_obj.get_ap_epg_events(dn)

    if events_resp:
        events_payload = []
        events_list = events_resp.get("eventRecords")
        for event in events_list:
            event_attr = event.get("eventRecord").get("attributes")
            event_dict = {
                "code": event_attr.get("code"),
                "severity": event_attr.get("severity"),
                "affected": event_attr.get("affected"),
                "descr": event_attr.get("descr"),
                "created": event_attr.get("created"),
                "cause": event_attr.get("cause")
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


@time_it
def get_audit_logs(dn):
    """
    Get List of Audit Log Records related to the given MO.
    """

    aci_util_obj = apic_utils.AciUtils()
    audit_logs_resp = aci_util_obj.get_ap_epg_audit_logs(dn)

    if audit_logs_resp:
        audit_logs_payload = []
        audit_logs_list = audit_logs_resp.get("auditLogRecords")
        for audit_log in audit_logs_list:
            audit_log_attr = audit_log.get("aaaModLR").get("attributes")
            audit_log_dict = {
                "affected": audit_log_attr.get("affected"),
                "descr": audit_log_attr.get("descr"),
                "created": audit_log_attr.get("created"),
                "id": audit_log_attr.get("id"),
                "action": audit_log_attr.get("ind"),
                "user": audit_log_attr.get("user")
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


@time_it
def get_children_ep_info(dn, mo_type, mac_list):
    aci_util_obj = apic_utils.AciUtils()
    if mo_type == "ep":
        mac_list = mac_list.split(",")
        mac_query_filter_list = []
        for mac in mac_list:
            mac_query_filter_list.append('eq(fvCEp.mac,"' + mac + '")')
        mac_query_filter = ",".join(mac_query_filter_list)

        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&query-target-filter=or(' + \
            mac_query_filter + \
            ')&rsp-subtree=children&rsp-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsToVm'
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
                "ip": ep_attr.get("ip"),
                "mac": ep_attr.get("mac"),
                "mcast_addr": mcast_addr,
                "learning_source": ep_attr.get("lcC"),
                "encap": ep_attr.get("encap"),
                "ep_name": ep_info.get("vm_name"),
                "hosting_server_name": ep_info.get("hosting_servername"),
                "iface_name": ep_info.get("interfaces"),
                "ctrlr_name": ep_info.get("controller")
            }
            ep_info_list.append(ep_info_dict)
        return json.dumps({
            "status_code": "200",
            "message": "OK",
            "payload": ep_info_list
        })
    except Exception as e:
        logger.exception(
            "Exception while getting Children Ep Info : " + str(e))
        return json.dumps({
            "status_code": "300",
            "message": {'errors': str(e)},
            "payload": []
        })


@time_it
def get_configured_access_policies(tn, ap, epg):
    aci_util_obj = apic_utils.AciUtils()
    cap_url = "/mqapi2/deployment.query.json?mode=epgtoipg&tn=" + \
        tn + "&ap=" + ap + "&epg=" + epg
    cap_resp = aci_util_obj.get_mo_related_item("", cap_url, "other_url")
    cap_list = []
    try:
        for cap in cap_resp:
            cap_dict = {
                "domain": "",
                "switch_prof": "",
                "aep": "",
                "iface_prof": "",
                "pc_vpc": "",
                "node": "",
                "path_ep": "",
                "vlan_pool": ""
            }
            cap_attr = cap["syntheticAccessPolicyInfo"]["attributes"]
            if re.search("/vmmp-", cap_attr["domain"]):
                # Get Domain Name of Configure Access Policy
                cap_vmm_prof = cap_attr["domain"].split(
                    "/vmmp-")[1].split("/")[0]
            else:
                logger.error("Attribute {} not found".format("domain"))
                cap_vmm_prof = ''

            if re.search("/dom-", cap_attr["domain"]):
                cap_domain_name = cap_attr["domain"].split("/dom-")[1]
            else:
                logger.error("Attribute {} not found".format("domain"))
                cap_domain_name = ''

            cap_dict["domain"] = cap_vmm_prof + "/" + cap_domain_name
            if re.search("/nprof-", cap_attr["nodeP"]):
                cap_dict["switch_prof"] = cap_attr["nodeP"].split("/nprof-")[1]
            else:
                logger.error("Attribute {} not found".format("nodeP"))

            if re.search("/attentp-", cap_attr["attEntityP"]):
                cap_dict["aep"] = cap_attr["attEntityP"].split("/attentp-")[1]
            else:
                logger.error("Attribute {} not found".format("attEntityP"))

            if re.search("/accportprof-", cap_attr["accPortP"]):
                cap_dict["iface_prof"] = cap_attr["accPortP"].split(
                    "/accportprof-")[1]
            else:
                logger.error("Attribute {} not found".format("accPortP"))

            if re.search("/accportgrp-", cap_attr["accBndlGrp"]):
                cap_dict["pc_vpc"] = cap_attr["accBndlGrp"].split(
                    "/accportgrp-")[1]
            elif re.search("/accbundle-", cap_attr["accBndlGrp"]):
                cap_dict["pc_vpc"] = cap_attr["accBndlGrp"].split(
                    "/accbundle-")[1]
            pc_pvc = re.search('\w+\/\w+\/\w+\/\w+-(.*)',
                               cap_attr["accBndlGrp"])
            if pc_pvc:
                cap_dict["pc_vpc"] = pc_pvc.groups()[0]
            else:
                logger.error("Attribute {} not found".format("accBndlGrp"))

            cap_dict["node"] = aci_util_obj.get_node_from_interface(
                cap_attr["pathEp"])
            if not cap_dict["node"]:
                logger.error("Attribute {} not found".format("node"))

            if re.search("/pathep-", cap_attr["pathEp"]):
                cap_dict["path_ep"] = cap_attr["pathEp"].split(
                    "/pathep-")[1][1:-1]
            else:
                logger.error("Attribute {} not found".format("pathEP"))

            if re.search("/from-", cap_attr["vLanPool"]):
                cap_dict["vlan_pool"] = cap_attr["vLanPool"].split("/from-")[1]
            else:
                logger.error("Attribute {} not found".format("vLanpool"))
            cap_list.append(cap_dict)

        return json.dumps({
            "status_code": "200",
            "message": "",
            "payload": cap_list
        })
    except Exception as ex:
        return json.dumps({
            "status_code": "300",
            "message": {'errors': str(ex)},
            "payload": []
        })

def get_to_epg(dn):
    """Function to get TO_EPG from dn 

    Arguments:
        dn {str} -- domain name str
        eg: "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Services"

    Returns:
        str -- TO EPG str
        eg: AppDynamics/AppD-AppProfile1/AppD-Services
    """
    epg = ''
    tn = ''
    ap = ''
    if re.search("/tn-", dn):
        tn = dn.split("/tn-")[1].split("/")[0]
    else:
        logger.error("attribute 'tn' not found in epgDn")

    if re.search("/ap-", dn):
        ap = dn.split("/ap-")[1].split("/")[0]
    elif re.match('(\w+|-)\/(\w+|-)+\/\w+-(.*)', dn):
        full_ap = dn.split('/')[2]
        ap = re.split('\w+-(.*)', full_ap)[1]
    else:
        logger.error("attribute 'ap' not found in epgDn")

    if re.search("/epg-", dn):
        epg = dn.split("/epg-")[1].split("/")[0]
    elif re.match('(\w+|-)\/(\w+|-)+\/\w+-(.*)', dn):
        full_epg = dn.split('/')[3]
        epg = re.split('\w+-(.*)', full_epg)[1]
    else:
        logger.error("attribute 'epg' not found in epgDn")

    to_epg = tn + "/" + ap + "/" + epg
    return to_epg

@time_it
def get_subnets(dn):
    """
    Gets the Subnets Information for an EPG
    """
    aci_util_obj = apic_utils.AciUtils()
    subnet_query_string = "query-target=children&target-subtree-class=fvSubnet"
    subnet_resp = aci_util_obj.get_mo_related_item(dn, subnet_query_string, "")
    subnet_list = []
    try:
        for subnet in subnet_resp:
            subnet_dict = {
                "ip": "",
                "to_epg": "",
                "epg_alias": ""
            }
            subnet_attr = subnet.get("fvSubnet").get("attributes")
            dn = subnet_attr.get("dn")
            subnet_dict["to_epg"] = get_to_epg(dn)
            subnet_dict["ip"] = subnet_attr["ip"]
            subnet_dict["epg_alias"] = subnet_attr.get("nameAlias", "")
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


@time_it
def get_to_epg_traffic(epg_dn):
    """
    Gets the Traffic Details from the given EPG to other EPGs
    """

    aci_util_obj = apic_utils.AciUtils()
    epg_traffic_query_string = 'query-target-filter=eq(vzFromEPg.epgDn,"' + epg_dn + \
        '")&rsp-subtree=full&rsp-subtree-class=vzToEPg,vzRsRFltAtt,vzCreatedBy&rsp-subtree-include=required'
    epg_traffic_resp = aci_util_obj.get_all_mo_instances(
        "vzFromEPg", epg_traffic_query_string)
    if epg_traffic_resp:

        from_epg_dn = epg_dn

        to_epg_traffic_list = []
        to_epg_traffic_set = set()

        try:
            for epg_traffic in epg_traffic_resp:
                to_epg_children = epg_traffic["vzFromEPg"]["children"]
                epg_alias = epg_traffic.get("vzFromEPg", {}).get("attributes", {}).get("nameAlias", "")
                type_mapping = {'prov': "Provider", 'cons': "Consumer"}
                contract_type = epg_traffic.get("vzFromEPg", {}).get("attributes", {}).get("membType", "")
                contract_type = type_mapping.get(contract_type, contract_type)
                for to_epg_child in to_epg_children:

                    vz_to_epg_child = to_epg_child["vzToEPg"]
                    to_epg_dn = vz_to_epg_child["attributes"]["epgDn"]
                    parsed_to_epg_dn = get_to_epg(to_epg_dn)

                    flt_attr_children = vz_to_epg_child["children"]
                    for flt_attr in flt_attr_children:
                        to_epg_traffic_dict = {
                            "to_epg": parsed_to_epg_dn,
                            "contract_subj": "",
                            "filter_list": [],
                            "ingr_pkts": "",
                            "egr_pkts": "",
                            "epg_alias": epg_alias,
                            "contract_type": "",
                            "type": contract_type
                        }

                        flt_attr_child = flt_attr["vzRsRFltAtt"]
                        flt_attr_tdn = flt_attr_child["attributes"]["tDn"]

                        traffic_id = parsed_to_epg_dn + "||" + flt_attr_tdn + "||" + contract_type

                        # Check if we have already encountered the filter for a particular destination EPG
                        if traffic_id in to_epg_traffic_set:
                            to_epg_traffic_set.add(traffic_id)
                            continue
                        if re.search("/fp-", flt_attr_tdn):
                            flt_name = flt_attr_tdn.split("/fp-")[1]
                        else:
                            logger.error("filter not found")
                            flt_name = ''
                        flt_attr_subj_dn = flt_attr_child["children"][0]["vzCreatedBy"]["attributes"]["ownerDn"]
                        if re.search("/rssubjFiltAtt-", flt_attr_subj_dn):
                            subj_dn = flt_attr_subj_dn.split(
                                "/rssubjFiltAtt-")[0]
                        else:
                            logger.error("filter attribute subject not found")
                            subj_dn = ''
                        if re.search("/tn-", flt_attr_subj_dn):
                            subj_tn = flt_attr_subj_dn.split(
                                "/tn-")[1].split("/")[0]
                        else:
                            logger.error(
                                "filter attribute subject dn not found")
                            subj_tn = ''

                        if re.search("/brc-", flt_attr_subj_dn):
                            subj_ctrlr = flt_attr_subj_dn.split(
                                "/brc-")[1].split("/")[0]
                        else:
                            logger.error("filter attribute ctrlr not found")
                            subj_ctrlr = ''

                        if re.search("/subj-", flt_attr_subj_dn):
                            subj_name = flt_attr_subj_dn.split(
                                "/subj-")[1].split("/")[0]
                        else:
                            logger.error(
                                "filter attribute subj_name not found")
                            subj_name = ''

                        contract_subject = subj_tn + "/" + subj_ctrlr + "/" + subj_name
                        flt_list = get_filter_list(flt_attr_tdn, aci_util_obj)
                        ingr_pkts, egr_pkts = get_ingress_egress(
                            from_epg_dn, to_epg_dn, subj_dn, flt_name, aci_util_obj)

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
            logger.exception(
                "Exception while fetching To EPG Traffic List : \n" + str(ex))

            return json.dumps({
                "status_code": "300",
                "message": {'errors': str(ex)},
                "payload": []
            })
    else:
        logger.error("Could not get Traffic Data related to EPG")
        return json.dumps({
            "status_code": "300",
            "message": "Exception while fetching Traffic Data related to EPG",
            "payload": []
        })


@time_it
def get_ingress_egress(from_epg_dn, to_epg_dn, subj_dn, flt_name, aci_util_obj):
    """
    Returns the Cumulative Ingress and Egress packets information for the last 15 minutes
    """
    cur_aggr_stats_query_url = "/api/node/mo/" + from_epg_dn + \
        "/to-[" + to_epg_dn + "]-subj-[" + subj_dn + "]-flt-" + \
        flt_name + "/CDactrlRuleHitAg15min.json"
    cur_aggr_stats_list = aci_util_obj.get_mo_related_item(
        "", cur_aggr_stats_query_url, "other_url")

    if cur_aggr_stats_list:
        cur_ag_stat_attr = cur_aggr_stats_list[0]["actrlRuleHitAg15min"]["attributes"]
        ingr_pkts = cur_ag_stat_attr.get("ingrPktsCum")
        egr_pkts = cur_ag_stat_attr.get("egrPktsCum")
        return ingr_pkts, egr_pkts
    else:
        return "0", "0"


@time_it
def get_filter_list(flt_dn, aci_util_obj):
    """
    Returns the list of filters for a given destination EPG
    """
    flt_list = []
    flt_entry_query_string = "query-target=children&target-subtree-class=vzRFltE"
    flt_entries = aci_util_obj.get_mo_related_item(
        flt_dn, flt_entry_query_string, "")

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

        flt_str = ether_type + ":" + protocol + ":" + src_str + " to " + dest_str

        flt_list.append(flt_str)

    return flt_list


def get_all_interfaces(interfaces):
    interface_list = ''
    for interface in interfaces:
        if re.search("/pathep-\[", interface):
            if interface_list != '':
                interface_list += (', ' +
                                   str(interface.split("/pathep-")[1][1:-1]))
            else:
                interface_list += str(interface.split("/pathep-")[1][1:-1])
        elif re.search("/pathgrp-", interface):
            if interface_list != '':
                interface_list += (', ' +
                                   str(interface.split("/pathgrp-")[1][1:-1])+"(vmm)")
            else:
                interface_list += str(interface.split("/pathgrp-")
                                      [1][1:-1]+"(vmm)")
        else:
            logger.error("Incompetible format of Interfaces found")
    return interface_list


@time_it
def read_creds():
    try:
        logger.info('Reading agents.')

        # handle db read faliure, just pass empty list from there
        agents = list(db_obj.select_from_table(db_obj.LOGIN_TABLE_NAME))
        if not agents:
            logger.info('Agents List Empty.')
            return json.dumps({'payload': [], 'status_code': '300', 'message': 'Agents not found'})
        payload = []
        for agent in agents:
            decoded_token = base64.b64decode(agent[3]).decode('ascii')
            consul_obj = Consul(agent[0], agent[1], decoded_token, agent[2])
            status, message = consul_obj.check_connection()

            datacenter = ''
            if status:
                datacenter = consul_obj.datacenter()
                if datacenter == '-':
                    datacenter = agent[5]

            if agent[4] != status or agent[5] != datacenter:
                agent_val = (agent[0], agent[1], agent[2], agent[3], status, datacenter)
                db_obj.insert_and_update(db_obj.LOGIN_TABLE_NAME, agent_val, {'agent_ip': agent[0], 'port': agent[1]})

            payload.append({
                'ip': agent[0],
                'port': agent[1],
                'protocol': agent[2],
                'token': agent[3],
                'status': status,
                'datacenter': datacenter
            })

        logger.debug('Read cretds resopnse: {}'.format(str(payload)))
        return json.dumps({'payload': payload, 'status_code': '200', 'message': 'OK'})

    except Exception as e:
        logger.exception('Error in read credentials: ' + str(e))
        return json.dumps({'payload': [], 'status_code': '300', 'message': 'Could not load the credentials.'})


@time_it
def write_creds(new_agent):
    try:
        new_agent = json.loads(new_agent)[0] # UI returns list of 1 object
        logger.info('Writing agent: {}:{}'.format(new_agent.get('ip'), str(new_agent.get('port'))))
        agents = list(db_obj.select_from_table(
                        db_obj.LOGIN_TABLE_NAME,
                        {'agent_ip': new_agent.get('ip'), 'port': new_agent.get('port')}))

        if agents:
            message = 'Agent ' + new_agent.get('ip') + ':' + str(new_agent.get('port')) + ' already exists.'
            logger.error(message)
            return json.dumps({'payload': new_agent, 'status_code': '300', 'message': message})

        if not new_agent['token']:
            new_agent['token'] = ''
        consul_obj = Consul(new_agent.get('ip'), new_agent.get('port'), new_agent.get('token'), new_agent.get('protocol'))
        status, message = consul_obj.check_connection()

        datacenter = '-'
        if status:
            datacenter = consul_obj.datacenter()

        new_agent['datacenter'] = datacenter
        new_agent['status'] = status
        new_agent['token'] = base64.b64encode(new_agent['token'].encode('ascii')).decode('ascii')

        db_obj.insert_into_table(db_obj.LOGIN_TABLE_NAME, 
                        [   new_agent.get('ip'),
                            new_agent.get('port'),
                            new_agent.get('protocol'),
                            new_agent.get('token'),
                            new_agent.get('status'),
                            new_agent.get('datacenter')
                        ])

        if status:
            return json.dumps({'payload': new_agent, 'status_code': '200', 'message': 'OK'})
        else:
            return json.dumps({'payload': new_agent, 'status_code': '301', 'message': str(message)})

    except Exception as e:
        logger.exception('Error in write credentials: ' + str(e))
        return json.dumps({'payload': [], 'status_code': '300', 'message': 'Could not write the credentials.'})


@time_it
def update_creds(update_input):
    try:
        logger.info('Updating agent: {}'.format(update_input))

        update_input = json.loads(update_input)
        old_agent = update_input.get('oldData')
        new_agent = update_input.get('newData')

        agents = list(db_obj.select_from_table(
            db_obj.LOGIN_TABLE_NAME).fetchall())
        if not agents:
            logger.info('Agents List Empty.')
            return json.dumps({'payload': [], 'status_code': '300', 'message': 'Agents not found'})

        if not (old_agent.get('ip') == new_agent.get('ip') and old_agent.get('port') == new_agent.get('port')):
            new_agent_db_data = db_obj.select_from_table(db_obj.LOGIN_TABLE_NAME,
                                        {'agent_ip': new_agent.get('ip'), 'port': new_agent.get('port')})
            new_agent_db_data = new_agent_db_data.fetchone()
            if new_agent_db_data:
                message = 'Agent ' + \
                    new_agent.get('ip') + ':' + \
                    str(new_agent.get('port')) + ' already exists.'
                logger.error(message)
                return json.dumps({'payload': new_agent, 'status_code': '300', 'message': message})
            
        for agent in agents:
            if old_agent.get('ip') == agent[0] and old_agent.get('port') == int(agent[1]):
                if new_agent.get('token') == agent[3]:
                    new_agent['token'] = base64.b64decode(new_agent.get('token')).decode('ascii')
                consul_obj = Consul(new_agent.get('ip'), new_agent.get('port'), new_agent.get('token'), new_agent.get('protocol'))

                status, message = consul_obj.check_connection()

                datacenter = ''
                if status:
                    datacenter = consul_obj.datacenter()
                    if datacenter == '-':
                        datacenter = agent[5]

                new_agent['datacenter'] = datacenter
                new_agent['status'] = status
                new_agent['token'] = base64.b64encode(new_agent['token'].encode('ascii')).decode('ascii')
                db_obj.insert_and_update(db_obj.LOGIN_TABLE_NAME, [new_agent.get('ip'),
                        new_agent.get('port'),
                        new_agent.get('protocol'),
                        new_agent.get('token'),
                        new_agent.get('status'),
                        new_agent.get('datacenter')
                    ], {'agent_ip': old_agent.get(
                    'ip'), 'port': old_agent.get('port')})

                if status:
                    return json.dumps({'payload': new_agent, 'status_code': '200', 'message': 'OK'})
                else:
                    return json.dumps({'payload': new_agent, 'status_code': '301', 'message': message})

    except Exception as e:
        logger.exception('Error in update credentials: ' + str(e))
        return json.dumps({'payload': [], 'status_code': '300', 'message': 'Could not update the credentials.'})


@time_it
def delete_creds(agent_data):
    try:
        logger.info('Deleting agent {}'.format(str(agent_data)))
        agent_data = json.loads(agent_data)

        # Agent deleted
        result = db_obj.delete_from_table(db_obj.LOGIN_TABLE_NAME, {'agent_ip': agent_data.get('ip'), 'port': agent_data.get('port')})

        logger.info('Agent {} deleted'.format(str(agent_data)))

        agent_dc = agent_data.get('datacenter')
        agent_list = list(db_obj.select_from_table(db_obj.LOGIN_TABLE_NAME))
        agent_list = [agent for agent in agent_list if agent[5] == agent_dc]
        if not agent_list:
            mappings = list(db_obj.select_from_table(db_obj.MAPPING_TABLE_NAME))
            for mapping in mappings:
                if mapping[2] == agent_dc:
                    db_obj.delete_from_table(db_obj.MAPPING_TABLE_NAME, {
                        'ip': mapping[0],
                        'dn': mapping[1],
                        'datacenter': mapping[2]
                    })
            logger.info('Mapping for Datacenter {} deleted'.format(str(agent_dc)))

        # Delete all the data fetched by this agent
        agent_addr = agent_data.get('ip') + ':' + str(agent_data.get('port'))
        
        # Delete Node data wrt this agent
        node_data = list(db_obj.select_from_table(db_obj.NODE_TABLE_NAME))
        for node in node_data:
            agents = node[4]
            if agent_addr not in agents:
                continue
            if len(agents) == 1:
                db_obj.delete_from_table(db_obj.NODE_TABLE_NAME,{'node_id': node[0]})
            else:
                node[4].remove(agent_addr)
                db_obj.insert_and_update(db_obj.NODE_TABLE_NAME, node, {'node_id': node[0]})
        logger.info('Agent {}\'s Node data deleted'.format(str(agent_addr)))

        # Delete Service data wrt this agent
        service_data = list(db_obj.select_from_table(db_obj.SERVICE_TABLE_NAME))
        for service in service_data:
            agents = service[10]
            if agent_addr not in agents:
                continue
            if len(agents) == 1:
                db_obj.delete_from_table(db_obj.SERVICE_TABLE_NAME,{'service_id': service[0],'node_id': service[1]})
            else:
                service[10].remove(agent_addr)
                db_obj.insert_and_update(db_obj.SERVICE_TABLE_NAME, service, {'service_id': service[0],'node_id': service[1]})
        logger.info('Agent {}\'s Service data deleted'.format(str(agent_addr)))

        # Delete Node Check data wrt this agent
        node_checks_data = list(db_obj.select_from_table(db_obj.NODECHECKS_TABLE_NAME))
        for node in node_checks_data:
            agents = node[9]
            if agent_addr not in agents:
                continue
            if len(agents) == 1:
                db_obj.delete_from_table(db_obj.NODECHECKS_TABLE_NAME,{'check_id': node[0], 'node_id': node[1]})
            else:
                node[9].remove(agent_addr)
                db_obj.insert_and_update(db_obj.NODECHECKS_TABLE_NAME, node, {'check_id': node[0], 'node_id': node[1]})
        logger.info('Agent {}\'s NodeChecks data deleted'.format(str(agent_addr)))

        # Delete Service Check data wrt this agent
        service_checks_data = list(db_obj.select_from_table(db_obj.SERVICECHECKS_TABLE_NAME))
        for service in service_checks_data:
            agents = service[8]
            if agent_addr not in agents:
                continue
            if len(agents) == 1:
                db_obj.delete_from_table(db_obj.SERVICECHECKS_TABLE_NAME,{'check_id': service[0],'service_id': service[1]})
            else:
                service[8].remove(agent_addr)
                db_obj.insert_and_update(db_obj.SERVICECHECKS_TABLE_NAME, service, {'check_id': service[0],'service_id': service[1]})
        logger.info('Agent {}\'s ServiceChecks data deleted'.format(str(agent_addr)))

        # it is assumed that no delete call to db would fail
        return json.dumps({'status_code': '200', 'message': 'OK'})
    except Exception as e:
        logger.exception('Error in delete credentials: ' + str(e))
        return json.dumps({'payload': [], 'status_code': '300', 'message': 'Could not delete the credentials.'})


@time_it
def details_flattened(tenant, datacenter):
    """Get correlated Details view data

    return: {
        agentIP: string
        payload: list of dict/{}
        status_code: string: 200/300
        message: string
    }
    """

    logger.info("Details view for tenant: {}".format(tenant))
    try:
        aci_consul_mappings = get_new_mapping(tenant, datacenter)

        apic_data = get_apic_data(tenant)
        consul_data = get_consul_data(datacenter)
        merged_data = merge.merge_aci_consul(tenant, apic_data, consul_data, aci_consul_mappings)

        details_list = []
        for each in merged_data:
            ep = {
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
                    'epgHealth': int(each.get('epg_health')),
                    'consulNode': each.get('node_name'),
                    'nodeChecks': each.get('node_check'),
                }

            services = change_key(each.get('node_services'))
            for service in services:
                record = {}
                record.update(ep)
                record.update(service)
                details_list.append(record)
        logger.debug("Details final data ended: " + str(details_list))

        # TODO: details = [dict(t) for t in set([tuple(d.items()) for d in details_list])]
        return json.dumps({
            "agentIP": ' ', # send ip if needed
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


@time_it
def get_datacenters():
    logger.info('In get datacenters')
    datacenters = []
    try:
        agents = list(db_obj.select_from_table(db_obj.LOGIN_TABLE_NAME))
        if agents:
            dc_list = {}
            for agent in agents:
                datacenter = str(agent[5])
                status = int(agent[4])
                if status == 1:
                    status = True
                else:
                    status = False

                # if the status is False, do not update it
                if datacenter != '-' and dc_list.get(datacenter, True):
                    dc_list[datacenter] = status

            for dc, status in dc_list.items():
                datacenters.append(
                    {
                        'status': status,
                        'datacenter': dc
                    }
                )

        logger.info("Datacenters found: {}".format(str(datacenters)))
        return json.dumps({'payload': datacenters, 'status_code': '200', 'message': 'OK'})
    except Exception as e:
        logger.exception('Error in get datacenters: ' + str(e))
        return json.dumps({'payload': [], 'status_code': '300', 'message': 'Error in fetching datacenters.'})


def post_tenant(tn):
    logger.info('Tenant received: {}'.format(str(tn)))
    try:
        response = list(db_obj.select_from_table(db_obj.TENANT_TABLE_NAME, {'tenant': tn}))
        if not response:
            response = db_obj.insert_into_table(db_obj.TENANT_TABLE_NAME, [tn])
            if not response:
                return json.dumps({'status_code': '300', 'message': 'Tenant not saved'})
        return json.dumps({'status_code': '200', 'message': 'OK'})
    except Exception as e:
        logger.exception('Error in post tenant: ' + str(e))
        return json.dumps({'status_code': '300', 'message': 'Tenant not saved'})


@time_it
def get_consul_data(datacenter):
    consul_data = []
    services = []
    node_data = list(db_obj.select_from_table(db_obj.NODE_TABLE_NAME))
    service_data = list(db_obj.select_from_table(db_obj.SERVICE_TABLE_NAME))
    node_checks_data = list(db_obj.select_from_table(db_obj.NODECHECKS_TABLE_NAME))
    service_checks_data = list(db_obj.select_from_table(db_obj.SERVICECHECKS_TABLE_NAME))
    for service in service_data:
        if service[9] != datacenter:
            continue
        service_dict = {
            'service_id': service[0],
            'node_id': service[1],
            'service_name': service[2],
            'service_ip': service[3],
            'service_port': service[4],
            'service_address': service[5],
            'service_tags': service[6],
            'service_kind': service[7],
            'service_namespace': service[8],
            'service_checks': {}
        }
        for check in service_checks_data:
            if check[1] == service[0]:
                status = check[7]
                check_dict = service_dict['service_checks']
                if 'passing' == status.lower():
                    if check_dict.get('passing'):
                        check_dict['passing'] += 1
                    else:
                        check_dict['passing'] = 1
                elif 'warning' == status.lower():
                    if check_dict.get('warning'):
                        check_dict['warning'] += 1
                    else:
                        check_dict['warning'] = 1
                else:
                    if check_dict.get('failing'):
                        check_dict['failing'] += 1
                    else:
                        check_dict['failing'] = 1
                service_dict['service_checks']  = check_dict
        services.append(service_dict)

    for node in node_data:
        if node[3] != datacenter:
            continue
        node_dict = {
            'node_id': node[0],
            'node_name': node[1],
            'node_ips': node[2],
            'node_check': {},
            'node_services': []
            }
        for check in node_checks_data:
            if check[1] == node[0]:
                status = check[8]
                check_dict = node_dict['node_check']
                if 'passing' == status.lower():
                    if check_dict.get('passing'):
                        check_dict['passing'] += 1
                    else:
                        check_dict['passing'] = 1
                elif 'warning' == status.lower():
                    if check_dict.get('warning'):
                        check_dict['warning'] += 1
                    else:
                        check_dict['warning'] = 1
                else:
                    if check_dict.get('failing'):
                        check_dict['failing'] += 1
                    else:
                        check_dict['failing'] = 1
                node_dict['node_check'] = check_dict
        for service in services:
            if service['node_id'] == node[0]:
                node_dict['node_services'].append(service)
        consul_data.append(node_dict)

    return consul_data


@time_it
def get_apic_data(tenant):
    apic_data = []
    ep_data = list(db_obj.select_from_table(db_obj.EP_TABLE_NAME))
    epg_data = list(db_obj.select_from_table(db_obj.EPG_TABLE_NAME))
    for ep in ep_data:
        if ep[2] != tenant:
            continue
        for epg in epg_data:
            ep_dn = '/'.join(ep[3].split('/')[:4])
            if ep_dn == epg[0]:
                apic_data.append({
                    'AppProfile': epg[7],
                    'EPG': epg[2],
                    'CEP-Mac': ep[0],
                    'IP': ep[1],
                    'Interfaces': ep[5],
                    'VM-Name': ep[4],
                    'BD': epg[3],
                    'VMM-Domain': ep[6],
                    'Contracts': epg[4],
                    'VRF': epg[5],
                    'dn': ep_dn,
                    'controllerName': ep[7],
                    'hostingServerName': ep[11],
                    'learningSource': ep[8],
                    'epg_health': epg[6]
                })
                break

    return apic_data
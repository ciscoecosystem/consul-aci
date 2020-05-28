import os
import re
import json
import time
import socket
import datetime
import base64
from flask import Flask


from . import consul_merge
from . import recommend_utils
from . import consul_tree_parser
from consul_utils import Consul
from decorator import time_it

import aci_utils
import alchemy_core
import custom_logger


app = Flask(__name__, template_folder="../UIAssets",
            static_folder="../UIAssets/public")
app.secret_key = "consul_key"
app.debug = True  # See use

logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")

db_obj = alchemy_core.Database()
db_obj.create_tables()

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
        logger.exception("Could not fetch agent list for datacenter {}, Error: {}".format(
            data_center, str(e)))
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

        # Get APIC data
        ep_data = list(db_obj.select_from_table(db_obj.EP_TABLE_NAME))
        parsed_eps = []
        for ep in ep_data:
            parsed_eps.append(
                {
                    'dn': ep[3],
                    'IP': ep[1],
                    'tenant': ep[2],
                    'cep_ip': ep[12],
                }
            )

        # Get consul data
        consul_data = get_consul_data() # db_obj.join(datacenter=True)
        ip_list = []
        for node in consul_data:
            ip_list += node.get('node_ips', [])
            # For fetching ips of services.
            for service in node.get('node_services', []):
                # check ip is not empty string
                if service.get('service_ip', ''):
                    ip_list.append(service.get('service_ip'))

        aci_consul_mappings = recommend_utils.recommanded_eps(
            list(set(ip_list)), parsed_eps)  # TODO: handle empty response

        if not aci_consul_mappings:
            logger.info("Empty ACI and Consul mappings.")
            return json.dumps({
                "agentIP": ' ',  # TODO: Is this required in UI, if no: change call, if yes return right val
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
                    already_mapped_data = all_datacenter_mapping.get(
                        datacenter)

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

        mapping_dict['target_cluster'] = [
            node for node in current_mapping if node.get('disabled') == False]

        for new_object in aci_consul_mappings:
            mapping_dict['source_cluster'].append(new_object)

        return json.dumps({
            "agentIP": ' ',  # TODO: what to return here
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
        end_time = datetime.datetime.now()
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
                    already_mapped_data = all_datacenter_mapping.get(
                        datacenter)

        for mapping in mapped_data_dict:
            if mapping.get('ipaddress') != "":
                data_list.append({'ipaddress': mapping.get(
                    'ipaddress'), 'domainName': mapping['domains'][0]['domainName'], 'disabled': False})

        if not data_list:
            all_datacenter_mapping.pop(datacenter)
        else:
            data_list = parse_mapping_before_save(
                already_mapped_data, data_list)
            all_datacenter_mapping[datacenter] = data_list

        with open(mapppings_file_path, 'w') as fwrite:
            json.dump(all_datacenter_mapping, fwrite)

        return json.dumps({"payload": "Saved Mappings", "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception(
            "Could not save mappings to the database. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not save mappings to the database."})
    finally:
        end_time = datetime.datetime.now()
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
                    aci_consul_mappings = all_datacenter_mapping.get(
                        datacenter)
        aci_obj = aci_utils.ACI_Utils()
        aci_data = aci_obj.main(tenant)
        agent = get_agent_list(datacenter)[0]
        consul_obj = Consul(agent.get('ip'), agent.get(
            'port'), agent.get('token'), agent.get('protocol'))
        consul_data = consul_obj.get_consul_data()

        merged_data = consul_merge.merge_aci_consul(
            tenant, aci_data, consul_data, aci_consul_mappings)

        logger.debug("ACI Consul mapped data: {}".format(merged_data))

        response = json.dumps(consul_tree_parser.consul_tree_dict(merged_data))
        logger.debug("Final Tree data: {}".format(response))

        return json.dumps({
            "agentIP": agent.get('ip'),  # TODO: send valid ip
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
        end_time = datetime.datetime.now()
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
                    aci_consul_mappings = all_datacenter_mapping.get(
                        datacenter)
        aci_obj = aci_utils.ACI_Utils()
        aci_data = aci_obj.main(tenant)
        agent = get_agent_list(datacenter)[0]
        consul_obj = Consul(agent.get('ip'), agent.get(
            'port'), agent.get('token'), agent.get('protocol'))
        consul_data = consul_obj.get_consul_data()

        merged_data = consul_merge.merge_aci_consul(
            tenant, aci_data, consul_data, aci_consul_mappings)

        details_list = []
        for each in merged_data:
            epg_health = aci_obj.get_epg_health(
                str(tenant), str(each['AppProfile']), str(each['EPG']))
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
        logger.exception(
            "Could not load the Details. Error: {}".format(str(e)))
        return json.dumps({
            "payload": {},
            "status_code": "300",
            "message": "Could not load the Details."
        })
    finally:
        end_time = datetime.datetime.now()
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
                logger.debug(
                    "Mapping found with ipaddress for "+str(map_object))
                target.append({'domainName': entry.get(
                    'domainName'), 'ipaddress': map_object.get('ipaddress'), 'disabled': False})
    return target


def change_key(services):
    final_list = []
    if services:
        for service in services:
            final_list.append({
                'service': service.get('service_name'),
                'serviceInstance': service.get('service_id'),
                'Port': service.get('service_port'),
                'serviceTags': service.get('service_tags'),
                'serviceKind': service.get('service_kind'),
                'serviceChecks': service.get('service_checks'),
                'serviceNamespace': service.get('service_namespace')
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

    logger.info("Service Check for service: {}, {}".format(
        service_name, service_id))
    start_time = datetime.datetime.now()
    try:
        agent = get_agent_list(datacenter)[0]
        consul_obj = Consul(agent.get('ip'), agent.get(
            'port'), agent.get('token'), agent.get('protocol'))
        response = consul_obj.detailed_service_check(service_name, service_id)
        logger.debug('Response of Service chceck: {}'.format(response))

        return json.dumps({
            "agentIP": agent.get('ip'),
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
    finally:
        end_time = datetime.datetime.now()
        logger.info("Time for get_service_check: " +
                    str(end_time - start_time))


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
        consul_obj = Consul(agent.get('ip'), agent.get(
            'port'), agent.get('token'), agent.get('protocol'))
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
        end_time = datetime.datetime.now()
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
        consul_obj = Consul(agent.get('ip'), agent.get(
            'port'), agent.get('token'), agent.get('protocol'))
        service_list = json.loads(service_list)

        for service_dict in service_list:
            service_name = service_dict["Service"]
            service_id = service_dict["ServiceID"]

            response += consul_obj.detailed_service_check(
                service_name, service_id)

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
        end_time = datetime.datetime.now()
        logger.info("Time for get_service_check_ep: " +
                    str(end_time - start_time))


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
        consul_obj = Consul(agent.get('ip'), agent.get(
            'port'), agent.get('token'), agent.get('protocol'))
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
        end_time = datetime.datetime.now()
        logger.info("Time for get_service_check_ep: " +
                    str(end_time - start_time))


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


def get_children_ep_info(dn, mo_type, mac_list):
    start_time = datetime.datetime.now()
    aci_util_obj = aci_utils.ACI_Utils()
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
                "ep_name": ep_info.get("VM-Name"),
                "hosting_server_name": ep_info.get("hostingServerName"),
                "iface_name": ep_info.get("Interfaces"),
                "ctrlr_name": ep_info.get("controllerName")
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
    finally:
        end_time = datetime.datetime.now()
        logger.info("Time for get_children_ep_info: " +
                    str(end_time - start_time))


def get_configured_access_policies(tn, ap, epg):
    start_time = datetime.datetime.now()
    aci_util_obj = aci_utils.ACI_Utils()
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
                raise Exception("Attribute {} not found".format("domain"))
            if re.search("/dom-", cap_attr["domain"]):
                cap_domain_name = cap_attr["domain"].split("/dom-")[1]
            else:
                logger.error("Attribute {} not found".format("domain"))
                raise Exception("Attribute {} not found".format("domain"))
            cap_dict["domain"] = cap_vmm_prof + "/" + cap_domain_name
            if re.search("/nprof-", cap_attr["nodeP"]):
                cap_dict["switch_prof"] = cap_attr["nodeP"].split("/nprof-")[1]
            else:
                logger.error("Attribute {} not found".format("nodeP"))
                raise Exception("Attribute {} not found".format("nodeP"))
            if re.search("/attentp-", cap_attr["attEntityP"]):
                cap_dict["aep"] = cap_attr["attEntityP"].split("/attentp-")[1]
            else:
                logger.error("Attribute {} not found".format("attEntityP"))
                raise Exception("Attribute {} not found".format("attEntityP"))
            if re.search("/accportprof-", cap_attr["accPortP"]):
                cap_dict["iface_prof"] = cap_attr["accPortP"].split(
                    "/accportprof-")[1]
            else:
                logger.error("Attribute {} not found".format("accPortP"))
                raise Exception("Attribute {} not found".format("accPortP"))
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
                raise Exception("Attribute {} not found".format("accBndlGrp"))
            cap_dict["node"] = aci_util_obj.get_node_from_interface(
                cap_attr["pathEp"])
            if not cap_dict["node"]:
                logger.error("Attribute {} not found".format("node"))
                raise Exception("attribute node not found")
            if re.search("/pathep-", cap_attr["pathEp"]):
                cap_dict["path_ep"] = cap_attr["pathEp"].split(
                    "/pathep-")[1][1:-1]
            else:
                logger.error("Attribute {} not found".format("pathEP"))
                raise Exception("Attribute {} not found".format("pathEp"))
            if re.search("/from-", cap_attr["vLanPool"]):
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
            "message": {'errors': str(ex)},
            "payload": []
        })
    finally:
        end_time = datetime.datetime.now()
        logger.info("Time for get_configured_access_policies: " +
                    str(end_time - start_time))


@time_it
def get_subnets(dn):
    """
    Gets the Subnets Information for an EPG
    """
    aci_util_obj = aci_utils.ACI_Utils()
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


def get_to_epg_traffic(epg_dn):
    """
    Gets the Traffic Details from the given EPG to other EPGs
    """

    start_time = datetime.datetime.now()
    aci_util_obj = aci_utils.ACI_Utils()
    epg_traffic_query_string = 'query-target-filter=eq(vzFromEPg.epgDn,"' + epg_dn + \
        '")&rsp-subtree=full&rsp-subtree-class=vzToEPg,vzRsRFltAtt,vzCreatedBy&rsp-subtree-include=required'
    epg_traffic_resp = aci_util_obj.get_all_mo_instances(
        "vzFromEPg", epg_traffic_query_string)
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
                    if re.search("/tn-", to_epg_dn):
                        tn = to_epg_dn.split("/tn-")[1].split("/")[0]
                    else:
                        logger.error("attribute 'tn' not found in epgDn")
                        raise Exception("attribute 'tn' not found in epgDn")
                    if re.search("/ap-", to_epg_dn):
                        ap = to_epg_dn.split("/ap-")[1].split("/")[0]
                    elif re.match('(\w+|-)\/(\w+|-)+\/\w+-(.*)', to_epg_dn):
                        full_ap = to_epg_dn.split('/')[2]
                        ap = re.split('\w+-(.*)', full_ap)[1]
                    else:
                        logger.error("attribute 'ap' not found in epgDn")
                        raise Exception("attribute 'ap' not found in epgDn")
                    if re.search("/epg-", to_epg_dn):
                        epg = to_epg_dn.split("/epg-")[1]
                    elif re.match('(\w+|-)\/(\w+|-)+\/\w+-(.*)', to_epg_dn):
                        full_epg = to_epg_dn.split('/')[3]
                        epg = re.split('\w+-(.*)', full_epg)[1]
                    else:
                        logger.error("attribute 'epg' not found in epgDn")
                        raise Exception("attribute 'epg' not found in epgDn")
                    parsed_to_epg_dn = tn + "/" + ap + "/" + epg

                    flt_attr_children = vz_to_epg_child["children"]

                    for flt_attr in flt_attr_children:
                        to_epg_traffic_dict = {
                            "to_epg": "",
                            "contract_subj": "",
                            "filter_list": [],
                            "ingr_pkts": "",
                            "egr_pkts": "",
                            "epg_alias": "",
                            "contract_type": ""
                        }

                        to_epg_traffic_dict["to_epg"] = parsed_to_epg_dn

                        flt_attr_child = flt_attr["vzRsRFltAtt"]
                        flt_attr_tdn = flt_attr_child["attributes"]["tDn"]

                        traffic_id = parsed_to_epg_dn + "||" + flt_attr_tdn

                        # Check if we have already encountered the filter for a particular destination EPG
                        if traffic_id in to_epg_traffic_set:
                            to_epg_traffic_set.add(traffic_id)
                            continue
                        if re.search("/fp-", flt_attr_tdn):
                            flt_name = flt_attr_tdn.split("/fp-")[1]
                        else:
                            logger.error("filter not found")
                            raise Exception("filter not found")
                        flt_attr_subj_dn = flt_attr_child["children"][0]["vzCreatedBy"]["attributes"]["ownerDn"]
                        if re.search("/rssubjFiltAtt-", flt_attr_subj_dn):
                            subj_dn = flt_attr_subj_dn.split(
                                "/rssubjFiltAtt-")[0]
                        else:
                            logger.error("filter attribute subject not found")
                            raise Exception(
                                "filter attribute subject not found")
                        if re.search("/tn-", flt_attr_subj_dn):
                            subj_tn = flt_attr_subj_dn.split(
                                "/tn-")[1].split("/")[0]
                        else:
                            logger.error(
                                "filter attribute subject dn not found")
                            raise Exception(
                                "filter attribute subject dn not found")

                        if re.search("/brc-", flt_attr_subj_dn):
                            subj_ctrlr = flt_attr_subj_dn.split(
                                "/brc-")[1].split("/")[0]
                        else:
                            logger.error("filter attribute ctrlr not found")
                            raise Exception("filter attribute ctrlr not found")
                        if re.search("/subj-", flt_attr_subj_dn):
                            subj_name = flt_attr_subj_dn.split(
                                "/subj-")[1].split("/")[0]
                        else:
                            logger.error(
                                "filter attribute subj_name not found")
                            raise Exception(
                                "filter attribute subj_name not found")

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
        finally:
            end_time = datetime.datetime.now()
            logger.info("Time for get_to_epg_traffic: " +
                        str(end_time - start_time))
    else:
        logger.error("Could not get Traffic Data related to EPG")
        end_time = datetime.datetime.now()
        logger.info("Time for get_to_epg_traffic: " +
                    str(end_time - start_time))
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
    cur_aggr_stats_query_url = "/api/node/mo/" + from_epg_dn + \
        "/to-[" + to_epg_dn + "]-subj-[" + subj_dn + "]-flt-" + \
        flt_name + "/CDactrlRuleHitAg15min.json"
    cur_aggr_stats_list = aci_util_obj.get_mo_related_item(
        "", cur_aggr_stats_query_url, "other_url")

    if cur_aggr_stats_list:
        cur_ag_stat_attr = cur_aggr_stats_list[0]["actrlRuleHitAg15min"]["attributes"]
        ingr_pkts = cur_ag_stat_attr.get("ingrPktsCum")
        egr_pkts = cur_ag_stat_attr.get("egrPktsCum")
        end_time = datetime.datetime.now()
        logger.info("Time for get_ingress_egress: " +
                    str(end_time - start_time))
        return ingr_pkts, egr_pkts
    else:
        end_time = datetime.datetime.now()
        logger.info("Time for get_ingress_egress: " +
                    str(end_time - start_time))
        return "0", "0"


def get_filter_list(flt_dn, aci_util_obj):
    """
    Returns the list of filters for a given destination EPG
    """
    start_time = datetime.datetime.now()
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

    end_time = datetime.datetime.now()
    logger.info("Time for get_filter_list: " + str(end_time - start_time))
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
            raise Exception("Incompetible format of Interfaces found")
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

            datacenter = '-'
            if status:
                datacenter = consul_obj.datacenter()

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

        logger.debug('agent data: ' + str(list(agents)))
        return json.dumps({'payload': payload, 'status_code': '200', 'message': 'OK'})

    except Exception as e:
        logger.exception('Error in read credentials: ' + str(e))
        return json.dumps({'payload': [], 'status_code': '300', 'message': 'Could not load the credentials.'})


@time_it
def write_creds(new_agent):
    try:
        logger.info('Writing agent: ' + str(new_agent))
        new_agent = json.loads(new_agent)[0] # TODO: UI should return single object, not list of one obj
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
                consul_obj = Consul(new_agent.get('ip'), new_agent.get(
                    'port'), new_agent.get('token'), new_agent.get('protocol'))
                status, message = consul_obj.check_connection()
                datacenter = '-'
                if status:
                    datacenter = consul_obj.datacenter()
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
        logger.info('deleting agents: ' + str(agent_data))
        agent_data = json.loads(agent_data)
        result = db_obj.delete_from_table(db_obj.LOGIN_TABLE_NAME,
                                        {'agent_ip': agent_data.get('ip'), 'port': agent_data.get('port')})
        if result:
            return json.dumps({'status_code': '200', 'message': 'OK'})
        return json.dumps({'status_code': '300', 'message': 'Could not delete the credentials.'})
    except Exception as e:
        logger.exception('Error in delete credentials: ' + str(e))
        return json.dumps({'payload': [], 'status_code': '300', 'message': 'Could not delete the credentials.'})


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

        apic_data = get_apic_data()
        consul_data = get_consul_data()
        merged_data = consul_merge.merge_aci_consul(tenant, apic_data, consul_data, aci_consul_mappings)

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
    finally:
        end_time =  datetime.datetime.now()
        logger.debug("Time for DETAILS: " + str(end_time - start_time))


def get_datacenters():
    logger.info('In get datacenters')
    datacenters = []
    try:
        agents = list(db_obj.select_from_table(db_obj.LOGIN_TABLE_NAME))
        if agents:
            dc_list = []
            for agent in agents:
                datacenter = str(agent[5])
                status = int(agent[4])
                if status == 1:
                    status = True
                else:
                    status = False
                if datacenter != '-' and datacenter not in dc_list:
                    datacenters.append(
                        {
                            'status': status,
                            'datacenter': datacenter
                        }
                    )
                    dc_list.append(datacenter)

        logger.info("Datacenters found")
        return json.dumps({'payload': datacenters, 'status_code': '200', 'message': 'OK'})
    except Exception as e:
        logger.exception('Error in get datacenters: ' + str(e))
        return json.dumps({'payload': [], 'status_code': '300', 'message': 'Error in fetching datacenters.'})


def post_tenant(tn):
    logger.info('Tenant received: {}'.format(str(tn)))
    try:
        response = list(db_obj.select_from_table(db_obj.TENANT_NAME, {'tenant': tn}))
        if not response:
            response = db_obj.insert_into_table(db_obj.TENANT_NAME, [tn])
            if not response:
                return json.dumps({'status_code': '300', 'message': 'Tenant not saved'})
        return json.dumps({'status_code': '200', 'message': 'OK'})
    except Exception as e:
        logger.exception('Error in post tenant: ' + str(e))
        return json.dumps({'status_code': '300', 'message': 'Tenant not saved'})


def get_consul_data():
    consul_data = []
    services = []
    node_data = list(db_obj.select_from_table(db_obj.NODE_TABLE_NAME))
    service_data = list(db_obj.select_from_table(db_obj.SERVICE_TABLE_NAME))
    node_checks_data = list(db_obj.select_from_table(db_obj.NODECHECKS_TABLE_NAME))
    service_checks_data = list(db_obj.select_from_table(db_obj.SERVICECHECKS_TABLE_NAME))
    for service in service_data:
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


def get_apic_data():
    apic_data = []
    ep_data = list(db_obj.select_from_table(db_obj.EP_TABLE_NAME))
    epg_data = list(db_obj.select_from_table(db_obj.EPG_TABLE_NAME))
    for ep in ep_data:
        for epg in epg_data:
            ep_dn = '/'.join(ep[3].split('/')[:4])
            if ep_dn == epg[0]:
                apic_data.append({
                    "AppProfile": epg[7],
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

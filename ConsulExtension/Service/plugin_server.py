import re
import json
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


@time_it
def set_polling_interval(interval):
    """Sets the polling interval for data fetch

    :interval: the interval to be set

    return: {
        status_code: string: 200/300
        message: string
    }
    """

    try:
        logger.info("Setting Polling Interval to: {}".format(str(interval)))
        connection = db_obj.engine.connect()
        with connection.begin():
            response = db_obj.insert_and_update(
                connection,
                db_obj.POLLING_TABLE_NAME,
                (
                    'interval',
                    interval
                ),
                {
                    'pkey': 'interval'
                }
            )
        connection.close()

        if not response:
            logger.error("Error in setting Polling Interval")
            return json.dumps({'status_code': '300', 'message': 'Some error occurred, could not set polling interval'})

        return json.dumps({
            "status_code": "200",
            "message": "Polling Interval Set!"
        })
    except Exception as e:
        logger.exception("Could not set polling interval, Error: {}".format(str(e)))
        return json.dumps({
            "status_code": "300",
            "message": 'Some error occurred, could not set polling interval'
        })


def get_polling_interval():

    try:
        logger.info("GetPollingInterval called")
        interval = []
        POLL_INTERVAL = 2
        connection = db_obj.engine.connect()
        with connection.begin():
            try:
                interval = db_obj.select_from_table(
                    connection,
                    db_obj.POLLING_TABLE_NAME,
                    {'pkey': 'interval'},
                    ['interval']
                )
            except Exception:
                interval = []
            if interval:
                POLL_INTERVAL = interval[0][0]
        connection.close()

        return json.dumps({
            "status_code": "200",
            "message": "Ok",
            "payload": {
                "interval": POLL_INTERVAL
            }
        })
    except Exception as e:
        logger.exception("Could not get polling interval, Error: {}".format(str(e)))
        return json.dumps({
            "status_code": "300",
            "message": "Could not get polling interval",
            "payload": []
        })


def get_vrf_specific_eps(tenant, datacenter=None):
    connection = db_obj.engine.connect()
    epg_data = list(db_obj.select_from_table(
        connection,
        db_obj.EPG_TABLE_NAME,
        {'tenant': tenant},
        ["dn", "vrf"]
    ))
    tmp_ep_data = list(db_obj.select_from_table(
        connection,
        db_obj.EP_TABLE_NAME,
        {'tenant': tenant},
        ["ip", "dn", "is_cep"]
    ))
    connection.close()

    if datacenter:
        vrfs = get_vrf_from_database(datacenter, tenant)
    else:
        vrfs = get_vrf_from_database(datacenter, tenant, True)

    ep_data = []
    if vrfs == "-":
        ep_data = tmp_ep_data
    else:
        dns = set()
        vrfs = set(map(format_vrf, vrfs))
        for each in epg_data:
            if each[1] in vrfs:
                dns.add(each[0])
        for each in tmp_ep_data:
            if each[1].split("/cep")[0] in dns:
                ep_data.append(each)
    return ep_data


@time_it
def get_new_mapping(tenant, datacenter):
    """Generate new mapping(recommendation)

    This fetches the APIC data for the tenant and Consul
    data for the datacenter; gets the recommendations,
    looks up db for enabled/disabled mapping(recommendations).

    :tenant: tenant for APIC data
    :datacenter: datacenter for Consul data

    return: [
        ip:            string: ip of the Mapped Node
        enabled:       boolean: toggled or not
        recommended:   boolean: recommendation as per the logic
        dn:            string: Mapped Node's dn
        vrf:           string: Mapped Node's VRF(Virtual routing and forwarding network)
        bd:            string: Mapped Node's Bridge Domain
        ap:            string: Mapped Node's Application Profile
        tenant:        string: Mapped Node's tenant
        epg:           string: Mapped Node's Endpoint Group
    ]
    """
    try:
        # Get APIC data
        ep_data = get_vrf_specific_eps(tenant, datacenter)
        parsed_eps = []
        for ep in ep_data:
            cep_ip = int(ep[2])
            if cep_ip == 1:
                cep_ip = True
            else:
                cep_ip = False
            parsed_eps.append(
                {
                    'dn': ep[1],
                    'IP': ep[0],
                    'cep_ip': cep_ip,
                }
            )

        apic_data = filter_apic_data(get_apic_data(tenant), get_vrf_from_database(datacenter, tenant))
        # Get consul data
        consul_data = get_consul_data(datacenter)
        ip_list = []
        for node in consul_data:
            ip_list.append(node.get('node_ip'))
            # For fetching ips of services.
            for service in node.get('node_services', []):
                # check ip is not empty string
                if service.get('service_ip', ''):
                    ip_list.append(service.get('service_ip'))

        aci_consul_mappings = recommend_utils.recommended_eps(
            set(ip_list), parsed_eps, apic_data)

        if not aci_consul_mappings:
            logger.info("Empty ACI and Consul mappings.")
            return []

        current_mapping = []
        for map_object in aci_consul_mappings:
            for entry in map_object.get('domains'):
                logger.debug("Mapping found with ipaddress for {}".format(str(map_object)))
                current_mapping.append({
                    'dn': entry.get('domainName'),
                    'ip': map_object.get('ipaddress'),
                    'recommended': entry.get('recommended'),
                    'enabled': entry.get('recommended')  # Initially only the recommended are true
                })

        apic_data = dictionary_data_formatter(apic_data, ['dn'])

        for mapped_obj in current_mapping:
            for ep in apic_data.get(mapped_obj.get('dn', [])):
                # if ep.get('dn') == mapped_obj.get('dn'):
                mapped_obj.update({
                    'vrf': ep.get('VRF'),
                    'bd': ep.get('BD'),
                    'ap': ep.get('AppProfile'),
                    'tenant': tenant,
                    'epg': ep.get('EPG')
                })

        logger.info('New mapping: {}'.format(str(current_mapping)))

        connection = db_obj.engine.connect()
        already_mapped_data = list(db_obj.select_from_table(
            connection,
            db_obj.MAPPING_TABLE_NAME,
            {'datacenter': datacenter},
            ["ip", "dn", "datacenter", "enabled"]
        ))
        connection.close()

        logger.info('Mapping in db mapping: {}'.format(str(already_mapped_data)))

        new_map_dc = dict()

        # current_mapping is new mapping between aci and consul
        # already_mapped_data is previously stored mapping by user
        # if node is already disabled then disable it from new mappings also
        tmp_already_mapped_data = list_data_formatter(already_mapped_data, [0, 1, 2])
        connection = db_obj.engine.connect()
        with connection.begin():
            for new_map in current_mapping:
                db_map = tmp_already_mapped_data.get(
                    '{}{}{}'.format(new_map.get('ip'), new_map.get('dn'), datacenter),
                    []
                )
                if db_map:
                    new_map['enabled'] = db_map[0][3]  # replace the enabled value with the one in db

                db_obj.insert_and_update(
                    connection,
                    db_obj.MAPPING_TABLE_NAME,
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

                new_map_dc[(new_map.get('ip'), new_map.get('dn'))] = True
        connection.close()

        connection = db_obj.engine.connect()
        with connection.begin():
            for mapping in already_mapped_data:
                if (mapping[0], mapping[1]) not in new_map_dc:
                    db_obj.delete_from_table(
                        connection,
                        db_obj.MAPPING_TABLE_NAME,
                        {
                            'ip': mapping[0],
                            'dn': mapping[1],
                            'datacenter': mapping[2]
                        }
                    )
        connection.close()

        return current_mapping
    except Exception as e:
        logger.exception("Could not load mapping, Error: {}".format(str(e)))
        return []


@time_it
def mapping(tenant, datacenter):
    """Returns mapping to UI and saves recommended mapping to db

    :tenant: tenant for APIC data
    :datacenter: datacenter for Consul data

    return: {
        payload: list of mapped Nodes/{}
        status_code: string: 200/300
        message: string
    }
    """

    try:
        current_mapping = get_new_mapping(tenant, datacenter)

        return json.dumps({
            "payload": current_mapping,  # Return current mapping
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
    """Save mapping to database

    :tenant: tenant for APIC data
    :datacenter: datacenter for Consul data
    :mapped_data: mapping from UI

    return: {
        payload: "Saved Mappings"/{}
        status_code: string: 200/300
        message: string
    }
    """

    try:
        logger.info("Saving mappings for datacenter : " + str(datacenter))
        logger.debug("Mapped Data : " + str(mapped_data))
        mapped_data = mapped_data.replace("'", '"')
        mapped_data_dict = json.loads(mapped_data)

        connection = db_obj.engine.connect()
        with connection.begin():
            for mapping in mapped_data_dict:
                db_obj.insert_and_update(
                    connection,
                    db_obj.MAPPING_TABLE_NAME,
                    (
                        mapping.get('ip'),
                        mapping.get('dn'),
                        datacenter,
                        mapping.get('enabled'),
                        mapping.get('ap'),
                        mapping.get('bd'),
                        mapping.get('epg'),
                        mapping.get('vrf'),
                        tenant
                    ),
                    {
                        'ip': mapping.get('ip'),
                        'dn': mapping.get('dn'),
                        'datacenter': datacenter
                    })
        connection.close()

        return json.dumps({
            "payload": "Saved Mappings",
            "status_code": "200",
            "message": "OK"
        })
    except Exception as e:
        logger.exception("Could not save mappings to the database. Error: {}".format(str(e)))
        return json.dumps({
            "payload": {},
            "status_code": "300",
            "message": "Could not save mappings to the database."
        })


@time_it
def tree(tenant, datacenter):
    """Get correlated Tree view data.

    :tenant: tenant for APIC data
    :datacenter: datacenter for Consul data

    return: {
        payload: list of tree(dict)/{}
        status_code: string: 200/300
        message: string
    }
    """

    logger.info("Tree view for tenant: {}".format(tenant))
    try:
        aci_consul_mappings = get_new_mapping(tenant, datacenter)

        apic_data = filter_apic_data(get_apic_data(tenant), get_vrf_from_database(datacenter, tenant))
        consul_data = get_consul_data(datacenter)
        merged_data = merge.merge_aci_consul(tenant, apic_data, consul_data, aci_consul_mappings)[0]

        logger.debug("ACI Consul mapped data: {}".format(merged_data))

        response = json.dumps(tree_parser.consul_tree_dict(merged_data))
        logger.debug("Final Tree data: {}".format(response))

        return json.dumps({
            "payload": response,
            "status_code": "200",
            "message": "OK"
        })
    except Exception as e:
        logger.exception("Error while building tree, Error: {}".format(str(e)))
        return json.dumps({
            "payload": {},
            "status_code": "300",
            "message": "Could not load the Tree."
        })


@time_it
def details_flattened(tenant, datacenter):
    """Get correlated Details view data

    :tenant: tenant for APIC data
    :datacenter: datacenter for Consul data

    return: {
        payload: list of dict/{}
        status_code: string: 200/300
        message: string
    }
    """

    logger.info("Details view for tenant: {}".format(tenant))
    try:
        aci_consul_mappings = get_new_mapping(tenant, datacenter)

        apic_data = filter_apic_data(get_apic_data(tenant), get_vrf_from_database(datacenter, tenant))
        consul_data = get_consul_data(datacenter)
        merged_data, non_merged_data, = merge.merge_aci_consul(tenant, apic_data, consul_data, aci_consul_mappings)

        details_list = []
        for each in merged_data:
            pods = set(list(map(lambda x: x.split("/")[0], each.get('Interfaces'))))
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
                'pod_name': list(pods)
            }

            services = change_key(each.get('node_services'))
            if not services:
                services.append({
                    'service': '',
                    'serviceInstance': '',
                    'port': '',
                    'serviceTags': [],
                    'serviceKind': '',
                    'serviceNamespace': '',
                    'serviceChecks': {},
                    'serviceAddress': ''
                })
            for service in services:
                record = {}
                record.update(ep)
                if service.get('serviceAddress', False) != "":
                    service['serviceAddress'] = ':'.join([each.get('IP'), service['port']])
                record.update(service)
                details_list.append(record)
        logger.debug("Details final data ended: " + str(details_list))

        return json.dumps({
            "payload": details_list,
            "non_merged_eps": non_merged_data,
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


def change_key(services):
    """Function used for changing as per the UI

    :services: list of services

    return: list of services with changed keys
    """

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

    :service_name: service name
    :service_id: service id
    :datacenter: datacenter for Consul data

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
    """

    logger.info("Service Check for service: {}, {}".format(service_name, service_id))
    try:
        response = []

        connection = db_obj.engine.connect()
        service_checks_data = list(db_obj.select_from_table(
            connection,
            db_obj.SERVICECHECKS_TABLE_NAME,
            {
                "service_id": service_id,
                "service_name": service_name
            },
            ["check_id", "name", "type", "notes", "output", "status"]
        ))
        connection.close()

        for check in service_checks_data:
            response.append({
                'ServiceName': service_name,
                'CheckID': check[0],
                'Type': check[2],
                'Notes': check[3],
                'Output': check[4],
                'Name': check[1],
                'Status': check[5]
            })

        return json.dumps({
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

    :node_name: node name
    :datacenter: datacenter for Consul data

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
    """

    logger.info("Node Check for node: {}".format(node_name))
    try:
        response = []
        node_checks_data = []

        connection = db_obj.engine.connect()
        node_id = db_obj.select_from_table(
            connection,
            db_obj.NODE_TABLE_NAME,
            {
                'node_name': node_name,
                'datacenter': datacenter
            },
            ['node_id']
        )
        if node_id:
            node_checks_data = list(db_obj.select_from_table(
                connection,
                db_obj.NODECHECKS_TABLE_NAME,
                {
                    'node_id': node_id[0][0],
                    'node_name': node_name
                },
                ["check_id", "check_name", "service_name", "type", "notes", "output", "status"]
            ))
        connection.close()

        for check in node_checks_data:
            response.append({
                'NodeName': node_name,
                'Name': check[1],
                'ServiceName': check[2],
                'CheckID': check[0],
                'Type': check[3],
                'Notes': check[4],
                'Output': check[5],
                'Status': check[6]
            })

        logger.debug('Response of Node check: {}'.format(response))

        return json.dumps({
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

    :service_list: list of servie id and service name
    :datacenter: datacenter for Consul data

    return: {
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
        connection = db_obj.engine.connect()
        service_checks_data = list(db_obj.select_from_table(
            connection,
            db_obj.SERVICECHECKS_TABLE_NAME,
            {},
            db_obj.SCHEMA_DICT[db_obj.SERVICECHECKS_TABLE_NAME][:8]
        ))
        connection.close()

        service_checks_data = list_data_formatter(service_checks_data, [1, 2])

        for service_dict in service_list:
            service_name = service_dict["Service"]
            service_id = service_dict["ServiceID"]
            checks = service_checks_data.get(
                ''.join([service_id, service_name]),
                []
            )
            for check in checks:
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

    :node_list: list of node name
    :datacenter: datacenter for Consul data

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
    """

    logger.info("Node Checks for nodes: {}".format(node_list))
    node_list = json.loads(node_list)
    response = []
    try:
        node_ids = []

        connection = db_obj.engine.connect()
        for node_name in node_list:
            node_id = db_obj.select_from_table(
                connection,
                db_obj.NODE_TABLE_NAME,
                {
                    'node_name': node_name,
                    'datacenter': datacenter
                },
                ['node_id']
            )
            node_ids.append(node_id)
        node_checks_data = list(db_obj.select_from_table(
            connection,
            db_obj.NODECHECKS_TABLE_NAME,
            {},
            db_obj.SCHEMA_DICT[db_obj.NODECHECKS_TABLE_NAME][:9]
        ))
        connection.close()
        node_ids = list(map(lambda x: x[0][0] if x else "", node_ids))

        node_checks_data = list_data_formatter(node_checks_data, [1, 2])

        for i, node_name in enumerate(node_list):
            checks = node_checks_data.get(
                ''.join([node_ids[i], node_name]),
                []
            )
            for check in checks:
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

    :dn: dn of epg

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
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

    :dn: dn of epg

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
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

    :dn: dn of epg

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
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
def get_children_ep_info(dn, mo_type, mac_list, ip_list, ip):
    """
    Get Operational for EP and Client EP for EPG

    :dn: dn of epg
    :mo_type: ep/epg
    :mac_list: mac list of EP
    :ip: ip in case of ep/""

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
    """
    aci_util_obj = apic_utils.AciUtils()
    if mo_type == "ep":
        mac_list = mac_list.split(",")
        mac_query_filter_list = []
        for mac in mac_list:
            mac_query_filter_list.append('eq(fvCEp.mac,"' + mac + '")')
        mac_query_filter = ",".join(mac_query_filter_list)

        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&query-target-filter=or(' + \
            mac_query_filter + ')&rsp-subtree=children&rsp-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsToVm'
    elif mo_type == "epg":
        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&rsp-subtree=children&rsp'\
            '-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsToVm,fvIp'

    ep_list = aci_util_obj.get_mo_related_item(dn, ep_info_query_string, "")
    logger.debug('Data returned by API call for get_children: {}'.format(str(len(ep_list))))
    ep_info_list = []
    if mo_type == "ep" and ip == "":
        mac_ip_dict = dict()
        ip_list = ip_list.split("-")
        for index, mac in enumerate(mac_list):
            mac_ip_dict[mac] = ip_list[index]
    try:
        for ep in ep_list:
            ep_info_dict = dict()

            ep_children = ep.get("fvCEp").get("children")
            ep_info = aci_util_obj.get_ep_info(ep_children)
            ep_attr = ep.get("fvCEp").get("attributes")

            mcast_addr = ep_attr.get("mcastAddr")
            if mcast_addr == "not-applicable":
                mcast_addr = ""

            if mo_type == "ep":
                if ip != "":
                    cep_ip = ip
                else:
                    cep_ip = mac_ip_dict[ep_attr.get("mac")]
            elif mo_type == "epg":
                ip_set = set()
                for eachip in ep_children:
                    if eachip.keys()[0] == 'fvIp':
                        ip_set.add(str(eachip.get('fvIp').get('attributes').get('addr')))
                ip_set.add(ep_attr.get('ip'))
                if "0.0.0.0" in ip_set:
                    ip_set.remove("0.0.0.0")
                    ip_set.add("N/A")
                cep_ip = ', '.join(ip_set)

            ep_info_dict = {
                "ip": cep_ip,
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
        logger.exception("Exception while getting Children Ep Info : " + str(e))
        return json.dumps({
            "status_code": "300",
            "message": "Could not get Operational info",
            "payload": []
        })


@time_it
def get_configured_access_policies(tn, ap, epg):
    """
    Get config access policy

    :tn: tenant for APIC
    :ap: Application Policy
    :epg: End Point Group

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
    """
    aci_util_obj = apic_utils.AciUtils()
    cap_url = "/mqapi2/deployment.query.json?mode=epgtoipg&tn=" + \
        tn + "&ap=" + ap + "&epg=" + epg
    cap_resp = aci_util_obj.get_mo_related_item("", cap_url, "other_url")
    logger.debug('=Data returned by API call for config access policy: {}'.format(str(len(cap_resp))))
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
                tmp_vlan_pool = cap_attr["vLanPool"].split("/from-")[1]
                vlans = tmp_vlan_pool.split("-to-")
                vlans = list(map(lambda x: x.split("vlan-")[1][:-1], vlans))
                cap_dict["vlan_pool"] = "{} to {}".format(vlans[0], vlans[1])
            else:
                logger.error("Attribute {} not found".format("vLanpool"))
            cap_list.append(cap_dict)

        return json.dumps({
            "status_code": "200",
            "message": "Ok",
            "payload": cap_list
        })
    except Exception as ex:
        logger.exception("Exception while getting config access policy: " + str(ex))
        return json.dumps({
            "status_code": "300",
            "message": "Could not get Configured access policies",
            "payload": []
        })


def get_to_epg(dn):
    """Function to get TO_EPG from dn

    :dn: dn of EPG(uni/tn-Tenant1/ap-AppProfile1/epg-EPG1)

    return: epg dn(Tenant1/AppProfile1/EPG1)
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

    :dn: epg dn

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
    """
    aci_util_obj = apic_utils.AciUtils()
    try:
        epg_traffic_query_string = 'query-target-filter=eq(vzFromEPg.epgDn,"' + dn + \
            '")&rsp-subtree=full&rsp-subtree-class=vzToEPg,vzRsRFltAtt,vzCreatedBy&rsp-subtree-include=required'
        epg_traffic_resp = aci_util_obj.get_all_mo_instances("vzFromEPg", epg_traffic_query_string)
        logger.debug("=Data returned by API call for to epg traffic {}".format(str(len(epg_traffic_resp))))

        to_epg_set = set()

        for epg_traffic in epg_traffic_resp:
            to_epg_children = epg_traffic["vzFromEPg"]["children"]
            for to_epg_child in to_epg_children:
                vz_to_epg_child = to_epg_child["vzToEPg"]
                to_epg_dn = vz_to_epg_child["attributes"]["epgDn"]
                flt_attr_children = vz_to_epg_child["children"]
                for flt_attr in flt_attr_children:
                    to_epg_set.add(to_epg_dn)

        subnet_list = []
        for epg in to_epg_set:
            subnet_resp = aci_util_obj.get_mo_related_item(
                epg,
                "query-target=children&target-subtree-class=fvSubnet",
                ""
            )
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
                subnet_dict["epg_alias"] = get_epg_alias(dn.split('/subnet')[0])
                subnet_list.append(subnet_dict)

        return json.dumps({
            "status_code": "200",
            "message": "",
            "payload": subnet_list
        })
    except Exception as ex:
        logger.exception("Exception while getting subnets: " + str(ex))
        return json.dumps({
            "status_code": "300",
            "message": "Could not get subnets",
            "payload": []
        })


@time_it
def get_to_epg_traffic(epg_dn):
    """
    Gets the Traffic Details from the given EPG to other EPGs

    :epg_dn: epg dn

    return: {
        payload: list of dict/[]
        status_code: string: 200/300
        message: string
    }
    """

    aci_util_obj = apic_utils.AciUtils()
    epg_traffic_query_string = 'query-target-filter=eq(vzFromEPg.epgDn,"' + epg_dn + \
        '")&rsp-subtree=full&rsp-subtree-class=vzToEPg,vzRsRFltAtt,vzCreatedBy&rsp-subtree-include=required'
    epg_traffic_resp = aci_util_obj.get_all_mo_instances("vzFromEPg", epg_traffic_query_string)
    logger.debug("=Data returned by API call for to epg traffic {}".format(str(len(epg_traffic_resp))))
    from_epg_dn = epg_dn
    to_epg_traffic_list = []
    to_epg_traffic_set = set()
    try:
        for epg_traffic in epg_traffic_resp:
            to_epg_children = epg_traffic["vzFromEPg"]["children"]
            for to_epg_child in to_epg_children:

                vz_to_epg_child = to_epg_child["vzToEPg"]
                to_epg_dn = vz_to_epg_child["attributes"]["epgDn"]
                parsed_to_epg_dn = get_to_epg(to_epg_dn)
                def_dn = vz_to_epg_child["attributes"]["epgDefDn"]
                contract_type = ""
                if re.search("/cons-", def_dn):
                    contract_type = "Consumer"
                elif re.search("/prov-", def_dn):
                    contract_type = "Provider"
                elif re.search("/intra-", def_dn):
                    contract_type = "Intra EPG"
                else:
                    logger.error("Contract type not prov/cons/intra")

                flt_attr_children = vz_to_epg_child["children"]
                for flt_attr in flt_attr_children:
                    to_epg_traffic_dict = {
                        "to_epg": parsed_to_epg_dn,
                        "contract_subj": "",
                        "filter_list": [],
                        "ingr_pkts": "",
                        "egr_pkts": "",
                        "alias": get_epg_alias(to_epg_dn),
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
            "Exception while fetching To EPG Traffic List : " + str(ex))

        return json.dumps({
            "status_code": "300",
            "message": "Could not get Traffic Data related to EPG",
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


@time_it
def read_creds(tn):
    """Returns list of all agents in DB with connection status

    return: {
        payload: list of dict/[]
        status_code: string: 200/300/301
        message: string
    }
    """
    try:
        logger.info('Reading agents.')

        # handle db read failure, just pass empty list from there
        connection = db_obj.engine.connect()
        agents = list(db_obj.select_from_table(connection, db_obj.LOGIN_TABLE_NAME, {'tenant': tn}))
        connection.close()

        if not agents:
            logger.info('Agents List Empty.')
            return json.dumps({'payload': [], 'status_code': '301', 'message': 'Agents not found'})
        payload = []

        connection = db_obj.engine.connect()
        with connection.begin():
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
                    agent_val = (agent[0], agent[1], agent[2], agent[3], status, datacenter, tn, agent[7])
                    db_obj.insert_and_update(
                        connection,
                        db_obj.LOGIN_TABLE_NAME,
                        agent_val,
                        {
                            'agent_ip': agent[0],
                            'port': agent[1]
                        }
                    )

                payload.append({
                    'ip': agent[0],
                    'port': agent[1],
                    'protocol': agent[2],
                    'token': agent[3],
                    'status': status,
                    'datacenter': datacenter,
                    'vrf': agent[7].split("ctx-")[1] if agent[7] != "-" else None
                })
        connection.close()
        logger.debug('Read creds response: {}'.format(str(payload)))
        return json.dumps({
            'payload': payload,
            'status_code': '200',
            'message': 'OK'
        })
    except Exception as e:
        logger.exception('Error in read credentials: ' + str(e))
        return json.dumps({
            'payload': [],
            'status_code': '300',
            'message': 'Could not load the credentials.'
        })


@time_it
def write_creds(tn, new_agent):
    """Writes an Agent to DB and returns it status
    to UI with encripted token

    :new_agent: list agent with one agent in it

    return: {
        payload: list of dict/[]
        status_code: string: 200/300/301
        message: string
    }
    """
    try:
        new_agent = json.loads(new_agent)[0]  # UI returns list of one object
        logger.info('Writing agent: {}:{}'.format(new_agent.get('ip'), str(new_agent.get('port'))))
        vrf_dn = "-"
        if new_agent.get('vrf') != "-" and new_agent.get('vrf') is not None:
            vrf_dn = "uni/tn-{}/ctx-{}".format(tn, new_agent.get('vrf'))
        connection = db_obj.engine.connect()
        agents = list(db_obj.select_from_table(
            connection,
            db_obj.LOGIN_TABLE_NAME,
            {
                'agent_ip': new_agent.get('ip'),
                'port': new_agent.get('port'),
                'tenant': tn
            }
        ))
        connection.close()

        if agents:
            message = 'Agent ' + new_agent.get('ip') + ':' + str(new_agent.get('port')) + ' already exists.'
            logger.error(message)
            return json.dumps({'payload': new_agent, 'status_code': '300', 'message': message})

        if not new_agent['token']:
            new_agent['token'] = ''
        consul_obj = Consul(
            new_agent.get('ip'),
            new_agent.get('port'),
            new_agent.get('token'),
            new_agent.get('protocol')
        )
        status, message = consul_obj.check_connection()

        datacenter = '-'
        if status:
            datacenter = consul_obj.datacenter()

        new_agent['datacenter'] = datacenter
        new_agent['status'] = status
        new_agent['token'] = base64.b64encode(new_agent['token'].encode('ascii')).decode('ascii')

        connection = db_obj.engine.connect()
        with connection.begin():
            db_obj.insert_into_table(
                connection,
                db_obj.LOGIN_TABLE_NAME,
                [
                    new_agent.get('ip'),
                    new_agent.get('port'),
                    new_agent.get('protocol'),
                    new_agent.get('token'),
                    new_agent.get('status'),
                    new_agent.get('datacenter'),
                    tn,
                    vrf_dn
                ])
        connection.close()

        change_data_fetch_status(True)

        if status:
            return json.dumps({
                'payload': new_agent,
                'status_code': '200',
                'message': 'OK'
            })
        else:
            return json.dumps({
                'payload': new_agent,
                'status_code': '301',
                'message': str(message)
            })
    except Exception as e:
        logger.exception('Error in write credentials: ' + str(e))
        return json.dumps({
            'payload': [],
            'status_code': '300',
            'message': 'Could not write the credentials.'
        })


@time_it
def update_creds(tn, update_input):
    """Update an Agent to DB and returns it status to UI

    :update_input: json with old agents data and new agents data

    return: {
        payload: list of dict/[]
        status_code: string: 200/300/301
        message: string
    }
    """
    try:
        logger.info('Updating agent: {}'.format(update_input))

        update_input = json.loads(update_input)
        old_agent = update_input.get('oldData')
        new_agent = update_input.get('newData')
        old_vrf_dn = "-"
        new_vrf_dn = "-"
        if old_agent.get('vrf') != "-" and old_agent.get('vrf') is not None:
            old_vrf_dn = "uni/tn-{}/ctx-{}".format(tn, old_agent.get('vrf'))
        if new_agent.get('vrf') != "-" and new_agent.get('vrf') is not None:
            new_vrf_dn = "uni/tn-{}/ctx-{}".format(tn, new_agent.get('vrf'))

        connection = db_obj.engine.connect()
        agents = list(db_obj.select_from_table(connection, db_obj.LOGIN_TABLE_NAME))
        connection.close()
        if not agents:
            logger.info('Agents List Empty.')
            return json.dumps({'payload': [], 'status_code': '300', 'message': 'Agents not found'})

        if not (
            old_agent.get('ip') == new_agent.get('ip') and
            old_agent.get('port') == new_agent.get('port')
        ):
            connection = db_obj.engine.connect()
            new_agent_db_data = db_obj.select_from_table(
                connection,
                db_obj.LOGIN_TABLE_NAME,
                {
                    'agent_ip': new_agent.get('ip'),
                    'port': new_agent.get('port'),
                    'tenant': tn
                }
            )
            connection.close()
            if new_agent_db_data:
                message = 'Agent ' + \
                    new_agent.get('ip') + ':' + \
                    str(new_agent.get('port')) + ' already exists.'
                logger.error(message)
                return json.dumps({'payload': new_agent, 'status_code': '300', 'message': message})

        for agent in agents:
            if (
                old_agent.get('ip') == agent[0] and
                old_agent.get('port') == int(agent[1]) and
                tn == agent[6]
            ):
                if new_agent.get('token') == agent[3]:
                    new_agent['token'] = base64.b64decode(new_agent.get('token')).decode('ascii')
                consul_obj = Consul(
                    new_agent.get('ip'),
                    new_agent.get('port'),
                    new_agent.get('token'),
                    new_agent.get('protocol')
                )

                status, message = consul_obj.check_connection()

                datacenter = ''
                if status:
                    datacenter = consul_obj.datacenter()
                    if datacenter == '-':
                        datacenter = agent[5]

                new_agent['datacenter'] = datacenter
                new_agent['status'] = status
                new_agent['token'] = base64.b64encode(new_agent['token'].encode('ascii')).decode('ascii')

                connection = db_obj.engine.connect()
                with connection.begin():
                    db_obj.insert_and_update(
                        connection,
                        db_obj.LOGIN_TABLE_NAME,
                        [
                            new_agent.get('ip'),
                            new_agent.get('port'),
                            new_agent.get('protocol'),
                            new_agent.get('token'),
                            new_agent.get('status'),
                            new_agent.get('datacenter'),
                            tn,
                            new_vrf_dn
                        ],
                        {
                            'agent_ip': old_agent.get('ip'),
                            'port': old_agent.get('port'),
                            'tenant': tn
                        })
                connection.close()

                change_data_fetch_status(True)

                if status:
                    return json.dumps({
                        'payload': new_agent,
                        'status_code': '200',
                        'message': 'OK'
                    })
                else:
                    return json.dumps({
                        'payload': new_agent,
                        'status_code': '301',
                        'message': message
                    })
    except Exception as e:
        logger.exception('Error in update credentials: ' + str(e))
        return json.dumps({
            'payload': [],
            'status_code': '300',
            'message': 'Could not update the credentials.'
        })


@time_it
def delete_creds(tn, agent_data):
    """Update an Agent to DB and returns it status to UI

    :update_input: json with old agents data and new agents data

    return: {
        payload: list of dict/[]
        status_code: string: 200/300/301
        message: string
    }
    """
    try:
        logger.info('Deleting agent {}'.format(str(agent_data)))
        agent_data = json.loads(agent_data)
        vrf_dn = "-"
        if agent_data.get('vrf') != "-" and agent_data.get('vrf') is not None:
            vrf_dn = "uni/tn-{}/ctx-{}".format(tn, agent_data.get('vrf'))

        # Agent deleted
        connection = db_obj.engine.connect()
        agent_count = 0
        with connection.begin():
            agent_count = len(list(db_obj.select_from_table(
                connection,
                db_obj.LOGIN_TABLE_NAME,
                {
                    'agent_ip': agent_data.get('ip'),
                    'port': agent_data.get('port')
                }
            )))
            db_obj.delete_from_table(
                connection,
                db_obj.LOGIN_TABLE_NAME,
                {
                    'agent_ip': agent_data.get('ip'),
                    'port': agent_data.get('port'),
                    'tenant': tn
                }
            )
        connection.close()

        logger.info('Agent {} deleted'.format(str(agent_data)))

        agent_dc = agent_data.get('datacenter')
        connection = db_obj.engine.connect()
        agent_list = list(db_obj.select_from_table(connection, db_obj.LOGIN_TABLE_NAME))
        connection.close()
        agent_list = [agent for agent in agent_list if agent[5] == agent_dc]
        if not agent_list:
            connection = db_obj.engine.connect()
            mappings = list(db_obj.select_from_table(
                connection,
                db_obj.MAPPING_TABLE_NAME,
                {"datacenter": agent_dc},
                ["ip", "dn", "datacenter"]
            ))
            connection.close()

            connection = db_obj.engine.connect()
            with connection.begin():
                for mapping in mappings:
                    db_obj.delete_from_table(
                        connection,
                        db_obj.MAPPING_TABLE_NAME,
                        {
                            'ip': mapping[0],
                            'dn': mapping[1],
                            'datacenter': mapping[2]
                        }
                    )
            connection.close()
            logger.info('Mapping for Datacenter {} deleted'.format(str(agent_dc)))

        if agent_count == 1:
            # Delete all the data fetched by this agent
            agent_addr = agent_data.get('ip') + ':' + str(agent_data.get('port'))

            # Delete Node data wrt this agent
            connection = db_obj.engine.connect()
            node_data = list(db_obj.select_from_table(connection, db_obj.NODE_TABLE_NAME))
            connection.close()

            connection = db_obj.engine.connect()
            with connection.begin():
                for node in node_data:
                    agents = node[4]
                    if agent_addr not in agents:
                        continue
                    if len(agents) == 1:
                        db_obj.delete_from_table(connection, db_obj.NODE_TABLE_NAME, {'node_id': node[0]})
                    else:
                        node[4].remove(agent_addr)
                        db_obj.insert_and_update(connection, db_obj.NODE_TABLE_NAME, node, {'node_id': node[0]})
            connection.close()
            logger.info('Agent {}\'s Node data deleted'.format(str(agent_addr)))

            change_data_fetch_status(True)

            # Delete Service data wrt this agent
            connection = db_obj.engine.connect()
            service_data = list(db_obj.select_from_table(connection, db_obj.SERVICE_TABLE_NAME))
            connection.close()

            connection = db_obj.engine.connect()
            with connection.begin():
                for service in service_data:
                    agents = service[10]
                    if agent_addr not in agents:
                        continue
                    if len(agents) == 1:
                        db_obj.delete_from_table(
                            connection,
                            db_obj.SERVICE_TABLE_NAME,
                            {
                                'service_id': service[0],
                                'node_id': service[1]
                            }
                        )
                    else:
                        service[10].remove(agent_addr)
                        db_obj.insert_and_update(
                            connection,
                            db_obj.SERVICE_TABLE_NAME,
                            service,
                            {
                                'service_id': service[0],
                                'node_id': service[1]
                            }
                        )
            connection.close()
            logger.info('Agent {}\'s Service data deleted'.format(str(agent_addr)))

            # Delete Node Check data wrt this agent
            connection = db_obj.engine.connect()
            node_checks_data = list(db_obj.select_from_table(connection, db_obj.NODECHECKS_TABLE_NAME))
            connection.close()

            connection = db_obj.engine.connect()
            with connection.begin():
                for node in node_checks_data:
                    agents = node[9]
                    if agent_addr not in agents:
                        continue
                    if len(agents) == 1:
                        db_obj.delete_from_table(
                            connection,
                            db_obj.NODECHECKS_TABLE_NAME,
                            {
                                'check_id': node[0],
                                'node_id': node[1]
                            }
                        )
                    else:
                        node[9].remove(agent_addr)
                        db_obj.insert_and_update(
                            connection,
                            db_obj.NODECHECKS_TABLE_NAME,
                            node,
                            {
                                'check_id': node[0],
                                'node_id': node[1]
                            }
                        )
            connection.close()
            logger.info('Agent {}\'s NodeChecks data deleted'.format(str(agent_addr)))

            # Delete Service Check data wrt this agent
            connection = db_obj.engine.connect()
            service_checks_data = list(db_obj.select_from_table(connection, db_obj.SERVICECHECKS_TABLE_NAME))
            connection.close()

            connection = db_obj.engine.connect()
            with connection.begin():
                for service in service_checks_data:
                    agents = service[8]
                    if agent_addr not in agents:
                        continue
                    if len(agents) == 1:
                        db_obj.delete_from_table(
                            connection,
                            db_obj.SERVICECHECKS_TABLE_NAME,
                            {
                                'check_id': service[0],
                                'service_id': service[1]
                            }
                        )
                    else:
                        service[8].remove(agent_addr)
                        db_obj.insert_and_update(
                            connection,
                            db_obj.SERVICECHECKS_TABLE_NAME,
                            service,
                            {
                                'check_id': service[0],
                                'service_id': service[1]
                            }
                        )
            connection.close()
            logger.info('Agent {}\'s ServiceChecks data deleted'.format(str(agent_addr)))

        # it is assumed that no delete call to db would fail
        return json.dumps({
            'status_code': '200',
            'message': 'OK'
        })
    except Exception as e:
        logger.exception('Error in delete credentials: ' + str(e))
        return json.dumps({
            'payload': [],
            'status_code': '300',
            'message': 'Could not delete the credentials.'
        })


@time_it
def get_datacenters(tn):
    """Return list of datacenter with connection status

    return: [{
        datacenter: string: datacenter name
        status:     boolean: True(Connected)/False(Disconnected)
    }]
    """
    logger.info('In get datacenters')
    datacenters = []
    try:
        connection = db_obj.engine.connect()
        agents = list(db_obj.select_from_table(connection, db_obj.LOGIN_TABLE_NAME, {'tenant': tn}))
        connection.close()

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
        return json.dumps({
            'payload': datacenters,
            'status_code': '200',
            'message': 'OK'
        })
    except Exception as e:
        logger.exception('Error in get datacenters: ' + str(e))
        return json.dumps({
            'payload': [],
            'status_code': '300',
            'message': 'Error in fetching datacenters.'
        })


def post_tenant(tn):
    """Put tenant in DB

    This returns the tenant name when the app is opened first time.
    This helps fetch tenant specific data

    :tn: tenant name to be put into DB

    return: {
        status: 200/300
        message: Ok/Tenant not saved
    }
    """
    logger.info('Tenant received: {}'.format(str(tn)))
    try:
        connection = db_obj.engine.connect()
        response = list(db_obj.select_from_table(connection, db_obj.TENANT_TABLE_NAME, {'tenant': tn}))
        connection.close()

        if not response:

            connection = db_obj.engine.connect()
            with connection.begin():
                response = db_obj.insert_into_table(connection, db_obj.TENANT_TABLE_NAME, [tn])
            connection.close()

            if not response:
                return json.dumps({'status_code': '300', 'message': 'Tenant not saved'})
        return json.dumps({'status_code': '200', 'message': 'OK'})
    except Exception as e:
        logger.exception('Error in post tenant: ' + str(e))
        return json.dumps({'status_code': '300', 'message': 'Tenant not saved'})


def list_data_formatter(data, key_index):
    dc = dict()
    for each in data:
        key = ''.join([each[i] for i in key_index])
        if key in dc:
            dc[key].append(each)
        else:
            dc[key] = [each]
    return dc


def dictionary_data_formatter(data, key_names):
    dc = dict()
    for each in data:
        key = ''.join([each.get(i, '') for i in key_names])
        if key in dc:
            dc[key].append(each)
        else:
            dc[key] = [each]
    return dc


@time_it
def get_consul_data(datacenter):
    consul_data = []
    services = []

    connection = db_obj.engine.connect()
    node_data = list(db_obj.select_from_table(
        connection,
        db_obj.NODE_TABLE_NAME,
        {'datacenter': datacenter},
        ["node_id", "node_name", "node_ip"]
    ))
    service_data = list(db_obj.select_from_table(
        connection,
        db_obj.SERVICE_TABLE_NAME,
        {'datacenter': datacenter},
        db_obj.SCHEMA_DICT[db_obj.SERVICE_TABLE_NAME][:9]
    ))
    node_checks_data = list(db_obj.select_from_table(
        connection,
        db_obj.NODECHECKS_TABLE_NAME,
        {},
        ["node_id", "status"]
    ))
    service_checks_data = list(db_obj.select_from_table(
        connection,
        db_obj.SERVICECHECKS_TABLE_NAME,
        {},
        ["service_id", "status"]
    ))
    connection.close()

    node_checks_data = list_data_formatter(node_checks_data, [0])
    service_checks_data = list_data_formatter(service_checks_data, [0])

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
        check_list = service_checks_data.get(service[0], [])
        check_dict = service_dict['service_checks']
        for check in check_list:
            status = check[1]
            if 'passing' == status.lower():
                if 'passing' in check_dict:
                    check_dict['passing'] += 1
                else:
                    check_dict['passing'] = 1
            elif 'warning' == status.lower():
                if 'warning' in check_dict:
                    check_dict['warning'] += 1
                else:
                    check_dict['warning'] = 1
            else:
                if 'failing' in check_dict:
                    check_dict['failing'] += 1
                else:
                    check_dict['failing'] = 1
        service_dict['service_checks'] = check_dict
        services.append(service_dict)

    services_dc = dictionary_data_formatter(services, ['node_id'])

    for node in node_data:
        node_dict = {
            'node_id': node[0],
            'node_name': node[1],
            'node_ip': node[2],
            'node_check': {},
            'node_services': services_dc.get(node[0], [])
        }
        check_list = node_checks_data.get(node[0], [])
        check_dict = node_dict['node_check']
        for check in check_list:
            status = check[1]
            if 'passing' == status.lower():
                if 'passing' in check_dict:
                    check_dict['passing'] += 1
                else:
                    check_dict['passing'] = 1
            elif 'warning' == status.lower():
                if 'warning' in check_dict:
                    check_dict['warning'] += 1
                else:
                    check_dict['warning'] = 1
            else:
                if 'failing' in check_dict:
                    check_dict['failing'] += 1
                else:
                    check_dict['failing'] = 1
        node_dict['node_check'] = check_dict
        consul_data.append(node_dict)
    return consul_data


@time_it
def get_apic_data(tenant):
    apic_data = []

    connection = db_obj.engine.connect()
    ep_data = list(db_obj.select_from_table(
        connection,
        db_obj.EP_TABLE_NAME,
        {'tenant': tenant},
        db_obj.SCHEMA_DICT[db_obj.EP_TABLE_NAME][:12]
    ))
    epg_data = list(db_obj.select_from_table(
        connection,
        db_obj.EPG_TABLE_NAME,
        {'tenant': tenant},
        db_obj.SCHEMA_DICT[db_obj.EPG_TABLE_NAME][:8]
    ))
    connection.close()

    epg_data = list_data_formatter(epg_data, [0])

    for ep in ep_data:
        ep_dn = '/'.join(ep[3].split('/')[:4])
        epgs = epg_data.get(ep_dn, [])
        for epg in epgs:
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
                'dn': '/'.join(ep[3].split('/')[:5]),
                'controllerName': ep[7],
                'hostingServerName': ep[11],
                'learningSource': ep[8],
                'epg_health': epg[6]
            })

    return apic_data


def get_agent_status(tn, datacenter=""):
    """Function to get overview agent

    Returns:
        dict: Response for agents
    """
    agents_res = {
        'up': {
            'value': 0,
            'label': 'Connected',
            'color': 'rgb(108, 192, 74)'
        },
        'down': {
            'value': 0,
            'label': 'Disconnected',
            'color': 'rgb(226, 35, 26)'
        },
        'total': 0
    }

    connection = db_obj.engine.connect()
    agents = list(db_obj.select_from_table(connection, db_obj.LOGIN_TABLE_NAME, {'tenant': tn}))
    connection.close()

    if not agents:
        logger.info('Agents List Empty.')
        return agents_res
    for agent in agents:
        if datacenter:
            if datacenter == agent[5] and agent[4] == '1':
                agents_res['up']['value'] += 1
            elif datacenter == agent[5] and agent[4] == '0':
                agents_res['down']['value'] += 1
        else:
            if agent[4] == '1':
                agents_res['up']['value'] += 1
            elif agent[4] == '0':
                agents_res['down']['value'] += 1
    agents_res['total'] = agents_res['up']['value'] + agents_res['down']['value']
    return agents_res


def add_check(add_check, add_to):
    """Adds consul checks"""

    for status, check_value in add_check.iteritems():
        add_to[status] += check_value


@time_it
def get_performance_dashboard(tenant):
    """Function to get payload for performance dashboard

    :tenant: Name of tenant

    return: {
        status: 200/300
        payload: response/{}
        message: message
    }
    """

    try:
        response = {}

        ep_len = len(get_vrf_specific_eps(tenant))
        mapped_ep = {}
        datacenters = json.loads(get_datacenters(tenant))['payload']
        for dc in datacenters:
            datacenter = dc['datacenter']
            if datacenter not in mapped_ep:
                mapped_ep[datacenter] = []

        for dc in mapped_ep:
            mapped_dc = get_new_mapping(tenant, dc)
            for map in mapped_dc:
                mapped_ep[dc].append(map)

        apic_data = filter_apic_data(get_apic_data(tenant), get_vrf_from_database(None, tenant, True))
        ep_res = {
            'service': {
                'color': 'rgb(108, 192, 74)',
                'value': 0,
                'label': 'Service Endpoints'
            },
            'non_service': {
                'color': 'rgb(128,128,128)',
                'value': 0,
                'label': 'Non-Service Endpoints'
            },
            'total': ep_len
        }

        ep_set = set()
        for dc in mapped_ep:
            service_res = {'passing': 0, 'warning': 0, 'failing': 0}
            nodes_res = {'passing': 0, 'warning': 0, 'failing': 0}
            node_ip_set = set()
            service_addr_set = set()
            consul_data = get_consul_data(dc)
            merged_data = merge.merge_aci_consul(tenant, apic_data, consul_data, mapped_ep[dc])[0]

            for ep in merged_data:
                # Add service eps to ep_resp
                if (ep['IP'], ep['dn']) not in ep_set:
                    ep_set.add((ep['IP'], ep['dn']))
                    ep_res['service']['value'] += 1

                if ep['node_ip'] not in node_ip_set:
                    node_ip_set.add(ep['node_ip'])
                    add_check(ep['node_check'], nodes_res)

                for service in ep['node_services']:
                    if service['service_address'] not in service_addr_set:
                        service_addr_set.add(service['service_address'])
                        add_check(service['service_checks'], service_res)

            response[dc] = dict()
            response[dc]['agents'] = get_agent_status(tenant, dc)
            response[dc]['service'] = service_res
            response[dc]['nodes'] = nodes_res

        ep_res['non_service']['value'] = ep_len - ep_res['service']['value']

        all_dc_data = dict()
        all_dc_data['agents'] = get_agent_status(tenant)
        all_dc_data['service'] = {'passing': 0, 'warning': 0, 'failing': 0}
        all_dc_data['nodes'] = {'passing': 0, 'warning': 0, 'failing': 0}

        for dc in response:
            for key in all_dc_data['service']:
                all_dc_data['service'][key] += response[dc]['service'][key]
            for key in all_dc_data['nodes']:
                all_dc_data['nodes'][key] += response[dc]['nodes'][key]
            response[dc]['service_endpoint'] = ep_res

        all_dc_data['service_endpoint'] = ep_res
        response['all'] = all_dc_data

        connection = db_obj.engine.connect()
        data_fetch_info = db_obj.select_from_table(
            connection,
            db_obj.DATA_FETCH_TABLE_NAME,
            {},
            ['running']
        )
        connection.close()

        return json.dumps({
            "status": "200",
            "payload": {
                'data_fetch': data_fetch_info[0][0],
                'data': response
            },
            "message": "OK"
        })
    except Exception as e:
        logger.exception("Exception occurred, Error: {}".format(e))
        return json.dumps({
            "status": "300",
            "payload": {},
            "message": "Could not load performance data"
        })


def get_epg_alias(dn):
    """This would return EPG alias from the db"""

    connection = db_obj.engine.connect()
    epg_data = db_obj.select_from_table(
        connection,
        db_obj.EPG_TABLE_NAME,
        {"dn": dn},
        ["epg_alias"]
    )
    connection.close()

    if epg_data:
        return epg_data[0][0]
    return ""


def get_vrf_from_database(datacenter, tn, dashboard=False):
    connection = db_obj.engine.connect()
    search_param = {'tenant': tn}
    if not dashboard:
        search_param['datacenter'] = datacenter
    tmp_vrfs = db_obj.select_from_table(
        connection,
        db_obj.LOGIN_TABLE_NAME,
        search_param,
        ['vrf_dn']
    )
    connection.close()
    vrfs = list(map(lambda x: x[0], tmp_vrfs))
    return "-" if "-" in vrfs else vrfs


@time_it
def get_vrf_from_apic(tn):
    """This would return VRFs of tenant tn"""
    response = []
    try:
        aci_util_obj = apic_utils.AciUtils()
        data = aci_util_obj.apic_fetch_vrf_tenant(tn)
        if data:
            for each in data:
                vrf_name = each.get("fvCtx").get("attributes").get("dn")
                response.append(vrf_name)
    except Exception as e:
        logger.exception("Exception occurred, Error: {}".format(e))
    logger.info("Vrf response after parsing: {}".format(response))
    return response


@time_it
def update_vrf_in_db(tn):
    """This would update vrf in database"""
    try:
        connection = db_obj.engine.connect()
        vrf_db = db_obj.select_from_table(
            connection,
            db_obj.VRF_TABLE_NAME
        )
        connection.close()
        vrf_dc = dict()
        for each in vrf_db:
            vrf_dc[each[0]] = True
        vrf_apic = get_vrf_from_apic(tn)
        connection = db_obj.engine.connect()
        with connection.begin():
            for each in vrf_apic:
                if each not in vrf_dc:
                    db_obj.insert_into_table(
                        connection,
                        db_obj.VRF_TABLE_NAME,
                        [each]
                    )
        connection.close()
        logger.info("Available vrfs in db: {}".format(vrf_db))
        vrf_to_send = vrf_apic[:]
        for each in vrf_db:
            tmp = each[0].split("/")
            if len(tmp) == 3:
                db_tn = tmp[1].split("-", 1)[-1]
                db_vrf = tmp[2].split("-", 1)[-1]
                if tn == db_tn:
                    vrf_to_send.append(db_vrf)
        logger.info("vrf to send: {}".format(vrf_to_send))
        vrf_to_send = set(list(map(lambda x: x.split("ctx-")[-1], vrf_to_send)))
        logger.info("vrf to send: {}".format(vrf_to_send))
        return json.dumps({
            "status_code": "200",
            "payload": list(vrf_to_send),
            "message": "OK"
        })
    except Exception as e:
        logger.exception("Exception occurred, Error: {}".format(e))
        return json.dumps({
            "status_code": "300",
            "payload": [],
            "message": "Could not load VRF for tenant {}".format(tn)
        })


def format_vrf(vrf):
    vrf = vrf.split("/")[1:]
    vrf = list(map(lambda x: x.split("-", 1)[1], vrf))
    return '/'.join(vrf)


def filter_apic_data(apic_data, vrfs):
    if "-" == vrfs:
        return apic_data

    try:
        vrfs = set(map(format_vrf, vrfs))
        response = []
        for each in apic_data:
            if each.get("VRF") in vrfs:
                response.append(each)
        return response
    except Exception as e:
        logger.info("Error in filter_apic_data, Error: {}".format(e))


def change_data_fetch_status(status):
    connection = db_obj.engine.connect()
    data = db_obj.select_from_table(
        connection,
        db_obj.DATA_FETCH_TABLE_NAME
    )
    if len(data) == 0:
        with connection.begin():
            db_obj.insert_and_update(
                connection,
                db_obj.DATA_FETCH_TABLE_NAME,
                [status]
            )
    elif data[0][0] is not status:
        with connection.begin():
            db_obj.insert_and_update(
                connection,
                db_obj.DATA_FETCH_TABLE_NAME,
                [status],
                {'running': not status}
            )
    connection.close()

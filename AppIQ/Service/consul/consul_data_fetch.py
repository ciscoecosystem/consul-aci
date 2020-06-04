"""This module get consul data and put in DB

This fetches data using consul_util on a regular 
intercal and then puts it into the database.

"""

# TODO: Node services and Node checks can run parallel,Servce Info and Check can run parallel
# TODO: Testcase for this - using mock/realtime things
# TODO: multi threading

import custom_logger
import alchemy_core as database
from consul_utils import Consul
from apic_utils import AciUtils
# from yaml_utils import get_conf_value
from decorator import exception_handler

import time
import json
import base64
import threading
from itertools import repeat
import concurrent.futures
from threading_util import ThreadSafeDict

logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")
db_obj = database.Database()
db_obj.create_tables()

POLL_INTERVAL = 2 #get_conf_value('POLL_INTERVAL')      # interval in minutes
CHECK_AGENT_LIST = 3 #get_conf_value('CHECK_AGENT_LIST') # interval in sec
THREAD_POOL = 10 #get_conf_value('THREAD_POOL') # Pool size for all thread pools


@exception_handler
def get_nodes(nodes_dict, agent):
    """Get catalog nodes and put it in the dict
    
    nodes_dict: dict to store all unique nodes of a DC
    agent: agent to be used to fetch the data
    """

    logger.info("Nodes for agent: {}".format(str(agent)))

    consul_obj = Consul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
    # consul_obj.check_connection()
    list_of_nodes = consul_obj.nodes()

    for node in list_of_nodes:
        node_id = node.get('node_id')
        agent_addr = agent.get('ip') + ':' + agent.get('port')
        if not nodes_dict.has_key(node_id):
            node.update({
                'agent_consul_obj': consul_obj,
                'agent_addr': [agent_addr]
            })
            with nodes_dict as active_node:
                active_node[node_id] = node
        elif agent_addr not in node['agent_addr']:
            node['agent_addr'].append(agent_addr)


@exception_handler
def get_services(services_dict, node):
    """Get node services and put it in the dict
    
    services_dict: dict to store all unique services of a DC
    node: node's service to be fetched
    """

    logger.info("Services for node: {}".format(str(node.get('node_name'))))

    consul_obj = node.get('agent_consul_obj')
    node_name = node.get('node_name')
    node_id = node.get('node_id')
    service_list = consul_obj.nodes_services(node_name)
    
    for service in service_list:
        service_key = service.get('service_id') + node_id
        if not services_dict.has_key(service_key):
            service.update({
                'agent_consul_obj': consul_obj,
                'node_id': node_id,
                'agent_addr': node.get('agent_addr')
            })
            with services_dict as active_service:
                active_service[service_key] = service
    

@exception_handler
def get_node_checks(node_checks_dict, node):
    """Get node checks
    
    node: node's checks to be fetched
    """

    logger.info("Node check for: {}".format(str(node.get('node_name'))))

    consul_obj = node.get('agent_consul_obj')
    node_name = node.get('node_name')
    node_checks = consul_obj.detailed_node_check(node_name)

    for node_check in node_checks:
        check_key = node_check.get('CheckID') + node.get('node_id')
        if not node_checks_dict.has_key(check_key):
            node_check.update({
                'node_id': node.get('node_id'),
                'node_name': node_name,
                'agent_addr': node.get('agent_addr')
            })
            with node_checks_dict as active_node:
                active_node[check_key] = node_check


@exception_handler
def get_service_info(service):
    """Get Service info
    
    service: service's info to be fetched
    """
    
    logger.info("Services info for: {}".format(str(service.get('service_name'))))

    consul_obj = service.get('agent_consul_obj')
    service_name = service.get('service_name')
    service_tags, service_kind, service_ns = consul_obj.service_info(service_name)

    service.update({
        'service_tags': service_tags,
        'service_kind': service_kind,
        'service_namespace': service_ns
    })


@exception_handler
def get_service_checks(service_checks_dict, service):
    """Get service checks
    
    service: service's checks to be fetched
    """

    logger.info("Services checks for: {}".format(str(service.get('service_name'))))

    consul_obj = service.get('agent_consul_obj')
    service_name = service.get('service_name')
    service_id = service.get('service_id')
    service_checks = consul_obj.detailed_service_check(service_name, service_id)

    for service_check in service_checks:
        check_key = service_check.get('CheckID') + service_id
        if not service_checks_dict.has_key(check_key):
            service_check.update({
                'service_id': service_id,
                'agent_addr': service.get('agent_addr')
            })
            with service_checks_dict as active_service:
                active_service[check_key] = service_check


def data_fetch():
    """Fetching Consul data and store it to DB

    This functions fetches all the Consul data and stores it to DB.
    This is done for each Datacenter one by one
    """

    while True:
    
        try:
            # Starting time of the thread
            start_time = time.time()

            # This is the list with all ips of consul
            consul_ip_list = set()

            # get agent list from db
            agents = list(db_obj.select_from_table(db_obj.LOGIN_TABLE_NAME))
            agent_list = []
            for agent in agents:
                status = int(agent[4])
                if status == 1:
                    decoded_token = base64.b64decode(agent[3]).decode('ascii')
                    agent_list.append(
                        {
                            'ip': agent[0],
                            'port': agent[1],
                            'protocol': agent[2],
                            'token': decoded_token,
                            'datacenter': agent[5],
                        }
                    )

            # if there is no agent list on 
            # db check it evety CHECK_AGENT_LIST sec
            if not agent_list:
                logger.info("No Agents found in the Login table, retrying after {}sec".format(CHECK_AGENT_LIST))
                time.sleep(CHECK_AGENT_LIST)
                continue

            datacenter_list = {}
            for agent in agent_list:
                datacenter_list.setdefault(agent.get('datacenter'), []).append(agent)

            # Ittrate over each datacenter to fetch the data
            for datacenter, agents in datacenter_list.items():
                
                logger.info("Data fetch for dc: {}".format(datacenter))

                # Creating a list of agents
                agent_addr_list = []
                for agent in agents:
                    agent_addr_list.append(agent.get('ip') + ':' + agent.get('port'))

                # Thread safe dicts
                nodes_dict = ThreadSafeDict()
                services_dict = ThreadSafeDict()
                node_checks_dict = ThreadSafeDict()
                service_checks_dict = ThreadSafeDict()

                nodes_key = set()
                services_key = set()
                node_checks_key = set()
                service_checks_key = set()

                # Ittrate for every agent of that DC 
                # and create a unique list of nodes.
                with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
                    for agent in agents:
                        executor.submit(get_nodes, nodes_dict, agent)

                # Inserting Nodes data in DB
                for node_id, node_val in nodes_dict.items():
                    db_obj.insert_and_update(db_obj.NODE_TABLE_NAME ,
                        (
                            node_val.get('node_id'),
                            node_val.get('node_name'),
                            node_val.get('node_ips'),
                            datacenter,
                            node_val.get('agent_addr')
                        ),
                        {
                            'node_id': node_val.get('node_id')
                        }
                    )

                    # Add node ip to consul ip list
                    for ip in node_val.get('node_ips'):
                        consul_ip_list.add(ip)

                    # Add node_id to key set
                    nodes_key.add(node_val.get('node_id'))

                # Remove deleted Node data.
                node_data = list(db_obj.select_from_table(db_obj.NODE_TABLE_NAME))
                for node in node_data:
                    agents = node[4]
                    for agent in agents:
                        if agent in agent_addr_list and node[0] not in nodes_key:
                            if len(agents) == 1:
                                db_obj.delete_from_table(db_obj.NODE_TABLE_NAME,{'node_id': node[0]})
                            elif len(agents) > 1:
                                node[4].remove(agent)
                                db_obj.insert_and_update(db_obj.NODE_TABLE_NAME, node, {'node_id': node[0]})

                logger.info("Data updation in Node Complete.")

                # Ittrate all nodes and get all services
                with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
                    for node in nodes_dict.values():
                        executor.submit(get_services, services_dict, node)
                
                # Ittrate all nodes and get node checks
                with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
                    for node in nodes_dict.values():
                        executor.submit(get_node_checks, node_checks_dict, node)

                # Inserting Nodes checks data in DB
                for node in node_checks_dict.values():
                    db_obj.insert_and_update(db_obj.NODECHECKS_TABLE_NAME,
                        (
                            node.get('CheckID'),
                            node.get('node_id'),
                            node.get('node_name'),
                            node.get('Name'),
                            node.get('ServiceName'),
                            node.get('Type'),
                            node.get('Notes'),
                            node.get('Output'),
                            node.get('Status'),
                            node.get('agent_addr')
                        ),
                        {
                            'check_id': node.get('CheckID'),
                            'node_id': node.get('node_id')
                        }
                    )

                    # Add node_id, check_id to key set
                    node_checks_key.add((node.get('CheckID'), node.get('node_id')))

                node_checks_data = list(db_obj.select_from_table(db_obj.NODECHECKS_TABLE_NAME))
                for node in node_checks_data:
                    agents = node[9]
                    for agent in agents:
                        if agent in agent_addr_list and (node[0], node[1]) not in node_checks_key:
                            if len(agents) == 1:
                                db_obj.delete_from_table(db_obj.NODECHECKS_TABLE_NAME,{'check_id': node[0], 'node_id': node[1]})
                            elif len(agents) > 1:
                                node[9].remove(agent)
                                db_obj.insert_and_update(db_obj.NODECHECKS_TABLE_NAME, node, {'check_id': node[0], 'node_id': node[1]})

                logger.info("Data updation in Node Checks Complete.")

                # Ittrate all services and get services info
                with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
                    for service in services_dict.values():
                        executor.submit(get_service_info, service)

                # Inserting Services into DB
                for service in services_dict.values():
                    db_obj.insert_and_update(db_obj.SERVICE_TABLE_NAME,
                        (
                            service.get('service_id'),
                            service.get('node_id'),
                            service.get('service_name'),
                            service.get('service_ip'),
                            service.get('service_port'),
                            service.get('service_address'),
                            service.get('service_tags'),
                            service.get('service_kind'),
                            service.get('service_namespace'),
                            datacenter,
                            service.get('agent_addr')
                        ),
                        {
                            'service_id': service.get('service_id'),
                            'node_id': service.get('node_id')
                        }
                    )

                    # Add service ip to consul ip list
                    consul_ip_list.add(service.get('service_ip'))

                    # Add service_id, node_id to key set
                    services_key.add((service.get('service_id'), service.get('node_id')))

                service_data = list(db_obj.select_from_table(db_obj.SERVICE_TABLE_NAME))
                for service in service_data:
                    agents = service[10]
                    for agent in agents:
                        if agent in agent_addr_list and (service[0], service[1]) not in services_key:
                            if len(agents) == 1:
                                db_obj.delete_from_table(db_obj.SERVICE_TABLE_NAME,{'service_id': service[0],'node_id': service[1]})
                            elif len(agents) > 1:
                                service[10].remove(agent)
                                db_obj.insert_and_update(db_obj.SERVICE_TABLE_NAME, service, {'service_id': service[0],'node_id': service[1]})

                logger.info("Data updation in Service Complete.")

                # Ittrate all services and get services checks
                with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
                    for service in services_dict.values():
                        executor.submit(get_service_checks, service_checks_dict, service)

                # Inserting Service Checks in DB
                for service in service_checks_dict.values():
                    db_obj.insert_and_update(db_obj.SERVICECHECKS_TABLE_NAME,
                        (
                            service.get('CheckID'),
                            service.get('service_id'),
                            service.get('ServiceName'),
                            service.get('Name'),
                            service.get('Type'),
                            service.get('Notes'),
                            service.get('Output'),
                            service.get('Status'),
                            service.get('agent_addr')
                        ),
                        {
                            'check_id': service.get('CheckID'),
                            'service_id': service.get('service_id')
                        }
                    )

                    # Add check_id and service_id to key set
                    service_checks_key.add((service.get('CheckID'), service.get('service_id')))

                service_checks_data = list(db_obj.select_from_table(db_obj.SERVICECHECKS_TABLE_NAME))
                for service in service_checks_data:
                    agents = service[8]
                    for agent in agents:
                        if agent in agent_addr_list and (service[0], service[1]) not in service_checks_key:
                            if len(agents) == 1:
                                db_obj.delete_from_table(db_obj.SERVICECHECKS_TABLE_NAME, {'check_id': service[0],'service_id': service[1]})
                            elif len(agents) > 1:
                                service[8].remove(agent)
                                db_obj.insert_and_update(db_obj.SERVICECHECKS_TABLE_NAME, service, {'check_id': service[0],'service_id': service[1]})

                logger.info("Data updation in Service Checks Complete.")

                logger.info("Data fetch for datacenter {} complete.".format(datacenter))

            logger.info("Data fetch for Consul complete.")


            # Data fetch for APIC
            logger.info("Start data fetch for APIC.")

            # get tenant list from db
            tenants = list(db_obj.select_from_table(db_obj.TENANT_TABLE_NAME))
            tenant_list = []
            for tenant in tenants:
                tenant_list.append(tenant[0])

            aci_obj = AciUtils()

            for tenant in tenant_list:
                ep_data = aci_obj.apic_fetch_ep_data(tenant)

                # check if even a single ip of ep is maped to consul
                flag = False
                for ep in ep_data:
                    if ep.get('ip') in consul_ip_list:
                        flag = True

                if not flag:
                    logger.info("NO EP in tenant {} mapped to any consul nodes or services.".format(tenant))
                    continue

                ep_key = set()
                epg_key = set()

                for ep in ep_data:
                    db_obj.insert_and_update(db_obj.EP_TABLE_NAME,
                        (
                            ep.get('mac'),
                            ep.get('ip'),
                            ep.get('tenant'),
                            ep.get('dn'),
                            ep.get('vm_name'),
                            ep.get('interfaces'),
                            ep.get('vmm_domain'),
                            ep.get('controller'),
                            ep.get('learning_src'),
                            ep.get('multi_cast_addr'),
                            ep.get('encap'),
                            ep.get('hosting_servername'),
                            ep.get('is_cep'),
                        ),
                        {
                            'mac': ep.get('mac'),
                            'ip': ep.get('ip'),
                        }
                    )

                    # Add mac, ip to key set
                    ep_key.add((ep.get('mac'), ep.get('ip')))

                ep_data = list(db_obj.select_from_table(db_obj.EP_TABLE_NAME))
                for ep in ep_data:
                    if ep[2] == tenant and (ep[0], ep[1]) not in ep_key:
                        db_obj.delete_from_table(db_obj.EP_TABLE_NAME, ep, {'mac': ep[0], 'ip': ep[1]})

                logger.info("Data updation in EP Complete.")

                epg_data = aci_obj.apic_fetch_epg_data(tenant)
                for epg in epg_data:
                    db_obj.insert_and_update(db_obj.EPG_TABLE_NAME,
                        (
                            epg.get('dn'),
                            epg.get('tenant'),
                            epg.get('epg'),
                            epg.get('bd'),
                            epg.get('contracts'),
                            epg.get('vrf'),
                            epg.get('epg_health'),
                            epg.get('app_profile'),
                        ),
                        {
                            'dn': epg.get('dn')
                        }
                    )

                    # Add dn to key set
                    epg_key.add(epg.get('dn'))

                epg_data = list(db_obj.select_from_table(db_obj.EPG_TABLE_NAME))
                for epg in epg_data:
                    if epg[1] == tenant and epg[0] not in epg_key:
                        db_obj.delete_from_table(db_obj.EPG_TABLE_NAME, epg, {'dn': epg[0]})

                logger.info("Data updation in EPG Complete.")

            logger.info("Data fetch complete:")

        except Exception as e:
            logger.info("Error in data fetch: {}".format(str(e)))

        current_time = time.time()
        time_to_sleep = (start_time + POLL_INTERVAL*60) - current_time
        if time_to_sleep > 0:
            logger.info("Data fetch thread sleeping for interval: {}".format(time_to_sleep))
            time.sleep(time_to_sleep)

"""This module get consul data and put in DB

This fetches data using consul_util on a regular 
intercal and then puts it into the database.


Algorithm:

    1. Fetch all agent from table.

    2. For all Datacenter

        2.1. Fetch all the agent of that datacenter

        2.2. Fetch all the dc nodes from each agent (using a thread pool)

        2.3. Aggregate to get set of nodes.

        2.4. Put Nodes in DB

            2.4.1. Insert new records.

            2.4.2. Update old records.

            2.4.3. Put updated old records in Audit table.

        2.5. Fetch Services, NodeChecks for every node (using a thread pool)

        2.6. Put NodeChecks in DB

            2.6.1. Insert new records.

            2.6.2. Update old records.

            2.6.3. Put updated old records in Audit table.

        2.7. Aggregate to get set of services

        2.8. Fetch Service info, Service Checks

        2.9. Put Service and ServiceChecks in DB

            2.9.1. Insert new records.

            2.9.2. Update old records.

            2.9.3. Put updated old records in Audit table.

"""

# TODO: Node services and Node checks can run parallel,Servce Info and Check can run parallel
# TODO: DB insertion everywhere
# TODO: Testcase for this - using mock/realtime things

import custom_logger
import alchemy_new as database
from consul_utils import Consul
from apic_utils import AciUtils

import time
import json
import threading
from itertools import repeat
from threading_util import ThreadSafeDict
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor

logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")
db_obj = database.Database()
db_obj.create_tables()

POLL_INTERVAL = 1       # interval in minutes
CHECK_AGENT_LIST = 3    # interval in sec
THREAD_POOL = 10        # Pool size for all thread pools
TENANT = 'AppDynamics'


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
        if not nodes_dict.has_key(node_id):
            node.update({
                'agent_consul_obj': consul_obj
            })
            with nodes_dict as active_node:
                active_node[node_id] = node


def get_services(services_dict, node):
    """Get node services and put it in the dict
    
    services_dict: dict to store all unique services of a DC
    node: node's service to be fetched
    """

    logger.info("Services for node: {}".format(str(node.get('node_name'))))

    consul_obj = node.get('agent_consul_obj')
    node_name = node.get('node_name')
    service_list = consul_obj.nodes_services(node_name)
    
    for service in service_list:
        service_id = service.get('service_id')
        if not services_dict.has_key(service_id):
            service.update({
                'agent_consul_obj': consul_obj
            })
            service['node_id'] = node.get('node_id')
            with services_dict as active_service:
                active_service[service_id] = service
    

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
                'node_name': node_name
            })
            with node_checks_dict as active_service:
                node_checks_dict[check_key] = node_check


def get_service_info(service):
    """Get Service info
    
    service: service's info to be fetched
    """
    
    logger.info("Services info for: {}".format(str(service.get('node_name'))))

    consul_obj = service.get('agent_consul_obj')
    service_name = service.get('service_name')
    service_tags, service_kind, service_ns = consul_obj.service_info(service_name)

    service.update({
        'service_tags': service_tags,
        'service_kind': service_kind,
        'service_namespace': service_ns  
    })


def get_service_checks(service_checks_dict, service):
    """Get service checks
    
    service: service's checks to be fetched
    """

    logger.info("Services checks for: {}".format(str(service.get('node_name'))))

    consul_obj = service.get('agent_consul_obj')
    service_name = service.get('service_name')
    service_id = service.get('service_id')
    service_checks = consul_obj.detailed_service_check(service_name, service_id)

    for service_check in service_checks:
        check_key = service_check.get('CheckID') + service_id
        if not service_checks_dict.has_key(check_key):
            service_check.update({
                'service_id': service_id
            })
            with service_checks_dict as active_service:
                service_checks_dict[check_key] = service_check


def data_fetch():
    """Fetching Consul data and store it to DB

    This functions fetches all the Consul data and stores it to DB.
    This is done for each Datacenter one by one
    """

    while True:
    
        try:
            # Starting time of the thread
            start_time = time.time()

            # get agent list from db
            # db.read_agent_list()/read_login
            agent_list = [
                {
                    'datacenter': 'cisco-ecosystem-internal-new',
                    'ip': '10.23.239.14',
                    'port': '8500',
                    'token': '',
                    'protocol': 'http'
                }
            ] 

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

                # Thread safe dicts
                nodes_dict = ThreadSafeDict()
                services_dict = ThreadSafeDict()
                node_checks_dict = ThreadSafeDict()
                service_checks_dict = ThreadSafeDict()

                # Define an executor for all thread processing
                # executor = ThreadPoolExecutor(max_workers = THREAD_POOL)

                # Ittrate for every agent of that DC 
                # and create a unique list of nodes.
                # executor.map(get_nodes, repeat(nodes_dict), agents)
                for agent in agents:
                    get_nodes(nodes_dict, agent)

                # Inserting Nodes data in DB
                nodes_list = []
                for node_id, node_val in nodes_dict.items():
                    nodes_list.append(
                        (
                            node_val.get('node_id'),
                            node_val.get('node_name'),
                            [str(node_val.get('node_ips'))], # This need to be only: node_val.get('node_ips')
                            datacenter
                        )
                    )
                db_obj.insert_into_node(nodes_list)

                logger.info("Nodes dict: {}".format(str(nodes_dict)))

                # Ittrate all nodes and get all services
                # executor.map(get_services, repeat(services_dict), nodes_dict.values())
                for node in nodes_dict.values():
                    get_services(services_dict, node)

                logger.info("Nodes dict: {}".format(str(nodes_dict)))

                # Ittrate all nodes and get node checks
                # executor.map(get_node_checks, repeat(node_checks_dict), nodes_dict.values())
                for node in nodes_dict.values():
                    get_node_checks(node_checks_dict, node)

                # Inserting Nodes checks data in DB
                node_checks_list = []
                for node in node_checks_dict.values():
                    node_checks_list.append(
                        (
                            node.get('node_id'),
                            node.get('CheckID'),
                            node.get('node_name'),
                            node.get('Name'),
                            node.get('ServiceName'),
                            node.get('Type'),
                            node.get('Notes'),
                            node.get('Output'),
                            str(node.get('Status')), # this should be a dict or json
                            datacenter
                        )
                    )
                db_obj.insert_into_node_checks(node_checks_list)

                # Ittrate all services and get services info
                # executor.map(get_service_info, services_dict.values())
                for service in services_dict.values():
                    get_service_info(service)

                # Inserting Services into DB
                service_list = []
                for service in services_dict.values():
                    service_list.append(
                        (
                            service.get('service_id'),
                            service.get('node_id'),
                            service.get('service_name'),
                            service.get('service_ip'),
                            int(service.get('service_port')),
                            service.get('service_address'),
                            [str(service.get('service_tags'))],
                            service.get('service_kind'),
                            service.get('service_namespace'),
                            datacenter
                        )
                    )
                db_obj.insert_into_service(service_list)

                # Ittrate all services and get services checks
                # executor.map(get_service_checks, repeat(service_checks_dict), services_dict.values())
                for service in services_dict.values():
                    get_service_checks(service_checks_dict, service)

                # Inserting Service Checks in DB
                service_check_list = []
                for service in service_checks_dict.values():
                    service_check_list.append(
                        (
                            service.get('CheckID'),
                            service.get('service_id'),
                            service.get('ServiceName'),
                            service.get('Name'),
                            service.get('Type'),
                            service.get('Notes'),
                            service.get('Output'),
                            str(service.get('Status'))
                        )
                    )
                db_obj.insert_into_service_checks(service_check_list)

                aci_obj = AciUtils()

                ep_data = aci_obj.apic_fetch_ep_data(TENANT)

                ep_list = []
                for ep in ep_data:
                    ep_list.append(
                        (
                            ep.get('mac'),
                            ep.get('ip'),
                            ep.get('tenant'),
                            ep.get('dn'),
                            ep.get('vm_name'),
                            [str(ep.get('interfaces'))],
                            ep.get('vmm_domain'),
                            ep.get('controller'),
                            ep.get('learning_src'),
                            ep.get('multi_cast_addr'),
                            ep.get('encap'),
                            ep.get('hosting_servername'),
                            ep.get('is_cep'),
                        )
                    )
                db_obj.insert_into_ep(ep_list)

                epg_data = aci_obj.apic_fetch_epg_data(TENANT)

                epg_list = []
                for epg in epg_data:
                    epg_list.append(
                        (
                            epg.get('dn'),
                            epg.get('tenant'),
                            epg.get('epg'),
                            epg.get('bd'),
                            [str(epg.get('contracts'))],
                            epg.get('vrf'),
                            epg.get('epg_health'),
                            epg.get('app_profile'),
                        )
                    )
                db_obj.insert_into_epg(epg_list)

                logger.info("Data fetch complete:")

        except Exception as e:
            logger.info("Error in data fetch: {}".format(str(e)))

        current_time = time.time()
        time_to_sleep = (start_time + POLL_INTERVAL*60) - current_time
        if time_to_sleep > 0:
            logger.info("Data fetch thread sleeping for interval: {}".format(time_to_sleep))
            time.sleep(time_to_sleep)

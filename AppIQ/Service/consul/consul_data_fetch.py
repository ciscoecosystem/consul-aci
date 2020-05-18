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
from consul_utils import Cosnul

import time
import threading
from itertools import repeat
from threading_util import ThreadSafeDict
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor

logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")

POLL_INTERVAL = 1       # interval in minutes
CHECK_AGENT_LIST = 3    # interval in sec
THREAD_POOL = 10


def data_fetch():
    """Fetching Consul data and store it to DB

    This functions fetches all the Consul data and stores it to DB.
    This is done for each Datacenter one by one
    """

    while True:
    
        # Starting time of the thread
        start_time = time.time()

        # get agent list from db
        agent_list = [] # db.get_agent_list()

        # if there is no agent list on 
        # db check it evety CHECK_AGENT_LIST sec
        if not agent_list:
            time.sleep(CHECK_AGENT_LIST)
            continue

        datacenter_list = {}
        for agent in agent_list:
            datacenter_list.setdefault(agent.get('datacenter'), []).append(agent)

        # Ittrate over each datacenter to fetch the data
        for datacenter, agents in datacenter_list.items():
            
            # Nodes thread safe dict
            nodes_dict = ThreadSafeDict()

            # Define an executor for all thread processing
            executor = ThreadPoolExecutor(max_workers = THREAD_POOL)

            # Ittrate for every agent of that DC 
            # and create a unique list of nodes.
            executor.map(get_nodes, repeat(nodes_dict), agents)

            # Services thread safe dict
            services_dict = ThreadSafeDict()

            # Ittrate all nodes and get all services
            executor.map(get_services, repeat(services_dict), nodes_dict.values())

            # Ittrate all nodes and get node checks
            executor.map(get_node_checks, nodes_dict.values())

            # Ittrate all services and get services info
            executor.map(get_service_info, services_dict.values())

            # Ittrate all services and get services checks
            executor.map(get_service_checks, services_dict.values())

        current_time = time.time()
        time_to_sleep = (start_time + POLL_INTERVAL*60) - current_time
        if time_to_sleep > 0:
            logger.info("Data fetch thread sleeping for interval: {}".format(time_to_sleep))
            time.sleep(time_to_sleep)
            

def get_nodes(nodes_dict, agent):
    """Get catalog nodes and put it in the dict
    
    nodes_dict: dict to store all unique nodes of a DC
    agent: agent to be used to fetch the data
    """

    consul_obj = Cosnul(agent.get('ip'), agent.get('port'), agent.get('token'), agent.get('protocol'))
    list_of_nodes = consul_obj.nodes()

    for node in list_of_nodes:
        node_id = node.get('node_id')
        if not nodes_dict.has_key(node_id):
            node['agent_consul_obj'] = consul_obj
            with nodes_dict as active_node:
                active_node[node_id] = node


def get_services(services_dict, node):
    """Get node services and put it in the dict
    
    services_dict: dict to store all unique services of a DC
    node: node's service to be fetched
    """

    consul_obj = node.get('agent_consul_obj')
    node_name = node.get('node_name')
    service_list = consul_obj.nodes_services(node_name)
    
    for service in service_list:
        service_id = service.get('service_id')
        if not services_dict.has_key(service_id):
            service['agent_consul_obj'] = consul_obj
            with services_dict as active_service:
                active_service[service_id] = service
    

def get_node_checks(node):
    """Get node checks
    
    node: node's checks to be fetched
    """

    consul_obj = node.get('agent_consul_obj')
    node_name = node.get('node_name')
    node_check = consul_obj.node_checks(node_name)


def get_service_info(service):
    """Get Service info
    
    service: service's info to be fetched
    """
    
    consul_obj = service.get('agent_consul_obj')
    service_name = service.get('service_name')
    service_tags, service_kind, service_ns = consul_obj.service_info(service_name)

    service.update({
        'service_tags': service_tags,
        'service_kind': service_kind,
        'service_namespace': service_ns  
    })


def get_service_checks(service):
    """Get service checks
    
    service: service's checks to be fetched
    """

    consul_obj = service.get('agent_consul_obj')
    service_name = service.get('service_name')
    node_check = consul_obj.service_checks(service_name)

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

# TODO: Thread pool implementation and Thread join everywhere
# TODO: DB insertion everywhere
# TODO: Testcase for this - using mock/realtime things



import time
import threading
import custom_logger
from consul_utils import Cosnul
from threading_util import ThreadSafeDict



logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")

POLL_INTERVAL = 1       # interval in minutes
CHECK_AGENT_LIST = 3    # interval in sec


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

            # Ittrate for every agent of that DC 
            # and create a unique list of nodes.
            for agent in agents:
                # TODO: First thread pool inplementation
                t = threading.Thread(target=get_nodes, args=(nodes_dict, agent))
                t.start()

            # TODO: all agents thread join

            # Services thread safe dict
            services_dict = ThreadSafeDict()

            for node_id in nodes_dict:
                node = nodes_dict[node_id]

                # TODO: thread pool
                t1 = threading.Thread(target=get_services, args=(services_dict, node))
                t1.start()

                # TODO: thread pool
                t2  = threading.Thread(target=get_node_checks, args=(node))
                t2.start()

            # TODO: all node services thread join

            for service_id in services_dict:
                service = services_dict[service_id]

                # TODO: thread pool
                t1 = threading.Thread(target=get_service_info, args=(services_dict, service))
                t1.start()

                # TODO: thread pool
                t2  = threading.Thread(target=get_service_checks, args=(service))
                t2.start()

            # TODO: all services thread join
            # TODO: all services checks thread join
            # TODO: all services details thread join

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


def get_service_info(services_dict, service):
    """Get Service info
    
    services_dict: dict to store all unique services of a DC
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

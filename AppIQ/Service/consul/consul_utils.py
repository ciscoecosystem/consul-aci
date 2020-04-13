"""This is a Class for all the API calls to Consul"""

import urls
import json
import requests
from .. import custom_logger


logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")


class Cosnul(object):
    """Consul class"""

    def __init__(self, agent_ip, port, token):
        
        logger.info('Consul Object init for agent: {}:{}'.format(agent_ip, port))

        self.agent_ip = str(agent_ip)
        self.port = str(port)
        self.token = token

        self.session = requests.Session()
        self.connected = False # TODO: remove if no use

        # The base URL is set with protocol http, 
        # if http failes https will be tried
        self.base_url = 'http://{}:{}'.format(self.agent_ip, self.port)
        if self.token:
            logger.info('Token provided')
            self.header = {'X-Consul-Token' : token}


    def check_connection(self):
        """Verify if connection to an agent is possible
        
        if token is provided checks for a token based access
         with both http and https if that fails then same 
         for without token

        if Token is not provided check connection with http
         and https
        """
        
        logger.info('Check Consul Connection')
        try:
            while True:
                if self.header:
                    logger.info("Token provided, trying connecting to agent with token.")
                    response = self.session.get(urls.AUTH.format(self.base_url), headers=self.header)
                    status_code = response.status_code
                    if status_code == 200 or status_code == 201: # TODO: check for range/ check doc
                        logger.info("Successfully connected to {}".format(self.agent_ip))
                        self.connected = True
                        return self.connected

                    # In case of faliure with http, try using https
                    elif 'http:' in self.base_url:
                        logger.info("Connection failed with status_code: {}".format(status_code))
                        logger.info("Trying connection using https")
                        self.base_url = self.base_url.replace("http:", "https:")
                        continue

                    # In case of failiure to connect using both http and https
                    # try connecting without token
                    else:
                        logger.info("Connection failed with https, status_code: {}".format(status_code))
                        logger.info("Trying connection without token using http")
                        self.base_url = self.base_url.replace("https:", "http:")
                        self.header = {} # TODO: header is removed for trying token less connection. Understand the usecsase where it fails
                        continue

                # This is the case when no token is provided by the user or 
                # it is provided but connection has failed
                else:
                    logger.info("Token NOT provided, trying connecting to agent without token.")
                    response = self.session.get(urls.AUTH.format(self.base_url))
                    status_code = response.status_code
                    if status_code == 200 or status_code == 201: # TODO: check for range/ check doc
                        logger.info("Successfully connected to {}".format(self.agent_ip))
                        self.connected = True
                        return self.connected

                    # In case of faliure with http, try using https
                    elif 'http:' in self.base_url:
                        logger.info("Connection failed with status_code: {}".format(status_code))
                        logger.info("Trying connection using https")
                        self.base_url = self.base_url.replace("http:", "https:")
                        continue

                    # When all the cases fail with/without token and with http/https
                    else:
                        logger.info("Connection FAILED for agent {}:{} ".format(self.agent_ip, self.port))
                        self.connected = False
                        return self.connected
        except Exception as e:
            logger.exception('Exception in Consul check connection: {}'.format(str(e)))


    def catalog_nodes(self):
        """Fetching all the nodes using an agent
        
        return: [
                    {
                        node_id:    string: id
                        node_name:  string: name
                        node_ips:   unique string list: ips
                    }, ...
                ]
        """

        logger.info('In Consul Node List')
        node_list = []
        try:
            catalog_nodes = requests.get(urls.CATALOG_NODES.format(self.base_url))
            catalog_nodes = json.loads(catalog_nodes.content)
            logger.debug('Catalog Nodes API data: {}'.format(str(catalog_nodes)))
            
            # Ittrate over each node and get all its unique ips
            for node in catalog_nodes:
                ip_list = []
                ip_list.append(node.get('Address', ''))
                tagged_addr = node.get('TaggedAddresses', {})
                if tagged_addr:
                    ip_list.append(tagged_addr.get('wan_ipv4', ''))
                    ip_list.append(tagged_addr.get('wan', ''))
                    ip_list.append(tagged_addr.get('lan', ''))
                    ip_list.append(tagged_addr.get('lan_ipv4', ''))

                # for removing '' from ip_list
                ip_list = [ip for ip in ip_list if ip]

                node_name = node.get('Node', '')

                node_list.append({
                    'node_id': node.get('ID', ''),
                    'node_name': node_name,
                    'node_ips': list(set(ip_list)),
                    'node_check': node_checks(node_name),
                    'node_services': node_services(node_name)
                })
        except Exception as e:
             logger.exception('Exception in Catalog Nodes: {}'.format(str(e)))

        logger.debug('catalog_nodes return: {}'.format(str(node_list)))
        return node_list


    def nodes_services(self, node_name):
        """This will return all the services of a node
        
        node_name: name of nodes for services
        
        return: [
                    {
                        'service_id':       string: id
                        'service_name':     string: name
                        'service_ip':       string: ip
                        'service_port':     string: port
                        'service_address':  string: service ip,if exists, else parent node ip + port
                        'service_tags':     string list: tags
                        'service_kind':     string: kind
                        'service_checks': {
                                        passing: int: if val > 0
                                        warning: int: if val > 0
                                        failing: int: if val > 0
                                    }
                    }, ...
                ]
        """

        logger.info('In Nodes Services for node: {}'.format(node_name))
        service_list = []
        try:
            # API works for node id also, ask and decide
            services_resp = requests.get(urls.NODE_SERVICES.format(self.base_url, node_name))
            services_resp = json.loads(services_resp.content)
            logger.debug('Node "{}" Services API data: {}'.format(node_name, str(services_resp)))

            for service in services_resp.get('Services'):
                
                # get service check, tags and kind using service name
                service_name = service.get('Service') # This may fail
                service_check = service_checks(service_name)
                service_tags, service_kind = service_tags_kind(service_name)

                # form service_address
                service_ip = service.get('Address')
                service_port = service.get('Port')
                if service_ip:
                    service_address = str(service_ip) + ':' + str(service_port)
                else:
                    service_address = str(node_ip = services_resp.get('Node', {}).get('Address', '')) + ':' + str(service_port)
                
                # Form a dict
                service_list.append({
                    'service_id': service.get('ID', ''),
                    'service_name': service_name,
                    'service_ip': service_ip,
                    'service_port': service_port,
                    'service_address': service_address,
                    'service_checks': service_check,
                    'service_tags': service_tags,
                    'service_kind': service_kind,
                })
        except Exception as e:
            logger.exception('Exception in Nodes Services: {}'.format(str(e)))

        logger.debug('catalog_nodes return: {}'.format(str(service_list)))
        return service_list


    def node_checks(self, node_name):
        """Get node checks

        node_name: name of the node for checks

        return: {
                passing: int: if val > 0
                warning: int: if val > 0
                failing: int: if val > 0
            }
        """

        logger.info('Node Checks for node: {}'.format(node_name))
        check_dict = {}
        try:
            node_resp = requests.get(urls.NODE_CHECK.format(self.base_url, node_name))
            node_resp = json.loads(node_resp.content)
            logger.debug('Node Check API data: {}'.format(node_resp))

            for check in node_resp:
                status = check.get('Status', '')

                # The API return the all the node and service checks,
                # but only the node checks are retuned
                if not check.get('ServiceID') and status:
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
        except Exception as e:
            logger.exception('Exception in Nodes Checks: {}'.format(str(e)))

        return check_dict


    def service_checks(self, service_name):
        """Get all the serveice checks
        
        service_name: name of the service for checks

        return: {
                passing: int: if val > 0
                warning: int: if val > 0
                failing: int: if val > 0
            }
        """

        logger.info('Service Checks for node: {}'.format(service_name))
        check_dict = {}
        try:
            service_resp = requests.get(urls.SERVICE_CHECK.format(self.base_url, service_name))
            service_resp = json.loads(service_resp.content)
            logger.debug('Service Check API data: {}'.format(service_resp))
        
            for check in service_resp:
                status = check.get('Status')
                if status:
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
        except Exception as e:
            logger.exception('Exception in Service Checks: {}'.format(str(e)))

        return check_dict


    def service_tags_kind(self, service_name):
        """Get tag and kind info from details of a service
        
        service_name: name of the service for checks

        return: tupple(tag_list, kind)
                    tag_list: string list
                    kind: string
        """

        logger.info('Service tag and kind info for service: {}'.format(service_name))
        tag_list = []
        service_kind = ''
        try:
            service_resp = requests.get(urls.SERVICE_INFO.format(self.base_url, service_name))
            service_resp = json.loads(service_resp.content)
            logger.debug('Service Details API data: {}'.format(service_resp))

            tags_set = set()
            for val in service_resp[0].get('ServiceTags'):
                tags_set.add(val)
            tag_list = list(tags_set)
            service_kind = service_resp[0].get('ServiceKind')
        except Exception as e:
            logger.exception('Exception in Service Details: {}'.format(str(e)))

        return tag_list, service_kind
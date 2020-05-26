"""This is a Class for all the API calls to Consul"""

import urls
import json
import requests
import custom_logger


logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")


class Consul(object):
    """Consul class"""

    def __init__(self, agent_ip, port, token, protocol):
        
        logger.info('Consul Object init for agent: {}:{}'.format(agent_ip, port))

        self.agent_ip = str(agent_ip)
        self.port = str(port)
        self.token = token
        self.protocol = protocol

        self.session = requests.Session()
        self.connected = False # TODO: remove if no use

        # The base URL is set with protocol http, 
        # if http failes https will be tried
        self.base_url = '{}://{}:{}'.format(self.protocol, self.agent_ip, self.port)
        self.header = {}
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
                    response = self.session.get(urls.AUTH.format(self.base_url), headers=self.header, timeout=5)
                    status_code = response.status_code
                    if status_code == 200:
                        logger.info("Successfully connected to {}".format(self.agent_ip))
                        self.connected = True
                        return self.connected, None

                    # try connecting without token
                    else:
                        logger.info("Connection failed with https, status_code: {}".format(status_code))
                        logger.info("Trying connection without token using http")
                        self.header = {} # TODO: header is removed for trying token less connection. Understand the usecsase where it fails
                        continue

                # This is the case when no token is provided by the user or 
                # it is provided but connection has failed
                else:
                    logger.info("Token NOT provided, trying connecting to agent without token.")
                    response = self.session.get(urls.AUTH.format(self.base_url), timeout=5)
                    status_code = response.status_code
                    if status_code == 200:
                        logger.info("Successfully connected to {}".format(self.agent_ip))
                        self.connected = True
                        message = None

                    elif status_code == 403:
                        logger.info("Connection FAILED for agent {}:{} ".format(self.agent_ip, self.port))
                        self.connected = False
                        message = "403: Authentication failed!"

                    elif status_code == 500:
                        logger.info("Connection FAILED for agent {}:{} ".format(self.agent_ip, self.port))
                        self.connected = False
                        message = "500: Consul Server Error!"

                    # When all the cases fail with/without token
                    else:
                        logger.info("Connection FAILED for agent {}:{} ".format(self.agent_ip, self.port))
                        self.connected = False
                        message = None

                    return self.connected, message

        except requests.exceptions.ConnectTimeout as e:
            logger.exception('ConnectTimeout Exception in Consul check connection: {}'.format(str(e)))
            return self.connected, "Connection Timeout Error"
        except requests.exceptions.RequestException as e:
            logger.exception('RequestException in Consul check connection: {}'.format(str(e)))
            return self.connected, "Connection failed! Please verify IP/DNS:Port."
        except Exception as e:
            logger.exception('Exception in Consul check connection: {}'.format(str(e)))
            return self.connected, None


    def nodes(self):
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
            catalog_nodes = self.session.get(urls.CATALOG_NODES.format(self.base_url))
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
                    'node_ips': list(set(ip_list))
                })
        except Exception as e:
             logger.exception('Exception in Catalog Nodes: {}'.format(str(e)))

        logger.debug('nodes return: {}'.format(str(node_list)))
        return node_list


    def nodes_services(self, node_name):
        """This will return all the services of a node
        
        node_name: name of nodes for services
        
        return: [
                    {
                        service_id:       string: id
                        service_name:     string: name
                        service_ip:       string: ip
                        service_port:     string: port
                        service_address:  string: service ip(if exists)/node ip : port
                    }, ...
                ]
        """

        logger.info('In Nodes Services for node: {}'.format(node_name))
        service_list = []
        try:
            # API works for node id also, ask and decide
            services_resp = self.session.get(urls.NODE_SERVICES.format(self.base_url, node_name))
            services_resp = json.loads(services_resp.content)
            logger.debug('Node "{}" Services API data: {}'.format(node_name, str(services_resp)))

            for service in services_resp.get('Services'):

                # form service_address
                service_ip = service.get('Address')
                service_port = service.get('Port')
                if service_ip:
                    service_address = str(service_ip) + ':' + str(service_port)
                else:
                    service_address = str(services_resp.get('Node', {}).get('Address', '')) + ':' + str(service_port)
                
                # Form a dict
                service_list.append({
                    'service_id': service.get('ID'),
                    'service_name': service.get('Service'),
                    'service_ip': service_ip,
                    'service_port': service_port,
                    'service_address': service_address
                })
        except Exception as e:
            logger.exception('Exception in Nodes Services: {}'.format(str(e)))

        logger.debug('nodes_services return: {}'.format(str(service_list)))
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
            node_resp = self.session.get(urls.NODE_CHECK.format(self.base_url, node_name))
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

        logger.debug('node_checks return: {}'.format(str(check_dict)))
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
            service_resp = self.session.get(urls.SERVICE_CHECK.format(self.base_url, service_name))
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

        logger.debug('service_checks return: {}'.format(str(check_dict)))
        return check_dict


    def service_info(self, service_name):
        """Get tag and kind info from details of a service
        
        service_name: name of the service for checks

        return: tupple(tag_list, kind, namespace)
                    tag_list: string list
                    kind: string
                    namespace/NA: string
        """

        logger.info('Service tag and kind info for service: {}'.format(service_name))
        tag_list = []
        service_kind = ''
        service_namespace = ''
        try:
            service_resp = self.session.get(urls.SERVICE_INFO.format(self.base_url, service_name))
            service_resp = json.loads(service_resp.content)
            logger.debug('Service Details API data: {}'.format(service_resp))

            tags_set = set()
            for val in service_resp[0].get('ServiceTags', []):
                tags_set.add(val)
            tag_list = list(tags_set)
            service_kind = service_resp[0].get('ServiceKind', '')

            # In case of OSS cluster, no key named Namespace is returned, 
            # thus NA will be returned. 
            service_namespace = service_resp[0].get('Namespace', 'NA')
        except Exception as e:
            logger.exception('Exception in Service Details: {}'.format(str(e)))

        logger.debug('service_info return: {}'.format(tag_list, service_kind))
        return tag_list, service_kind, service_namespace


    def datacenter(self):
        """This will return datacenter of an agent
        
        return: string
        """

        logger.info('Datacentres for agent: {}:{}'.format(self.agent_ip, self.port))
        datacenter_name = ''
        try:
            agent_resp = self.session.get(urls.CATALOG_DC.format(self.base_url))
            agent_resp = json.loads(agent_resp.content)
            datacenter_name = agent_resp.get('Config', {}).get('Datacenter', '')
            logger.debug('Datacenter API data: {}'.format(datacenter_name))

        except Exception as e:
            logger.exception("Error in Datacenter: {}".format(e))
        
        logger.debug('datacenter return: {}'.format(str(datacenter_name)))
        return datacenter_name


    def detailed_service_check(self, service_name, service_id):
        """Get serveice checks details
        
        service_name: name of the service for checks

        return: [{
            ServiceName: string
            CheckID: string
            Type: string
            Notes: string
            Output: string
            Name: string
            Status: {
                passing: int: if val > 0
                warning: int: if val > 0
                failing: int: if val > 0
                }
            },...]
        """

        logger.info('Service Checks for service: {}, {}'.format(service_name, service_id))
        service_checks_list = []
        try:
            service_resp = self.session.get(urls.SERVICE_CHECK.format(self.base_url, service_name))
            service_resp = json.loads(service_resp.content)
            logger.debug('Service Check API data: {}'.format(service_resp))
            
            for check in service_resp:
                if check.get("ServiceID").lower() == service_id.lower():
                    service_check = {}
                    service_check["ServiceName"] = check.get("ServiceName")
                    service_check["CheckID"] = check.get("CheckID")
                    service_check["Type"] = check.get("Type")
                    service_check["Notes"] = check.get("Notes")
                    service_check["Output"] = check.get("Output")
                    service_check["Name"] = check.get("Name")
                    if 'passing' == check.get('Status').lower() or 'warning' == check.get('Status').lower():
                        service_check["Status"] = check.get("Status")
                    else:
                        service_check["Status"] = 'failing'
                    service_checks_list.append(service_check)
        except Exception as e:
            logger.exception("error in fatching service checks : " + str(e))

        logger.debug('detailed_service_check return: {}'.format(str(service_checks_list)))
        return service_checks_list


    def detailed_node_check(self, node_name):
        """Get node checks details

        node_name: name of the node for checks

        return: [{
            Name: streing
            ServiceName: string
            CheckID: string
            Type: string
            Notes: string
            Output: string
            Status: {
                passing: int: if val > 0
                warning: int: if val > 0
                failing: int: if val > 0
                }
            },...]
        """

        logger.info('Node Checks for node: {}'.format(node_name))
        node_checks_list = []
        try:
            node_resp = self.session.get(urls.NODE_CHECK.format(self.base_url, node_name))
            node_resp = json.loads(node_resp.content)
            logger.debug('Node Check API data: {}'.format(node_resp))

            for check in node_resp:
                if not check.get("ServiceName"):
                    node_check = {}
                    node_check["Name"] = check.get("Name")
                    node_check["NodeName"] = node_name
                    node_check["ServiceName"] = "-"
                    node_check["CheckID"] = check.get("CheckID")
                    node_check["Type"] = check.get("Type")
                    node_check["Notes"] = check.get("Notes")
                    node_check["Output"] = check.get("Output")
                    if 'passing' == check.get('Status').lower() or 'warning' == check.get('Status').lower():
                        node_check["Status"] = check.get("Status")
                    else:
                        node_check["Status"] = 'failing'
                    node_checks_list.append(node_check)
        except Exception as e:
            logger.exception("error in fatching node checks : " + str(e))

        logger.debug('detailed_node_check return: {}'.format(str(node_checks_list)))
        return node_checks_list


    def get_consul_data(self):
        """
        This will fetch the data from the API and return for now
        Decide the form of data neede in the merge logic and return as per that.

        return: [
                    {
                        node_id:    string: id
                        node_name:  string: name
                        node_ips:   unique string list: ips
                        node_check: {
                                passing: int: if val > 0
                                warning: int: if val > 0
                                failing: int: if val > 0
                            }
                        node_services: [
                                {
                                    service_id:        string: id
                                    service_name:      string: name
                                    service_ip:        string: ip
                                    service_port:      string: port
                                    service_address:   string: service ip(if exists)/node ip : port
                                    service_tags:      string list: tags
                                    service_kind:      string: kind
                                    service_namespace: string: namespace
                                    service_checks: {
                                                    passing: int: if val > 0
                                                    warning: int: if val > 0
                                                    failing: int: if val > 0
                                                }
                                }, ...
                            ]
                    }, ...
                ]
        """

        logger.info('Get all consul data.')
        consul_data = []
        try:

            list_of_nodes = self.nodes()

            for node in list_of_nodes:

                # get all the services info using name
                node_name = node.get('node_name')
                service_list = self.nodes_services(node_name)
                final_service_list = []

                for service in service_list:

                    # get service check, tags and kind using service name
                    service_name = service.get('service_name') # This may fail
                    service_check = self.service_checks(service_name)
                    service_tags, service_kind, service_ns = self.service_info(service_name)

                    # Form final dict
                    final_service_list.append({
                        'service_id': service.get('service_id'),
                        'service_ip': service.get('service_ip'),
                        'service_port': service.get('service_port'),
                        'service_address': service.get('service_address'),
                        'service_name': service_name,
                        'service_checks': service_check,
                        'service_tags': service_tags,
                        'service_kind': service_kind,
                        'service_namespace': service_ns
                    })

                consul_data.append({
                    'node_id': node.get('node_id'),
                    'node_name': node_name,
                    'node_ips': node.get('node_ips'),
                    'node_check': self.node_checks(node_name),
                    'node_services': final_service_list
                })
        except Exception as e:
            logger.exception("Error while merge_aci_data : "+str(e))

        logger.debug('get_consul_data return: {}'.format(str(consul_data)))
        return consul_data
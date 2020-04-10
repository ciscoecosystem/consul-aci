"""This is a Class for all the API calls to Consul"""

import requests
from .. import custom_logger


logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")


class Cosnul(object):
    """Consul class"""

    urls = {
        'members': '/v1/agent/members'
    }

    def __init__(self, agent_ip, port, token):
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
        
        try:
            
            while True:
                if self.header:
                    logger.info("Token provided, trying connecting to agent with token.")
                    response = self.session.get('{}{}'.format(self.base_url, self.urls.get('members')), headers=self.header)
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
                    response = self.session.get('{}{}'.format(self.base_url, self.urls.get('members')))
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

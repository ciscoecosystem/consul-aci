"""This class returns recomanded EP"""

class generateD3Dict(object):
    # Put it in another file named 'generate_d3.py'
    def health_colour(self,health):
        if health == 'NORMAL':
            return 'seagreen'
        if health == 'WARNING':
            return 'orange'
        if health == 'CRITICAL':
            return 'red'


    def generate_d3_compatible_dict(self, data):
        # Get distinct app profiles
        app_profs = set()

        for node in data:
            app_profs.add(node['AppProfile'])
        app_profs_converted = []

        for app_prof in app_profs:
            # Filter out app prof nodes
            app_nodes = filter(lambda x: x['AppProfile'] == app_prof, data)

            # Top level node in Tree (Application Profile)
            app_prof_node = {}
            app_prof_node['name'] = 'AppProf'
            app_prof_node['type'] = '#581552'
            #app_prof_node['label'] = "abc" # app_nodes[0]['appName']##
            app_prof_node['sub_label'] = app_nodes[0]['AppProfile']
            app_prof_node['attributes'] = {}
            app_prof_node['children'] = []

            # 2nd layer nodes in Tree (EPG)
            # distinct EPGs for current application profile
            epgs = set()
            for app_node in app_nodes:
                epgs.add(app_node['EPG'])

            # Iterating for each EPG
            epg_cnt = 1
            for epg in epgs:
                # distinct_epg_tiers = set()
                distinct_epg_ips = set()
                # Extract EPG nodes with same EPG value and get distinct tier name and ip
                epg_nodes = filter(lambda x: x['EPG'] == epg, app_nodes)
                for epg_node in epg_nodes:
                    # distinct_epg_tiers.add(epg_node['tierName'])
                    distinct_epg_ips.add(epg_node['IP'])
                epg_service_list = set()
                epg_service_detalis_list = []

                for epg_node in epg_nodes:
                    service_list = epg_node.get("services", {})
                    for service in service_list:
                        epg_service_list.add(service.get("serviceInstance", ""))
                        service_dict = {
                                "Service" : service["serviceInstance"],
                                "Address" : str(service["serviceIP"]) + ":" + str(service["port"]),
                                "Service Checks" : service["serviceChecks"]
                            }
                        epg_service_detalis_list.append(service_dict)


                epg_dict = {}
                epg_dict['name'] = "EPG"
                epg_dict['fraction'] = epg_nodes[0]['fraction']
                epg_dict['type'] = '#085A87'
                epg_dict['sub_label'] = epg_nodes[0]['EPG']
                epg_dict['label'] = list(epg_service_list)[0] + ", ..." #",".join(epg_service_list)
                epg_dict['attributes'] = {
                    'VRF': epg_nodes[0]['VRF'],
                    'BD': epg_nodes[0]['BD'],
                    'Contracts': epg_nodes[0]['Contracts'],
                    'Nodes': list([{"Node": n['nodeName'], "Node Checks": n['nodeCheck']} for n in epg_nodes]),
                    'Services_List' : epg_service_detalis_list
                }

                epg_dict['children'] = []

                for epg_ip in distinct_epg_ips:
                    # distinct_ep_tiers = set()
                    ep_nodes = filter(lambda x: x['IP'] == epg_ip, epg_nodes)

                    for ep_node in ep_nodes:
                        ep_service_list = []
                        for service in ep_node["services"]:
                            service_dict = {
                                "Service" : service["serviceInstance"],
                                "Address" : str(service["serviceIP"]) + ":" + str(service["port"]),
                                "Service Checks" : service["serviceChecks"]
                            }
                            ep_service_list.append(service_dict)

                        ep_dict = {}
                        ep_dict['name'] = "EP"
                        ep_dict['type'] = '#2DBBAD'
                        ep_dict['sub_label'] = ep_nodes[0]['VM-Name']   # ep_node should be instead of ep_nodes[0]
                        ep_dict['label'] =  ep_node["nodeName"] #",".join(epg_service_list)

                        ep_dict['attributes'] = {
                            "Node" : ep_node["nodeName"],
                            "Node Checks" : ep_node["nodeCheck"],
                            "Services_List" : ep_service_list,
                            'IP': ep_node['IP'],
                            'Interfaces': list(set([x['Interfaces'][0] for x in ep_nodes])),
                            'VMM-Domain': ep_nodes[0]['VMM-Domain'] # ep_node should be instead of ep_nodes[0]
                        }

                        ep_dict['children'] = []
                        for service in ep_node["services"]:
                            node_dict = {}
                            node_dict['name'] = "Service"
                            node_dict['type'] = '#C5D054'
                            if len(service['serviceInstance']) > 11:
                                node_dict['label'] = service['serviceInstance'][:11] + '..'
                            else:
                                node_dict['label'] = service['serviceInstance']

                            node_dict['attributes'] = {
                                "Service" : service['service'],
                                "Service Instance" : service['serviceInstance'],
                                "Address" : str(service["serviceIP"]) + ":" + str(service["port"]),
                                "Service Kind" : service['serviceKind'],
                                "Service Tag" : service['serviceTags'],
                                "Service Checks" : service['serviceChecks']
                            }
                            ep_dict['children'].append(node_dict)
                        
                        epg_dict['children'].append(ep_dict)

                if epg_nodes[0]['Non_IPs']:
                    non_ep_dict={}
                    non_ep_dict['name'] = 'EP'
                    non_ep_dict['type'] = 'grey'
                    non_ep_dict['level'] = 'grey'
                    non_ep_dict['label'] = ''#'App Unmapped EPs'
                    non_ep_dict['sub_label'] = ''#'App Unmapped EPs'
                    non_ep_dict['attributes'] = epg_nodes[0]['Non_IPs']
                    non_ep_dict['fractions'] = epg_nodes[0]['fraction']
                    epg_dict['children'].append(non_ep_dict)

                # List of IPs -
                app_prof_node['children'].append(epg_dict)
                epg_cnt = epg_cnt + 1   # not used

            app_profs_converted.append(app_prof_node)
        return app_profs_converted

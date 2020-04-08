"""Module for TODO:parsing/generating tree data for consul"""

def consul_tree_dict(self, data):
    """Create tree specific dict
    
    input:   The merged CEps data
    output:  list of dict of trees
    """


    # Final list of ap(application profile)
    ap_list = []

    
    # distinct APs
    ap_set= set([node['AppProfile'] for node in data])

    # Iterating for each AP
    for ap in ap_set:

        # Extract ap EPs
        ap_eps = [ep for ep in data if ep['AppProfile'] == ap]

        # Top level node in Tree
        # TODO: lable not sent because not needed in Consul: Try send ''
        ap_node = {
            'name': 'AppProf',
            'type': '#581552',
            'sub_label': ap,
            'attributes': {},
            'children': []
        }

        # distinct EPGs in current AP
        epgs_set = set([ep['EPG'] for ep in ap_eps])

        # Iterating for each EPG
        for epg in epgs_set:

            # Extract EPG EPs
            epg_eps = [ep for ep in ap_eps if ep['EPG'] == epg]

            # 2nd layer nodes in Tree (EPG)
            epg_dict = {
                'name': 'EPG',
                'type': '#085A87',
                'label': "",
                'sub_label': epg,
                'fraction': epg_eps[0]['fraction'],
                'attributes': {
                    'VRF': epg_eps[0]['VRF'],
                    'BD': epg_eps[0]['BD'],
                    'Contracts': epg_eps[0]['Contracts'],
                    'Nodes': list([{"Node": n['nodeName'], "Node Checks": n['nodeCheck'], "Reporting Node IP": n['ipAddressList'][0]} for n in epg_eps]),
                    'Services_List': []
                },
                'children': []
            }

            # distinct ips in current EPg
            epg_ip_set = set([ep['IP'] for ep in epg_eps])

            # Iterating for each IP in EPG
            for epg_ip in epg_ip_set:

                # Extract EPs with above ip
                ep_nodes = [ep for ep in epg_eps if ep['IP'] == epg_ip]

                # TODO: understand if we need to ittrate over distinct ip and merge all EPs,
                #  is there possiblity if getting EPs with same IP from the correlation logic for Consul. 
                # It is possible in AppD (Every node is maped to and Ep and 
                # then that EP added to the list) 
                # Can be done keepinf it in safe side. But then same thing needs to be verified in Detais too
                for ep_node in ep_nodes:

                    # TODO: this is the issue,
                    # Either it should be in the above loope,
                    # Or both the loops shoild be merged

                    # 3rd layer nodes in Tree (EP)
                    ep_dict = {
                        'name': "EP",
                        'type': '#2DBBAD',
                        'label': ep_node["node_name"],
                        'sub_label': ep_node['VM-Name'],
                        'attributes': {
                            "Node" : ep_node["node_name"],
                            "Node Checks" : ep_node["node_check"],
                            "Reporting Node IP": ep_node['ipAddressList'][0],
                            "Services_List" : [],
                            'IP': ep_node['IP'],
                            'Interfaces': list(set([x['Interfaces'][0] for x in ep_nodes])), # TODO: understand y is this [0]
                            'VMM-Domain': ep_node['VMM-Domain']
                        },
                        'children': []
                    }

                    # Iterating for each Service in EP
                    for service in ep_node["services"]:

                        if len(service['service_instance']) > 11:
                            service_label = service['service_instance'][:11] + '..'
                        else:
                            service_label = service['service_instance']

                        if service["service_ip"]:
                            service_address = str(service["service_ip"]) + ":" + str(service["port"])
                        else:
                            service_address = str(ep_node['ip_list'][0]) + ":" + str(service["port"]) # for now 0th is taken, will change

                        # 4rd layer nodes in Tree (Service)
                        service_dict = {
                            'name': "Service",
                            'type': '#C5D054',
                            'label': service_label,
                            'attributes': {
                                "Service" : service['service'],
                                "Service Instance" : service['service_instance'],
                                "Address" : service_address,
                                "Service Kind" : service['service_kind'],
                                "Service Tag" : service['service_tags'],
                                "Service Checks" : service['service_checks']
                            }
                        }


                        # Service for side pane
                        service_side_pane = {
                            "Service" : service["service_instance"],
                            "Address" : service_address,
                            "Service Checks" : service["service_checks"]
                        }

                        # Adding services to EP attributes
                        if service_side_pane not in ep_dict['attributes']['Services_List']:
                            ep_dict['attributes']['Services_List'].append(service_side_pane)

                        # Adding services to EPG attributes
                        if service_side_pane not in epg_dict['attributes']['Services_List']:
                            epg_dict['attributes']['Services_List'].append(service_side_pane)

                        # Add lable to EPG if not there
                        if not epg_dict['label']:
                            epg_dict['label'] = service["service_instance"] + ", ..."

                        # Add Service to EP
                        ep_dict['children'].append(service_dict)


                    # Node for side pane
                    ep_side_pane = {
                        "Node": ep_node['nodeName'],
                        "Node Checks": ep_node['nodeCheck']
                    }

                    # Adding Node to EPG attributes
                    if ep_side_pane not in epg_dict['attributes']['Nodes']:
                        epg_dict['attributes']['Nodes'].append(ep_side_pane)


                    # Add EP to EPG
                    epg_dict['children'].append(ep_dict)

            #  Iterating for each Non service end point in EPG
            if epg_eps[0]['Non_IPs']: # TODO: understand Y is this [0], Also the key
                non_ep_dict={}
                non_ep_dict['name'] = 'EP'
                non_ep_dict['type'] = 'grey'
                non_ep_dict['level'] = 'grey' # Verify 2 labels
                non_ep_dict['label'] = '' # Verify 2 labels
                non_ep_dict['sub_label'] = '' # Verify if this is needed or not.
                non_ep_dict['attributes'] = epg_eps[0]['Non_IPs']
                non_ep_dict['fractions'] = epg_eps[0]['fraction']
                epg_dict['children'].append(non_ep_dict)

            # Add EPG to AP
            ap_node['children'].append(epg_dict)

        # Add AP to responce list
        ap_list.append(ap_node)
    return ap_list

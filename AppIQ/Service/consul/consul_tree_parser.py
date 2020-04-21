"""Module for parsing tree data for consul

    This module will gets the mapped data and return a 
    hirachical Tree data for the D3 component in UI.

    Multiple Tree will be returned in case of multiple
    AP in that mapped data.
    Along with every node(AP,EP,EPG,Service) information 
    to be show in the side pane is also displayed is also
    sent in attributes.

    TODO: add checks in each tree node
"""

def consul_tree_dict(data):
    """Create tree specific dict
    
    input:   The merged CEps data
    output:  list of dict of trees
    """


    # Final list of ap(application profile)
    ap_list = []

    
    # distinct APs
    ap_set= set([node['AppProfile'] for node in data])

    # Iterating for each AP and creating a tree view for 
    # each AP, with all node's info to be shown in the tree
    # and its Side Pane(when clicked on the node).
    for ap in ap_set:

        # Extract all AP EPs
        ap_eps = [ep for ep in data if ep['AppProfile'] == ap]

        # Top level node in Tree
        # TODO: lable not sent because not needed in Consul: Try send ''
        ap_dict = {
            'name': 'AppProf',
            'type': '#581552',
            'sub_label': ap,
            'attributes': {},
            'children': [],
            'checks': {}
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
                'label': '',
                'sub_label': epg,
                'fraction': epg_eps[0]['fraction'],
                'attributes': {
                    'VRF': epg_eps[0]['VRF'],
                    'BD': epg_eps[0]['BD'],
                    'Contracts': epg_eps[0]['Contracts'],
                    'Nodes': [],
                    'Services_List': []
                },
                'children': [],
                'checks': {}
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
                        'name': 'EP',
                        'type': '#2DBBAD',
                        'label': ep_node['node_name'],
                        'sub_label': ep_node['VM-Name'],
                        'attributes': {
                            'Node' : ep_node['node_name'],
                            'Node Checks' : ep_node['node_check'],
                            'Reporting Node IP': ep_node['node_ips'][0],
                            'Mac': ep_node['CEP-Mac'],
                            'Services_List' : [],
                            'IP': ep_node['IP'],
                            'Interfaces': list(set([x['Interfaces'][0] for x in ep_nodes])), # TODO: understand y is this [0]
                            'VMM-Domain': ep_node['VMM-Domain']
                        },
                        'children': [],
                        'checks': ep_node['node_check']
                    }

                    # Iterating for each Service in EP
                    for service in ep_node['node_services']:

                        if len(service['service_id']) > 11:
                            service_label = service['service_id'][:11] + '..'
                        else:
                            service_label = service['service_id']

                        if service['service_ip']:
                            service_address = str(service['service_ip']) + ':' + str(service['service_port'])
                        else:
                            service_address = str(ep_node['node_ips'][0]) + ':' + str(service['service_port']) # for now 0th is taken, will change

                        # 4rd layer nodes in Tree (Service)
                        service_dict = {
                            'name': 'Service',
                            'type': '#C5D054',
                            'label': service_label,
                            'attributes': {
                                'Service' : service['service_name'],
                                'Service Instance' : service['service_id'],
                                'Address' : service_address,
                                'Service Kind' : service['service_kind'],
                                'Service Tags' : service['service_tags'],
                                'Service Checks' : service['service_checks']
                            },
                            'checks': service['service_checks']
                        }

                        # Add Service to EP
                        ep_dict['children'].append(service_dict)

                        # Add Service checks to EP checks
                        ep_dict['checks'] = add_checks(ep_dict['checks'], service_dict['checks'])


                        # Now adding the service info in EP and EPG attributes
                        # for the Side Pane info, 
                        # And adding services lable to EPG

                        # Service for side pane
                        service_side_pane = {
                            'Service' : service['service_id'],
                            'Address' : service_address,
                            'Service Checks' : service['service_checks']
                        }

                        # Adding services to EP attributes
                        if service_side_pane not in ep_dict['attributes']['Services_List']:
                            ep_dict['attributes']['Services_List'].append(service_side_pane)

                        # Adding services to EPG attributes
                        if service_side_pane not in epg_dict['attributes']['Services_List']:
                            epg_dict['attributes']['Services_List'].append(service_side_pane)

                        # Add lable to EPG if not there, a EPG can have more then one services in 
                        # the EPs, But as it is difficult to show all of those in the tree view 
                        # UI only 1 is shown with ellipsis
                        if not epg_dict['label']:
                            epg_dict['label'] = service['service_id'] + ', ...'


                    # Add EP to EPG
                    epg_dict['children'].append(ep_dict)

                    # Add EP checks to EPG checks
                    epg_dict['checks'] = add_checks(epg_dict['checks'], ep_dict['checks'])


                    # Now adding the Node info in the EPG Side Pane 
                    # if it does not exist

                    # Node for side pane
                    ep_side_pane = {
                        'Node': ep_node['node_name'],
                        'Node Checks': ep_node['node_check'],
                        'Reporting Node IP': ep_node['node_ips'][0]
                    }

                    # Adding Node to EPG attributes
                    if ep_side_pane not in epg_dict['attributes']['Nodes']:
                        epg_dict['attributes']['Nodes'].append(ep_side_pane)


            # 3rd layer nodes in Tree (EP)
            #  Iterating for each Non service end point in EPG
            if epg_eps[0]['Non_IPs']: # TODO: understand Y is this [0], Also the key
                non_ep_dict={}
                non_ep_dict['name'] = 'EP'
                non_ep_dict['type'] = 'grey'
                non_ep_dict['label'] = '' # No lable is shown in the ui for a non-service ep
                non_ep_dict['sub_label'] = '' # No sub_lable is shown in the ui for a non-service ep
                non_ep_dict['attributes'] = epg_eps[0]['Non_IPs']
                non_ep_dict['fractions'] = epg_eps[0]['fraction']
                epg_dict['children'].append(non_ep_dict)

            # Add EPG to AP
            ap_dict['children'].append(epg_dict)

            # Add EPG checks to AP checks
            ap_dict['checks'] = add_checks(ap_dict['checks'], epg_dict['checks'])

        # Add AP to responce list
        ap_list.append(ap_dict)
    return ap_list


def add_checks(base_checks, new_checks):
    """Adding up checks for every node"""
    
    final_check = {}

    for status, check_value in base_checks.iteritems():
        if status in final_check:
            final_check[status] += check_value
        else:
            final_check[status] = check_value

    for status, check_value in new_checks.iteritems():
        if status in final_check:
            final_check[status] += check_value
        else:
            final_check[status] = check_value

    return final_check

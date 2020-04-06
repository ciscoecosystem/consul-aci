import requests
import datetime
import aci_utils
import json
from custom_logger import CustomLogger

logger = CustomLogger.get_logger("/home/app/log/app.log")


def merge_aci_consul(tenant, data_center, aci_util_obj):
    """
    Initial algo implementaion.

    Merge ACI data with Consul Data fetched from API directly
    """

    start_time = datetime.datetime.now()
    logger.info('Merging objects for Tenant:'+str(tenant)+', data_centre'+str(data_center)) # change appdid

    try:
        merge_list = []  # TODO: these should go above 946
        merged_eps = []
        total_epg_count = {}
        merged_epg_count = {}
        non_merged_ep_dict = {}

        aci_data = aci_util_obj.main(tenant)
        consul_data = get_consul_data()

        # mapping should come from alchemy
        # correlatoin should be part of mapping
        aci_consul_mappings = correlate_aci_consul(tenant, data_center, consul_data)

        # Changing the data from the correlate_aci_consul(tenant, data_centre)
        aci_consul_mappings = get_mapping_dict_target_cluster(aci_consul_mappings)

        logger.debug("ACI Data: {}".format(str(aci_data)))
        logger.debug("Mapping Data: {}".format(str(aci_consul_mappings)))

        for aci in aci_data:
            if aci['EPG'] not in total_epg_count.keys():
                total_epg_count[aci['EPG']] = 1
            else:
                total_epg_count[aci['EPG']] += 1

            if aci_consul_mappings:
                mappings = [node for node in aci_consul_mappings if node.get('disabled') == False]
                for each in mappings:
                    mapping_key = 'ipaddress'
                    aci_key = 'IP'

                    if aci.get(aci_key) and each.get(mapping_key) and aci.get(aci_key).upper() == each.get(mapping_key).upper() and each['domainName'] == str(aci['dn']):
                        # Service to CEp mapping
                        for node in consul_data:
                            new_node = {
                                'nodeId': node.get('nodeId'),
                                'nodeName': node.get('nodeName'),
                                'ipAddressList': node.get('ipAddressList'),
                                'nodeCheck': node.get('nodeCheck'),
                                'services': []
                            }
                            # All the services which matches CEp and its ip is different from its nodes ip
                            for service in node.get('services', []):
                                if aci.get(aci_key).upper() == service.get('serviceIP') and aci.get(aci_key).upper() not in node.get('ipAddressList'):
                                    node['services'].remove(service)
                                    new_node['services'].append(service)
                                # Below statements is supposed to remove all the services which do not map to any ip in mappings.
                                # but this will remove all the non mapped services in first itteration node
                                elif service.get('serviceIP') != "" and service.get('serviceIP') not in [each.get(mapping_key) for each in mappings]:
                                    node['services'].remove(service)
                            if new_node['services']:
                                new_node.update(aci)
                                merge_list.append(new_node)
                                # what is this for?
                                if aci[aci_key] not in merged_eps:
                                    merged_eps.append(aci[aci_key])
                                    if aci['EPG'] not in merged_epg_count:
                                        merged_epg_count[aci['EPG']] = [aci[aci_key]]
                                    else:
                                        merged_epg_count[aci['EPG']].append(aci[aci_key])

                        logger.info('Service to CEp mapped:' + str(merge_list))

                        # node to EP mapping
                        mapped_consul_nodes = [node for node in consul_data if aci.get(aci_key).upper() in node.get('ipAddressList', [])]
                        if mapped_consul_nodes:
                            for each in mapped_consul_nodes:
                                each.update(aci)
                                merge_list.append(each)
                                if aci[aci_key] not in merged_eps:
                                    merged_eps.append(aci[aci_key])
                                    if aci['EPG'] not in merged_epg_count:
                                        merged_epg_count[aci['EPG']] = [aci[aci_key]]
                                    else:
                                        merged_epg_count[aci['EPG']].append(aci[aci_key])

        for aci in aci_data:
            if aci['IP'] in merged_eps:
                continue
            else:
                if aci['EPG'] not in non_merged_ep_dict:
                    non_merged_ep_dict[aci['EPG']] = {aci['CEP-Mac']: str(aci['IP'])}
                
                if aci['CEP-Mac'] in non_merged_ep_dict[aci['EPG']].keys():
                    multipleips = non_merged_ep_dict[aci['EPG']][aci['CEP-Mac']]+", " + str(aci['IP'])
                    non_merged_ep_dict[aci['EPG']].update({aci['CEP-Mac']: multipleips})
                else:
                    non_merged_ep_dict[aci['EPG']].update({aci['CEP-Mac']: str(aci['IP'])})

        final_non_merged = {}
        if non_merged_ep_dict:
            for key,value in non_merged_ep_dict.items():
                if not value:
                    continue
                final_non_merged[key] = value

        fractions = {}
        if total_epg_count:
            for epg in total_epg_count.keys():
                #fractions[epg] = str(len(merged_epg_count.get(epg, [])))+"/"+str(total_epg_count.get(epg, []))
                un_map_eps = int(total_epg_count.get(epg, [])) - len(merged_epg_count.get(epg, []))
                fractions[epg] = int(un_map_eps)
                logger.info('Total Unmapped Eps (Inactive):'+str(un_map_eps)+" - "+str(epg))

        updated_merged_list = []
        if fractions:
            for key, value in fractions.iteritems():
                for each in merge_list:
                    if key == each['EPG']:
                        each['fraction'] = value
                        each['Non_IPs'] = final_non_merged.get(key, {})
                        updated_merged_list.append(each)

        final_list = []
        for each in updated_merged_list:
            if 'fraction' not in each.keys():
                each['fraction'] = '0'
                each['Non_IPs'] = {}
            final_list.append(each)
        logger.info('Merge complete. Total objects correlated: ' + str(len(final_list)))

        return final_list #updated_merged_list#,total_epg_count # TBD for returning values
    except Exception as e:
        logger.exception("Error while merge_aci_data : "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the Merge ACI and AppDynamics objects."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for merge_aci_appd: " + str(end_time - start_time))


def get_consul_data():
    """
    This will fetch the data from the API and return for now
    Decide the form of data neede in the merge logic and return as per that.
    """
    try:
        consul_data = []

        list_of_nodes = consul_node_list() # here data should come from db

        for node in list_of_nodes:
            consul_data.append({
                'nodeId': node.get('nodeID'),
                'nodeName': node.get('nodeName'),
                'ipAddressList': node.get('nodesIPs'),
                'nodeCheck': consul_node_check(node.get('nodeName')),
                'services': consul_nodes_services(node.get('nodeName'))
            })
        return consul_data
    except Exception as e:
        logger.exception("Error while merge_aci_data : "+str(e))
        return []



def get_mapping_dict_target_cluster(mapped_objects):
    """
    return mapping dict from recommended objects
    """
    target = []
    for map_object in mapped_objects:
        for entry in map_object.get('domains'):
            if entry.get('recommended') == True:
                logger.debug("Mapping found with ipaddress for "+str(map_object))
                target.append({'domainName': entry.get('domainName'), 'ipaddress': map_object.get('ipaddress'), 'disabled': False})
    return target


def correlate_aci_consul(tenant, data_center, consul_data):
    """
    Initial algo imp

    This shoild go in the recommandation and not be called in mapping instead
    """
    logger.info('Finding Correlations for ACI and AppD')

    aci_util_obj = aci_utils.ACI_Utils()
    end_points = aci_util_obj.apic_fetchEPData(tenant)
    if not end_points:
        logger.error('Error: Empty end_points ' + str(end_points))
        return []

    try:
        # returns dn, ip and tenant info for each ep
        parsed_eps = aci_util_obj.parseEPs(end_points,tenant)
        if not parsed_eps:
            logger.error('Error: Empty parsed_eps ' + str(parsed_eps))
            return []
        else:
            # Example of each EP dn
            # "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-test/cep-00:50:56:92:BA:4A/ip-[20.20.20.10]"
            # Example of extracted Epg dn
            # "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-test"
            for each in parsed_eps:
                each['dn'] = '/'.join(each['dn'].split('/',4)[0:4])
    except Exception as e:
        logger.exception('Exception in parsed eps list, Error: ' + str(e))
        return []

    if not consul_data:
        logger.exception('Error: consul_data is Empty!')
        return []

    ip_list = []
    for node in consul_data:
        ip_list += node.get('ipAddressList', [])
        # For fetching ips of services.
        for service in node.get('services', []):
            # check ip is not empty string
            if service.get('serviceIP', ''):
                ip_list.append(service.get('serviceIP'))
    ip_list = list(set(ip_list))

    logger.debug('Final Consul IP List ' + str(ip_list))

    # Extract common based on Ips
    try:
        common_eps = getCommonEPs(ip_list, parsed_eps)
        logger.debug('Common EPs:'+str(common_eps))
        if common_eps:
            extract_ap_epgs = extract_ap_and_epgs(common_eps)
        else:
            return []
    except Exception as e:
        logger.exception('Exception in common eps list, Error:'+str(e))
        return []

    try:
        rec_list = determine_recommendation(extract_ap_epgs,common_eps)
    except Exception as e:
        logger.exception('Exception while determining recommended list, Error:'+str(e))
        return []

    if rec_list:
        logger.info('Recommendation list for app:'+str(data_center)+'  rec_list= '+str(rec_list))
        fin_list = set(map(tuple,rec_list))
        final_list = map(list,fin_list)
        logger.info('Final List final_list '+str(rec_list))
    else:
        logger.info('Error: Empty rec_list ' + str(rec_list))
        return []
    
    try:
        generated_list = generatelist(final_list)
    except Exception as e:
        logger.exception('Exception in generate list, Error:'+str(e))
        return []
    
    if generated_list:
        logger.info('Generated List = '+str(generated_list))
        return generated_list
    else:
        logger.info('Error: Empty generated_list ' + str(generated_list))
        return []


def getCommonEPs(consul_ip_list, aci_parsed_eps):
    """Map EP(ACI) to Nodes(Consul)
    
    Matches the IP of ACI fvIp with Consul Node IPs and returns a list of matched ACI fvIps dicts"""
    
    common_list = []
    for each in aci_parsed_eps:
        if each['IP'] in consul_ip_list:
            common_list.append(each)
    return common_list


def extract_ap_and_epgs(eps):
    count_dict = {}
    for ep in eps:
        ap, epg = extract(ep['dn'])
        if ap not in count_dict.keys():
            count_dict[ap] = {epg:1}
        elif epg not in count_dict[ap].keys():
            count_dict[ap][epg] = 1
        else:
            count_dict[ap][epg] += 1
    return count_dict


def extract(dn):
    """
    Extract ap and epg from given dn
    """
    ap = dn.split('/')[2].split('-',1)[1]
    epg = dn.split('/')[3].split('-',1)[1]
    return ap, epg


# returns a list of list
def determine_recommendation(extract_ap_epgs, common_eps):
    recommendation_list = []
    for each in common_eps:
        accounted = 0
        for duplicate in common_eps:

            # For different elements, if IP/Mac is same and 'dn' is different
            if each['IP'] == duplicate['IP'] and each['dn'] != duplicate['dn'] and common_eps.index(each) != common_eps.index(duplicate):
                ap_main,epg_main = extract(each['dn'])
                ap_dup,epg_dup = extract(duplicate['dn'])
                
                # Compare count of 'EPG' for an 'AP'
                main_count = extract_ap_epgs[ap_main][epg_main]
                dup_count = extract_ap_epgs[ap_dup][epg_dup]
                
                if main_count > dup_count:
                    recommendation_list.append([each['IP'],each['dn'],'Yes','IP'])
                    break
                elif main_count == dup_count:
                    ap_main_c = len(extract_ap_epgs[ap_main])
                    ap_dup_c = len(extract_ap_epgs[ap_dup])
                    # Add one with more number of Epgs
                    if ap_main_c > ap_dup_c:
                        recommendation_list.append([each['IP'],each['dn'],'Yes','IP'])
                        break
                    elif ap_main_c < ap_dup_c:
                        recommendation_list.append([each['IP'],each['dn'],'No','IP'])
                        break
                    else:
                        recommendation_list.append([each['IP'],each['dn'],'None','IP'])
                else:
                    recommendation_list.append([each['IP'],each['dn'],'No','IP'])
            elif each['IP'] != duplicate['IP'] and each['dn'] != duplicate['dn'] and common_eps.index(each) != common_eps.index(duplicate) and any(each['IP'] in d for d in recommendation_list) != True:
                recommendation_list.append([each['IP'],each['dn'],'None','IP'])
            elif accounted == 0:
                recommendation_list.append([each['IP'],each['dn'],'None','IP'])
                accounted = 1

    for a in recommendation_list:
        for b in recommendation_list:
            # If same recommendation already exist with b[2] == 'None' than remove it.
            if a[0] == b[0] and a[1] == b[1] and (a[2] == 'Yes' or a[2] == 'No') and b[2] == 'None':
                recommendation_list.remove(b)
    return recommendation_list


def generatelist(ipList):
    """
    Generate list based on the IP or Mac.
    """
    src_clus_list = []
    # logger.info("ip_list" + type + ipList)
    ips = list(set([x[0] for x in ipList]))
    ip_dict = dict((el,[]) for el in ips)
    for each in ipList:
        if each[2] == 'No':
            each[2] = False
        if each[2] == 'Yes' or each[2] == 'None':
            each[2] = True

        ip_dict[each[0]].append({'domainName':each[1],'recommended':each[2]})

    for key,value in ip_dict.iteritems():
        src_clus_list.append({'ipaddress':key,'domains':value})

    return src_clus_list


def consul_node_list():
    """
    This should fetch the data from db using the dc field, not directly
    
    For now fetching nodes and returning [{name: '', iplist: []},..]
    """
    
    node_list = []
    catalog_nodes = requests.get('{}/v1/catalog/nodes'.format('http://10.23.239.14:8500'))
    nodes = json.loads(catalog_nodes.content)
    # logger.debug(str(nodes))
    for node in nodes:
        ip_list = []
        ip_list.append(node.get('Address', ''))
        if node.get('TaggedAddresses', {}):
            ip_list.append(node.get('TaggedAddresses', {}).get('wan_ipv4', ''))
            ip_list.append(node.get('TaggedAddresses', {}).get('wan', ''))
            ip_list.append(node.get('TaggedAddresses', {}).get('lan', ''))
            ip_list.append(node.get('TaggedAddresses', {}).get('lan_ipv4', ''))

        # for removing '' from ip_list
        ip_list = [ip for ip in ip_list if ip]

        node_list.append({
            'nodeID': node.get('ID', ''),
            'nodeName': node.get('Node', ''),
            'nodesIPs': list(set(ip_list)),
        })

    return node_list


def consul_nodes_services(node_name):
    """This will return all the services of a node"""

    # API works for node id also, ask and decide
    services_resp = requests.get('{}/v1/catalog/node-services/{}'.format('http://10.23.239.14:8500', node_name))
    services_resp = json.loads(services_resp.content)

    service_list = []
    for service in services_resp.get('Services'):
        s_check = consul_service_check(service.get('Service'))
        s_tags, s_kind = consul_service_tags_kind(service.get('Service'))
        service_list.append({
            'serviceInstance': service.get('ID', ''),
            'service': service.get('Service', ''),
            'serviceIP': service.get('Address', ''),
            'port': service.get('Port', ''),
            'serviceChecks': s_check,
            'serviceTags': s_tags,
            'serviceKind': s_kind
        })

    return service_list


def consul_service_check(service_name):
    """This will return the dict of services health(and numbers) check"""

    service_resp = requests.get('{}/v1/health/checks/{}'.format('http://10.23.239.14:8500', service_name))
    service_resp = json.loads(service_resp.content)

    check_dict = {}
    for check in service_resp:
        if check.get('Status'):
            if 'passing' == check.get('Status').lower():
                if check_dict.get('passing'):
                    check_dict['passing'] += 1
                else:
                    check_dict['passing'] = 1
            elif 'warning' == check.get('Status').lower():
                if check_dict.get('warning'):
                    check_dict['warning'] += 1
                else:
                    check_dict['warning'] = 1
            else:
                if check_dict.get('failing'):
                    check_dict['failing'] += 1
                else:
                    check_dict['failing'] = 1

    return check_dict


def consul_service_tags_kind(service_name):
    """Details of a service from service-details API"""

    service_resp = requests.get('{}/v1/catalog/service/{}'.format('http://10.23.239.14:8500', service_name))
    service_resp = json.loads(service_resp.content)

    tags_set = set()
    for val in service_resp[0].get('ServiceTags'):
        tags_set.add(val)

    service_kind = service_resp[0].get('ServiceKind')

    return list(tags_set), service_kind


def consul_node_check(node_name):

    node_resp = requests.get('{}/v1/health/node/{}'.format('http://10.23.239.14:8500', node_name))
    node_resp = json.loads(node_resp.content)

    check_dict = {}
    for check in node_resp:
        if not check.get('ServiceID') and check.get('Status'):
            if 'passing' == check.get('Status').lower():
                if check_dict.get('passing'):
                    check_dict['passing'] += 1
                else:
                    check_dict['passing'] = 1
            elif 'warning' == check.get('Status').lower():
                if check_dict.get('warning'):
                    check_dict['warning'] += 1
                else:
                    check_dict['warning'] = 1
            else:
                if check_dict.get('failing'):
                    check_dict['failing'] += 1
                else:
                    check_dict['failing'] = 1

    return check_dict


def consul_detailed_service_check(service_name, service_id):
    try:
        service_resp = requests.get('{}/v1/health/checks/{}'.format('http://10.23.239.14:8500', service_name))
        service_resp = json.loads(service_resp.content)

        service_checks_list = []
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

        return service_checks_list
    except Exception as e:
        logger.exception("error in fatching service checks : " + str(e))
        return [] 
import custom_logger
from decorator import time_it

logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")


@time_it
def merge_aci_consul(tenant, aci_data, consul_data, aci_consul_mappings):
    """
    Function for merging data of ACI and consul based on mappings

    Arguments:
        tenant              {string} -->    name of tenant
        aci_data            {list}   -->    list of dict of aci data
        consul_data         {list}   -->    list of dict of consul data
        aci_consul_mappings {list}   -->    list of dict of aci consul mappings

    Returns:
        {tuple{list, list}} --> final merged list of eps, non-merged eps info
    """

    logger.info('Merging objects')

    try:
        merge_list = []
        merged_eps = dict()
        total_epg_count = {}
        merged_epg_count = {}
        non_merged_ep_dict = {}

        logger.debug("ACI Data: {}".format(str(aci_data)))
        logger.debug("Mapping Data: {}".format(str(aci_consul_mappings)))

        mappings = [node for node in aci_consul_mappings if node.get('enabled')]

        new_mappings = aci_consul_mappings_formatter(mappings)

        mapping_ips = dict()
        for each in mappings:
            mapping_ips[each.get('ip')] = True

        aci_key = 'IP'

        consul_data_formatter(consul_data, mapping_ips)
        mapped_consul_nodes_list = mapped_consul_nodes_formatter(consul_data)
        mapped_consul_services_list = mapped_consul_services_formatter(consul_data)

        for aci in aci_data:
            if aci['EPG'] not in total_epg_count:
                total_epg_count[aci['EPG']] = 1
            else:
                total_epg_count[aci['EPG']] += 1

            mapped_detail = new_mappings.get(
                (
                    aci.get('dn'),
                    aci.get(aci_key)
                ),
                {}
            )
            if mapped_detail:
                logger.info('mapping: {}, aci: {}'.format(str(mapped_detail), str(aci)))
                # Service to CEp mapping
                mapped_node_service_dict = dict()
                for service, node in mapped_consul_services_list.get(aci.get(aci_key), []):
                    if aci.get(aci_key) != node.get('node_ip'):
                        node_id = node.get('node_id')
                        if node_id not in mapped_node_service_dict:
                            new_node = {
                                'node_id': node.get('node_id'),
                                'node_name': node.get('node_name'),
                                'node_ip': node.get('node_ip'),
                                'node_check': node.get('node_check'),
                                'node_services': [service]
                            }
                            new_node.update(aci)
                            mapped_node_service_dict[node_id] = new_node
                        else:
                            mapped_node_service_dict.get(node_id)['node_services'].append(service)
                for new_node in mapped_node_service_dict.values():
                    merge_list.append(new_node)
                    if (aci[aci_key], aci['CEP-Mac'], aci['dn']) not in merged_eps:
                        merged_eps[(aci[aci_key], aci['CEP-Mac'], aci['dn'])] = True
                        if aci['EPG'] not in merged_epg_count:
                            merged_epg_count[aci['EPG']] = [aci[aci_key]]
                        else:
                            merged_epg_count[aci['EPG']].append(aci[aci_key])

                # node to EP mapping
                mapped_consul_nodes = custom_copy(
                    mapped_consul_nodes_list.get(aci.get(aci_key), False))
                if mapped_consul_nodes:
                    for mapped_node in mapped_consul_nodes:
                        mapped_node.update(aci)
                        mapped_node['node_services'] = mapped_node['node_services_copy']
                        merge_list.append(mapped_node)
                        if (aci[aci_key], aci['CEP-Mac'], aci['dn']) not in merged_eps:
                            merged_eps[(aci[aci_key], aci['CEP-Mac'], aci['dn'])] = True
                            if aci['EPG'] not in merged_epg_count:
                                merged_epg_count[aci['EPG']] = [aci[aci_key]]
                            else:
                                merged_epg_count[aci['EPG']].append(aci[aci_key])
        for aci in aci_data:
            aci_dn = get_formatted_dn(aci['dn'])
            if (aci['IP'], aci['CEP-Mac'], aci['dn']) in merged_eps:
                continue
            else:
                if aci_dn not in non_merged_ep_dict:
                    non_merged_ep_dict[aci_dn] = {aci['CEP-Mac']: str(aci['IP'])}

                if aci['CEP-Mac'] in non_merged_ep_dict[aci_dn] \
                        and aci.get('IP') \
                        and aci['IP'] != non_merged_ep_dict[aci_dn][aci['CEP-Mac']]:
                    multipleips = non_merged_ep_dict[aci_dn][aci['CEP-Mac']] + ", " + str(aci['IP'])
                    non_merged_ep_dict[aci_dn].update({aci['CEP-Mac']: multipleips})
                else:
                    non_merged_ep_dict[aci_dn].update({aci['CEP-Mac']: str(aci['IP'])})

        final_non_merged = {}
        if non_merged_ep_dict:
            for key, value in non_merged_ep_dict.items():
                if not value:
                    continue
                final_non_merged[key] = value

        fractions = {}
        if total_epg_count:
            for epg in total_epg_count:
                un_map_eps = int(total_epg_count.get(epg, [])) - len(merged_epg_count.get(epg, []))
                fractions[epg] = int(un_map_eps)
                logger.info('Total Unmapped Eps (Inactive): {} - {}'.format(str(un_map_eps), str(epg)))

        updated_merged_list = []
        if fractions:
            for each in merge_list:
                if each['EPG'] in fractions:
                    each['fraction'] = fractions[each['EPG']]
                    each['Non_IPs'] = final_non_merged.get(get_formatted_dn(each['dn']), {})
                    updated_merged_list.append(each)

        final_list = []
        for each in updated_merged_list:
            if 'fraction' not in each:
                each['fraction'] = '0'
                each['Non_IPs'] = {}
            final_list.append(each)
        logger.info('Merge complete. Total objects correlated: ' + str(len(final_list)))

        for each in final_list:
            if 'node_services_copy' in each:
                del each['node_services_copy']

        return final_list, final_non_merged  # updated_merged_list#,total_epg_count # TBD for returning values
    except Exception as e:
        logger.exception("Error in merge_aci_data : {}".format(str(e)))
        return []


def custom_copy(obj):
    """
    Function for deepcopy object having datatypes list, dict, tuple, string, int, float
    """
    if isinstance(obj, (list,)):
        new_ls = []
        for each in obj:
            x = custom_copy(each)
            new_ls.append(x)
        return new_ls
    elif isinstance(obj, (tuple,)):
        new_ls = []
        for each in obj:
            x = custom_copy(each)
            new_ls.append(x)
        return tuple(new_ls)
    elif isinstance(obj, (dict,)):
        new_dc = dict()
        for each in obj:
            new_dc[each] = custom_copy(obj[each])
        return new_dc
    else:
        return obj


def aci_consul_mappings_formatter(data):
    """
    Function to create dict from list of aci_consul_mappings based on dn and ip
    """
    dc = dict()
    for each in data:
        dn = each.get('dn')
        ip = each.get('ip')
        if ip:
            new_key = (dn, ip)
            dc[new_key] = each
    return dc


def mapped_consul_nodes_formatter(consul_data):
    """
    Function to create dict from consul_data based on node_ip
    """
    dc = dict()
    for node in consul_data:
        ip = node.get('node_ip')
        obj = dc.get(ip, [])
        if obj:
            obj.append(node)
        else:
            dc[ip] = [node]
    return dc


def mapped_consul_services_formatter(consul_data):
    dc = dict()
    for node in consul_data:
        for service in node.get('node_services'):
            ip = service.get('service_ip')
            if ip:
                if ip in dc:
                    dc[ip].append([service, node])
                else:
                    dc[ip] = [[service, node]]
    return dc


def consul_data_formatter(consul_data, mapping_ips):
    """
    Function to formate consul data based on mapped ips
    """
    for node in consul_data:
        services = []
        rem = []
        service_list = node.get('node_services', [])
        for i, service in enumerate(service_list):
            if service.get('service_ip') != "" and service.get('service_ip') not in mapping_ips:
                rem.append(i)
        for i in range(len(service_list)):
            if i in rem:
                rem = rem[1:]
            else:
                services.append(service_list[i])
        node['node_services'] = services
        node['node_services_copy'] = [
            service for service in node['node_services'] if (
                service.get('service_ip') == ""
                or service.get('service_ip') == node.get('node_ip')
            )
        ]


def get_formatted_dn(dn):
    """ Function to get dn without cep-mac """
    tmp = "/".join(dn.split("/", 4)[:4])
    return tmp

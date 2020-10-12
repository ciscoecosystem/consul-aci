""""""

import custom_logger
logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")


def get_common_eps(source_ip_list, aci_parsed_eps):
    """Map EP(ACI) to Nodes(Consul)

    Matches the IP of ACI fvIp with Source Node IPs and returns a list of matched ACI fvIps dicts"""

    common_list = []
    for each in aci_parsed_eps:
        if each['IP'] in source_ip_list:
            common_list.append(each)
    return common_list


def extract(dn):
    """
    Extract ap and epg from given dn
    """
    ap = dn.split('/')[2].split('-', 1)[1]
    epg = dn.split('/')[3].split('-', 1)[1]
    return ap, epg


def extract_ap_and_epgs(eps):
    count_dict = {}
    for ep in eps:
        ap, epg = extract(ep['dn'])
        if ap not in count_dict.keys():
            count_dict[ap] = {epg: 1}
        elif epg not in count_dict[ap].keys():
            count_dict[ap][epg] = 1
        else:
            count_dict[ap][epg] += 1

    return count_dict


def sort_eps(each):
    if 'IP' in each:
        return each['IP']
    else:
        return each['mac']


def extract_vrf(apic_data):
    vrf_dict = {}
    for each in apic_data:
        vrf = each['VRF']
        dn = each['dn']
        key = 'IP'
        if 'mac' in each:
            key = 'mac'
        if vrf in vrf_dict:
            vrf_dict[vrf].add(dn + '|' + each[key])
        else:
            vrf_dict[vrf] = {dn + '|' + each[key]}

    return vrf_dict


def apic_data_formatter(apic_data):
    dc = dict()
    for each in apic_data:
        if 'IP' in each:
            key_ip = '{}#{}'.format(
                each.get('IP', ""),
                each.get('dn', "")
            )
            dc[key_ip] = each
        if 'mac' in each:
            key_mac = '{}#{}'.format(
                each.get('mac', ""),
                each.get('dn', "")
            )
            dc[key_mac] = each
    return dc


def search_ep_in_apic(apic_data, search_param):
    if 'mac' in search_param:
        key = '{}#{}'.format(
            search_param['mac'],
            search_param['dn']
        )
    if 'IP' in search_param:
        key = '{}#{}'.format(
            search_param['IP'],
            search_param['dn']
        )
    return apic_data.get(key, None)


def determine_recommendation(extract_ap_epgs, common_eps, apic_data):

    common_eps = sorted(common_eps, key=sort_eps)
    logger.debug('sorted eps {} '.format(common_eps))
    each_key = 'IP'
    recommendation_list = []

    extracted_vrfs = extract_vrf(apic_data)
    logger.debug('extracted vrfs {} '.format(extracted_vrfs))
    for i in range(len(common_eps)):
        recommendation_list.append([common_eps[i][each_key], common_eps[i]['dn'], 'Yes', each_key])
    return recommendation_list


def generatelist(ip_list):
    """
    Generate list based on the IP or Mac.
    """
    src_clus_list = []
    ips = []
    macs = []
    for each in ip_list:
        if each[3] == 'IP':
            ips.append(each[0])
        else:
            macs.append(each[0])
    ips = list(set(ips))
    macs = list(set(macs))
    ip_dict = dict((el, []) for el in ips)
    mac_dict = dict((el, []) for el in macs)
    for each in ip_list:
        if each[2] == 'No':
            each[2] = True
        if each[2] == 'Yes' or each[2] == 'None':
            each[2] = True
        if each[3] == 'IP':
            ip_dict[each[0]].append({'domainName': each[1], 'recommended': each[2]})
        else:
            mac_dict[each[0]].append({'domainName': each[1], 'recommended': each[2]})
    for key, value in ip_dict.iteritems():
        entry = {'ipaddress': key, 'domains': value}
        src_clus_list.append(entry)
    for key, value in mac_dict.iteritems():
        entry = {'macaddress': key, 'domains': value}
        src_clus_list.append(entry)
    return src_clus_list


def recommended_eps(source_ip_list, parsed_eps, apic_data):
    """This finds all the recommended EPs in APIC wrt the source data

    TODO: explain
    """
    logger.info('Finding Recommended EPs for ACI and Consul')

    try:
        if not parsed_eps:
            logger.error('Error: Empty parsed_eps ' + str(parsed_eps))
            return []
        else:
            # Example of each EP dn
            # "uni/tn-Tenant1/ap-AppProfile1/epg-Epg-test/cep-AA:BB:CC:DD:EE:FF"
            # Example of extracted Epg dn
            # "uni/tn-Tenant1/ap-AppProfile1/epg-Epg-test"
            for each in parsed_eps:
                each['dn'] = '/'.join(each['dn'].split('/', 5)[0:5])
    except Exception as e:
        logger.exception('Exception in parsed eps list, Error: ' + str(e))
        return []

    logger.debug('Final IP List ' + str(source_ip_list))

    # Extract common based on Ips
    try:
        common_eps = get_common_eps(source_ip_list, parsed_eps)
        logger.debug('Common EPs: {}'.format(str(common_eps)))
        if common_eps:
            extract_ap_epgs = extract_ap_and_epgs(parsed_eps)
        else:
            return []
    except Exception as e:
        logger.exception('Exception in common eps list, Error: {}'.format(str(e)))
        return []

    try:
        rec_list = determine_recommendation(extract_ap_epgs, common_eps, apic_data)
    except Exception as e:
        logger.exception('Exception while determining recommended list, Error: {}'.format(str(e)))
        return []

    if rec_list:
        logger.info('Recommendation list: rec_list {}'.format(str(rec_list)))
        fin_list = set(map(tuple, rec_list))
        final_list = map(list, fin_list)
        logger.info('Final List final_list {}'.format(str(final_list)))
    else:
        logger.info('Error: Empty rec_list ' + str(rec_list))
        return []

    try:
        generated_list = generatelist(final_list)
    except Exception as e:
        logger.exception('Exception in generate list, Error: {}'.format(str(e)))
        return []

    if generated_list:
        logger.info('Generated List {}'.format(str(generated_list)))
        return generated_list
    else:
        logger.info('Error: Empty generated_list ' + str(generated_list))
        return []

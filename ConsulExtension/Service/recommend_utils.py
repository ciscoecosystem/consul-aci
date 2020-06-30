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


def search_ep_in_apic(apic_data, search_param):
    for each in apic_data:
        flag = False
        for key, val in search_param.items():
            # logger.debug(' key , val :'+key+' , '+val)
            if key in each and each[key] == val:
                # logger.debug(' Inside search and element found ')
                flag = True
            else:
                break
        if flag:
            return each
    return None


def determine_recommendation(extract_ap_epgs, common_eps, apic_data):

    common_eps = sorted(common_eps, key=sort_eps)
    logger.debug('sorted eps {} '.format(common_eps))
    recommended_ep = common_eps[0]
    del common_eps[0]
    peers = []

    rec_key = 'IP'
    each_key = 'IP'
    recommendation_list = []

    extracted_vrfs = extract_vrf(apic_data)
    logger.debug('extracted vrfs {} '.format(extracted_vrfs))

    for i in range(len(common_eps)):
        each = common_eps[i]
        ap_rec, epg_rec = extract(recommended_ep['dn'])
        ap_each, epg_each = extract(each['dn'])

        ap_rec_count = len(extract_ap_epgs[ap_rec])
        ap_each_count = len(extract_ap_epgs[ap_each])

        epg_rec_count = extract_ap_epgs[ap_rec][epg_rec]
        epg_each_count = extract_ap_epgs[ap_each][epg_each]

        if 'mac' in recommended_ep:
            rec_key = 'mac'
        if 'mac' in each:
            each_key = 'mac'

        search_params_rec = {rec_key: recommended_ep[rec_key], 'dn': recommended_ep['dn']}
        apic_rec = search_ep_in_apic(apic_data, search_params_rec)['VRF']

        search_params_each = {rec_key: each[rec_key], 'dn': each['dn']}
        apic_each = search_ep_in_apic(apic_data, search_params_each)['VRF']

        # When we encounter the ep whose IP is different from the current recommended IP.
        # We add all peers and recommended to recommended list as recommended
        if recommended_ep[rec_key] != each[each_key]:
            recommendation_list.append([recommended_ep[rec_key], recommended_ep['dn'], 'Yes', rec_key])
            for temp in peers:
                recommendation_list.append([temp[rec_key], temp['dn'], 'Yes', rec_key])
            recommended_ep = each
            peers = []
            continue 

        if (recommended_ep['cep_ip'] and each['cep_ip']) or (not recommended_ep['cep_ip'] and not each['cep_ip']):
            if apic_rec and apic_each and len(extracted_vrfs[apic_rec]) > len(extracted_vrfs[apic_each]):
                recommendation_list.append([each[each_key], each['dn'], 'No', each_key])
            elif apic_rec and apic_each and len(extracted_vrfs[apic_rec]) < len(extracted_vrfs[apic_each]):
                recommendation_list.append([recommended_ep[rec_key], recommended_ep['dn'], 'No', rec_key])
                recommended_ep = each
            else:
                if ap_rec_count > ap_each_count:
                    recommendation_list.append([each[each_key], each['dn'], 'No', each_key])
                elif ap_rec_count < ap_each_count:
                    recommendation_list.append([recommended_ep[rec_key], recommended_ep['dn'], 'No', rec_key])
                    recommended_ep = each
                else:
                    if epg_rec_count > epg_each_count:
                        recommendation_list.append([each[each_key], each['dn'], 'No', each_key])
                    elif epg_rec_count < epg_each_count:
                        recommendation_list.append([recommended_ep[rec_key], recommended_ep['dn'], 'No', rec_key])
                        recommended_ep = each
                    else:
                        peers.append(each)
        elif recommended_ep.get('cep_ip', '') is False and each.get('cep_ip', ''):
            recommendation_list.append([each[each_key], each['dn'], 'No', each_key])
        else:
            recommendation_list.append([recommended_ep[rec_key], recommended_ep['dn'], 'No', rec_key])
            recommended_ep = each

    recommendation_list.append([recommended_ep[rec_key], recommended_ep['dn'], 'Yes', rec_key])

    for temp in peers:
        recommendation_list.append([temp[rec_key], temp['dn'], 'Yes', rec_key])

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
            each[2] = False
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
                each['dn'] = '/'.join(each['dn'].split('/', 4)[0:4])
    except Exception as e:
        logger.exception('Exception in parsed eps list, Error: ' + str(e))
        return []

    logger.debug('Final IP List ' + str(source_ip_list))

    # Extract common based on Ips
    try:
        common_eps = get_common_eps(source_ip_list, parsed_eps)
        logger.debug('Common EPs: {}'.format(str(common_eps)))
        if common_eps:
            extract_ap_epgs = extract_ap_and_epgs(common_eps)
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

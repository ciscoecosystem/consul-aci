""""""

import copy
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


# returns a list of list
def determine_recommendation(extract_ap_epgs, common_eps):
    recommendation_list = []
    for each in common_eps:
        accounted = 0
        for duplicate in common_eps:

            key = 'IP'
            dup_key = 'IP'
            if 'mac' in each:
                key = 'mac'
            if 'mac' in duplicate:
                dup_key = 'mac'

            # For different elements, if IP/Mac is same and 'dn' is different
            if each[key] == duplicate[dup_key] and each['dn'] != duplicate['dn'] and common_eps.index(each) != common_eps.index(duplicate):

                # This is the condition when there are 2 CEp's
                # EP1: CEp's child fvIp.addr = 1.1.1.1
                # EP2: CEp.ip = 1.1.1.1
                # Then the first one will be selected giving fvIp priority
                if each.get('cep_ip', ''):
                    recommendation_list.append([each[key], each['dn'], 'No', key])
                    break
                if duplicate.get('cep_ip', ''):
                    recommendation_list.append([each[key], each['dn'], 'Yes', key])
                    break

                ap_main, epg_main = extract(each['dn'])
                ap_dup, epg_dup = extract(duplicate['dn'])

                # Compare count of 'EPG' for an 'AP'
                main_count = extract_ap_epgs[ap_main][epg_main]
                dup_count = extract_ap_epgs[ap_dup][epg_dup]
                # recommendation logic
                #     first compare the number of EPG in an application profile in which the EP belong
                #     recommend the EP with highest EPG count
                #     if the count is same then consider the count of EP in EPG in which the EP belong
                #     recommend the EP with highest EP count
                #     If both of the counts are same then the EP with fvIP is given priority

                if main_count > dup_count:
                    recommendation_list.append([each[key], each['dn'], 'Yes', key])
                    break
                elif main_count == dup_count:
                    ap_main_c = len(extract_ap_epgs[ap_main])
                    ap_dup_c = len(extract_ap_epgs[ap_dup])
                    # Add one with more number of Epgs
                    if ap_main_c > ap_dup_c:
                        recommendation_list.append([each[key], each['dn'], 'Yes', key])
                        break
                    elif ap_main_c < ap_dup_c:
                        recommendation_list.append([each[key], each['dn'], 'No', key])
                        break
                    else:
                        recommendation_list.append([each[key], each['dn'], 'None', key])
                else:
                    recommendation_list.append([each[key], each['dn'], 'No', key])
            elif each[key] != duplicate[dup_key] and each['dn'] != duplicate['dn'] and common_eps.index(each) != common_eps.index(duplicate) and any(each[key] in d for d in recommendation_list) is not True:
                recommendation_list.append([each[key], each['dn'], 'None', key])
            elif accounted == 0:
                recommendation_list.append([each[key], each['dn'], 'None', key])
                accounted = 1

    recommendation_set = set(map(tuple, recommendation_list))
    recommendation_list = map(list, recommendation_set)
    temp_list = copy.deepcopy(recommendation_list)
    for a in temp_list:
        for b in temp_list:
            # If same recommendation already exist with b[2] == 'None' than remove it.
            if a[0] == b[0] and a[1] == b[1] and ((a[2] == 'Yes' or a[2] == 'No') and b[2] == 'None'):
                recommendation_list.remove(b)
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


def recommended_eps(source_ip_list, parsed_eps):
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
        rec_list = determine_recommendation(extract_ap_epgs, common_eps)
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

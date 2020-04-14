import datetime
import json
import custom_logger

logger = custom_logger.CustomLogger.get_logger("/home/app/log/app.log")


def merge_aci_consul(tenant, aci_data, consul_data, aci_consul_mappings):
    """
    Initial algo implementaion.

    Merge ACI data with Consul Data fetched from API directly
    """

    start_time = datetime.datetime.now()
    logger.info('Merging objects for Tenant:'+str(tenant))

    try:
        merge_list = []  # TODO: these should go above 946
        merged_eps = []
        total_epg_count = {}
        merged_epg_count = {}
        non_merged_ep_dict = {}

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

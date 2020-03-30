__author__ = 'nilayshah'

import alchemy as database
import json
import aci_utils
from custom_logger import CustomLogger

db_object = database.Database()

logger = CustomLogger.get_logger("/home/app/log/app.log")

class Recommend(object):

    def getCommonEPs(self, appd_ip_list, aci_parsed_eps):
        """Map EP(ACI) to Nodes(AppD)
        
        Matches the IP of ACI fvIp with AppD Node IPs and returns a list of matched ACI fvIps dicts"""
        
        common_list = []
        for each in aci_parsed_eps:
            if each['IP'] in appd_ip_list:
                common_list.append(each)
        return common_list


    def extract(self, dn):
        """
        Extract ap and epg from given dn
        """
        ap = dn.split('/')[2].split('-',1)[1]
        epg = dn.split('/')[3].split('-',1)[1]
        return ap, epg


    # count_dict Example
    # count_dict = 
    # {
    #     "ap1": {
    #         "epg11":2,
    #         "epg12":3
    #     },
    #     "ap2": {
    #         "epg21":3,
    #         "epg22":1
    #     }
    # }
    def extract_ap_and_epgs(self, eps):
        count_dict = {}
        for ep in eps:
            ap, epg = self.extract(ep['dn'])
            if ap not in count_dict.keys():
                count_dict[ap] = {epg:1}
            elif epg not in count_dict[ap].keys():
                count_dict[ap][epg] = 1
            else:
                count_dict[ap][epg] += 1
        return count_dict


    # returns a list of list
    def determine_recommendation(self, extract_ap_epgs, common_eps):
        recommendation_list = []
        key = ''
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
                    ap_main,epg_main = self.extract(each['dn'])
                    ap_dup,epg_dup = self.extract(duplicate['dn'])
                    
                    # Compare count of 'EPG' for an 'AP'
                    main_count = extract_ap_epgs[ap_main][epg_main]
                    dup_count = extract_ap_epgs[ap_dup][epg_dup]
                    
                    if main_count > dup_count:
                        recommendation_list.append([each[key],each['dn'],'Yes',key])
                        break
                    elif main_count == dup_count:
                        ap_main_c = len(extract_ap_epgs[ap_main])
                        ap_dup_c = len(extract_ap_epgs[ap_dup])
                        # Add one with more number of Epgs
                        if ap_main_c > ap_dup_c:
                            recommendation_list.append([each[key],each['dn'],'Yes',key])
                            break
                        elif ap_main_c < ap_dup_c:
                            recommendation_list.append([each[key],each['dn'],'No',key])
                            break
                        else:
                            recommendation_list.append([each[key],each['dn'],'None',key])
                    else:
                        recommendation_list.append([each[key],each['dn'],'No',key])
                elif each[key] != duplicate[dup_key] and each['dn'] != duplicate['dn'] and common_eps.index(each) != common_eps.index(duplicate) and any(each[key] in d for d in recommendation_list) != True:
                    recommendation_list.append([each[key],each['dn'],'None',key])
                elif accounted == 0:
                    recommendation_list.append([each[key],each['dn'],'None',key])
                    accounted = 1

        for a in recommendation_list:
            for b in recommendation_list:
                # If same recommendation already exist with b[2] == 'None' than remove it.
                if a[0] == b[0] and a[1] == b[1] and (a[2] == 'Yes' or a[2] == 'No') and b[2] == 'None':
                    recommendation_list.remove(b)
        return recommendation_list


    # Sample Return Value
    # [
    #     {
    #         "ipaddress": "1.1.1.1",
    #         "domains": [
    #             {
    #                 "domainName": "dn of epg1",
    #                 "recommended": True
    #             },
    #             {
    #                 "domainName": "dn of epg2",
    #                 "recommended": False
    #             }
    #         ]
    #     },
    #     {
    #         "ipaddress": "2.2.2.2",
    #         "domains": [
    #             {
    #                 "domainName": "dn of epg3",
    #                 "recommended": True
    #             },
    #             {
    #                 "domainName": "dn of epg4",
    #                 "recommended": False
    #             }
    #         ]
    #     }
    # ]
    def generatelist(self,ipList):
        """
        Generate list based on the IP or Mac.
        """
        src_clus_list = []
        ips = []
        macs = []
        for each in ipList:
            if each[3] == 'IP':
                ips.append(each[0])
            else:
                macs.append(each[0])
        ips = list(set(ips))
        macs = list(set(macs))
        ip_dict = dict((el,[]) for el in ips)
        mac_dict = dict((el,[]) for el in macs)
        for each in ipList:
            if each[2] == 'No':
                each[2] = False
            if each[2] == 'Yes' or each[2] == 'None':
                each[2] = True
            if each[3] == 'IP':
                ip_dict[each[0]].append({'domainName':each[1],'recommended':each[2]})
            else:
                mac_dict[each[0]].append({'domainName':each[1],'recommended':each[2]})
        for key,value in ip_dict.iteritems():
            entry = {'ipaddress':key,'domains':value}
            src_clus_list.append(entry)
        for key,value in mac_dict.iteritems():
            entry = {'macaddress':key,'domains':value}
            src_clus_list.append(entry)
        return src_clus_list


    def correlate_aci_appd(self, tenant, appId):
        """
        Correlate API with AppDynamics
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

        common_eps = []
        # Get all nodes for the app
        appd_nodes = list(set(db_object.ips_for_app(appId)))
        logger.info('AppD IPs: '+str(appd_nodes))
        ip_list = []
        mac_nodes_dict = {}
        if not appd_nodes:
            logger.exception('Error: appd_nodes is Empty!')
            return []

        for node in appd_nodes:
            if node.macAddress:
                logger.debug('Node {} with MAC address {}'.format(str(node.nodeId), str(node.macAddress)))
                node_mac_list = node.macAddress
                for node_mac in node_mac_list:
                    if node_mac not in mac_nodes_dict.keys():
                        mac_nodes_dict[node_mac] = [node]
                    else:
                        if node not in mac_nodes_dict[node_mac]:
                            mac_nodes_dict[node_mac].append(node)
            else:
                logger.debug('Node {} with IP address {}'.format(str(node.nodeId), str(node.ipAddress)))
                ip_list += node.ipAddress

        logger.debug("mac_nodes_dict:::"+str(mac_nodes_dict))

        for mac,nodes in mac_nodes_dict.items():
            # If mac exist and unicast routing is true then consider mac
            check,dn = aci_util_obj.get_unicast_routing(mac)
            if not check:
                logger.info('Check failed for MAC address {}'.format(str(mac)))
                for each_node in nodes:
                    ip_list += each_node.ipAddress
            else:
                common_eps.append({'dn': str(dn), 'mac': str(mac), 'tenant': str(tenant)})

        logger.debug('Final IP List ' + str(ip_list))

        # Extract common based on Ips
        try:
            common_eps += self.getCommonEPs(ip_list, parsed_eps)
            logger.debug('Common EPs:'+str(common_eps))
            if common_eps:
                extract_ap_epgs = self.extract_ap_and_epgs(common_eps)
            else:
                return []
        except Exception as e:
            logger.exception('Exception in common eps list, Error:'+str(e))
            return []

        try:
            rec_list = self.determine_recommendation(extract_ap_epgs,common_eps)
        except Exception as e:
            logger.exception('Exception while determining recommended list, Error:'+str(e))
            return []
        
        if rec_list:
            logger.info('Recommendation list for app:'+str(appId)+'  rec_list= '+str(rec_list))
            fin_list = set(map(tuple,rec_list))
            final_list = map(list,fin_list)
            logger.info('Final List final_list '+str(rec_list))
        else:
            logger.info('Error: Empty rec_list ' + str(rec_list))
            return []
        
        try:
            generated_list = self.generatelist(final_list)
        except Exception as e:
            logger.exception('Exception in generate list, Error:'+str(e))
            return []
        
        if generated_list:
            logger.info('Generated List = '+str(generated_list))
            return generated_list
        else:
            logger.info('Error: Empty generated_list ' + str(generated_list))
            return []


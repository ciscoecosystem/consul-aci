import graphene
import plugin_server as app


"""Response Classes"""


class Mapping(graphene.ObjectType):
    mappings = graphene.String()


class SaveMapping(graphene.ObjectType):
    savemapping = graphene.String()


class GetFaults(graphene.ObjectType):
    faultsList = graphene.String()


class GetEvents(graphene.ObjectType):
    eventsList = graphene.String()


class GetAuditLogs(graphene.ObjectType):
    auditLogsList = graphene.String()


class GetOperationalInfo(graphene.ObjectType):
    operationalList = graphene.String()


class GetConfiguredAccessPolicies(graphene.ObjectType):
    accessPoliciesList = graphene.String()


class GetToEpgTraffic(graphene.ObjectType):
    toEpgTrafficList = graphene.String()


class GetSubnets(graphene.ObjectType):
    subnetsList = graphene.String()


class SetPollingInterval(graphene.ObjectType):
    response = graphene.String()

class GetPollingInterval(graphene.ObjectType):
    response = graphene.String()

class OperationalTree(graphene.ObjectType):
    response = graphene.String()


class ServiceChecks(graphene.ObjectType):
    response = graphene.String()


class NodeChecks(graphene.ObjectType):
    response = graphene.String()


class MultiServiceChecks(graphene.ObjectType):
    response = graphene.String()


class MultiNodeChecks(graphene.ObjectType):
    response = graphene.String()


class ReadCreds(graphene.ObjectType):
    creds = graphene.String()


class WriteCreds(graphene.ObjectType):
    creds = graphene.String()


class UpdateCreds(graphene.ObjectType):
    creds = graphene.String()


class DeleteCreds(graphene.ObjectType):
    message = graphene.String()


class DetailsFlattened(graphene.ObjectType):
    details = graphene.String()


class GetDatacenters(graphene.ObjectType):
    datacenters = graphene.String()


class PostTenant(graphene.ObjectType):
    tenant = graphene.String()


class GetPerformanceDashboard(graphene.ObjectType):
    response = graphene.String()


class Query(graphene.ObjectType):
    """Query class which resolves all the incoming requests"""

    Mapping = graphene.Field(Mapping,
                             tn=graphene.String(),
                             datacenter=graphene.String())

    SaveMapping = graphene.Field(SaveMapping,
                                 tn=graphene.String(),
                                 datacenter=graphene.String(),
                                 data=graphene.String())

    OperationalTree = graphene.Field(OperationalTree,
                                     tn=graphene.String(),
                                     datacenter=graphene.String())

    GetFaults = graphene.Field(GetFaults, dn=graphene.String())

    GetEvents = graphene.Field(GetEvents, dn=graphene.String())

    GetAuditLogs = graphene.Field(GetAuditLogs, dn=graphene.String())

    GetOperationalInfo = graphene.Field(GetOperationalInfo,
                                        dn=graphene.String(),
                                        mo_type=graphene.String(),
                                        mac_list=graphene.String(),
                                        ip_list=graphene.String(),
                                        ip=graphene.String())

    GetConfiguredAccessPolicies = graphene.Field(GetConfiguredAccessPolicies,
                                                 tn=graphene.String(),
                                                 ap=graphene.String(),
                                                 epg=graphene.String())

    GetToEpgTraffic = graphene.Field(GetToEpgTraffic, dn=graphene.String())

    GetSubnets = graphene.Field(GetSubnets, dn=graphene.String())

    SetPollingInterval = graphene.Field(SetPollingInterval, interval=graphene.Int())
    
    GetPollingInterval = graphene.Field(GetPollingInterval)

    ServiceChecks = graphene.Field(ServiceChecks,
                                   service_name=graphene.String(),
                                   service_id=graphene.String(),
                                   datacenter=graphene.String())

    NodeChecks = graphene.Field(NodeChecks,
                                node_name=graphene.String(),
                                datacenter=graphene.String())

    MultiServiceChecks = graphene.Field(MultiServiceChecks,
                                        service_list=graphene.String(),
                                        datacenter=graphene.String())

    MultiNodeChecks = graphene.Field(MultiNodeChecks,
                                     node_list=graphene.String(),
                                     datacenter=graphene.String())

    ReadCreds = graphene.Field(ReadCreds)

    WriteCreds = graphene.Field(WriteCreds, agent_list=graphene.String())

    UpdateCreds = graphene.Field(UpdateCreds, update_input=graphene.String())

    DeleteCreds = graphene.Field(DeleteCreds, agent_data=graphene.String())

    DetailsFlattened = graphene.Field(DetailsFlattened,
                                      tn=graphene.String(),
                                      datacenter=graphene.String())

    GetDatacenters = graphene.Field(GetDatacenters)

    PostTenant = graphene.Field(PostTenant, tn=graphene.String())

    GetPerformanceDashboard = graphene.Field(GetPerformanceDashboard,
                                             tn=graphene.String())

    """All the resolve methods of class Query"""
    def resolve_GetFaults(self, info, dn):
        GetFaults.faultsList = app.get_faults(dn)
        return GetFaults

    def resolve_GetEvents(self, info, dn):
        GetEvents.eventsList = app.get_events(dn)
        return GetEvents

    def resolve_GetAuditLogs(self, info, dn):
        GetAuditLogs.auditLogsList = app.get_audit_logs(dn)
        return GetAuditLogs

    def resolve_GetOperationalInfo(self, info, dn, mo_type, mac_list, ip_list, ip):
        GetOperationalInfo.operationalList = app.get_children_ep_info(dn, mo_type, mac_list, ip_list, ip)
        return GetOperationalInfo

    def resolve_GetConfiguredAccessPolicies(self, info, tn, ap, epg):
        GetConfiguredAccessPolicies.accessPoliciesList = app.get_configured_access_policies(tn, ap, epg)
        return GetConfiguredAccessPolicies

    def resolve_GetToEpgTraffic(self, info, dn):
        GetToEpgTraffic.toEpgTrafficList = app.get_to_epg_traffic(dn)
        return GetToEpgTraffic

    def resolve_GetSubnets(self, info, dn):
        GetSubnets.subnetsList = app.get_subnets(dn)
        return GetSubnets

    def resolve_SetPollingInterval(self, info, interval):
        SetPollingInterval.response = app.set_polling_interval(interval)
        return SetPollingInterval

    def resolve_GetPollingInterval(self, info):
        GetPollingInterval.response = app.get_polling_interval()
        return GetPollingInterval

    def resolve_Mapping(self, info, tn, datacenter):
        Mapping.mappings = app.mapping(tn, datacenter)
        return Mapping

    def resolve_SaveMapping(self, info, tn, datacenter, data):
        mapped_data = data
        SaveMapping.savemapping = app.save_mapping(str(tn), str(datacenter), mapped_data)
        return SaveMapping

    def resolve_OperationalTree(self, info, tn, datacenter):
        OperationalTree.response = app.tree(tn, datacenter)
        return OperationalTree

    def resolve_ServiceChecks(self, info, service_name, service_id, datacenter):
        ServiceChecks.response = app.get_service_check(service_name, service_id, datacenter)
        return ServiceChecks

    def resolve_NodeChecks(self, info, node_name, datacenter):
        NodeChecks.response = app.get_node_checks(node_name, datacenter)
        return NodeChecks

    def resolve_MultiServiceChecks(self, info, service_list, datacenter):
        MultiServiceChecks.response = app.get_multi_service_check(service_list, datacenter)
        return MultiServiceChecks

    def resolve_MultiNodeChecks(self, info, node_list, datacenter):
        MultiNodeChecks.response = app.get_multi_node_check(node_list, datacenter)
        return MultiNodeChecks

    def resolve_ReadCreds(self, info):
        ReadCreds.creds = app.read_creds()
        return ReadCreds

    def resolve_WriteCreds(self, info, agent_list):
        WriteCreds.creds = app.write_creds(agent_list)
        return WriteCreds

    def resolve_UpdateCreds(self, info, update_input):
        UpdateCreds.creds = app.update_creds(update_input)
        return UpdateCreds

    def resolve_DeleteCreds(self, info, agent_data):
        DeleteCreds.message = app.delete_creds(agent_data)
        return DeleteCreds

    def resolve_DetailsFlattened(self, info, tn, datacenter):
        DetailsFlattened.details = app.details_flattened(tn, datacenter)
        return DetailsFlattened

    def resolve_GetDatacenters(self, info):
        GetDatacenters.datacenters = app.get_datacenters()
        return GetDatacenters

    def resolve_PostTenant(self, info, tn):
        PostTenant.tenant = app.post_tenant(tn)
        return PostTenant

    def resolve_GetPerformanceDashboard(self, info, tn):
        GetPerformanceDashboard.response = app.get_performance_dashboard(tn)
        return GetPerformanceDashboard


schema = graphene.Schema(query=Query)

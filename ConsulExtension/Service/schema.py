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


class ServiceChecksClick(graphene.ObjectType):
    response = graphene.String()


class NodeChecksClick(graphene.ObjectType):
    response = graphene.String()


class GetDatacenters(graphene.ObjectType):
    datacenters = graphene.String()


class PostTenant(graphene.ObjectType):
    tenant = graphene.String()


class GetPerformanceDashboard(graphene.ObjectType):
    response = graphene.String()


class GetVrf(graphene.ObjectType):
    response = graphene.String()


class NonServiceEndpoints(graphene.ObjectType):
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

    ReadCreds = graphene.Field(ReadCreds, tn=graphene.String())

    WriteCreds = graphene.Field(WriteCreds, tn=graphene.String(),
                                agent_list=graphene.String())

    UpdateCreds = graphene.Field(UpdateCreds, tn=graphene.String(),
                                 update_input=graphene.String())

    DeleteCreds = graphene.Field(DeleteCreds, tn=graphene.String(),
                                 agent_data=graphene.String())

    DetailsFlattened = graphene.Field(DetailsFlattened,
                                      tn=graphene.String(),
                                      datacenter=graphene.String())

    ServiceChecksClick = graphene.Field(ServiceChecksClick,
                                        tn=graphene.String(),
                                        datacenters=graphene.String())

    NodeChecksClick = graphene.Field(NodeChecksClick,
                                     tn=graphene.String(),
                                     datacenters=graphene.String())

    GetDatacenters = graphene.Field(GetDatacenters, tn=graphene.String())

    PostTenant = graphene.Field(PostTenant, tn=graphene.String())

    GetPerformanceDashboard = graphene.Field(GetPerformanceDashboard,
                                             tn=graphene.String())

    GetVrf = graphene.Field(GetVrf, tn=graphene.String())

    NonServiceEndpoints = graphene.Field(NonServiceEndpoints,
                                         tn=graphene.String(),
                                         datacenters=graphene.String())

    """All the resolve methods of class Query"""
    def resolve_GetFaults(self, info, dn):
        """Resolve GetFaults query"""
        GetFaults.faultsList = app.get_faults(dn)
        return GetFaults

    def resolve_GetEvents(self, info, dn):
        """Resolve GetEvents query"""
        GetEvents.eventsList = app.get_events(dn)
        return GetEvents

    def resolve_GetAuditLogs(self, info, dn):
        """Resolved GetAuditLogs query"""
        GetAuditLogs.auditLogsList = app.get_audit_logs(dn)
        return GetAuditLogs

    def resolve_GetOperationalInfo(self, info, dn, mo_type, mac_list, ip_list, ip):
        """Resolved GetOperationalInfo query"""
        GetOperationalInfo.operationalList = app.get_children_ep_info(dn, mo_type, mac_list, ip_list, ip)
        return GetOperationalInfo

    def resolve_GetConfiguredAccessPolicies(self, info, tn, ap, epg):
        """Resolved GetConfiguredAccessPolicies query"""
        GetConfiguredAccessPolicies.accessPoliciesList = app.get_configured_access_policies(tn, ap, epg)
        return GetConfiguredAccessPolicies

    def resolve_GetToEpgTraffic(self, info, dn):
        """Resolved GetToEpgTraffic query"""
        GetToEpgTraffic.toEpgTrafficList = app.get_to_epg_traffic(dn)
        return GetToEpgTraffic

    def resolve_GetSubnets(self, info, dn):
        """Resolved GetSubnets query"""
        GetSubnets.subnetsList = app.get_subnets(dn)
        return GetSubnets

    def resolve_SetPollingInterval(self, info, interval):
        """Resolved SetPollingInterval query"""
        SetPollingInterval.response = app.set_polling_interval(interval)
        return SetPollingInterval

    def resolve_GetPollingInterval(self, info):
        """Resolved GetPollingInterval query"""
        GetPollingInterval.response = app.get_polling_interval()
        return GetPollingInterval

    def resolve_Mapping(self, info, tn, datacenter):
        """Resolved GetOperationalInfo query"""
        Mapping.mappings = app.mapping(tn, datacenter)
        return Mapping

    def resolve_SaveMapping(self, info, tn, datacenter, data):
        """Resolved SaveMapping query"""
        mapped_data = data
        SaveMapping.savemapping = app.save_mapping(str(tn), str(datacenter), mapped_data)
        return SaveMapping

    def resolve_OperationalTree(self, info, tn, datacenter):
        """Resolved GetOperationalInfo query"""
        OperationalTree.response = app.tree(tn, datacenter)
        return OperationalTree

    def resolve_ServiceChecks(self, info, service_name, service_id, datacenter):
        """Resolved ServiceChecks query"""
        ServiceChecks.response = app.get_service_check(service_name, service_id, datacenter)
        return ServiceChecks

    def resolve_NodeChecks(self, info, node_name, datacenter):
        """Resolved NodeChecks query"""
        NodeChecks.response = app.get_node_checks(node_name, datacenter)
        return NodeChecks

    def resolve_MultiServiceChecks(self, info, service_list, datacenter):
        """Resolved MultiServiceChecks query"""
        MultiServiceChecks.response = app.get_multi_service_check(service_list, datacenter)
        return MultiServiceChecks

    def resolve_MultiNodeChecks(self, info, node_list, datacenter):
        """Resolved MultiNodeChecks query"""
        MultiNodeChecks.response = app.get_multi_node_check(node_list, datacenter)
        return MultiNodeChecks

    def resolve_ReadCreds(self, info, tn):
        """Resolved ReadCreds query"""
        ReadCreds.creds = app.read_creds(tn)
        return ReadCreds

    def resolve_WriteCreds(self, info, tn, agent_list):
        """Resolved WriteCreds query"""
        WriteCreds.creds = app.write_creds(tn, agent_list)
        return WriteCreds

    def resolve_UpdateCreds(self, info, tn, update_input):
        """Resolved UpdateCreds query"""
        UpdateCreds.creds = app.update_creds(tn, update_input)
        return UpdateCreds

    def resolve_DeleteCreds(self, info, tn, agent_data):
        """Resolved DeleteCreds query"""
        DeleteCreds.message = app.delete_creds(tn, agent_data)
        return DeleteCreds

    def resolve_DetailsFlattened(self, info, tn, datacenter):
        """Resolved DetailsFlattened query"""
        DetailsFlattened.details = app.details_flattened(tn, datacenter)
        return DetailsFlattened

    def resolve_ServiceChecksClick(self, info, tn, datacenters):
        """Resolved ServiceChecksClick query"""
        ServiceChecksClick.response = app.servicecheck_clickable(tn, datacenters)
        return ServiceChecksClick

    def resolve_NodeChecksClick(self, info, tn, datacenters):
        """Resolved NodeChecksClick query"""
        NodeChecksClick.response = app.nodecheck_clickable(tn, datacenters)
        return NodeChecksClick

    def resolve_GetDatacenters(self, info, tn):
        """Resolved GetDatacenters query"""
        GetDatacenters.datacenters = app.get_datacenters(tn)
        return GetDatacenters

    def resolve_PostTenant(self, info, tn):
        """Resolved PostTenant query"""
        PostTenant.tenant = app.post_tenant(tn)
        return PostTenant

    def resolve_GetPerformanceDashboard(self, info, tn):
        """Resolved GetPerformanceDashboard query"""
        GetPerformanceDashboard.response = app.get_performance_dashboard(tn)
        return GetPerformanceDashboard

    def resolve_GetVrf(self, info, tn):
        """Resolved GetVrf query"""
        GetVrf.response = app.update_vrf_in_db(tn)
        return GetVrf

    def resolve_NonServiceEndpoints(self, info, tn, datacenters):
        """Resolved NonServiceEndpoints query"""
        NonServiceEndpoints.response = app.non_service_endpoints(tn, datacenters)
        return NonServiceEndpoints


schema = graphene.Schema(query=Query)

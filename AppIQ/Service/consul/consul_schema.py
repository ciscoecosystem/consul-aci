import graphene
from . import consul_plugin_server as app


"""Response Classes"""
class Check(graphene.ObjectType):
    checkpoint = graphene.String()


class LoginApp(graphene.ObjectType):
    loginStatus = graphene.String()


class Application(graphene.ObjectType):
    apps = graphene.String()


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
    status = graphene.String()
    message = graphene.String()


class Run(graphene.ObjectType):
    response = graphene.String()


class Details(graphene.ObjectType):
    details = graphene.String()


class ServiceChecks(graphene.ObjectType):
    response = graphene.String()


class NodeChecks(graphene.ObjectType):
    response = graphene.String()


class ServiceChecksEP(graphene.ObjectType):
    response = graphene.String()


class NodeChecksEPG(graphene.ObjectType):
    response = graphene.String()


class ReadCreds(graphene.ObjectType):
    creds = graphene.String()

class WriteCreds(graphene.ObjectType):
    creds = graphene.String()

class UpdateCreds(graphene.ObjectType):
    creds = graphene.String()

class DeleteCreds(graphene.ObjectType):
    message = graphene.String()

class Query(graphene.ObjectType):
    """Query class which resolves all the incomming requests"""
    
    Check = graphene.Field(Check)

    LoginApp = graphene.Field(LoginApp, 
                                ip = graphene.String(), 
                                port = graphene.String(), 
                                username = graphene.String(),
                                account = graphene.String(),
                                password = graphene.String()
                            )

    Application = graphene.Field(Application, tn=graphene.String())

    Mapping = graphene.Field(Mapping, tn=graphene.String(), datacenter=graphene.String())

    SaveMapping = graphene.Field(SaveMapping, 
                                    appId = graphene.String(),
                                    tn = graphene.String(),
                                    data = graphene.String()
                                )

    Run = graphene.Field(Run, tn=graphene.String(), datacenter=graphene.String())

    GetFaults = graphene.Field(GetFaults, dn=graphene.String())

    GetEvents = graphene.Field(GetEvents, dn=graphene.String())

    GetAuditLogs = graphene.Field(GetAuditLogs, dn=graphene.String())

    GetOperationalInfo = graphene.Field(GetOperationalInfo, 
                                            dn = graphene.String(),
                                            moType = graphene.String(),
                                            macList = graphene.String()
                                        )

    GetConfiguredAccessPolicies = graphene.Field(GetConfiguredAccessPolicies,
                                                    tn = graphene.String(),
                                                    ap = graphene.String(),
                                                    epg = graphene.String()
                                                )

    GetToEpgTraffic = graphene.Field(GetToEpgTraffic, dn = graphene.String())

    GetSubnets = graphene.Field(GetSubnets, dn = graphene.String())

    SetPollingInterval = graphene.Field(SetPollingInterval, interval = graphene.String())

    Details = graphene.Field(Details, tn=graphene.String(), datacenter=graphene.String())

    ServiceChecks = graphene.Field(ServiceChecks,
                                    service_name = graphene.String(),
                                    service_id = graphene.String(),
                                    datacenter = graphene.String()
                                )

    NodeChecks = graphene.Field(NodeChecks, node_name=graphene.String(), datacenter=graphene.String())

    ServiceChecksEP = graphene.Field(ServiceChecksEP, service_list=graphene.String(), datacenter=graphene.String())

    NodeChecksEPG = graphene.Field(NodeChecksEPG, node_list=graphene.String(), datacenter=graphene.String())

    ReadCreds = graphene.Field(ReadCreds)
    WriteCreds = graphene.Field(WriteCreds, agent_list=graphene.String())
    UpdateCreds = graphene.Field(UpdateCreds, update_input=graphene.String())
    DeleteCreds = graphene.Field(DeleteCreds, agent_data=graphene.String())

    def resolve_GetFaults(self, info, dn):
        GetFaults.faultsList = app.get_faults(dn)
        return GetFaults


    def resolve_GetEvents(self, info, dn):
        GetEvents.eventsList = app.get_events(dn)
        return GetEvents


    def resolve_GetAuditLogs(self, info, dn):
        GetAuditLogs.auditLogsList = app.get_audit_logs(dn)
        return GetAuditLogs


    def resolve_GetOperationalInfo(self, info, dn, moType, macList):
        GetOperationalInfo.operationalList = app.get_childrenEp_info(dn, moType, macList)
        return GetOperationalInfo


    def resolve_GetConfiguredAccessPolicies(self, info, tn, ap, epg):
        GetConfiguredAccessPolicies.accessPoliciesList = app.get_configured_access_policies(tn, ap, epg)
        return GetConfiguredAccessPolicies


    def resolve_GetToEpgTraffic(self, info, dn):
        GetToEpgTraffic.toEpgTrafficList = app.get_to_Epg_traffic(dn)
        return GetToEpgTraffic


    def resolve_GetSubnets(self, info, dn):
        GetSubnets.subnetsList = app.get_subnets(dn)
        return GetSubnets


    def resolve_SetPollingInterval(self, info, interval):
        status, message = app.set_polling_interval(interval)
        SetPollingInterval.status = status
        SetPollingInterval.message = message
        return SetPollingInterval


    def resolve_Check(self,info): #On APIC
        Check.checkpoint = app.checkFile()
        return Check


    def resolve_LoginApp(self, info, ip, port, username, account, password):
        app_creds = {"appd_ip": ip, "appd_port": port, "appd_user": username, "appd_account": account,
                     "appd_pw": password}
        loginResp = app.login(app_creds)
        LoginApp.loginStatus = loginResp
        return LoginApp


    def resolve_Application(self, info, tn): # TODO: remove the tn
        Application.apps = app.get_datacenter_list()
        return Application


    def resolve_Mapping(self, info, tn, datacenter):
        Mapping.mappings = app.mapping(tn, datacenter)
        return Mapping


    def resolve_SaveMapping(self, info, appId, tn, data):
        mappedData = data
        SaveMapping.savemapping = app.save_mapping(int(appId), str(tn), mappedData)
        return SaveMapping


    def resolve_Run(self, info, tn, datacenter):
        Run.response = app.tree(tn, datacenter)
        return Run


    def resolve_Details(self, info, tn, datacenter):
        Details.details = app.details(tn, datacenter)
        return Details


    def resolve_ServiceChecks(self, info, service_name, service_id, datacenter):
        ServiceChecks.response = app.get_service_check(service_name, service_id, datacenter)
        return ServiceChecks


    def resolve_NodeChecks(self, info, node_name, datacenter):
        NodeChecks.response = app.get_node_checks(node_name, datacenter)
        return NodeChecks


    def resolve_ServiceChecksEP(self, info, service_list, datacenter):
        ServiceChecksEP.response = app.get_service_check_ep(service_list, datacenter)
        return ServiceChecksEP


    def resolve_NodeChecksEPG(self, info, node_list, datacenter):
        NodeChecksEPG.response = app.get_node_check_epg(node_list, datacenter)
        return NodeChecksEPG 

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


schema = graphene.Schema(query=Query)

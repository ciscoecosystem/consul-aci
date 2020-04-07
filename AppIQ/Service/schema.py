__author__ = 'nilayshah'
import graphene
import plugin_server as app

class Check(graphene.ObjectType):
    checkpoint = graphene.String()


class LoginApp(graphene.ObjectType):
    loginStatus = graphene.String()
    # loginMessage = graphene.String()


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


# class EnableView(graphene.ObjectType):
#     view = graphene.String()

class Details(graphene.ObjectType):
    details = graphene.String()

class ServiceChecks(graphene.ObjectType):
    response = graphene.String()

class NodeChecks(graphene.ObjectType):
    response = graphene.String()

class ServiceChecksEP(graphene.ObjectType):
    response = graphene.String()

class Query(graphene.ObjectType):
    Check = graphene.Field(Check)
    LoginApp = graphene.Field(LoginApp, ip=graphene.String(), port=graphene.String(), username=graphene.String(),
                              account=graphene.String(),
                              password=graphene.String())
    Application = graphene.Field(Application, tn=graphene.String())
    Mapping = graphene.Field(Mapping, tn=graphene.String(), appId=graphene.String())
    SaveMapping = graphene.Field(SaveMapping, appId=graphene.String(),tn=graphene.String(),
                                 data=graphene.String())  # data can be a list or string.. Check!
    Run = graphene.Field(Run, tn=graphene.String(), appId=graphene.String())

    GetFaults = graphene.Field(GetFaults, dn=graphene.String())
    GetEvents = graphene.Field(GetEvents, dn=graphene.String())
    GetAuditLogs = graphene.Field(GetAuditLogs, dn=graphene.String())
    GetOperationalInfo = graphene.Field(GetOperationalInfo, dn = graphene.String(), moType = graphene.String(), ipList = graphene.String())
    GetConfiguredAccessPolicies = graphene.Field(GetConfiguredAccessPolicies, tn = graphene.String(), ap = graphene.String(), epg = graphene.String())
    GetToEpgTraffic = graphene.Field(GetToEpgTraffic, dn = graphene.String())
    GetSubnets = graphene.Field(GetSubnets, dn = graphene.String())
    SetPollingInterval = graphene.Field(SetPollingInterval, interval = graphene.String())

    # EnableView = graphene.Field(EnableView,view=graphene.String())
    Details = graphene.Field(Details, tn=graphene.String(), appId=graphene.String())
    ServiceChecks = graphene.Field(ServiceChecks, service_name=graphene.String(), service_id=graphene.String())
    NodeChecks = graphene.Field(NodeChecks, node_name=graphene.String())
    ServiceChecksEP = graphene.Field(ServiceChecksEP, service_list=graphene.String())


    def resolve_GetFaults(self, info, dn):
        GetFaults.faultsList = app.get_faults(dn)
        return GetFaults

    def resolve_GetEvents(self, info, dn):
        GetEvents.eventsList = app.get_events(dn)
        return GetEvents

    def resolve_GetAuditLogs(self, info, dn):
        GetAuditLogs.auditLogsList = app.get_audit_logs(dn)
        return GetAuditLogs
    
    def resolve_GetOperationalInfo(self, info, dn, moType, ipList):
        GetOperationalInfo.operationalList = app.get_childrenEp_info(dn, moType, ipList)
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
    #def resolve_Check(self, args, context, info):  # On local desktop
        Check.checkpoint = app.checkFile()
        return Check

    def resolve_LoginApp(self, info, ip, port, username, account, password):  # On APIC
        app_creds = {"appd_ip": ip, "appd_port": port, "appd_user": username, "appd_account": account,
                     "appd_pw": password}
        # def resolve_LoginApp(self, args, context, info): # On local desktop
        #    app_creds = {"appd_ip": args.get('ip'),"appd_port": args.get('port'), "appd_user": args.get('username'), "appd_account": args.get('account'),
        #                "appd_pw": args.get('password')}
        loginResp = app.login(app_creds)
        # print loginResp
        LoginApp.loginStatus = loginResp
        # LoginApp.loginMessage = loginResp['message']

        return LoginApp

    def resolve_Application(self, info, tn):  # On APIC
        # def resolve_Application(self,args,context,info): # On local desktop
        Application.apps = app.apps(tn)
        return Application

    def resolve_Mapping(self, info, tn, appId):  # args, context, info): # On APIC
        # def resolve_Mapping(self, args, context, info): # On local desktop
        #    tn = args.get('tn')
        #    appId = int(args.get('appId'))
        Mapping.mappings = app.mapping(tn, int(appId))  # Add params to plugin_server for this method
        return Mapping

    def resolve_SaveMapping(self, info, appId, tn, data):  # On APIC
        # def resolve_SaveMapping(self,args,context,info): # On local desktop (Uncomment appId and data args)
        #    appId = int(args.get('appId'))
        #    mappedData = args.get('data')
        mappedData = data
        #print info
        SaveMapping.savemapping = app.save_mapping(int(appId), str(tn), mappedData)
        return SaveMapping

    def resolve_Run(self, info, tn):  # On APIC
        # def resolve_Run(self,args,context,info): # On local desktop (Uncomment appId and tn args)
        #    tn = args.get('tn')
        #    appId = int(args.get('appId'))
        Run.response = app.tree(tn, 9)
        return Run

    def resolve_Details(self, info, tn):  # On APIC
        # def resolve_Details(self,args,context,info):# On local desktop (Uncomment appId and tn args)
        #    tn = args.get('tn')
        #    appId = int(args.get('appId'))
        Details.details = app.get_details(tn, 9)
        return Details

    def resolve_ServiceChecks(self, info, service_name, service_id):
        ServiceChecks.response = app.get_service_check(service_name, service_id)
        return ServiceChecks
    
    def resolve_NodeChecks(self, info, node_name):
        NodeChecks.response = app.get_node_checks(node_name)
        return NodeChecks

    def resolve_ServiceChecksEP(self, info, service_list):
        ServiceChecksEP.response = app.get_service_check_ep(service_list)
        return ServiceChecksEP

        # def resolve_EnableView(self, args, context, info):
        #
        #     return EnableView


schema = graphene.Schema(query=Query)

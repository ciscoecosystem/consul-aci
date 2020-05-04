#Aci Utils

LOGIN_URL_SUFFIX = '/api/requestAppToken.json'
LOGIN_URL = '{0}{1}' + LOGIN_URL_SUFFIX
FVEP_URL = '{0}{1}/api/class/fvCEp.json'
FVIP_URL = '{0}{1}/api/class/fvIp.json'
FVAEPG_URL = '{0}{1}/api/class/fvAEPg.json'

MO_URL = '{0}{1}/api/node/mo/{2}.json?{3}'
MO_HEALTH_URL = '{0}{1}/api/node/class/healthRecord.json?query-target-filter=eq(healthRecord.affected,\"{2}\")'
MO_OTHER_URL = '{0}{1}/api/node/mo/uni/epp/fv-[{2}].json?{3}'

MO_INSTANCE_URL = '{0}{1}/api/node/class/{2}.json'
EPG_HEALTH_URL = '{0}{1}/api/node/mo/uni/tn-{2}/ap-{3}/epg-{4}.json?rsp-subtree-include=health,no-scoped'
FETCH_EP_DATA_URL = '{0}?query-target-filter=wcard(fvIp.dn,"{1}/")'
FETCH_EPG_DATA_URL = '{0}?query-target-filter=wcard(fvCEp.dn,"tn-{1}/")&query-target=children&target-subtree-class=fvCEp&rsp-subtree=children&rsp-subtree-class=fvRsToVm,fvRsCEpToPathEp,fvIp,fvRsHyper'
FETCH_BD_URL = '{0}{1}/api/node/mo/{2}.json?query-target=children&target-subtree-class=fvRsBd'
FETCH_VRF_URL = '{0}{1}/api/node/mo/{2}.json?query-target=children&target-subtree-class=fvRsCtx'
FETCH_CONTRACT_URL = '{0}{1}/api/node/mo/{2}.json?query-target=children&target-subtree-class=fvRsCons,fvRsProv,fvRsConsIf,fvRsProtBy,fvRsConsIf'

CHECK_UNICAST_URL = '{0}{1}/api/node/class/fvBD.json?query-target-filter=eq(fvBD.name,"{2}")'
FETCH_EP_MAC_URL = '{0}{1}/api/node/class/fvCEp.json?query-target-filter=eq(fvCEp.mac,"{2}")'

AUDIT_LOGS_QUERY = 'rsp-subtree-include=audit-logs,no-scoped,subtree'
FAULTS_QUERY = 'rsp-subtree-include=fault-records,no-scoped,subtree'
EVENTS_QUERY = 'rsp-subtree-include=event-logs,no-scoped,subtree'

#AppD Urls
#All urls containing "/restui" are non documented Appd API
APPD_LOGIN_URL = '{0}:{1}/controller/auth?action=login'
APP_HEALTH_URL = '{0}:{1}/controller/restui/app/list/ids'
APP_HEALTH_URL_V1 = '{0}:{1}/controller/restui/v1/app/list/ids'
TIER_HEALTH_URL = '{0}:{1}/controller/restui/tiers/list/health/ids'
TIER_HEALTH_URL_V1 = '{0}:{1}/controller/restui/v1/tiers/list/health/ids'
NODE_HEALTH_URL = '{0}:{1}/controller/restui/nodes/list/health/ids'
NODE_HEALTH_URL_V1 = '{0}:{1}/controller/restui/v1/nodes/list/health/ids'
SERVICE_ENDPOINTS_URL = '{0}:{1}/controller/restui/serviceEndpoint/listViewData/{2}/{3}?time-range=last_5_minnutes.BEFORE_NOW.-1.-1.5'
NODE_MAC_URL = '{0}:{1}/controller/sim/v2/user/machines?nodeIds={2}&output=JSON'
APP_INFO_URL = '{0}:{1}/controller/rest/applications?output=JSON'
TIER_INFO_URL = '{0}:{1}/controller/rest/applications/{2}/tiers?output=JSON'
NODE_INFO_URL = '{0}:{1}/controller/rest/applications/{2}/tiers/{3}/nodes?output=JSON'
HEALTH_VIOLATIONS_URL = '{0}:{1}/controller/restui/incidents/application/{2}'
NODE_DETAILS_URL = '{0}:{1}/controller/rest/applications/{2}/nodes/{3}?output=JSON'
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
# EPG_HEALTH_URL = '{0}{1}/api/node/mo/uni/tn-{2}/ap-{3}/epg-{4}.json?rsp-subtree-include=health,no-scoped'
FETCH_EP_DATA_URL = '{0}?query-target-filter=wcard(fvCEp.dn,"tn-{1}/")&query-target=children&target-subtree-class=fvCEp&rsp-subtree=children&rsp-subtree-class=fvRsToVm,fvRsCEpToPathEp,fvIp,fvRsHyper'
EPG_HEALTH_URL = '{0}{1}/api/node/mo/{2}.json?rsp-subtree-include=health,no-scoped'
FETCH_EPG_DATA_URL = '{0}?query-target-filter=wcard(fvCEp.dn, "tn-{1}")'

FETCH_BD_URL = '{0}{1}/api/node/mo/{2}.json?query-target=children&target-subtree-class=fvRsBd'
FETCH_VRF_URL = '{0}{1}/api/node/mo/{2}.json?query-target=children&target-subtree-class=fvRsCtx'
FETCH_CONTRACT_URL = '{0}{1}/api/node/mo/{2}.json?query-target=children&target-subtree-class=fvRsCons,fvRsProv,fvRsConsIf,fvRsProtBy,fvRsConsIf'

CHECK_UNICAST_URL = '{0}{1}/api/node/class/fvBD.json?query-target-filter=eq(fvBD.name,"{2}")'
FETCH_EP_MAC_URL = '{0}{1}/api/node/class/fvCEp.json?query-target-filter=eq(fvCEp.mac,"{2}")'

AUDIT_LOGS_QUERY = 'rsp-subtree-include=audit-logs,no-scoped,subtree'
FAULTS_QUERY = 'rsp-subtree-include=fault-records,no-scoped,subtree'
EVENTS_QUERY = 'rsp-subtree-include=event-logs,no-scoped,subtree'

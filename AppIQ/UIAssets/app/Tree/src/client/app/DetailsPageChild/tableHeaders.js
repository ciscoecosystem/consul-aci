import React from "react"
const ROWS_FAULTS = [{
    "code": "F0956",
    "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX0-leaf102]",
    "severity": "cleared",
    "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX0-leaf102 of class vmmDomP",
    "created": "2019-01-23T02:05:42.497-07:00"
},
{
    "code": "F0956",
    "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX0-leaf102]",
    "severity": "warning",
    "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX0-leaf102 of class vmmDomP",
    "created": "2019-01-22T23:16:02.555-07:00"
},
{
    "code": "F0956",
    "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX0-leaf102]",
    "severity": "cleared",
    "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX0-leaf102 of class vmmDomP",
    "created": "2019-01-17T03:07:42.083-07:00"
},
{
    "code": "F0956",
    "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX1-Leaf102]",
    "severity": "cleared",
    "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX1-Leaf102 of class infraDomP",
    "created": "2018-11-16T17:39:07.208-07:00"
},
{
    "code": "F0956",
    "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX1-Leaf102]",
    "severity": "cleared",
    "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX1-Leaf102 of class infraDomP",
    "created": "2018-11-16T16:38:54.692-07:00"
}];
const TABLE_TOEPG = [
    {
        Header: 'To EPG',
        accessor: 'to_epg'
    }, {
        Header: 'EPG Alias',
        accessor: 'alias'
    }, {
        Header: 'Type',
        accessor: 'type',
    }, {
        Header: 'Contract Subject',
        accessor: 'contract_subj'
    }, {
        Header: 'Filter : EtherT:Protocol:srcFromPort-srcToPort to destFromPort-destToPort',
        accessor: 'filter_list',
        Cell: row => {
            return <div>{row.value.map(item => [<span>{item}</span>, <br></br>])}</div>
        },
        styles: { display: "table-column" }
    }, {
        Header: 'Egress 15min: Cumulative Packets',
        accessor: 'egr_pkts',

    }, {
        Header: 'Ingress 15min: Cumulative Packets',
        accessor: 'ingr_pkts',
    }, {
        id: 3,
        Header: 'Total 15min: Cumulative Packets',
        accessor: d => parseInt(d.egr_pkts) + parseInt(d.ingr_pkts),
    }

]
const TABLE_SUBNETS = [
    {
        Header: 'IP',
        accessor: 'ip'
    },
    {
        Header: 'To EPG',
        accessor: 'to_epg'
    },
    {
        Header: 'EPG Alias',
        accessor: 'epg_alias'
    },
]
const TABLE_OPERATIONAL = [
    {
        Header: 'End Point',
        accessor: 'ep_name'
    },
    {
        Header: 'IP',
        accessor: 'ip'
    },
    {
        Header: 'MAC',
        accessor: 'mac'
    },
    {
        Header: 'Learning Resource',
        accessor: 'learning_source'
    },
    {
        Header: 'Hosting Server',
        accessor: 'hosting_server_name'
    },
    {
        Header: 'Reporting Controller Name',
        accessor: 'ctrlr_name'
    },
    {
        Header: 'Interface',
        accessor: 'iface_name',
        width: 190,
        Cell: row => {
            return (<div>
                {row.value.map(function (val) {
                    return <React.Fragment>
                        {val}
                        <br />
                    </React.Fragment>
                })}
            </div>)
        }
    },
    {
        Header: "Multicast Address",
        accessor: 'mcast_addr'
    },
    {
        Header: 'Encap',
        accessor: 'encap'
    },
]
const TABLE_POLICIES = [
    {
        Header: 'Domain',
        accessor: 'domain'
    },
    {
        Header: 'Switch Profile',
        accessor: 'switch_prof'
    },
    {
        Header: 'Attachable Entity Profile',
        accessor: 'aep'
    },
    {
        Header: 'Interface Profile',
        accessor: 'iface_prof'
    },
    {
        Header: 'PC/vPC/If Policy Group',
        accessor: 'pc_vpc'
    },
    {
        Header: 'Node',
        accessor: 'node'
    },
    {
        Header: 'Path Endpoint',
        accessor: 'path_ep'
    },
    {
        Header: "VLAN Pool",
        accessor: 'vlan_pool'
    },

]
const TABLE_COLUMNS_FAULTS = [
    {
        Header: 'Severity',
        accessor: 'severity'

    },
    {
        Header: 'Code',
        accessor: 'code'
    },
    {
        Header: 'Cause',
        accessor: 'cause'
    },
    {
        Header: 'Affected Object',
        accessor: 'affected'
    },
    {
        Header: 'Description',
        accessor: 'descr'
    },
    {
        Header: 'Creation Time',
        accessor: 'created'
    }];
const TABLE_COLUMNS_EVENTS = [
    {
        Header: 'Severity',
        accessor: 'severity'

    },
    {
        Header: 'Code',
        accessor: 'code'
    },
    {
        Header: 'Cause',
        accessor: 'cause'
    },
    {
        Header: 'Affected Object',
        accessor: 'affected'
    },
    {
        Header: 'Description',
        accessor: 'descr'
    },
    {
        Header: 'Creation Time',
        accessor: 'created'
    }];
const TABLE_COLUMNS_AUDIT_LOG = [
    {
        Header: 'ID',
        accessor: 'id'

    },
    {
        Header: 'Affected Object',
        accessor: 'affected'
    },
    {
        Header: 'Description',
        accessor: 'descr'
    },
    {
        Header: 'Action',
        accessor: 'action'
    },
    {
        Header: 'User',
        accessor: 'user'
    },
    {
        Header: 'Creation Time',
        accessor: 'created'
    }];

export { TABLE_SUBNETS, TABLE_TOEPG, TABLE_POLICIES, ROWS_FAULTS, TABLE_COLUMNS_FAULTS, TABLE_COLUMNS_AUDIT_LOG, TABLE_COLUMNS_EVENTS, TABLE_OPERATIONAL }

import React from "react"

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
        Header: 'Filters',
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
        Header: 'PC/vPC/Interface Policy Group',
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

export { TABLE_SUBNETS, TABLE_TOEPG, TABLE_POLICIES, TABLE_COLUMNS_FAULTS, TABLE_COLUMNS_AUDIT_LOG, TABLE_COLUMNS_EVENTS, TABLE_OPERATIONAL }

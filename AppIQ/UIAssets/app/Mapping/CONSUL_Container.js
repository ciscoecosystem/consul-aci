import React from 'react'
import { Switch, Table, Button, Icon } from 'blueprint-react';
import { PROFILE_NAME, QUERY_URL, getCookie } from '../../constants.js';
import './consulmapping.css';
// import './style.css'

const dummyData = [{ ip: "192.168.128.20", dns: "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord", status: true, recommended: true },
{ ip: "20.20.20.10", dns: "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-test", status: false, recommended: true },
{ ip: "20.20.20.10", dns: "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-abc", status: true, recommended: false },
{ ip: "19.11.12.11", dns: "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord", status: false, recommended: false }]

export default class CONSUL_Container extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            mappingData: dummyData
        }
    }


    render() {

        const tableColumns = [{
            Header: 'IP',
            accessor: 'ip',
            Cell: row => {
                let { ip, recommended } = row.original;
                return <div> {ip} {recommended && <Icon style={{ color: "green !important" }} key={"d"} className="recommend-icon" size="icon-small" type="icon-check-outline" />} </div>
            }
        },
        {
            Header: 'Domain Name',
            accessor: 'dns'
        },
        {
            Header: 'Action',
            accessor: 'status',
            Cell: row => {
                let { status } = row.original
                return <div className="">
                    <Switch key="s0" checked={status} onChange={() => { console.log("Handling") }} />
                </div>
            }
        }
        ]

        return (
            <div>
                {/* <Header text={this.props.headertext} applinktext={this.props.applinktext} instanceName={headerInstanceName} /> */}
                <div className="" style={{ margin: "0px 20px"}}>
                    <div style={{display:"flex", justifyContent: "space-between" }}>
                        <p>Selected <b>2</b> out of 4 clusters <Icon style={{ color: "green !important" }} key={"d"} className="recommend-icon" size="icon-small" type="icon-check-outline" /> Recommended </p>
                        <Button key={"savemapping"}
                            className={"savemapping"}
                            size="btn--small"
                            type="btn--primary-ghost"
                            onClick={() => { console.log("Save") }}>Save</Button>
                    </div>

                    <Table key={"mappingtable"}
                        loading={false}
                        loadingText={"Loading Mapping detail...."}
                        className="-striped -highlight"
                        noDataText="No Mapping Found."
                        data={this.state.mappingData}
                        columns={tableColumns}
                    />
                    {/* <div style={{ padding: "15px 0px", textAlign: "right" }}>
                        <Button key={"savemapping"}
                            className={""}
                            size="btn--small"
                            type="btn--primary-ghost"
                            onClick={() => { console.log("Save") }}>Save</Button>

                    </div> */}
                </div>
            </div>
        )
    }
}

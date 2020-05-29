import React from 'react'
import { Switch, Table, Button, Icon, FilterableTable } from 'blueprint-react';
import { toast } from 'react-toastify';
import { PROFILE_NAME, QUERY_URL, getCookie } from '../../constants.js';
import 'react-toastify/dist/ReactToastify.css';
import './consulmapping.css';
// import './style.css'

const dummyData = [{
    ip: "192.168.128.20", "ap": "AppD-AppProfile1",
    "vrf": "AppDynamics/AppD-VRF",
    "epg": "Appd-Ecom-Cont",
    "bd": "AppD-BD3",
    tenant: "tenant101", enabled: true, recommended: true
},
{
    ip: "192.168.128.21", "ap": "AppD-AppProfile2",
    "vrf": "AppDynamics22/AppD-VRF",
    "epg": "Appd-tyty-Cont",
    "bd": "AppD-BD7",
    tenant: "tenant101", enabled: true, recommended: false
},
{
    ip: "192.168.128.23", "ap": "AppD-AppProfile3",
    "vrf": "AppDynamics77/AppD-VRF",
    "epg": "Appd-erer-Cont",
    "bd": "AppD-BD1",
    tenant: "tenant101", enabled: false, recommended: false
},
{
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
},
{
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
},
{
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
},
{
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
},
{
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
},
{
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
},
{
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
}, {
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
}, {
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
}, {
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
}, {
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
}, {
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: true, recommended: true
}, {
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: true, recommended: true
}, {
    ip: "192.168.128.21", "ap": "AppD-AppProfile4",
    "vrf": "AppDynamics11/AppD-VRF",
    "epg": "Appd-fdgdf-Cont",
    "bd": "AppD-BD55",
    tenant: "tenant101", enabled: false, recommended: true
}
]

export default class CONSUL_Container extends React.Component {
    constructor(props) {
        super(props);
        console.log("cONSUL container; props", this.props); //datacenterName & tenantName

        this.getStaticData = this.getStaticData.bind(this);
        this.handleSwitchChange = this.handleSwitchChange.bind(this);
        this.saveMapping = this.saveMapping.bind(this);

        this.state = {
            mappingData: [],
            loading: true,
            sortOptions: [{ id: 'ip', desc: false }],
            totalEnabled: 0,
            loadingText: "Loading mapping..."
        }
    }

    componentDidMount() {
        this.getStaticData();
    }

    saveMapping(){
        let thiss = this;
        this.setState({loading: true, loadingText:"Saving..."}, function() {

            setTimeout(() => {
                thiss.setState({
                    loading: false
                })
                toast.success("Saved successfully", {
                    position: toast.POSITION.TOP_CENTER
                });
                thiss.props.onClose(); // close the mapping screen on successfull save

            }, 2000);

        })
    }

    getStaticData() {
        setTimeout(() => {
            console.log("Got data");
            let totalEnabled = 0;
            this.setState({
                mappingData: dummyData,
                loading: false
            })

            dummyData.forEach(function (elem) {
                totalEnabled += elem.enabled ? 1 : 0;
            })
            this.setState({ totalEnabled });
        }, 2000)
    }

    handleSwitchChange(index) {
        // let data = this.state.mappingData;
        let { totalEnabled, mappingData } = this.state;
        console.log("==> ", mappingData[index]);

        mappingData[index]["enabled"] = !mappingData[index]["enabled"];
        totalEnabled += mappingData[index]["enabled"] ? 1 : -1;

        this.setState({
            mappingData,
            totalEnabled
        });
    }

    render() {

        const tableColumns = [{
            Header: 'IP',
            accessor: 'ip',
        },
        {
            Header: 'Recommended',
            accessor: 'recommended',
            Cell: row => {
                let { recommended } = row.original;
                return recommended ? <Icon style={{ color: "green !important" }} key={"d"} className="recommend-icon" size="icon-small" type="icon-check-outline" /> : <span></span>
            }
        },
        {
            Header: 'VRF',
            accessor: 'vrf'
        },
        {
            Header: 'BD',
            accessor: 'bd'
        },
        {
            Header: 'EPG',
            accessor: 'epg'
        },
        {
            Header: 'Application Profile',
            accessor: 'ap'
        },
        {
            Header: 'Tenant',
            accessor: 'tenant'
        },
        {
            Header: 'Action',
            accessor: 'enabled',
            filterable: false,
            Cell: row => {
                console.log("==> action ", row);
                let { enabled } = row.original;
                return <div>
                    <Switch key={"clustr-" + row.index} checked={enabled}
                    onChange={() => this.handleSwitchChange(row.index)} />
                </div>
            }
        }
        ]

        let { mappingData, totalEnabled, loading } = this.state;

        return (
            <div>
                {/* <Header text={this.props.headertext} applinktext={this.props.applinktext} instanceName={headerInstanceName} /> */}
                <div className="" style={{ margin: "0px 20px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>

                        <p>Selected <b>{totalEnabled}</b> out of {mappingData.length}  </p>

                        <Button key={"savemapping"}
                            className={`savemapping ${loading && "disabled"}`}
                            size="btn--small"
                            type="btn--primary-ghost"
                            onClick={this.saveMapping}>Save</Button>
                    </div>

                    <Table key={"mappingtable"}
                        loading={this.state.loading}
                        sorted={this.state.sortOptions}
                        onSortedChange={val => { this.setState({ sortOptions: val }) }}
                        loadingText={this.state.loadingText}
                        className="-striped -highlight"
                        noDataText="No Mapping Found."
                        data={this.state.mappingData}
                        columns={tableColumns}
                    />
                </div>
            </div>
        )
    }
}

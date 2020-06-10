import React from 'react'
import { Switch, Table, Button, Icon } from 'blueprint-react';
import { toast } from 'react-toastify';
import { QUERY_URL, getCookie, DEV_TOKEN, URL_TOKEN } from '../../constants.js';
import 'react-toastify/dist/ReactToastify.css';
import './consulmapping.css';
// import './style.css'

export default class CONSUL_Container extends React.Component {
    constructor(props) {
        super(props);
        console.log("cONSUL container; props", this.props); //datacenterName & tenantName

        this.xhrMapping = new XMLHttpRequest();
        this.getStaticData = this.getStaticData.bind(this);
        this.fetchMappingData = this.fetchMappingData.bind(this);
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
        // this.getStaticData();
        this.fetchMappingData();
    }

    saveMapping() {
        let thiss = this;
        this.setState({ loading: true, loadingText: "Saving..." }, function () {

            // setTimeout(() => {
            //     thiss.setState({
            //         loading: false
            //     })
            //     toast.success("Saved successfully", {
            //         position: toast.POSITION.TOP_CENTER
            //     });
            //     thiss.props.onClose(); // close the mapping screen on successfull save

            // }, 2000);

            try {
                let xhrMapping = thiss.xhrMapping;

                let mappingList = JSON.stringify(thiss.state.mappingData);
                let payload = { query: 'query{SaveMapping(datacenter:"' + thiss.props.datacenterName + '",tn:"' + thiss.props.tenantName + '",data:"' + mappingList.replace(/"/g, '\'') + '"){savemapping}}' }

                xhrMapping.open("POST", QUERY_URL, true);
                xhrMapping.setRequestHeader("Content-type", "application/json");
                window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
                window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
                xhrMapping.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
                xhrMapping.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);

                xhrMapping.onreadystatechange = function () {
                    if (xhrMapping.readyState == 4 && xhrMapping.status == 200) {

                        let json = JSON.parse(xhrMapping.responseText);
                        console.log("save mapping response ", json);

                        if ('errors' in json) {
                            toast.error("Could not Fetch. The query may be invalid.", {
                                position: toast.POSITION.TOP_CENTER
                            });
                        }
                        else if ('savemapping' in json.data.SaveMapping) {
                            let resp = JSON.parse(json.data.SaveMapping.savemapping);
                            console.log("save mapping ", resp);

                            if (resp.status_code == 200) {
                                toast.success("Saved successfully", {
                                    position: toast.POSITION.TOP_CENTER
                                });
                                thiss.props.onClose(); // close the mapping screen on successfull save
                            }
                            else if (resp.status_code == 300) {
                                try {
                                    toast.error(resp.message, {
                                        position: toast.POSITION.TOP_CENTER
                                    });
                                } catch (e) {
                                    console.log("message error", e)
                                }
                            }
                            else {
                                console.log("ERROR Revert changes----");
                                console.error("Invalid status code");
                            }
                        }
                        else {
                            toast.error("Something went wrong!", {
                                position: toast.POSITION.TOP_CENTER
                            });
                            console.error("mappingsave: response structure invalid")
                        }

                        thiss.setState({
                            loading: false
                        })
                    }
                    else {
                        console.log("ERROR Revert changes----");
                    }
                }
                xhrMapping.send(JSON.stringify(payload));
            }
            catch (e) {
                console.error("Error api savemapping", e);
            }
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

    fetchMappingData() {
        let thiss = this;
        let { tenantName, datacenterName } = this.props;
        let payload = { query: 'query{Mapping(tn:"' + tenantName + '",datacenter:"' + datacenterName + '"){mappings}}' }

        let xhrMapping = this.xhrMapping;
        try {
            xhrMapping.open("POST", QUERY_URL, true);
            xhrMapping.setRequestHeader("Content-type", "application/json");
            window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
            window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
            xhrMapping.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhrMapping.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhrMapping.onreadystatechange = function () {
                console.log("chr== state ", xhrMapping.readyState);

                if (xhrMapping.readyState == 4 && xhrMapping.status == 200) {
                    let checkData = JSON.parse(xhrMapping.responseText);
                    let mappingResonse = JSON.parse(checkData.data.Mapping.mappings);

                    if (parseInt(mappingResonse.status_code) === 200) {

                        if (!Array.isArray(mappingResonse.payload)) {
                            toast.error("Payload format Invalid", {
                                position: toast.POSITION.TOP_CENTER
                            });
                        } else {
                            let totalEnabled = 0;
                            thiss.setState({ mappingData: mappingResonse.payload })
                            mappingResonse.payload.forEach(function (elem) {
                                totalEnabled += elem.enabled ? 1 : 0;
                            })
                            thiss.setState({ totalEnabled });
                        }

                    } else if (parseInt(mappingResonse.status_code) === 300) {
                        try {
                            toast.error(mappingResonse.message, {
                                position: toast.POSITION.TOP_CENTER
                            });
                        } catch (e) {
                            console.log("message error", e)
                        }
                    } else {
                        toast.error("Something went wrong", {
                            position: toast.POSITION.TOP_CENTER
                        });
                    }
                    thiss.setState({ loading: false });
                }
                else {
                    console.log("Not fetching");
                }

            }
            xhrMapping.send(JSON.stringify(payload));
        }
        catch (e) {
            console.error('Error getting agents', e);
        }
    }

    handleSwitchChange(index) {
        // let data = this.state.mappingData;
        let { totalEnabled, mappingData } = this.state;

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
            Header: 'Map',
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

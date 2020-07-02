import React from 'react';
import { BrowserRouter as Router, Link } from 'react-router-dom';
import { Loader, Select, Button } from 'blueprint-react';
import { ToastContainer, toast } from 'react-toastify';
import Mapping from "./Mapping/Mapping.js";
import Agent from "./Agent/index.js";
import Modal from "./commonComponent/Modal.js";
import { PROFILE_NAME, getCookie, QUERY_URL, READ_DATACENTER_QUERY, POST_TENANT_QUERY, AGENTS, URL_TOKEN, DEV_TOKEN, INTERVAL_API_CALL } from "../constants.js";
import Container from "./Container"
import 'react-toastify/dist/ReactToastify.css';
import './style.css'

// const dummyItems = [{
//     'datacenter': 'dc1',
//     'status': true
// }, {
//     'datacenter': 'dc2',
//     'status': true
// }]

function toOperationalRedirect(dc, tn) {
    return `/toOperational?${PROFILE_NAME}=` + encodeURIComponent(dc) + "&tn=" + encodeURIComponent(tn);
}

function ToMappingRedirect(dc, tn) {
    return `/toMapping?${PROFILE_NAME}=` + encodeURIComponent(dc) + "&tn=" + encodeURIComponent(tn);
}

// const dummylist = [
//     { "protocol": "http", "ip": "10.0.0.0", "port": 8050, "token": "lnfeialilsacirvjlnlaial", "status": true, "datacenter": "datacenter1" },
//     { "protocol": "https", "ip": "10.0.0.1", "port": 8051, "token": "lnfeialilsacirvjlglaial", "status": false, "datacenter": "datacenter1" },
//     { "protocol": "http", "ip": "10.0.0.2", "port": 8051, "token": "lnfeialilsacirvjhnlaial", "status": true, "datacenter": "datacenter2" }
// ]

export default class App extends React.Component {
    constructor(props) {
        super(props);
        // // Fetching TenantName 'tn' from url
        this.tenantName = null;
        this.xhrCred = new XMLHttpRequest();
        try {
            const rx = /Tenants:(.*)\|/g;
            const topUrl = window.top.location;
            const tenantNames = rx.exec(topUrl);
            this.tenantName = tenantNames[1];
            console.log("Tenant name", this.tenantName);
        } catch (err) {
            console.error("error in getting tenants ", err);
        }

        this.intervalCall = null;

        // getting pathname for route
        let pathname = window.location.pathname;
        pathname = pathname.split("/");
        pathname.pop();
        this.pathname = pathname.join("/");

        this.notify = this.notify.bind(this);
        this.setDetails = this.setDetails.bind(this);
        this.readDatacenter = this.readDatacenter.bind(this);
        this.readDcCall = this.readDcCall.bind(this);
        this.postTenant = this.postTenant.bind(this);
        this.handleAgent = this.handleAgent.bind(this);
        this.handleMapping = this.handleMapping.bind(this);
        this.setSidebar = this.setSidebar.bind(this);
        this.handleSelectChange = this.handleSelectChange.bind(this);
        this.handlePollingIntervalPopUp = this.handlePollingIntervalPopUp.bind(this);
        this.state = {
            agentPopup: false,
            pollingIntervalPopup: false,
            mappingDcname: undefined,
            mappingPopup: false,
            items: [
                { label: AGENTS , action: this.handleAgent },
                { label: "Polling interval", action: this.handlePollingIntervalPopUp }
            ],
            pollingIntervalOptions : [
                { label: 2, value: 2, selected: true },
                { label: 3, value: 3,  selected: false },
                { label: 4, value: 4,  selected: false },
                { label: 5, value: 5,  selected: false },
                { label: 6, value: 6,  selected: false },
                { label: 7, value: 7,  selected: false },
                { label: 8, value: 8,  selected: false },
                { label: 9, value: 9,  selected: false },
                { label: 10, value: 10,  selected: false },
            ],
            selectedPollingInterval : 2,
            details: [],
            tenantApiCallCnt: 2, // indicates no of time "PostTenant" api could be called.
            sidebarItems: [
                {
                    id: 'dash',
                    icon: "icon-call-rate",
                    path: this.pathname + '/',
                    title: 'Dashboard'
                },
                {
                    id: 'Operations',
                    icon: "icon-diagnostics",
                    title: 'Operations',
                    subItems: [
                        {
                            id: 'dc1',
                            content: <Loader></Loader>,
                            title: "dummy"
                        }
                    ]
                },
                {
                    id: 'mapping',
                    icon: "icon-popup-dialogue",
                    title: 'Mapping',
                    subItems: [{
                        id: 'dc1',
                        content: <Loader></Loader>,
                        title: "dummy"
                    }]
                },
                {
                    id: 'Agent',
                    icon: "icon-analysis",
                    title: 'Agent',
                    content: <li class="sidebar__item "> <a className="" aria-current="false" href="javascript:void(0)" onClick={() => this.handleAgent(true)}>
                        <span className="icon-analysis ">
                        </span><span className="qtr-margin-left">Agent</span></a>
                    </li>
                },
                {
                    id: 'serviceint',
                    icon: "icon-admin",
                    path: this.pathname + '/serviceintention',
                    title: 'Service Intentions'
                },
            ]
        }
    }

    componentDidMount() {
        // this.setSidebar(dummyItems);
        this.postTenant();
        this.readDatacenter();
        this.intervalCall  = setInterval(() => this.readDatacenter(), INTERVAL_API_CALL);
    }


    componentWillUnmount() {
        console.log("Component will unmount; intervalcall")
        clearInterval(this.intervalCall); // this clears the interval calls
        this.xhrCred.abort(); // cancel all apis
    }

    shouldComponentUpdate(nextProps, nextState){
        console.log("In should component Update")
        console.log(_.isEqual(this.state.details, nextState.details))
        if(_.isEqual(this.state, nextState)){
            return false
        }
        return true
    }

    readDatacenter() {
        let thiss = this;
        this.setState({ readDatacenterLoading: true }, function () {
            console.log("LOading----")
            thiss.readDcCall();
        })
    }


    handleSelectChange(selected, options) {
        this.setState({
            selectedPollingInterval: selected[0].value,
            pollingIntervalOptions: options
        })
    }

    setSidebar(details = this.state.details) {
        let thiss = this;
        let sidebarItems = [...this.state.sidebarItems];

        let ifAnyDCconnected = false;
        details.some(data =>{
            ifAnyDCconnected = ifAnyDCconnected || data.status
            return data.status;
        })

        // filter out and show 
        function datacenterSubitem(pageind) {
            // let thiss= this;
            // if no datacenters
            if (details.length === 0 || !ifAnyDCconnected) {
                return ["No Datacenter found"].map(function (elem) {
                    return {
                        id: 'dc0',
                        content:
                            <li className={"sidebar__item dc-item"} >
                                <a aria-current="false" href="javascript:void(0)">
                                    <span className="qtr-margin-left">{elem}</span>
                                </a>
                            </li>,
                        title: elem["datacenter"]
                    }
                })
            }

            // if datacenter exist
            return details.filter(function (elem) {
                let datacenterName = elem['datacenter'];
                if (!datacenterName || datacenterName === "-") {
                    return false; // skips where datacenter is not given
                }
                return true;
            }).map(function (elem, ind) {
                // let toLocation = (pageind === 1) ? treeRedirect(elem["datacenter"], thiss.tenantName) : mappingRedirect(elem["datacenter"], thiss.tenantName);
                let toLocation = (pageind === 1) ? toOperationalRedirect(elem["datacenter"], thiss.tenantName) : null;
                return {
                    id: 'dc1' + ind,
                    content: <li className={"sidebar__item dc-item"} >
                        {(pageind === 2) ? (
                        <a className="" aria-current="false" href="javascript:void(0)" onClick={() => thiss.handleMapping(true, elem["datacenter"]) }>
                            <span className={`health-bullet ${elem.status ? 'healthy' : 'dead'}`}></span>
                            <span className="qtr-margin-left">{elem["datacenter"]}</span>
                        </a>) : (
                            <Link to={thiss.pathname + toLocation}>
                                <span className={`health-bullet ${elem.status ? 'healthy' : 'dead'}`}></span>
                                <span className="qtr-margin-left">{elem["datacenter"]}</span>
                            </Link>) }
                        
                    </li>,
                    title: elem["datacenter"]
                }
            })
        }

        try {
            delete sidebarItems[1].content;
            sidebarItems[1].subItems = datacenterSubitem(1) // for Operations

            delete sidebarItems[2].content;
            sidebarItems[2].subItems = datacenterSubitem(2) // for mapping

        } catch (err) {
            console.log("setsidebar err ", err);
        }

        this.setState({ details, sidebarItems })
    }

    setDetails(details) {
        // this.setState({
        //     details
        // })
        this.setSidebar(details);
    }

    notify(message, isSuccess = false, isWarning = false) {
        isWarning ? toast.warn(message, {
            position: toast.POSITION.BOTTOM_CENTER
        }) :
            isSuccess ? toast.success(message, {
                position: toast.POSITION.BOTTOM_CENTER
            }) :
                toast.error(message, {
                    position: toast.POSITION.BOTTOM_CENTER
                });
    }

    handleAgent(agentPopup = true) {
        this.setState({ agentPopup })
    }

    handleMapping(mappingPopup = true, mappingDcname=undefined) {
        this.setState({ mappingPopup, mappingDcname  })
    }

    handlePollingIntervalPopUp(pollingIntervalPopup = true){
        this.setState({ pollingIntervalPopup })
    }

    postTenant() {
        let thiss = this;
        let { tenantApiCallCnt } = this.state;
        if (!this.tenantName && tenantApiCallCnt <= 0) {
            console.log("Error: didnt receive tenantname or trial already done");
            return;
        }
        let payload = POST_TENANT_QUERY(this.tenantName)
        let xhrPostTenant = this.xhrCred;
        try {
            xhrPostTenant.open("POST", QUERY_URL, true);
            xhrPostTenant.setRequestHeader("Content-type", "application/json");
            window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
            window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
            xhrPostTenant.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhrPostTenant.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhrPostTenant.onreadystatechange = function () {

                if (xhrPostTenant.readyState == 4 && xhrPostTenant.status == 200) {
                    let responsejson = JSON.parse(xhrPostTenant.responseText);

                    let datacenterData = JSON.parse(responsejson.data.PostTenant.tenant);

                    if (parseInt(datacenterData.status_code) === 200) {
                        console.log("Tenant posted successfully")
                    } else if (parseInt(datacenterData.status_code) === 300) {
                        thiss.setState({ tenantApiCallCnt: tenantApiCallCnt - 1 }, function () {
                            thiss.postTenant();
                        })
                    }
                }
            }
            xhrPostTenant.send(JSON.stringify(payload));
        }
        catch (e) {
            // thiss.notify("Error while posting tenant")
            console.error('Error getting agents', e);
        }
    }

    readDcCall() {
        let thiss = this;
        let xhrReadDc = this.xhrCred;
        try {
            xhrReadDc.open("POST", QUERY_URL, true);
            xhrReadDc.setRequestHeader("Content-type", "application/json");
            window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
            window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
            xhrReadDc.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhrReadDc.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhrReadDc.onreadystatechange = function () {

                if (xhrReadDc.readyState == 4 && xhrReadDc.status == 200) {
                    let checkData = JSON.parse(xhrReadDc.responseText);
            
                    let datacenterData = JSON.parse(checkData.data.GetDatacenters.datacenters);

                    if (parseInt(datacenterData.status_code) === 200) {
                        thiss.setDetails(datacenterData.payload);
                    } else if (parseInt(datacenterData.status_code) === 300) {
                        try {
                            thiss.notify(datacenterData.message)
                        } catch (e) {
                            console.log("message error", e)
                        }
                    }
                    // thiss.setState({ readDatacenterLoading: false });
                }
                else {
                    console.log("Not fetching");
                }
            }
            xhrReadDc.send(JSON.stringify(READ_DATACENTER_QUERY));
        }
        catch (e) {
            thiss.notify("Error while fetching agent information please refresh")
            console.error('Error getting agents', e);
        }

    }

    render() {


        return (
            <Router>
                <div>
                    <ToastContainer />
                    {/* {this.state.agentPopup && <Redirect to="/agent" />} */}
                    <Modal isOpen={this.state.pollingIntervalPopup} title="Configure polling interval" onClose={()=>{this.handlePollingIntervalPopUp(false)} }>

                        <div className="polling-interval">
                            <div className="panel">
                                <form>
                                    <div className="integration-form">
                                        <Select items={this.state.pollingIntervalOptions} onChange={this.handleSelectChange} label={"Select polling interval (in minutes)"} />
                                        <div className="form-action-buttons">
                                            <Button key={"configurePollingInterval"}
                                                    size="btn--small"
                                                    type="btn--primary"
                                                    onClick={()=>{console.log("Selected polling interval: ", this.state.selectedPollingInterval )}}
                                            >Save</Button>
                                        </div>
                                    </div>
                                </form></div>
                        </div>
                    </Modal>
                    {this.state.mappingPopup && <Mapping handleMapping={this.handleMapping} mappingDcname={this.state.mappingDcname} tenantName={this.tenantName} />}
                    {this.state.agentPopup && <Agent updateDetails={this.readDatacenter} handleAgent={this.handleAgent} />}
                    {this.state.agentPopup || this.state.mappingPopup?null: <Container tenantName={this.tenantName} items={this.state.items} sidebarItems={this.state.sidebarItems} detailsItem={this.state.details} />}
                </div >
            </Router>
        );
    }
}



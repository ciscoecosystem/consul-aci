import React from 'react';
import { BrowserRouter as Router, Link } from 'react-router-dom';
import { Loader } from 'blueprint-react';
import { ToastContainer, toast } from 'react-toastify';
import Agent from "./Agent/index.js"
import { PROFILE_NAME, getCookie, QUERY_URL, READ_DATACENTER_QUERY, POST_TENANT_QUERY } from "../constants.js";
import Container from "./Container"
import 'react-toastify/dist/ReactToastify.css';
import './style.css'

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
// const dummyredirect = `/tree.html?${PROFILE_NAME}=` + encodeURIComponent("cisco-ecosystem-internal-new") + "&tn=" + encodeURIComponent("AppDynamics");

export default class App extends React.Component {
    constructor(props) {
        super(props);
        // // Fetching TenantName 'tn' from url
        this.tenantName = null;
        try {
            const rx = /Tenants:(.*)\|/g;
            const topUrl = window.top.location;
            const tenantNames = rx.exec(topUrl);
            this.tenantName = tenantNames[1];
            console.log("Tenant name", this.tenantName);
        } catch (err) {
            console.error("error in getting tenants ", err);
        }

        console.log("Pathname ", window.location);
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
        this.handleAgent = this.handleAgent.bind(this)
        this.setSidebar = this.setSidebar.bind(this);
        this.state = {
            agentPopup: false,
            items: [
                { label: "Agents", action: this.handleAgent },
                { label: "Polling interval", action: function () { console.log("polling interval") } }
            ],
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
                    id: 'Operational',
                    icon: "icon-diagnostics",
                    title: 'Operational',
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
                }
            ],
            readDatacenterLoading: true
        }
    }

    componentDidMount() {
        this.postTenant();
        this.readDatacenter();
    }

    readDatacenter() {
        let thiss = this;
        this.setState({ readDatacenterLoading: true }, function () {
            console.log("LOading----")
            thiss.readDcCall();
        })
    }

    setSidebar(details = this.state.details) {
        let thiss = this;
        let sidebarItems = [...this.state.sidebarItems];

        // filter out and show 
        function datacenterSubitem(pageind) {
            // if no datacenters
            if (details.length === 0) {
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
                let toLocation = (pageind === 1) ? toOperationalRedirect(elem["datacenter"], thiss.tenantName) : ToMappingRedirect(elem["datacenter"], thiss.tenantName);
                return {
                    id: 'dc1' + ind,
                    content: <li className={"sidebar__item dc-item"} >
                        <Link to={thiss.pathname + toLocation}>
                            {/* <a className="" aria-current="false" href="javascript:void(0)" onClick={() => window.location.href = toLocation}> */}
                            <span className={`health-bullet ${elem.status ? 'healthy' : 'dead'}`}></span>
                            <span className="qtr-margin-left">{elem["datacenter"]}</span>
                        </Link>
                        {/* </a> */}
                    </li>,
                    title: elem["datacenter"]
                }
            })
        }

        try {
            delete sidebarItems[1].content;
            sidebarItems[1].subItems = datacenterSubitem(1) // for operational

            delete sidebarItems[2].content;
            sidebarItems[2].subItems = datacenterSubitem(2) // for mapping

        } catch (err) {
            console.log("setsidebar err ", err);
        }
        console.log("Setted sidebar ", sidebarItems);
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

    postTenant() {
        let thiss = this;
        let { tenantApiCallCnt } = this.state;
        if (!this.tenantName && tenantApiCallCnt <= 0) {
            console.log("Error: didnt receive tenantname or trial already done");
            return;
        }
        let payload = POST_TENANT_QUERY(this.tenantName)
        let xhrPostTenant = new XMLHttpRequest();
        try {
            xhrPostTenant.open("POST", QUERY_URL, true);
            xhrPostTenant.setRequestHeader("Content-type", "application/json");
            window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token"); // fetch for loginform
            window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken"); // fetch for loginform
            xhrPostTenant.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhrPostTenant.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhrPostTenant.onreadystatechange = function () {
                console.log("xhrPostTenant state ", xhrPostTenant.readyState);

                if (xhrPostTenant.readyState == 4 && xhrPostTenant.status == 200) {
                    let responsejson = JSON.parse(xhrPostTenant.responseText);
                    console.log("Response of dc: ", responsejson);

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
        let xhrReadDc = new XMLHttpRequest();
        try {
            xhrReadDc.open("POST", QUERY_URL, true);
            xhrReadDc.setRequestHeader("Content-type", "application/json");
            window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token"); // fetch for loginform
            window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken"); // fetch for loginform
            xhrReadDc.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhrReadDc.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhrReadDc.onreadystatechange = function () {
                console.log("chr== state ", xhrReadDc.readyState);

                if (xhrReadDc.readyState == 4 && xhrReadDc.status == 200) {
                    let checkData = JSON.parse(xhrReadDc.responseText);
                    console.log("Response of dc: ", checkData);
                    // let datacenterData = JSON.parse(checkData.data.ReadCreds.creds);
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
                    thiss.setState({ readDatacenterLoading: false });
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
        console.log("Appb Render state ", this.state);
        return (
            <Router>
                <div>
                    <ToastContainer />
                    {/* {this.state.agentPopup && <Redirect to="/agent" />} */}
                    {this.state.agentPopup && <Agent updateDetails={this.readDatacenter} handleAgent={this.handleAgent} />}
                    <Container items={this.state.items} sidebarItems={this.state.sidebarItems} />
                </div >
            </Router>
        );
    }
}



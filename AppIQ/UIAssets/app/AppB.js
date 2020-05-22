import React from 'react';
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom';
import { Sidebar, Dropdown, Loader, ButtonGroup, Icon } from 'blueprint-react';
import { ToastContainer, toast } from 'react-toastify';
import Agent from "./Agent/index.js"
import Iframe from 'react-iframe';
import { PROFILE_NAME, getCookie, QUERY_URL, getParamObject } from "../constants.js";
import 'react-toastify/dist/ReactToastify.css';
import './style.css'

function treeRedirect(dc, tn) {
    return `/tree.html?${PROFILE_NAME}=` + encodeURIComponent(dc) + "&tn=" + encodeURIComponent(tn);
}
function detailRedirect(dc, tn) {
    return `/details.html?${PROFILE_NAME}=` + encodeURIComponent(dc) + "&tn=" + encodeURIComponent(tn);
}
function mappingRedirect(dc, tn) {
    return `/mapping.html?${PROFILE_NAME}=` + encodeURIComponent(dc) + "&tn=" + encodeURIComponent(tn);
}

// const dummyredirect = `/tree.html?${PROFILE_NAME}=` + encodeURIComponent("cisco-ecosystem-internal-new") + "&tn=" + encodeURIComponent("AppDynamics");

window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token"); // fetch for loginform
window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken"); // fetch for loginform

export default class AppB extends React.Component {
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
        this.readAgentsCall = this.readAgentsCall.bind(this);
        this.handleAgent = this.handleAgent.bind(this)
        this.setSidebar = this.setSidebar.bind(this);
        this.state = {
            agentPopup: false,
            items: [
                { label: "Agents", action: this.handleAgent },
                { label: "Polling interval", action: function () { console.log("polling interval") } }
            ],
            details: [],
            sidebarItems: [
                {
                    id: 'dash',
                    icon: "icon-call-rate",
                    path: '/',
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
            readAgentLoading: true
        }
    }

    componentDidMount() {
        let thiss = this;
        this.setState({ readAgentLoading: true }, function () {
            console.log("LOading----")
            thiss.readAgentsCall();
        })
    }

    setSidebar(details = this.state.details) {
        let thiss = this;
        let sidebarItems = [...this.state.sidebarItems];

        // filter out and show 
        function datacenterSubitem(pageind) {
            return details.filter(function (elem) {
                let datacenterName = elem['datacenter'];
                if (!datacenterName || datacenterName === "-") {
                    return false; // skips where datacenter is not given
                }
                return true;
            }).map(function (elem, ind) {
                let toLocation = (pageind === 1) ? treeRedirect(elem["datacenter"], thiss.tenantName) : mappingRedirect(elem["datacenter"], thiss.tenantName);
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

    readAgentsCall() {
        let thiss = this;
        const payload = {
            query: `query{
            ReadCreds{creds}
        }`}
        let xhrReadCred = new XMLHttpRequest();
        try {
            xhrReadCred.open("POST", QUERY_URL, true);
            xhrReadCred.setRequestHeader("Content-type", "application/json");
            xhrReadCred.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhrReadCred.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhrReadCred.onreadystatechange = function () {
                console.log("chr== state ", xhrReadCred.readyState);

                if (xhrReadCred.readyState == 4 && xhrReadCred.status == 200) {
                    let checkData = JSON.parse(xhrReadCred.responseText);
                    let credsData = JSON.parse(checkData.data.ReadCreds.creds);

                    if (parseInt(credsData.status_code) === 200) {
                        // thiss.setState({ details: credsData.payload })
                        thiss.setDetails(credsData.payload);
                    } else if (parseInt(credsData.status_code) === 300) {
                        try {
                            thiss.notify(credsData.message)
                        } catch (e) {
                            console.log("message error", e)
                        }
                    }
                }
                else {
                    console.log("Not fetching");
                }
                thiss.setState({ readAgentLoading: false });
            }
            xhrReadCred.send(JSON.stringify(payload));
        }
        catch (e) {
            thiss.notify("Error while fetching agent information please refresh")
            console.error('Error getting agents', e);
        }

    }

    render() {
        let thiss = this;
        console.log("Appb Render state ", this.state);
        return (
            <Router>
                <div>
                    <ToastContainer />
                    {/* {this.state.agentPopup && <Redirect to="/agent" />} */}
                    {this.state.agentPopup && <Agent details={this.state.details} readAgentLoading={this.state.readAgentLoading} setDetails={this.setDetails} handleAgent={this.handleAgent} />}
                    <div className="app-container">
                        <Sidebar title={'Consul'}
                            items={this.state.sidebarItems}
                            theme={Sidebar.THEMES.THEME_TYPE}
                        />

                        <div className="main-content-wrapper">
                            <header className="global-header">
                                <img src="hashicorp-consul.png" style={{ height: "95%" }}></img>
                                <div className="app-title"><h4></h4></div>
                                <div className="header-buttons">
                                    <div className="right-menu-icons ">

                                        <Dropdown
                                            label={<span class="icon-help icon-small"></span>}
                                            size="btn--small"
                                            disabled={true}
                                            items={[]}>
                                        </Dropdown>
                                        <Dropdown
                                            label={<span class="icon-cog icon-small"></span>}
                                            size="btn--small"
                                            items={this.state.items}>
                                        </Dropdown>
                                    </div>
                                </div>
                            </header>
                            <main>
                                <div className="routed-content">

                                    <Switch>

                                        <Route exact path="/" >
                                            <div style={{ height: "10%" }}>
                                                Here Goes Dashboard Under construction
                                            </div>
                                        </Route>

                                        <Route path={this.pathname + "/tree.html"} component={function () {
                                            return <ViewComponent pathname={thiss.pathname} />
                                        }} />
                                        <Route path={this.pathname + "/details.html"} component={function () {
                                            return <ViewComponent pathname={thiss.pathname} />
                                        }} />
                                        <Route path={this.pathname + "/mapping.html"} component={MappingViewComponent} />

                                    </Switch>

                                </div>
                            </main>
                        </div>

                    </div>

                </div >
            </Router>
        );
    }
}


class ViewComponent extends React.Component {

    constructor(props) {
        super(props);

        let { search } = window.location;
        let pathname = props.pathname;

        this.paramsObject = getParamObject(window.location); // query string as object

        console.log("extracted paramsObject ", this.paramsObject);

        this.handleIsListView = this.handleIsListView.bind(this);
        this.state = {
            isListView: true, // True signifies detailview and False for Treeview
            treeViewLocation: pathname + "/treeno.html" + search,
            detailViewLocation: pathname + "/details.html" + search,
        }
    }

    handleIsListView(selectedView) {
        this.setState({
            isListView: (selectedView.value === "detail")
        })
    }

    render() {
        let { isListView, treeViewLocation, detailViewLocation } = this.state;
        let toLocation = isListView ? detailViewLocation : treeViewLocation;

        let dcName = this.paramsObject[PROFILE_NAME];

        console.log("Operational view Render", this.state);

        return (<div>
            <div className="page-container-header ">
                <h4>Operational | <span className="dc-title"> {dcName.toUpperCase()} </span> </h4>
                <div className="page-actions">
                    <ButtonGroup type={"btn--primary-ghost"}
                        buttons={[
                            { value: "detail", contents: <Icon type="icon-list-view" /> },
                            { value: "tree", contents: <Icon type="icon-graph" /> }
                        ]}
                        size={"btn--small"}
                        selectedIndex={0}
                        onChange={this.handleIsListView} />
                </div>
            </div>
            <FrameComponent toLocation={toLocation} />}

        </div>)
    }
}

function FrameComponent(props) {
    return <Iframe url={props.toLocation}
        width="450px"
        height="80vh"
        id="myId"
        className="myClassname"
        display="initial"
        position="relative" styles={{ height: "max-content" }} />
}

function MappingViewComponent(props) {
    // let { pathname, search } = props.location;
    // let toLocation = pathname + search;
    // console.log("View tree view ", props.location)
    return (<div>
        Mapping under construction
        {/* <Iframe url={toLocation}
            width="450px"
            height="80vh"
            id="myId"
            className="myClassname"
            display="initial"
            position="relative" styles={{ height: "max-content" }} /> */}
    </div>)
}
import React from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { Sidebar, Dropdown } from 'blueprint-react';
import { ToastContainer } from 'react-toastify';
import Agent from "./Agent/index.js"
import Iframe from 'react-iframe';
import { PROFILE_NAME } from "../constants.js";
import 'react-toastify/dist/ReactToastify.css';
import './style.css'

const treeRedirect = `/tree.html?${PROFILE_NAME}=` + encodeURIComponent("cisco-wordpress") + "&tn=" + encodeURIComponent("AppDynamics");
const detailRedirect = `/details.html?${PROFILE_NAME}=` + encodeURIComponent("cisco-wordpress") + "&tn=" + encodeURIComponent("AppDynamics");
const mappingRedirect = `/mapping.html?${PROFILE_NAME}=` + encodeURIComponent("cisco-wordpress") + "&tn=" + encodeURIComponent("AppDynamics");

const sidebarItems = [
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
                path: treeRedirect,
                title: '10.111.222.12'
            },
            {
                id: 'dc2 details',
                path: detailRedirect,
                title: '10.54.22.11'
            }
        ]
    },
    {
        id: 'mapping',
        icon: "icon-popup-dialogue",
        title: 'Mapping',
        subItems: [
            {
                id: 'dc12',
                path: mappingRedirect,
                title: '10.111.222.12'
            },
            {
                id: 'dc12',
                path: mappingRedirect,
                title: '10.54.22.11'
            }
        ]
    },
    {
        id: 'Agent',
        icon: "icon-analysis",
        title: 'Agent',
        path: '/agent',
    }
]

export default class AppB extends React.Component {
    constructor(props) {
        super(props)
        this.handleAgent = this.handleAgent.bind(this)
        this.state = {
            agentPopup: false,
            items: [
                { label: "Agents", action: this.handleAgent }
            ]
        }
    }

    handleAgent(agentPopup = true) {
        this.setState({ agentPopup })
    }

    render() {
        return (
            <Router>
                <div>
                    <ToastContainer />
                    {this.state.agentPopup && <Redirect to="/agent" />}
                    <div className="app-container">
                        <Sidebar title={'Consul'}
                            items={sidebarItems}
                            theme={Sidebar.THEMES.THEME_TYPE}
                            compressed={true}
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
                                            <div>
                                                Here Goes Dashboard
                                            </div>
                                        </Route>
                                        <Route path="/tree.html" >
                                            <div>
                                                tree view
                                                <Iframe url={treeRedirect}
                                                    width="450px"
                                                    height="80vh"
                                                    id="myId"
                                                    className="myClassname"
                                                    display="initial"
                                                    position="relative" styles={{ height: "max-content" }} />
                                            </div>
                                        </Route>
                                        <Route path="/mapping.html" >
                                            <div>
                                                mapping view
                                                <Iframe url={mappingRedirect}
                                                    width="450px"
                                                    height="80vh"
                                                    id="myId"
                                                    className="myClassname"
                                                    display="initial"
                                                    position="relative" styles={{ height: "max-content" }} />
                                            </div>
                                        </Route>
                                        <Route path="/details.html" >
                                            <div>
                                                detail view
                                                <Iframe url={detailRedirect}
                                                    width="450px"
                                                    height="80vh"
                                                    id="myId"
                                                    className="myClassname"
                                                    display="initial"
                                                    position="relative" styles={{ height: "max-content" }} />
                                            </div>
                                        </Route>

                                        <Route exact path="/agent"><div>

                                            <Agent handleAgent={this.handleAgent} />
                                        </div>
                                        </Route>
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
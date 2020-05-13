import React from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { Sidebar, Dropdown, Screen } from 'blueprint-react';
import Agent from "./Agent/index.js"
import './style.css'

const sidebarItems = [
    {
        id: 'dash',
        icon: "icon-call-rate",
        path: '/dashboard',
        title: 'Dashboard'
    },
    {
        id: 'Operational',
        icon: "icon-diagnostics",
        path: '/',
        title: 'Operational',
        subItems: [
            {
                id: 'dc1',
                path: '',
                title: '10.111.222.12'
            },
            {
                id: 'dc2',
                path: '',
                title: '10.54.22.11'
            }
        ]
    },
    {
        id: 'mapping',
        icon: "icon-popup-dialogue",
        path: '/mapping',
        title: 'Mapping',
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
        console.log("Appb");
        super(props)
        this.handleAgent = this.handleAgent.bind(this)
        this.state = {
            agentPopup: false,
            items: [
                { label: "Agent", action: this.handleAgent }
            ]
        }
    }

    handleAgent(agentPopup = true) {
        this.setState({ agentPopup })
    }

    render() {
        console.log("Render ", this.state, Dropdown);
        return (
            <Router>
                <div>
                {this.state.agentPopup && <Redirect to="/agent"/> }
                    <div className="app-container">
                        <Sidebar title={'Consul'}
                            items={sidebarItems}
                            theme={Sidebar.THEMES.THEME_TYPE}
                        />

                        <div className="main-content-wrapper">
                            <header className="global-header">
                                <img src="hashicorp-consul.png" style={{ height: "95%" }}></img>
                                <div className="app-title"><h4></h4></div>
                                <div className="header-buttons">
                                    <div className="right-menu-icons ">

                                        <Dropdown
                                            label={<span class="icon-cog icon-small"></span>}
                                            style={{ overflow: "visible" }}
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
                                                Here details goes
                                            </div>
                                        </Route>

                                        <Route exact path="/agent"><div>
                                            
                                            <Agent handleAgent={this.handleAgent}/>
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
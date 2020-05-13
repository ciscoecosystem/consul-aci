import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { Sidebar, Dropdown, Screen } from 'blueprint-react';
import './style.css'

const sidebarItems = [
    {
        id: 'dash',
        icon: "icon-check",
        path: '/',
        title: 'Dashboard'
    },
    {
        id: 'Operational',
        icon: "icon-check",
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
        icon: "icon-check",
        path: '/',
        title: 'Mapping',
    },
    {
        id: 'Agent',
        icon: "icon-check",
        title: 'Agent',
        onClick: () => {
            console.log("On click");
        }
    }
]

export default class App extends React.Component {
    constructor(props) {
        super(props)
        this.handleAgent = this.handleAgent.bind(this)
        this.state = {
            agentPopup: false,
            items: [
                { label: "Add Agent", action: this.handleAgent }
            ]
        }
    }

    handleAgent() {
        this.setState({ agentPopup: !this.state.agentPopup })
    }

    render() {
        return (
            <Router>
                <div>

                    <Switch>
                        <Route path="/">
                            <div className="app-container">
                                <Sidebar title={'Consul'}
                                    items={sidebarItems}
                                    theme={Sidebar.THEMES.THEME_TYPE}
                                    className="display-in-blk"
                                // style={{display: "inline-block"}}
                                // expanded={true}
                                />

                                <div id="viewpanel" className="" style={{}}>

                                    <div className="">
                                        {/* <img src="hashicorp-consul.png" style={{ height: "7%" }}></img> */}
                                        {/* TEMPORARY change to index.html */}
                                        {/* <a href="index.html" className="sub-header floal">{this.props.applinktext}</a> */}
                                        {/* <div className="sub-header floal">{"Consul"}</div> */}

                                        <div className="content-header" style={{ float: "right" }}>
                                            <div className="right-menu-icons ">

                                                <Dropdown
                                                    label={<span class="icon-cog icon-small"></span>}
                                                    style={{ overflow: "visible" }}
                                                    size="btn--small"
                                                    items={this.state.items}>
                                                </Dropdown>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                {(this.state.agentPopup) &&
                                    <Screen hideFooter={true} title={"Agent list"} allowMinimize={false} onClose={this.handleAgent}>
                                    </Screen>}
                            </div>


                        </Route>

                        <Route exact path="/agent">
                            <div> yooo hooooooooooooooooooooooooooo
                            <Screen hideFooter={true} title={"Agent list"} allowMinimize={false} onClose={() => { console.log("close") }}>
                            </Screen>
                            </div>
                        </Route>
                    </Switch>
                </div>
            </Router>
        );
    }
}
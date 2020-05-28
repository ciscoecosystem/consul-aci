import React from 'react';
import { Route, Switch, Redirect } from 'react-router-dom';
import { Sidebar, Dropdown, ButtonGroup, Icon } from 'blueprint-react';
import Iframe from 'react-iframe';
import { PROFILE_NAME, getParamObject } from "../constants.js";
import 'react-toastify/dist/ReactToastify.css';
// import './style.css'

export default class Container extends React.Component {
    constructor(props) {
        super(props);

        // getting pathname for route
        let pathname = window.location.pathname;
        pathname = pathname.split("/");
        pathname.pop();
        this.pathname = pathname.join("/");
    }

    render() {
        let thiss = this;
        return (
            <div className="app-container">
                <Sidebar title={'Consul'}
                    items={this.props.sidebarItems}
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
                                    items={this.props.items}>
                                </Dropdown>
                            </div>
                        </div>
                    </header>
                    <main>
                        <div className="routed-content">

                            <Switch>

                                <Route exact path="/" >
                                    <div style={{ height: "10%" }}>
                                        Dashboard Under construction
                                </div>
                                </Route>

                                <Route path={this.pathname + "/toOperational"} component={function () {
                                    // this results into unmounting of operational view if already in place
                                    return <Redirect to={thiss.pathname + "/operational" + window.location.search} />
                                }} />
                                <Route path={this.pathname + "/toMapping"} component={function () {
                                    // this results into unmounting of operational view if already in place
                                    return <Redirect to={thiss.pathname + "/mapping" + window.location.search} />
                                }} />

                                <Route path={this.pathname + "/operational"} component={function () {
                                    return <OperationalViewComponent pathname={thiss.pathname} />
                                }} />
                                <Route path={this.pathname + "/mapping"} component={function () {
                                    return <MappingViewComponent pathname={thiss.pathname} />
                                }} />

                            </Switch>

                        </div>
                    </main>
                </div>

            </div>

        )
    }
}



class OperationalViewComponent extends React.Component {

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
    componentWillMount() {
        console.log("Mounting operational view")
    }
    componentWillUnmount() {
        console.log("Unmounting Operational view")
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


function MappingViewComponent(props) {
    let { search } = window.location;
    let pathname = props.pathname;

    let paramsObject = getParamObject(window.location); // query string as object
    let dcName = paramsObject[PROFILE_NAME];

    let toLocation = pathname + "/mapping.html" + search;
    // console.log("View tree view ", props.location)
    return (<div>
        <div className="page-container-header ">
            <h4>Mapping | <span className="dc-title"> {dcName.toUpperCase()}  </span> </h4>
        </div>
        <FrameComponent toLocation={toLocation} />
    </div>)
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
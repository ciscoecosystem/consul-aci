import React from 'react';
import { Route, Switch, Redirect } from 'react-router-dom';
import { Sidebar,  ButtonGroup, Icon, Screen, Button, Dropdown, Carousel } from 'blueprint-react';
import Iframe from 'react-iframe';
import { PROFILE_NAME, getParamObject } from "../constants.js";
import Modal from './commonComponent/Modal.js';
import Dashboard from './Dashboard/Dashboard.js';
import 'react-toastify/dist/ReactToastify.css';
// import qsimg from './Asset/qs-details.png';

// const img2 = require("./Asset/qs-details.png");
// const img3 = "./public/Asset/qs-details.png"
const QSIMG_PATH = "./public/Asset/qs-details.png";

export default class Container extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            showHelpPopUpIsOpen: false,
            images:[
                QSIMG_PATH
            ]
        }
        // getting pathname for route
        let pathname = window.location.pathname;
        pathname = pathname.split("/");
        pathname.pop();
        this.pathname = pathname.join("/");
        this.closeHelpPopUp = this.closeHelpPopUp.bind(this)
        this.openHelpPopUp = this.openHelpPopUp.bind(this)
        console.log("container constructor");
        // <Redirect to={this.pathname + "/" + window.location.search} />
    }
    
    closeHelpPopUp() {
        this.setState({ showHelpPopUpIsOpen: false })
    }

    openHelpPopUp(){
        this.setState({showHelpPopUpIsOpen: true})
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

                                <Button size="btn--small" onClick={this.openHelpPopUp}>
                                    <span class="icon-help icon-small"></span>
                                </Button>
                                <Dropdown
                                    label={<span class="icon-cog icon-small"></span>}
                                    size="btn--small"
                                    items={this.props.items}
                                    type="dropdown--type-button">
                                </Dropdown>
                            </div>
                        </div>
                    </header>
                    <main>
                        <Modal className="help-popup" isOpen={this.state.showHelpPopUpIsOpen} title="Quickstart guide" onClose={this.closeHelpPopUp}>
                                <div className="panel">
                                    <div className="wrapper" >
                                    {/* <img src={QSIMG_PATH} className="slid-img" alt="help"/> */}
                                    {/* {this.state.images.map(item=><img src={item} className="slid-img" alt="help"/>)} */}
                                        <Carousel>
                                            {this.state.images.map(item=><img src={item} className="slid-img" alt="help"/>)}
                                        </Carousel>
                                    </div>
                                </div>
                        </Modal>
                        
                        <div className="routed-content">

                            <Switch>

                                <Route exact path={[this.pathname + "/", this.pathname + "/index.html"]} component={() => {
                                    return <div style={{ height: "100%" }}>
                                        <Dashboard tenantName={this.props.tenantName}/>
                                    </div>
                                }} />

                                <Route exact path={this.pathname + "/serviceintention"} component={function () {
                                    return <div style={{ height: "fit-content", margin: "30px", background: "white", padding: "20px" }}>
                                        <h5 style={{ textAlign: "center" }}>Network Middleware Automation is under construction</h5>
                                        <ul style={{listStyle:"upper-alpha", padding:"20px"}}>
                                            <li>Service mesh defined service-to-service communication topology overlay with ACI logical and fabric constructs </li>
                                            <li>Verification of ACI policy (contract and filter) to support Consul service mesh intentions</li>
                                            <li>ACI policy (contract and filter) recommendation and creation based on Consul service mesh intentions</li>
                                        </ul>
                                    </div>
                                }} />

                                <Route path={this.pathname + "/toOperational"} component={function () {
                                    // this results into unmounting of operational view if already in place
                                    return <Redirect to={thiss.pathname + "/operational" + window.location.search} />
                                }} />

                                <Route path={this.pathname + "/operational"} component={function () {
                                    return <OperationalViewComponent pathname={thiss.pathname} />
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
            treeViewLocation: pathname + "/tree.html" + search,
            detailViewLocation: pathname + "/details.html" + search,
        }
    }

    handleIsListView(selectedView) {
        this.setState({
            isListView: (selectedView.value === "detail")
        })
    }
    componentWillMount() {
        console.log("Mounting Operations view")
    }
    componentWillUnmount() {
        console.log("Unmounting Operations view")
    }

    render() {
        let { isListView, treeViewLocation, detailViewLocation } = this.state;
        let toLocation = isListView ? detailViewLocation : treeViewLocation;

        let dcName = this.paramsObject[PROFILE_NAME];

        console.log("Operations view Render", this.state);

        return (<div>
            <div className="page-container-header ">
                <h4>Operations | <span className="dc-title"> {dcName.toUpperCase()} </span> </h4>
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
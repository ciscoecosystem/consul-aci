import React from 'react';
import { render } from 'react-dom';
import { ToastContainer, toast } from 'react-toastify';
import { Loader } from "blueprint-react"
import TestComponent from './TestComponent.js';
// import Header from './Header.js'
import { TREE_VIEW_QUERY_PAYLOAD, PROFILE_NAME, INTERVAL_API_CALL, QUERY_URL, getCookie, DEV_TOKEN, URL_TOKEN } from "../../../../../constants.js"
import 'react-toastify/dist/ReactToastify.css';
var key = 0;


var headerInstanceName;

function loadingBoxShow() {
    let health = document.getElementById("health-indicators")
    if (health) {
        health.style.display = "none";
    }
    document.getElementById("loading-box").style.display = "block";
}

function loadingBoxHide() {
    let health = document.getElementById("health-indicators")
    if (health) {
        health.style.display = "block";
    }
    document.getElementById("loading-box").style.display = "none";
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            result: {},
            treedata: undefined,

            detailsPane: {
                visible: false,
                data: {}
            },

            detailsPage: {
                visible: false,
                data: {}
            },
            treeApiLoading: false,
            initialTreeRender: 0,
            treeTranslate: { x: 400, y: -60 },
            treeScale: 1
        }

        this.reload = this.reload.bind(this);
        this.getData = this.getData.bind(this);
        this.notify = this.notify.bind(this);
        // this.getStaticData = this.getStaticData.bind(this);
        this.toggleDetailsPane = this.toggleDetailsPane.bind(this);
        this.toggleeDetailsPage = this.toggleeDetailsPage.bind(this);
        this.handleTransitionTree = this.handleTransitionTree.bind(this);
    }

    componentWillMount() {
        document.body.style.overflow = "scroll"
    }

    componentDidMount() {
        this.getData();
        // this.getStaticData();
        setInterval(this.getData, INTERVAL_API_CALL);
    }

    reload() {
        // alert("Reloading");
        loadingBoxShow();
        this.handleTransitionTree([400, -60], 1);
        this.setState({ initialTreeRender: 0 }, function () {
            this.getData(true);
            // this.getStaticData(true);
        })
    }

    notify(message, isSuccess = false, isWarning = false) {
        isWarning ? toast.warn(message, {
            position: toast.POSITION.TOP_CENTER
        }) :
            isSuccess ? toast.success(message, {
                position: toast.POSITION.TOP_CENTER
            }) :
                toast.error(message, {
                    position: toast.POSITION.TOP_CENTER
                });
    }

    toggleDetailsPane(nodeData = undefined) { // if no argument that means details pane to be closed
        let isOpen = (nodeData !== undefined);
        this.setState({
            detailsPane: {
                visible: isOpen,
                data: isOpen ? nodeData : {}
            }
        })
    }

    toggleeDetailsPage(nodeData = undefined) { // if no argument that means details pane to be closed
        let isOpen = (nodeData !== undefined);
        this.setState({
            detailsPage: {
                visible: isOpen,
                data: isOpen ? nodeData : {}
            }
        })
    }

    handleTransitionTree(translate, treeScale) {
        this.setState({
            treeTranslate: { x: translate[0], y: translate[1] },
            treeScale
        })
    }

    /** To run in local 
    getStaticData(fullyReload = false) {
        let thiss = this;
        let { detailsPage, detailsPane, treeApiLoading } = this.state;

        if (detailsPage.visible || detailsPane.visible) return;

        let xhr = new XMLHttpRequest();

        try {
            console.log("opening post")
            //   xhr.open("POST", QUERY_URL,true);
            xhr.open('GET', 'treeData.json', true)
            xhr.responseType = 'json';
            xhr.setRequestHeader("Content-type", "application/json");

            xhr.onreadystatechange = function () {
                console.log("Response ====> ", xhr)
                if (xhr.readyState == 4) {
                    if (xhr.status == 200 || xhr.status == 304) {
                        console.log("In 200 or 304 resposnse")
                        console.log("Tree data", xhr.response, typeof (xhr.response));
                        let treedata = xhr.response;

                        if ((JSON.stringify(thiss.state.treedata) !== JSON.stringify(treedata) || fullyReload) && !treeApiLoading) {
                            console.log("Tree data taking ");
                            thiss.setState({ treeApiLoading: true }, function () {
                                thiss.setState({ treedata, treeApiLoading: false, initialTreeRender: thiss.state.initialTreeRender + 1 });
                            })
                        } else {
                            console.log("Didnt change as before");
                        }

                    }
                    else {
                        // Status code of XHR request not 200
                        console.log("Api fail");
                    }
                }
            }
            console.log("sending post")
            xhr.send(null);
        }
        catch (except) {
            thiss.setState({ treeApiLoading: false })
            console.log("Cannot fetch data to fetch Tree data.", except);
        }
    }
*/

    getData(fullyReload = false) {
        let { detailsPage, detailsPane, treeApiLoading } = this.state;

        if (detailsPage.visible || detailsPane.visible) return; // IF any popup is open dont call api

        let thiss = this;
        var urlToParse = location.search;
        let urlParams = {};
        urlToParse.replace(
            new RegExp("([^?=&]+)(=([^&]*))?", "g"),
            function ($0, $1, $2, $3) {
                urlParams[$1] = $3;
            }
        );
        let result = urlParams;

        try {
            result && this.setState({ result });
        } catch (err) {
            console.error("set state error", err);
        }

        let payload = TREE_VIEW_QUERY_PAYLOAD(result['tn'], result[PROFILE_NAME])
        let xhr = new XMLHttpRequest();

        try {
            console.log("opening post")
            xhr.open("POST", QUERY_URL, true);
            xhr.setRequestHeader("Content-type", "application/json");
            window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for operational
            window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for operational
            xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            console.log("header set")
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4) {
                    if (xhr.status == 200) {
                        let json = JSON.parse(xhr.responseText);
                        if ('errors' in json) {
                            // Error related to query
                            try {
                            thiss.notify(JSON.stringify(json.errors));
                            } catch(err){
                                console.log("Error ", err);
                            }
                            // localStorage.setItem('message', JSON.stringify(json.errors));
                            // window.location.href = "index.html?gqlerror=1";
                        }
                        else {
                            // Response successful
                            const response = JSON.parse(json.data.OperationalTree.response);
                            if (response.status_code != "200") {
                                // Problem with backend fetching data
                                // const message = {
                                //     "errors": [{
                                //         "message": response.message
                                //     }]
                                // }
                                thiss.notify(response.message);
                                // localStorage.setItem('message', JSON.stringify(message.errors));
                                // window.location.href = "index.html?gqlerror=1";
                            }
                            else {
                                // Success
                                var treedata_raw = JSON.parse(json.data.OperationalTree.response).payload;
                                headerInstanceName = JSON.parse(json.data.OperationalTree.response).agentIP; //  CONSUL : change from instanceName to agentIp

                                if ((JSON.stringify(thiss.state.treedata) !== JSON.stringify(JSON.parse(treedata_raw)) || fullyReload)
                                    && !treeApiLoading) {

                                    thiss.setState({ treeApiLoading: true }, function () {
                                        thiss.setState({
                                            treedata: JSON.parse(treedata_raw),
                                            treeApiLoading: false,
                                            initialTreeRender: thiss.state.initialTreeRender + 1
                                        })
                                    })

                                } else {
                                    console.log("Didnt change as before");
                                }
                            }
                        }
                    }
                    else {
                        // Status code of XHR request not 200
                        console.log("Cannot fetch data to fetch Tree data.");
                        // if (typeof message_set !== 'undefined') {
                        //     const message = { "errors": [{ "message": "Error while fetching data for Tree. Status code" + xhr.status }] }
                        //     localStorage.setItem('message', JSON.stringify(message.errors));
                        // }
                        // window.location.href = "index.html?gqlerror=1";
                    }
                }
            }
            console.log("sending post")
            xhr.send(JSON.stringify(payload));
        }
        catch (except) {
            console.error("Cannot fetch tree data", except)
            thiss.notify("Something went wrong.");
            // if (typeof message_set == 'undefined') {
            //     const message = {
            //         "errors": [{
            //             "message": "Error while fetching data for Tree"
            //         }]
            //     }
            //     localStorage.setItem('message', JSON.stringify(message.errors));
            // }
            thiss.setState({ treeApiLoading: false })
            // window.location.href = "index.html?gqlerror=1";
        }
        key = key + 1;
        return true;
    }

    render() {
        let { treedata, treeApiLoading, initialTreeRender, treeTranslate, treeScale } = this.state;
        loadingBoxHide();
        let apptext = " " + this.state.result[PROFILE_NAME]; // CONSUL changes
        let title = " | Operational"

        return (
            <div>
                <ToastContainer />
                {/* <Header text={title} applinktext={apptext} instanceName={headerInstanceName} /> */}
                {(treedata === undefined || treeApiLoading) ? <Loader> loading </Loader> : <TestComponent key={key}
                    detailsPage={this.state.detailsPage}
                    detailsPane={this.state.detailsPane}
                    toggleDetailsPane={this.toggleDetailsPane}
                    toggleeDetailsPage={this.toggleeDetailsPage}
                    data={this.state.treedata}
                    reloadController={this.reload}
                    datacenterName={this.state.result[PROFILE_NAME]}
                    initialTreeRender={initialTreeRender}
                    treeScale={treeScale}
                    treeTranslate={treeTranslate}
                    handleTransitionTree={this.handleTransitionTree} />}
            </div>
        );
    }
}

render(<App />, document.getElementById('app'));


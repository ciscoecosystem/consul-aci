import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';
import DataTable from "./DataTable";
import DetailPanel from "./DetailPanel";
import DetailPage from "./DetailsPage";
import { DC_DETAILS_QUERY_PAYLOAD, QUERY_URL, getCookie, INTERVAL_API_CALL, DEV_TOKEN, URL_TOKEN } from "../../constants.js";
import { toast } from 'react-toastify';
// import { dummyData } from "./dummyData.js";

var params_tn;
var details_raw;

var urlToParse = location.search;
var urlParams = {};
urlToParse.replace(
    new RegExp("([^?=&]+)(=([^&]*))?", "g"),
    function ($0, $1, $2, $3) {
        urlParams[$1] = $3;
    }
);
var result = urlParams;

var headerInstanceName;

class Container extends Component {
    constructor(props) {
        super(props);

        this.reload = this.reload.bind(this);
        this.fetchData = this.fetchData.bind(this);
        this.fetchDataCall = this.fetchDataCall.bind(this);
        // this.staticFetchDataCall = this.staticFetchDataCall.bind(this);

        this.notify = this.notify.bind(this);
        this.setData = this.setData.bind(this);
        this.setSummaryDetail = this.setSummaryDetail.bind(this);
        this.setSummaryIsOpen = this.setSummaryIsOpen.bind(this);

        // params_tn = result['tn'];
        let pathname = window.location.pathname;
        pathname = pathname.split("/");
        pathname.pop();
        this.pathname = pathname.join("/");
        this.state = {
            "data": [],
            loading: false,
            // expanded: {},
            summaryPaneIsOpen: false,
            summaryDetail: {},
            expansionViewOpen: false,
        };

        this.handleBackClick = this.handleBackClick.bind(this);
        // this.CONSUL_setExpand = this.CONSUL_setExpand.bind(this);
        // this.CONSUL_resetExpanded = this.CONSUL_resetExpanded.bind(this);

        setInterval(() => this.fetchData(true), INTERVAL_API_CALL);
    }
    componentDidMount() {
        this.fetchData();
    }

    setSummaryIsOpen(summaryPaneIsOpen = false) {
        this.setState({ summaryPaneIsOpen })
    }

    setSummaryDetail(summaryDetail) {
        this.setState({
            summaryDetail,
            summaryPaneIsOpen: true
        })

    }

    setData(data) {
        data = data.map(elem => {
            let nodeChecksFilter = "";
            let serviceChecksFilter = "";
            let serviceTagFilter = "";

            if (elem.nodeChecks.passing && elem.nodeChecks.passing > 0){
                nodeChecksFilter = "passing";
            }
            if (elem.nodeChecks.warning && elem.nodeChecks.warning > 0){
                nodeChecksFilter += "warning";
            }
            if (elem.nodeChecks.failing && elem.nodeChecks.failing > 0){
                nodeChecksFilter += "critical";
            }

            if (elem.serviceChecks.passing && elem.serviceChecks.passing > 0){
                serviceChecksFilter = "passing";
            }
            if (elem.serviceChecks.warning && elem.serviceChecks.warning > 0){
                serviceChecksFilter += "warning";
            }
            if (elem.serviceChecks.failing && elem.serviceChecks.failing > 0){
                serviceChecksFilter += "critical";
            }

            if (elem.serviceTags && Array.isArray(elem.serviceTags)){
                serviceTagFilter = elem.serviceTags.join("");
            }

            return Object.assign({}, elem, { nodeChecksFilter, serviceChecksFilter, serviceTagFilter });
        })

        this.setState({ data })
    }

    fetchData(dontLoad = false) {
        let { loading } = this.state;
        if (loading === true) return;

        this.setState({ loading: !dontLoad }, () => {
            this.fetchDataCall();
            // this.staticFetchDataCall();
        })
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

    // staticFetchDataCall() {
    //     setTimeout(() => {
    //         console.log("Got data");
    //         this.notify("Fecthed the data");
    //         this.setData(dummyData);
    //         this.setState({
    //             loading: false
    //         })
    //     }, 2000)
    // }

    fetchDataCall() {
        let payload = DC_DETAILS_QUERY_PAYLOAD(this.props.tenantName, this.props.dcName);
        let thiss = this;
        let xhr = new XMLHttpRequest();
        try {
            xhr.open("POST", QUERY_URL, true);
            xhr.setRequestHeader("Content-type", "application/json");
            xhr.setRequestHeader("DevCookie", getCookie(DEV_TOKEN));
            xhr.setRequestHeader("APIC-challenge", getCookie(URL_TOKEN));

            xhr.onreadystatechange = () => {

                console.log("Sending req");
                if (xhr.readyState == 4) {
                    if (xhr.status == 200) {
                        let json = JSON.parse(xhr.responseText);

                        if ("errors" in json) {
                            // Error related to query
                            thiss.notify("Could not Fetch. The query may be invalid.");
                            // window.location.href = "index.html?gqlerror=1";
                        } else {
                            // Response successful
                            let response = JSON.parse(json.data.DetailsFlattened.details)

                            if (response.status_code == "200") {
                                    // Success
                                    headerInstanceName = response.instanceName;
                                    thiss.setData(response.payload)
                                }
                             else if (response.status_code == "300") {
                                // Problem with backend fetching data
                                try {
                                    thiss.setData(response.payload);
                                    thiss.notify(response.message)
                                } catch (e) {
                                    console.log("message error", e)
                                }
                            }
                            thiss.setState({ loading: false })
                        }
                    } else {
                        // Status code of XHR request not 200
                        thiss.notify("Error while fetching data for details.");
                        // window.location.href = "index.html?gqlerror=1";
                    }
                }
            };
            xhr.send(JSON.stringify(payload));
        } catch (except) {
            thiss.notify("Technical glitch.");
            console.log("Error ", except);
            // window.location.href = "index.html?gqlerror=1";
        }
    }

    handleBackClick() {
        // window.location.href = "index.html";
    }


    reload(loading) {
        if (!this.state.loading) {
            if (loading) {
                this.setState({ loading: true })
            }
            this.fetchData();
        }
    }

    render() {
        let { summaryPaneIsOpen, summaryDetail } = this.state;

        return (
            <div>

                <DetailPanel summaryPaneIsOpen={summaryPaneIsOpen}
                    summaryDetail={summaryDetail}
                    title={summaryDetail["endPointName"]}
                    setSummaryIsOpen={this.setSummaryIsOpen}
                    setExpansionViewOpen={()=>{this.setState({expansionViewOpen: true})}}
                />

                {this.state.expansionViewOpen?<div className="detail-expansion"><DetailPage data={summaryDetail} tenantName={this.props.tenantName} dataCenter={this.props.dcName} title={summaryDetail["endPointName"]} closeDetailsPage={()=>{this.setState({expansionViewOpen: false})}}/></div>:null}

                {/* <Header polling={true} text={title} applinktext={apptext} instanceName={headerInstanceName} /> */}
                <div className="scroll" style={{ padding: "0px 14px", marginBottom: "240px" }}>
                    <DataTable
                        loading={this.state.loading}
                        data={this.state.data}
                        onReload={this.reload}
                        setSummaryDetail={this.setSummaryDetail}>
                    </DataTable>
                </div>
                {this.props.isDeleted === true?this.notify("Datacenter has been deleted") || <Redirect to={this.pathname + "/"}></Redirect>:null}
            </div>
        )
    }
}

export default Container

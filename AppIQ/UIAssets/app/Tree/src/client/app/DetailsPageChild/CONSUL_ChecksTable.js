import React, { Component } from "react";
import { Table, Panel, Icon, Label } from "blueprint-react";

import { ToastContainer, toast } from 'react-toastify';
import { INTERVAL_API_CALL, QUERY_URL } from '../../../../../../constants.js';
import 'react-toastify/dist/ReactToastify.css';
import "./styleTabs.css"

const successColor = "#6ebe4a";
const failColor = "#e2231a";
const warningColor = "#f49141";

function getCookieVal(offset) {
    var endstr = document.cookie.indexOf(";", offset);
    if (endstr == -1) {
        endstr = document.cookie.length;
    }
    return unescape(document.cookie.substring(offset, endstr));
}

function getCookie(name) {
    var arg = name + "=";
    var alen = arg.length;
    var clen = document.cookie.length;
    var i = 0;
    var j = 0;
    while (i < clen) {
        j = i + alen;
        if (document.cookie.substring(i, j) == arg) {
            return getCookieVal(j);
        }
        i = document.cookie.indexOf(" ", i) + 1;
        if (i === 0) {
            break;
        }
    }
    return null;
}
window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");

export default class CONSUL_ChecksTable extends Component {
    constructor(props) {
        super(props);

        this.fetchData = this.fetchData.bind(this);
        this.handleError = this.handleError.bind(this);
        this.state = {
            rows: [],
            loading: true,
            expanded: {},
            intervalId: undefined
        };
    }
    handleError(error) {
        console.error(error);
        var errorText = "Error: "
        if (typeof (error) == "object") {
            errorText += JSON.stringify(error);
        }
        else {
            errorText += error
        }
        this.setState({ loading: false });

        toast.error(unescape(errorText), {
            position: toast.POSITION.BOTTOM_CENTER,
            autoClose: 2500
        });
    }
    componentWillMount() {
        if (!this.props.query) {
            this.setState({ loading: false })
        }
        else {
            this.fetchData();
            let intervalId = setInterval(this.fetchData, INTERVAL_API_CALL);
            this.setState({ intervalId })
        }
    }
    componentWillUnmount() {
        clearInterval(this.state.intervalId)
    }
    fetchData() {
        let query = this.props.query;
        let payload = query

        let xhr = new XMLHttpRequest();
        try {
            xhr.open("POST", QUERY_URL, true);
            window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
            window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");
            xhr.setRequestHeader("Content-type", "application/json");
            xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);

            xhr.onreadystatechange = () => {

                console.log("Sending req");
                if (xhr.readyState == 4) {
                    if (xhr.status == 200) {
                        let json = JSON.parse(xhr.responseText);
                        if ("errors" in json) {
                            // Error related to query
                            this.handleError(json.errors[0]["message"] || "Error while fetching data");
                        } else {
                            // Response successful
                            const type = Object.keys(json.data)[0];
                            const listData = Object.keys(json.data[type])[0];
                            const response = JSON.parse(json.data[type][listData]);

                            if (response.status_code != "200") {
                                // Problem with backend fetching data
                                this.handleError(response.message.errors);
                            } else {
                                // Success
                                this.setState({ rows: response.payload });
                                this.setState({ loading: false });
                            }
                        }
                    } else {
                        // Status code of XHR request not 200
                        let jsonError = JSON.parse(xhr.responseText);
                        this.handleError(jsonError.errors[0]["message"]);
                    }
                }
            };
            xhr.send(JSON.stringify(payload));
        } catch (except) {
            this.handleError("Error in API request please check configuration");
            console.log(except);
        }

    }

    CONSUL_handleRowExpanded(newExpanded, index, event) {
        // we override newExpanded, keeping only current selected row expanded
        index = index[0];
        let { expanded } = this.state;
        let newGenExpanded = Object.assign(expanded, { [index]: (expanded[index] === true) ? false : true })
        this.setState({ expanded: newGenExpanded })
    }

    render() {
        let { extraColumn } = this.props;
        const headerColumns = [
            {
                Header: 'Name',
                accessor: "Name", // key for table header
                Cell: row => {
                    let { Name, Status } = row.original;
                    return <div>
                        <span style={{ marginRight: "15px", marginLeft: "5px" }}>
                            {(Status === "passing") && (<span> <Icon size="icon-small" type=" icon-check-square" style={{ color: successColor }}></Icon></span>)}
                            {(Status === "warning") && (<span> <Icon size="icon-small" type=" icon-warning" style={{ color: warningColor }}></Icon></span>)}
                            {(Status === "failing") && (<span> <Icon size="icon-small" type=" icon-exit-contain" style={{ color: failColor }}></Icon></span>)}
                        </span>
                        {Name}
                    </div>
                }
            },
            {
                Header: 'ServiceName',
                accessor: 'ServiceName'
            },
            {
                Header: 'CheckID',
                accessor: 'CheckID'
            },
            {
                Header: 'Type',
                accessor: 'Type'
            },
            {
                Header: 'Notes',
                accessor: 'Notes'
            }
        ]

        if (extraColumn) {
            headerColumns.splice(extraColumn.index, 0, extraColumn.value); // adding extra column at spicified index
        }

        return (
            <Panel style={{ width: "100%" }} border="panel--bordered">
                <ToastContainer></ToastContainer>
                <Table
                    noDataText="No data found"
                    data={this.state.rows}
                    columns={headerColumns}
                    loading={this.state.loading}
                    onPageChange={() => { this.setState({ expanded: {} }) }}
                    expanded={this.state.expanded}
                    onExpandedChange={(newExpanded, index, event) => this.CONSUL_handleRowExpanded(newExpanded, index, event)}
                    SubComponent={row => {
                        let { Output } = row.original;
                        return (<div className="table-cell-output">
                            <div className="d-flex">
                                <div className="cell-label"> Output: </div>
                                <div className="cell-code">
                                    <Label theme={"MEDIUM_GRAYY"} size={"MEDIUM"} border={false}>
                                        <pre>
                                            {Output.split("\n").map(ele => {
                                                return <code>
                                                    {ele}
                                                    <br />
                                                </code>
                                            })}
                                        </pre>
                                    </Label>
                                </div>
                            </div>
                        </div>)
                    }} />

            </Panel>
        );
    }
}   
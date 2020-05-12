import React, { Component } from "react";
import { Table, Panel } from "blueprint-react";
import { ToastContainer, toast } from 'react-toastify';
import {
  TABLE_COLUMNS_AUDIT_LOG,
  TABLE_COLUMNS_EVENTS,
  TABLE_COLUMNS_FAULTS,
  ROWS_FAULTS, TABLE_POLICIES,
  TABLE_OPERATIONAL,
  TABLE_TOEPG,
  TABLE_SUBNETS
} from "./tableHeaders.js";
import { INTERVAL_API_CALL, QUERY_URL, getCookie } from '../../../../../../constants.js';
import 'react-toastify/dist/ReactToastify.css';
import "./styleTabs.css"

window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token"); // fetch for expansion view
window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken"); // fetch for expansion view

export default class DataTable extends Component {
  constructor(props) {
    super(props);
    this.tableHeaders = [
      TABLE_COLUMNS_FAULTS,
      TABLE_COLUMNS_EVENTS,
      TABLE_COLUMNS_AUDIT_LOG,
      TABLE_OPERATIONAL,
      TABLE_POLICIES,
      TABLE_TOEPG,
      TABLE_SUBNETS
    ];
    this.fetchData = this.fetchData.bind(this);
    this.handleError = this.handleError.bind(this);
    this.state = {
      rows: [],
      loading: true,
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
  componentDidMount() {
    if (!this.props.query.param) {
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

    var urlToParse = location.search;
    let urlParams = {};
    urlToParse.replace(new RegExp("([^?=&]+)(=([^&]*))?", "g"), function (
      $0,
      $1,
      $2,
      $3
    ) {
      urlParams[$1] = $3;
    });
    let result = urlParams;

    if (result["tn"] == undefined) {
      this.handleError("Can not find Tanent name");

    }
    else {
      let tanent = "tn-" + result["tn"];
      let query = this.props.query;

      let payload = {
        query:
          "query{" +
          query.type +
          '(dn:"uni/' +
          tanent +
          "/" +
          query.param +
          '")' +
          query.list +
          "}"
      };
      if (this.props.customQuery) {
        let custom = this.props.customQuery;
        payload = {
          query:
            "query{" +
            custom.type +
            '(tn:"' +
            result["tn"] +
            '",ap:"' +
            custom.param.ap +
            '",epg:"' + custom.param.epg +
            '")' +
            custom.list +
            "}"
        }
      }
      let xhrDataTable = new XMLHttpRequest();
      try {
        xhrDataTable.open("POST", QUERY_URL, true);
        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token"); // fetch for expansion
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken"); // fetch for expansion
        xhrDataTable.setRequestHeader("Content-type", "application/json");
        xhrDataTable.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
        xhrDataTable.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);

        xhrDataTable.onreadystatechange = () => {

          console.log("Sending req");
          if (xhrDataTable.readyState == 4) {
            if (xhrDataTable.status == 200) {
              let json = JSON.parse(xhrDataTable.responseText);
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
              let jsonError = JSON.parse(xhrDataTable.responseText);
              this.handleError(jsonError.errors[0]["message"]);
            }
          }
        };
        xhrDataTable.send(JSON.stringify(payload));
      } catch (except) {
        this.handleError("[Expansion] Error in API request please check configuration");
        console.log(except);
      }
    }
  }
  render() {
    return (
      <Panel style={{ width: "100%" }} border="panel--bordered">
        <ToastContainer></ToastContainer>
        <Table
          noDataText="No data found"
          data={this.state.rows}
          defaultSorted={this.props.defaultSorted}
          columns={this.tableHeaders[this.props.index]}
          loading={this.state.loading}
        />
      </Panel>
    );
  }
}
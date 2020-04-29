import React, { Component } from "react";
import { Table, Panel } from "blueprint-react";
import {
  TABLE_COLUMNS_AUDIT_LOG,
  TABLE_COLUMNS_EVENTS,
  TABLE_COLUMNS_FAULTS,
  ROWS_FAULTS, TABLE_POLICIES,
  TABLE_OPERATIONAL,
  TABLE_TOEPG,
  TABLE_SUBNETS
} from "./tableHeaders.js";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import "./styleTabs.css"
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
      intervalId : undefined
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
      let intervalId = setInterval(this.fetchData, 5000 );
      this.setState({intervalId})
    }
  }
  componentWillUnmount(){
    console.log("Component will unount Datatable ", this.state.intervalId);
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
      console.log(payload);
      let xhr = new XMLHttpRequest();
      let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
      try {
        xhr.open("POST", url, true);
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
              console.log(json);
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
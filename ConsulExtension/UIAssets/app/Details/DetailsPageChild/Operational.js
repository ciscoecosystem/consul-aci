import React, { Component } from "react";
import { Table, Panel } from "blueprint-react";
import { ToastContainer, toast } from "react-toastify";
import {
  QUERY_URL,
  getCookie,
  DEV_TOKEN,
  URL_TOKEN,
} from "../../../constants.js";

const TABLE_OPERATIONAL = [
  {
    Header: "End Point",
    accessor: "ep_name",
  },
  {
    Header: "MAC",
    accessor: "mac",
  },
  {
    Header: "IP",
    accessor: "ip",
  },
  {
    Header: "Learning Resource",
    accessor: "learning_source",
  },
  {
    Header: "Hosting Server",
    accessor: "hosting_server_name",
  },
  {
    Header: "Reporting Controller Name",
    accessor: "ctrlr_name",
  },
  {
    Header: "Interface",
    accessor: "iface_name",
    width: 190,
    Cell: (row) => {
      return (
        <div>
          {row.value.map(function (val) {
            return (
              <React.Fragment>
                {val}
                <br />
              </React.Fragment>
            );
          })}
        </div>
      );
    },
  },
  {
    Header: "Encap",
    accessor: "encap",
  },
];

export default class Operational extends Component {
  constructor(props) {
    super(props);
    console.log(props)
    this.state = {
      rows: [],
      loading: false,
    };
    this.fetchOperationalData = this.fetchOperationalData.bind(this);
    this.handleError = this.handleError.bind(this);
  }

  componentDidMount() {
    this.setState({ loading: true})
    this.fetchOperationalData();
  }

  handleError(error) {
    console.error(error);
    var errorText = "Error: ";
    if (typeof error == "object") {
      errorText += JSON.stringify(error);
    } else {
      errorText += error;
    }
    this.setState({ loading: false });

    toast.error(unescape(errorText), {
      position: toast.POSITION.BOTTOM_CENTER,
      autoClose: 2500,
    });
  }

  fetchOperationalData() {
    const payload = {
      query:
        'query{GetOperationalInfo(dn:"' +
        this.props.domainName +
        '",moType:"' +
        this.props.moType +
        '",macList:"' +
        this.props.macList +
        '",ipList:"' +
        this.props.ipList.join("-") +
        '",ip:"' +
        this.props.ip +
        '"){operationalList}}',
    };

    let xhrDataTable = new XMLHttpRequest();
    try {
      xhrDataTable.open("POST", QUERY_URL, true);
      window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for expansion
      window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for expansion
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
              this.handleError(
                json.errors[0]["message"] || "Error while fetching data"
              );
            } else {
              const response = JSON.parse(json.data.GetOperationalInfo.operationalList)
              console.log(response)
              if (response.status_code != "200") {
                // Problem with backend fetching data
                this.handleError(response.message);
              } else {
                // Success
                this.setState({ rows: response.payload });
              }
            }
          } else {
            // Status code of XHR request not 200
            let jsonError = JSON.parse(xhrDataTable.responseText);
            this.handleError(jsonError.errors[0]["message"]);
          }
        }
        this.setState({ loading: false });
      };
      xhrDataTable.send(JSON.stringify(payload));
    } catch (except) {
      this.handleError(
        "[Expansion] Error in API request please check configuration"
      );
      console.log(except);
    }
  }

  render() {
    return <div><Panel style={{ width: "100%" }} border="panel--bordered">
    <ToastContainer></ToastContainer>
    <Table
      noDataText="No data found"
      data={this.state.rows}
      // defaultSorted={this.props.defaultSorted}
      columns={TABLE_OPERATIONAL}
      loading={this.state.loading}
    />
  </Panel></div>;
  }
}

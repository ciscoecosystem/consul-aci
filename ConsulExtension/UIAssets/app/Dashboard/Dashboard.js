import React from "react";
import { Loader } from "blueprint-react";
import PieChartAndCounter from "../commonComponent/PieChartAndCounter.js";
import {
  QUERY_URL,
  getCookie,
  DEV_TOKEN,
  URL_TOKEN,
  AGENTS,
  INTERVAL_API_CALL
} from "../../constants.js";
import { toast } from "react-toastify";
import "./Dashboard.css";

// const dummydata = { 'nodes': { 'passing': 0, 'warning': 0, 'failing': 0 }, 'agents': { 'down': 0, 'up': 2 }, 'service': { 'passing': 1, 'warning': 1, 'failing': 2 }, 'service_endpoint': { 'non_service': 21, 'service': 11 } }

const BILLION = 1000000000
const MILLION = 1000000000
const THOUSAND = 1000

export default class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loadingDashBoard: false,
    };

    this.xhrReadDashboard = new XMLHttpRequest();
    this.loadDashBoardData = this.loadDashBoardData.bind(this);
    this.formateDataToChartData = this.formateDataToChartData.bind(this);
    this.nFormatter = this.nFormatter.bind(this);
    this.getDashboardData = this.getDashboardData.bind(this);
    this.notify = this.notify.bind(this);
    this.formateData = this.formateData.bind(this);
  }

  componentDidMount() {
    this.setState({ loadingDashBoard: true }, this.getDashboardData);
    // this.loadDashBoardData(dummydata);
  }

  loadDashBoardData(data) {
    let agents = {
      ...data.agents,
      "order": ["up", "down"]
    }
    let endpoints = {
      ...data.service_endpoint,
      "order": ["service", "non_service"]
    }
    this.setState({
      agents,
      endpoints,
      services: data.service,
      nodes: data.nodes,
    });
  }

  nFormatter(num) {
    if (num >= BILLION) {
      return (num / BILLION).toFixed(1).replace(/\.0$/, "") + "B";
    }
    if (num >= MILLION) {
      return (num / MILLION).toFixed(1).replace(/\.0$/, "") + "M";
    }
    if (num >= THOUSAND) {
      return (num / THOUSAND).toFixed(1).replace(/\.0$/, "") + "K";
    }
    return num;
  }

  notify(message, isSuccess = false, isWarning = false) {
    isWarning
      ? toast.warn(message, {
          position: toast.POSITION.TOP_BOTTOM,
          delay: 1500,
        })
      : isSuccess
      ? toast.success(message, {
          position: toast.POSITION.TOP_BOTTOM,
          delay: 1500,
        })
      : toast.error(message, {
          position: toast.POSITION.TOP_BOTTOM,
          delay: 1500,
        });
  }

  formateDataToChartData(data) {
    let totalCnt = 0;
    let formattedData = [];

    let datakeys = Object.keys(data);
    datakeys.forEach(function (elem) {
      let dataElem = {};
      dataElem.label = elem;
      dataElem.value = data[elem];
      totalCnt += data[elem];

      if (elem === "passing") {
        dataElem.color = "rgb(108, 192, 74)";
      } else if (elem === "warning") {
        dataElem.color = "rgb(255, 204, 0)";
      } else if (elem === "failing") {
        dataElem.color = "rgb(226, 35, 26)";
      }
      formattedData.push(dataElem);
    });
    return {
      formattedData, // format as per chart
      totalCnt, // total count of all (passing,warning,failing)
    };
  }

  formateData(data){
    let formateData = []
    data.order.forEach(item => {
        formateData.push(data[item])})
    return formateData
  }

  getDashboardData() {

    const payload = {
      query:
        'query{GetPerformanceDashboard(tn:"' +
        this.props.tenantName +
        '"){response}}',
    };

    try {
      this.xhrReadDashboard.open("POST", QUERY_URL, true);
      this.xhrReadDashboard.setRequestHeader(
        "Content-type",
        "application/json"
      );
      // window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
      // window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
      this.xhrReadDashboard.setRequestHeader("DevCookie", getCookie(DEV_TOKEN));
      this.xhrReadDashboard.setRequestHeader(
        "APIC-challenge",
        getCookie(URL_TOKEN)
      );

      this.xhrReadDashboard.onreadystatechange = () => {
        if (
          this.xhrReadDashboard.readyState == 4 &&
          this.xhrReadDashboard.status == 200
        ) {
          let checkData = JSON.parse(this.xhrReadDashboard.responseText);
          let dashboardData = JSON.parse(
            checkData.data.GetPerformanceDashboard.response
          );

          if (parseInt(dashboardData.status) === 200) {
            if( JSON.parse(localStorage.getItem("dashboardPollingInterval")) && JSON.parse(dashboardData.payload.data_fetch)) {
              this.loadDashBoardData(dashboardData.payload);
              setTimeout(()=> this.getDashboardData(), INTERVAL_API_CALL)
            }
            else {
              this.loadDashBoardData(dashboardData.payload);
              localStorage.setItem("dashboardPollingInterval", "false")
            }
          } else if (parseInt(dashboardData.status) === 300) {
            try {
              this.notify(dashboardData.message);
            } catch (e) {
            }
          }
        }
        this.setState({ loadingDashBoard: false });
      };
      this.xhrReadDashboard.send(JSON.stringify(payload));
    } catch (e) {
      this.notify("Something went wrong.");
    }
  }

  render() {
    return (
      <React.Fragment>
        <div style={{ margin: "10px" }}>
          <h4>Dashboard</h4>
        </div>
        <div className="overview">
          {/* <ExamplesHeader title="Charts"/> */}
          <div className="header-text">
            <b>Overview</b>
          </div>
          {this.state.loadingDashBoard ? (
            <Loader></Loader>
          ) : (
            <div class="row">
              {this.state.agents ? (
                <div class="col">
                  <div class="row">{AGENTS}</div>
                  <div class="row">
                    <PieChartAndCounter
                      data={this.formateData(this.state.agents)}
                      totalCount={this.state.agents.total}
                    />
                  </div>
                </div>
              ) : null}

              {this.state.services ? (
                <div class="col">
                  <div class="row">Service checks</div>
                  <div class="row">
                    <PieChartAndCounter
                      data={
                        this.formateDataToChartData(this.state.services)
                          .formattedData
                      }
                      totalCount={
                        this.formateDataToChartData(this.state.services)
                          .totalCnt
                      }
                    />
                  </div>
                </div>
              ) : null}

              {this.state.nodes ? (
                <div class="col">
                  <div class="row">Node checks</div>
                  <div class="row">
                    <PieChartAndCounter
                      data={
                        this.formateDataToChartData(this.state.nodes)
                          .formattedData
                      }
                      totalCount={
                        this.formateDataToChartData(this.state.nodes).totalCnt
                      }
                    />
                  </div>
                </div>
              ) : null}
              {this.state.endpoints ? (
                <div class="col">
                  <div class="row">Endpoints</div>
                  <div class="row">
                    <PieChartAndCounter
                      data={this.formateData(this.state.endpoints)}
                      totalCount={this.state.endpoints.total}
                    />
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </div>
      </React.Fragment>
    );
  }
}

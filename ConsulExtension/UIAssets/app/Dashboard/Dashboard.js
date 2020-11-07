import React from "react";
import { Loader } from "blueprint-react";
import PieChartAndCounter from "../commonComponent/PieChartAndCounter.js";
import {
  QUERY_URL,
  getCookie,
  DEV_TOKEN,
  URL_TOKEN,
  AGENTS,
  INTERVAL_API_CALL,
} from "../../constants.js";
import DashboardPopUp from "./DashboardPopUp";
import {
  SERVICE_HEADER,
  NODE_COLUMNS,
  NON_SERVICE_ENDPOINT_COLUMNS,
  SERVICE_ENDPOINT_COLUMNS,
} from "./TabelHeaders";
import { toast } from "react-toastify";
import "./Dashboard.css";

// const dummydata = { 'nodes': { 'passing': 0, 'warning': 0, 'failing': 0 }, 'agents': { 'down': 0, 'up': 2 }, 'service': { 'passing': 1, 'warning': 1, 'failing': 2 }, 'service_endpoint': { 'non_service': 21, 'service': 11 } }

const BILLION = 1000000000;
const MILLION = 1000000000;
const THOUSAND = 1000;

const AGENT_ORDER = ["up", "down"];
const ENDPOINT_ORDER = ["service", "non_service"];

export default class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loadingDashBoard: false,
      isDisplayPopUp: false,
      dashboardPopUp: {},
      datacenters: [],
      overviewData: {},
      allData: {},
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

  loadDashBoardData(dashboard_data) {
    let overviewData = dashboard_data.data.overview;
    let allData = dashboard_data.data.all;
    let datacenters = Object.keys(dashboard_data.data.all);

    this.setState({
      overviewData: overviewData,
      allData: allData,
      datacenters: datacenters,
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

  formateData(data, who) {
    let formateData = [];
    let order = who === "agents" ? AGENT_ORDER : ENDPOINT_ORDER;

    order.forEach((item) => {
      formateData.push(data[item]);
    });
    return formateData;
  }

  configurePop(type, label, datacenter) {
    let dashboardPopUp = {};
    let datacenter_list = [];
    if (datacenter === "overview") {
      datacenter_list = JSON.stringify(JSON.stringify(this.state.datacenters));
      
    } else {
      datacenter_list = JSON.stringify(JSON.stringify([datacenter]));
    }
    datacenter_list = datacenter_list.substring(1, datacenter_list.length - 1);

    if (type === "service") {
      dashboardPopUp.title = "Service Checks";
      dashboardPopUp.query =
        'query{ServiceChecksClick(tn:"' +
        this.props.tenantName +
        '",datacenters:"' +
        datacenter_list +
        '"){response}}';
      dashboardPopUp.queryKey = "ServiceChecksClick";
      dashboardPopUp.defaultFilters = [
        {
          category: "serviceChecksFilter",
          categoryLabel: "Service Check(s)",
          operator: "==",
          value: label,
        },
      ];
      dashboardPopUp.columns = SERVICE_HEADER;
    } else if (type === "node") {
      dashboardPopUp.title = "Node Checks";
      dashboardPopUp.query =
        'query{NodeChecksClick(tn:"' +
        this.props.tenantName +
        '",datacenters:"' +
        datacenter_list +
        '"){response}}';
      dashboardPopUp.queryKey = "NodeChecksClick";
      dashboardPopUp.defaultFilters = [
        {
          category: "nodeChecksFilter",
          categoryLabel: "Node Check(s)",
          operator: "==",
          value: label,
        },
      ];
      dashboardPopUp.columns = NODE_COLUMNS;
    } else if (type === "endpoint") {
      if (label === "service endpoints") {
        dashboardPopUp.title = "Service Endpoints";
        dashboardPopUp.query =
          'query{ServiceChecksClick(tn:"' +
          this.props.tenantName +
          '",datacenters:"' +
          datacenter_list +
          '"){response}}';
        dashboardPopUp.queryKey = "ServiceChecksClick";
        dashboardPopUp.columns = SERVICE_ENDPOINT_COLUMNS;
      } else {
        dashboardPopUp.title = "Non-Service Endpoints";
        dashboardPopUp.query =
          'query{NonServiceEndpoints(tn:"' +
          this.props.tenantName +
          '",datacenters:"' +
          datacenter_list +
          '"){response}}';
        dashboardPopUp.queryKey = "NonServiceEndpoints";
        dashboardPopUp.columns = NON_SERVICE_ENDPOINT_COLUMNS;
      }
    }

    this.setState({ dashboardPopUp: dashboardPopUp }, () =>
      this.setState({ isDisplayPopUp: true })
    );
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
            if (
              JSON.parse(localStorage.getItem("dashboardPollingInterval")) &&
              JSON.parse(dashboardData.payload.data_fetch)
            ) {
              this.loadDashBoardData(dashboardData.payload);
              setTimeout(() => this.getDashboardData(), INTERVAL_API_CALL);
            } else {
              this.loadDashBoardData(dashboardData.payload);
              this.setState({ data });
              localStorage.setItem("dashboardPollingInterval", "false");
            }
          } else if (parseInt(dashboardData.status) === 300) {
            try {
              this.notify(dashboardData.message);
            } catch (e) {}
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
    let { overviewData, allData } = this.state;

    return (
      <React.Fragment>
        {this.state.isDisplayPopUp ? (
          <DashboardPopUp
            title={this.state.dashboardPopUp.title}
            columns={this.state.dashboardPopUp.columns}
            query={this.state.dashboardPopUp.query}
            queryKey={this.state.dashboardPopUp.queryKey}
            defaultFilters={this.state.dashboardPopUp.defaultFilters}
            closePopUp={() => this.setState({ isDisplayPopUp: false })}
          />
        ) : null}
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
              {overviewData.agents ? (
                <div class="col">
                  <div class="row">{AGENTS}</div>
                  <div class="row">
                    <PieChartAndCounter
                      data={this.formateData(overviewData.agents, "agents")}
                      totalCount={overviewData.agents.total}
                      clickable={true}
                      onClick={(label) => {
                        console.log(label);
                        let status = "Disconnected";
                        if (label === "connected") status = "Connected";
                        this.props.setDefaultFilter([
                          {
                            category: "status",
                            categoryLabel: "Status",
                            operator: "==",
                            value: status,
                          },
                        ]);
                        this.props.handleAgent(true);
                      }}
                    />
                  </div>
                </div>
              ) : null}

              {overviewData.service ? (
                <div class="col">
                  <div class="row">Service checks</div>
                  <div class="row">
                    <PieChartAndCounter
                      data={
                        this.formateDataToChartData(overviewData.service)
                          .formattedData
                      }
                      totalCount={
                        this.formateDataToChartData(overviewData.service)
                          .totalCnt
                      }
                      clickable={true}
                      onClick={(label) => {
                        this.configurePop("service", label, "overview");
                      }}
                    />
                  </div>
                </div>
              ) : null}

              {overviewData.nodes ? (
                <div class="col">
                  <div class="row">Node checks</div>
                  <div class="row">
                    <PieChartAndCounter
                      data={
                        this.formateDataToChartData(overviewData.nodes)
                          .formattedData
                      }
                      totalCount={
                        this.formateDataToChartData(overviewData.nodes).totalCnt
                      }
                      clickable={true}
                      onClick={(label) => {
                        this.configurePop("node", label, "overview");
                      }}
                    />
                  </div>
                </div>
              ) : null}
              {overviewData.service_endpoint ? (
                <div class="col">
                  <div class="row">Endpoints</div>
                  <div class="row">
                    <PieChartAndCounter
                      data={this.formateData(
                        overviewData.service_endpoint,
                        "endpoints"
                      )}
                      totalCount={overviewData.service_endpoint.total}
                      clickable={true}
                      onClick={(label) => {
                        this.configurePop("endpoint", label, "overview");
                      }}
                    />
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </div>
        {Object.keys(allData).reverse().map((item) => (
          <div className="overview">
            {/* <ExamplesHeader title="Charts"/> */}
            <div className="header-text">
              <b>
                {item ? item+"-" : ""}
                {allData[item].agents.up.value ? "Connected" : "Disconnected" + " ("+ allData[item].agents.down.value +")"}
              </b>
            </div>
            {this.state.loadingDashBoard ? (
              <Loader></Loader>
            ) : (
              <div class="row">
                {allData[item].service ? (
                  <div class="col">
                    <div class="row">Service checks</div>
                    <div class="row">
                      <PieChartAndCounter
                        data={
                          this.formateDataToChartData(allData[item].service)
                            .formattedData
                        }
                        totalCount={
                          this.formateDataToChartData(allData[item].service)
                            .totalCnt
                        }
                        clickable={true}
                        onClick={(label) => {
                          this.configurePop("service", label, item);
                        }}
                      />
                    </div>
                  </div>
                ) : null}

                {allData[item].nodes ? (
                  <div class="col">
                    <div class="row">Node checks</div>
                    <div class="row">
                      <PieChartAndCounter
                        data={
                          this.formateDataToChartData(allData[item].nodes)
                            .formattedData
                        }
                        totalCount={
                          this.formateDataToChartData(allData[item].nodes)
                            .totalCnt
                        }
                        clickable={true}
                        onClick={(label) => {
                          this.configurePop("node", label, item);
                        }}
                      />
                    </div>
                  </div>
                ) : null}
                {allData[item].service_endpoint ? (
                  <div class="col">
                    <div class="row">Endpoints</div>
                    <div class="row">
                      <PieChartAndCounter
                        data={this.formateData(
                          allData[item].service_endpoint,
                          "endpoints"
                        )}
                        totalCount={allData[item].service_endpoint.total}
                        clickable={true}
                        onClick={(label) => {
                          this.configurePop("endpoint", label, item);
                        }}
                      />
                    </div>
                  </div>
                ) : null}
              </div>
            )}
          </div>
        ))}
      </React.Fragment>
    );
  }
}

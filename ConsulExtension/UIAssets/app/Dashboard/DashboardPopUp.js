import React, { Component } from "react";
import { Screen, FilterableTable } from "blueprint-react";
import {  getCookie, QUERY_URL, URL_TOKEN, DEV_TOKEN } from "../../constants.js";

export default class DashboardPopUp extends Component {
  constructor(props) {
    super(props);
    this.myRef = React.createRef();
    this.state = {
      isLoading: false,
      data: [],
      loadingText:"Loading"
    }
    this.getData = this.getData.bind(this);
    this.setData = this.setData.bind(this);
  }

  componentDidMount() {
    this.setState({ isLoading: true})
    this.getData();
  }

  setData(data) {
    if(this.props.queryKey !== "NonServiceEndpoints"){
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
    }

      this.setState({ data: data})
  }

  getData() {

    let xhrReadDashboard = new XMLHttpRequest();

    const payload = {
      query: this.props.query,
    };

    console.log(payload)

    try {
      xhrReadDashboard.open("POST", QUERY_URL, true);
      xhrReadDashboard.setRequestHeader(
        "Content-type",
        "application/json"
      );
      window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
      window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
      xhrReadDashboard.setRequestHeader("DevCookie", getCookie(DEV_TOKEN));
      xhrReadDashboard.setRequestHeader(
        "APIC-challenge",
        getCookie(URL_TOKEN)
      );

      xhrReadDashboard.onreadystatechange = () => {
        if (
          xhrReadDashboard.readyState == 4 &&
          xhrReadDashboard.status == 200
        ) {
          let checkData = JSON.parse(xhrReadDashboard.responseText);
          checkData = checkData.data
          checkData = checkData[this.props.queryKey]
          console.log(checkData)
          console.log(this.props.queryKey)
          let getDataResponse = JSON.parse(
            checkData.response
          );
          console.log(getDataResponse)
          if (parseInt(getDataResponse.status_code) === 200) {
            let data = getDataResponse.payload;
            // this.setPollingIntervalDefaultValue(data.interval)
            this.setData(data)
          }
        }
        this.setState({ isLoading: false });
      };
      xhrReadDashboard.send(JSON.stringify(payload));
    } catch (e) {
      // this.notify("Something went wrong.");
      console.log(e)
    }
  }


  render() {
    return (
      <div>
        {console.log(this.props)}
        <Screen
          id="pop-up"
          key="pop"
          className="modal-layer-1"
          hideFooter={true}
          title={this.props.title}
          allowMinimize={false}
          onClose={this.props.closePopUp}
        >
          <div className="dialog-content">
            <div className="screen-content">
              <div className="panel  panel-with-header ">
                <div className="panel-header with-config-group  ">
                  <div className="heading-container">
                    {/* <div className="panel-label">Agents</div> */}
                  </div>
                </div>
                <div className="panel-body">
                  <div className="dashboard-pop">
                    <FilterableTable
                      ref={this.myRef}
                      loading={this.state.isLoading}
                      loadingText={this.state.loadingText}
                      className="-striped -highlight"
                      noDataText={this.props.noDataText}
                      data={this.state.data}
                      columns={this.props.columns}
                      defaultFilters={this.props.defaultFilters || []}
                    />
                  </div>
                  {/* This is parixit */}
                </div>
              </div>
            </div>
          </div>
        </Screen>
      </div>
    );
  }
}

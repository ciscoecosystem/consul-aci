import React, { Component } from "react";
import "./DetailsPage.css";
import EventAnalytics from "./DetailsPageChild/EventAnalytics";
import { Icon, Tab, Screen } from "blueprint-react";
import clone from "clone";
import DataTable from "./DetailsPageChild/DataTable.js";
import Operational from "./DetailsPageChild/Operational";
import SubTable from "./DetailsPageChild/SubTable";
import CONSUL_ServiceChecksTable from "./DetailsPageChild/CONSUL_ServiceChecksTable";

export default class DetailePage extends Component {
  constructor(props) {
    super(props);
    this.test = this.test.bind(this);
    this.getIPList = this.getIPList.bind(this);
    this.getQueryParams = this.getQueryParams.bind(this);
    this.getCustomQuery = this.getCustomQuery.bind(this);
    this.setNewTab = this.setNewTab.bind(this);

    this.state = {
      data: this.props.data,
      tabs: [

        {
          label: "Operational",
          key: "Operational",
          content: this.test("Operational")
        },
        {
          label: "Event Analytics",
          key: "EventAnalytics",
          content: this.test("event")
        }
      ]
    };
  }
  getQueryParams() {
    var query = false;
    console.log("with data");
    console.log(this.state.data);
    if (this.state.data.name === "AppProf") {
      query = "ap-" + this.state.data.sub_label
    } else if (this.state.data.name === "EPG") {
      const AppProf = "ap-" + this.state.data.parent.sub_label;
      const EPG = "epg-" + this.state.data.sub_label;
      query = AppProf + "/" + EPG;
    } else if (this.state.data.name === "EP") {

      const AppProf = "ap-" + this.state.data.parent.parent.sub_label;
      const EPG = "epg-" + this.state.data.parent.sub_label;
      query = AppProf + "/" + EPG
      //Pass
    }
    return query;
  }
  getCustomQuery() {
    var query = false

    return {
      ap: this.state.data.parent.sub_label,
      epg: this.state.data.sub_label
    }
  }
  getIPList() {
    if (this.state.data.type === "grey") {
      return Object.values(this.state.data.attributes) || ""
    }
    else {
      return this.state.data.attributes.IP || ""
    }
  }
  setNewTab(clonedObj) {
    let newTab = {
      label: "Health Rules Violations",
      key: "hrv",
      content: <SubTable data={this.state.data.attributes.HealthRuleViolations || false}></SubTable>
    }
    clonedObj.push(newTab);
    this.setState({ tabs: clonedObj });


  }
  componentWillMount() {
    const { data } = this.state;

    const queryParams = this.getQueryParams()
    let clonedObj = clone(this.state.tabs)
    if (data.name == "AppProf" || data.name == "EPG") {
      clonedObj[1]["content"] = <EventAnalytics queryParams={queryParams} key="analytics"></EventAnalytics>;

    }
    if (data.name == "AppProf") {
      clonedObj.splice(0, 1);
      console.log(clonedObj);

      this.setState({ tabs: clonedObj });
    }
    if (data.name == "EPG") {
      let moType = data.name.toLowerCase();
      let ipList = "";
      let param = queryParams + '",moType:"' + moType + '",ipList:"' + ipList
      let noMotype = queryParams;
      let newquery = this.getCustomQuery();
      clonedObj[0]["content"] = <Operational nomo={noMotype} customQuery={newquery} query={param}></Operational>

      this.setState({ tabs: clonedObj });
    }
    if (data.name == "EP") {
      clonedObj.splice(1, 1);
      let moType = data.name.toLowerCase();
      let ipList = this.getIPList();

      let param = queryParams + '",moType:"' + moType + '",ipList:"' + ipList
      let query = {
        param, type: "GetOperationalInfo",
        list: "{operationalList}"
      }
      clonedObj[0]["content"] = <DataTable key="operational" query={query} index="3" />

      this.setState({ tabs: clonedObj });
    }

    // service checks tab
    if (data.name == "Service") {
      let serviceInstance = data.attributes['Service Instance'];
      let query = "";
      try {
        query = 'query{ServiceChecks(service_name:"AppDynamics",service_id:"' + serviceInstance + '"){response}}';
        console.log("== query build ", query);
      } catch (err) {
        console.log("error in query:- ", err);
      }

      this.setState({
        tabs: [
          {
            label: "Service Checks",
            key: "Service Checks",
            content: <CONSUL_ServiceChecksTable key={"serviceChecks"} query={query} />
          }
        ]
      })
    }

    if (data.attributes.HealthRuleViolations) {
      this.setNewTab(clonedObj);
    }
  }

  test(props) {
    return <div style={{ margin: "11px" }}>{props} Details</div>;
  }

  render() {
    let { data } = this.state;
    console.log("[detailpage]== allstate ", this.state);
    console.log("[detailpage]== tab ", this.state.tabs)

    let title = "";
    if (data.name === "Service") {
      title = data.attributes['Service Instance']
    } else {
      title = this.state.data.sub_label || this.state.data.label || "EndPoint Information";
    }

    return (
      <Screen hideFooter={true} title={title} allowMinimize={false} onClose={this.props.closeDetailsPage}>

        {/* // <div className="page-overlay">
      //   <div className="panel-header">
      //     {this.state.data.sub_label || this.state.data.label}
      //     <Icon
      //       type="icon-close"
      //       className="pull-right toggle"
      //       onClick={this.props.closeDetailsPage}
      //     />
      //   </div> */}

        <Tab type="secondary-tabs" tabs={this.state.tabs} />
      </Screen>
    );
  }
}

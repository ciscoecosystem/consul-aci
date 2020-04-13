import React, { Component } from "react";
import "./DetailsPage.css";
import EventAnalytics from "./DetailsPageChild/EventAnalytics";
import { Loader, Tab, Screen } from "blueprint-react";
import clone from "clone";
import DataTable from "./DetailsPageChild/DataTable.js";
import Operational from "./DetailsPageChild/Operational";
import SubTable from "./DetailsPageChild/SubTable";
import CONSUL_ChecksTable from "./DetailsPageChild/CONSUL_ChecksTable";
import CONSUL_ConsulTab from "./DetailsPageChild/CONSUL_ConsulTab";

export default class DetailePage extends Component {
  constructor(props) {
    super(props);
    this.test = this.test.bind(this);
    this.getMacList = this.getMacList.bind(this);
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
  getMacList() {
    if (this.state.data.type === "grey") {
      return Object.keys(this.state.data.attributes) || ""
    }
    else {
      return this.state.data.attributes.Mac || ""
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
  componentDidMount() {
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
      let macList = "";
      let param = queryParams + '",moType:"' + moType + '",macList:"' + macList
      let noMotype = queryParams;
      let newquery = this.getCustomQuery();

      // let tabsObj =  [
      //   {
      //     label: "Operational",
      //     key: "Operational",
      //     content: <Operational nomo={noMotype} customQuery={newquery} query={param}></Operational>
      //   }
      // ]
      clonedObj[0]["content"] = <Operational nomo={noMotype} customQuery={newquery} query={param}></Operational>

      /**
       * Consul tab:- 
       */

      // Setting query ...
      let nodeList = [];
      let serviceList = [];
      let finalServiceList = [];

      try {
        nodeList = data.attributes['Nodes'].map(val => val["Node"])
        let epList = data.children; // List of EP

        if (epList && epList.length > 0) {
          // traversing all EP and appending its childen service in serviceList 
          epList.forEach(element => {

            let epServices = element.children;
            if (epServices && epServices.length > 0) {

              let serviceListNew = epServices.map(inData => {
                return Object.assign({},
                  {
                    'Service': inData.attributes['Service'],
                    'ServiceID': inData.attributes['Service Instance']
                  })
              })
              serviceList.push(serviceListNew);
            }
          });
        }

        finalServiceList = [].concat.apply([], serviceList);

      } catch (error) {
        console.log("error in setting query", error);
      }

      let NodeCheckQuery = {"query": 'query{NodeChecksEPG(nodeList:' + JSON.stringify(JSON.stringify(nodeList)) + '){response}}'};
      let ServiceCheckQuery = {"query":  'query{ ServiceChecksEP(serviceList:' + JSON.stringify(JSON.stringify(finalServiceList)) + '){response}}'};

      clonedObj.push({
        label: "Consul",
        key: "Consul",
        content: <CONSUL_ConsulTab NodeCheckQuery={NodeCheckQuery} ServiceCheckQuery={ServiceCheckQuery} /> // contains subTabs: nodeCheck | serviceChecks 
      });

      this.setState({ tabs: clonedObj });
    }
    // for EP detail view expansion ; Tabs are [Operational, Health Check, Node check, Service Check]
    if (data.name == "EP") {
      console.log("SEttting tab in EP");
      // clonedObj.splice(1, 1);
      let moType = data.name.toLowerCase();
      let macList = this.getMacList();

      let param = queryParams + '",moType:"' + moType + '",macList:"' + macList
      let query = {
        param, type: "GetOperationalInfo",
        list: "{operationalList}"
      }

      // Setting query ...

      let nodeName = "";
      let serviceList = [];

      try {
        nodeName = data.attributes['Node'];
        let epServices = data.children;
        console.log("epServies ", epServices);

        if (epServices && epServices.length > 0){
          serviceList = epServices.map(inData => {
            return Object.assign({},
              { 'Service': inData.attributes['Service'],
                'ServiceID':inData.attributes['Service Instance']
              })
            })
        } else {
          serviceList = [];
        }
      } catch (error) {
        console.log("error in setting quert", error);
      }

      let NodeCheckQuery = {"query": 'query{NodeChecks(nodeName:"' + nodeName + '"){response}}'};
      let ServiceCheckQuery = {"query": 'query{ ServiceChecksEP(serviceList:' + JSON.stringify(JSON.stringify(serviceList)) + '){response}}'};

      let tabsObj = [
        {
          label: "Operational",
          key: "Operational",
          content: <DataTable key="operational" query={query} index="3" />
        },
        {
          label: "Node Checks",
          key: "Node Checks",
          content: <CONSUL_ChecksTable key={"nodeChecks"} query={NodeCheckQuery} />
        },
        {
          label: "Service Checks",
          key: "Service Checks",
          content: <CONSUL_ChecksTable key={"serviceChecks"} query={ServiceCheckQuery} />
        }
      ]

      this.setState({
        tabs: tabsObj
      }, () => {
        console.log("Settin tab for ", this.state.tabs);
      })

      // clonedObj[0]["content"] = <DataTable key="operational" query={query} index="3" />
      // this.setState({ tabs: clonedObj });
    }

    // Service detail view ; Tabs: [Service Checks]
    if (data.name == "Service") {
      let serviceInstance = data.attributes['Service Instance'];
      let serviceName = data.attributes['Service'];
      let query = "";
      try {
        query = { "query": 'query{ServiceChecks(serviceName:"' + serviceName + '", serviceId:"' + serviceInstance + '"){response}}'};
        console.log("== query build ", query);
      } catch (err) {
        console.log("error in query:- ", err);
      }

      this.setState({
        tabs: [
          {
            label: "Service Checks",
            key: "Service Checks",
            content: <CONSUL_ChecksTable key={"serviceChecks"} query={query} />
          }
        ]
      })
    }

    // if (data.attributes.HealthRuleViolations) {
    //   this.setNewTab(clonedObj);
    // }
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
        {(this.state.tabs.length > 0) ?
          <Tab type="secondary-tabs" tabs={this.state.tabs} />
          : <Loader> loading </Loader>}
      </Screen>
    )
  }
}

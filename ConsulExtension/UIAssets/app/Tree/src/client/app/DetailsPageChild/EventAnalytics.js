import React, { Component } from "react";
import { Tab } from "blueprint-react";
import clone from "clone";
import DataTable from "./DataTable.js";
import "./styleTabs.css"

export default class EventAnalytics extends Component {
  constructor(props) {
    super(props);
    this.state = {
      queryParams: this.props.queryParams,
      tabs: [
        {
          label: "Faults",
          key: "faults",
          content: <div>No Component</div>, //add your component here
          gqlCall: "GetFaults",
          list: "{faultsList}"

        },
        {
          label: "Events",
          key: "events",
          content: <div>NO Component</div>, //add your component here
          gqlCall: "GetEvents",
          list: "{eventsList}"
        },
        {
          label: "Audit Logs",
          key: "auditlogs",
          content: <div>No Component</div>, //add your component here
          gqlCall: "GetAuditLogs",
          list: "{auditLogsList}"

        }
      ]

    };

    console.log(this.props.name)
    console.log(this.props.queryParams)
  }

  componentDidMount() {

    var temp = clone(this.state.tabs)
    this.setState({ tabs: [] })
    temp.forEach(ele => {
      let query = {
        param: this.state.queryParams,
        type: ele.gqlCall,
        list: ele.list
      }
      ele.content = <DataTable key={ele.gqlCall} query={query} index={temp.indexOf(ele)} ></DataTable>
    })

    this.setState({ tabs: temp })

  }

  render() {
    return (
      <div className="events-tab" style={{ margin: "7px" }}>
        <Tab vertical={false} type="secondary-tabs" tabs={this.state.tabs} />
      </div>
    );
  }
}

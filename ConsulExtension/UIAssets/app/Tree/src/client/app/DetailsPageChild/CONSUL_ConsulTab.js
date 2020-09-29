import React from "react";
import { Tab } from "blueprint-react";
import CONSUL_ChecksTable from "./CONSUL_ChecksTable";
import "../DetailsPage.css";

// Containes subtabs: nodechecks and service checks
export default class CONSUL_ConsulTab extends React.Component {
  constructor(props) {
    super(props);
    let { NodeCheckQuery, ServiceCheckQuery } = props;

    this.state = {
      tabs: [
        {
          label: "Node Checks",
          key: "Node Checks",
          content: <CONSUL_ChecksTable key={"nodeChecks"}
            extraColumn={{ index: 1, value: { Header: 'Node', accessor: 'NodeName' } }}
            query={NodeCheckQuery} />
        },
        {
          label: "Service Checks",
          key: "Service Checks",
          content: <CONSUL_ChecksTable key={"serviceChecks"} query={ServiceCheckQuery} />
        }
      ]
    }
  }
  render() {
    return (
      <Tab type="secondary-tabs" tabs={this.state.tabs} />)
  }
}
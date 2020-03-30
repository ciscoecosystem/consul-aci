import React, { Component } from "react"
import { Table, Button } from "blueprint-react"
import ToolBar from "./ToolBar"
import tablestyle from "./tablestyle.css"
export default class DataTable extends Component {
  constructor(props) {
    super(props);
    const HEADER_DETAILS = [
      {
        Header: 'Fabric',
        headerClassName : "center-class",
        columns: [
          {
            Header: "Node",
            accessor: "node"
          },
          {
            Header: "Interface",
            accessor: "interface"
          }
        ]
      },
      {
        Header: 'APIC',
        headerClassName : "center-class",
        columns: [
          {
            Header: "IP",
            accessor: "IP"
          },
          {
            Header: "Mac",
            accessor: "mac"
          },
          {
            Header: "End Point",
            accessor: "endPointName"
          },
          {
            Header: "EPG",
            accessor: "epgName"
          },
          {
            Header: "EPG-DN",
            accessor: 'dn'
          },
          {
            Header: "Health",
            accessor: "epgHealth",
            Cell: row => {
              let epgcolor = "56b72a";
              if (row.value < 70) {
                epgcolor = "#ffcc00";
              }
              if (row.value < 40) {
                epgcolor = "#FF6666";
              }
              return <Button style={{ width: "66px", backgroundColor: epgcolor, opacity: "1" }} disabled={true} key="dd" type="btn--success" size="btn--small">{row.value}</Button>
            }
          }
        ]
      },
      {
        Header: 'AppDynamics',
        headerClassName : "tableborder",
        columns: [
          {
            Header: "Name",
            accessor: "tierName",
            headerClassName : "tableborder",
            className : "tableborder"
          },
          {
            Header: "Health",
            accessor: "tierHealth",
            Cell: row => {
              let tiercolor = "56b72a";
              if (row.value == "WARNING") {
                tiercolor = "#ffcc00";
              }
              if (row.value == "CRITICAL") {
                tiercolor = "#FF6666";
              }
              return <Button style={{ backgroundColor: tiercolor, opacity: "1" }} disabled={true} key="S" type="btn--success" size="btn--small">{row.value}</Button>
            }
          }
        ]
      }
    ]
    this.state = {
      row: this.props.data,
      columns: HEADER_DETAILS,
      loading: this.props.loading
    }
  }
  componentWillReceiveProps(newprops) {
    this.setState({ loading: newprops.loading })
    this.setState({ row: newprops.data })
  }
  render() {
    return (
      <div>
        <ToolBar onReload={() => this.props.onReload(true)} />
        <Table loading={this.state.loading} className="-striped -highlight" noDataText="No endpoints found for the given Application in the given Tenant." data={this.state.row} columns={this.state.columns}></Table>
      </div>
    )


  }
}
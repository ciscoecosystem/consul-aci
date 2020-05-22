import React, { Component } from "react"

import { Table, Button, Label, Icon } from "blueprint-react"
import ToolBar from "./ToolBar"

const successColor = "#6ebe4a";
const failColor = "#e2231a";
const warningColor = "#f49141";

export default class DataTable extends Component {
  constructor(props) {
    super(props);

    const SERVICE_TABLE_HEADER = [
      {
        Header: "Service",
        accessor: "service"
      },
      {
        Header: "Service Instance",
        accessor: "serviceInstance"
      },
      {
        Header: "Port",
        accessor: "port"
      },
      {
        Header: "Service Kind",
        accessor: "serviceKind"
      },
      {
        Header: "Service Tags",
        accessor: "serviceTags",
        Cell: row => {
          return row.value.map(tagData => <Label theme={"MEDIUM_GRAYY"} size={"SMALL"} border={false}>{tagData}</Label>)
        }
      },
      {
        Header: "Service Checks",
        accessor: "serviceChecks",
        Cell: row => {
          return (<span>
            {(row.value.passing !== undefined) && (<span> <Icon size="icon-small" type=" icon-check-square" style={{ color: successColor }}></Icon>&nbsp;{row.value.passing}&nbsp;&nbsp;</span>)}
            {(row.value.warning !== undefined) && (<span> <Icon size="icon-small" type=" icon-warning" style={{ color: warningColor }}></Icon>&nbsp;{row.value.warning}&nbsp;&nbsp;</span>)}
            {(row.value.failing !== undefined) && (<span> <Icon size="icon-small" type=" icon-exit-contain" style={{ color: failColor }}></Icon>&nbsp;{row.value.failing} </span>)}
          </span>)
        }
      },
      {
        Header: "Namespace",
        accessor: "serviceNamespace"
      }
    ]


    const HEADER_DETAILS = [
      // {
      //   Header: "Interface",
      //   accessor: "interface",
      //   width: 190,
      //   Cell: row => {
      //     return (<div>
      //       {row.value.map(function (val) {
      //         return <React.Fragment>
      //           {val}
      //           <br />
      //         </React.Fragment>
      //       })}
      //     </div>)
      //   }
      // },
      {
        Header: "Endpoint",
        accessor: "endPointName"
      },
      {
        Header: "IP",
        accessor: "ip"
      },
      // {
      //   Header: "MAC",
      //   accessor: "mac"
      // },
      // {
      //   Header: "Learning Source",
      //   accessor: "learningSource"
      // },
      // {
      //   Header: "Hosting Server",
      //   accessor: "hostingServer"
      // },
      // {
      //   Header: "Reporting Controller",
      //   accessor: "reportingController"
      // },
      // {
      //   Header: "VRF",
      //   accessor: "vrf"
      // },
      // {
      //   Header: "BD",
      //   accessor: "bd"
      // },
      {
        Header: "Application Profile",
        accessor: "ap"
      },
      {
        Header: "EPG",
        accessor: "epgName"
      },
      {
        Header: "EPG Health",
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
      },
      {
        Header: "Consul Node",
        accessor: "consulNode"
      },
      {
        Header: "Node checks",
        accessor: "nodeChecks",
        width: 150,
        Cell: row => {
          return (<span>
            {(row.value.passing !== undefined) && (<span> <Icon size="icon-small" type=" icon-check-square" style={{ color: successColor }}></Icon>&nbsp;{row.value.passing}&nbsp;&nbsp;</span>)}
            {(row.value.warning !== undefined) && (<span> <Icon size="icon-small" type=" icon-warning" style={{ color: warningColor }}></Icon>&nbsp;{row.value.warning}&nbsp;&nbsp;</span>)}
            {(row.value.failing !== undefined) && (<span> <Icon size="icon-small" type=" icon-exit-contain" style={{ color: failColor }}></Icon>&nbsp;{row.value.failing} </span>)}
          </span>)
        }
      },
      ...SERVICE_TABLE_HEADER
    ]

   

    this.state = {
      row: this.props.data,
      columns: HEADER_DETAILS,
      loading: this.props.loading,
      serviceColumn: SERVICE_TABLE_HEADER
    }
  }

  componentWillReceiveProps(newprops) {
    this.setState({ loading: newprops.loading })
    this.setState({ row: newprops.data })
  }

  CONSUL_handleRowExpanded(newExpanded, index, event) {
    // we override newExpanded, keeping only current selected row expanded
    this.props.setExpand(index[0])
  }

  render() {
    let thiss = this;
    return (
      <div>
        <ToolBar onReload={() => this.props.onReload(true)} />
        <Table loading={this.state.loading}
          className="-striped -highlight"
          noDataText="No endpoints found for the given Application in the given Tenant."
          data={this.state.row}
          columns={this.state.columns}
          onPageChange={() => this.props.resetExpanded()}
          expanded={this.props.expanded}
          onExpandedChange={(newExpanded, index, event) => this.CONSUL_handleRowExpanded(newExpanded, index, event)} 
          getTrProps={(state, rowInfo) => {
            if (rowInfo && rowInfo.row) {
              return {
                onClick: (e) => {
                  thiss.props.setSummaryDetail(rowInfo.row)
                  // console.log("Select row on click ", rowInfo );
                }
              }
            }else{
              return {}
            }
          }} >
            
          {/* // SubComponent={row => {
          //   return (
          //     <Table
          //       data={row.original.services}
          //       columns={this.state.serviceColumn}
          //       noDataText={"No services found"}
          //       defaultPageSize={100}
          //       minRows={0}
          //       showPagination={false} />
          //   )
          // }} */}
         

        </Table>
      </div>
    )
  }
}
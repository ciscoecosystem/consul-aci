import React, { Component } from "react"

import { Button, Label, Icon, FilterableTable } from "blueprint-react"
import ToolBar from "./ToolBar"

const successColor = "#6ebe4a";
const failColor = "#e2231a";
const warningColor = "#f49141";

export default class DataTable extends Component {
  constructor(props) {
    super(props);
    this.myRef = React.createRef();
    const SERVICE_TABLE_HEADER = [
      {
        Header: "Service",
        accessor: "service",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      },
      {
        Header: "Service Instance",
        accessor: "serviceInstance",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      },
      {
        Header: "Port",
        accessor: "port",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      },
      {
        Header: "Service Kind",
        accessor: "serviceKind",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      },
      {
        Header: "Service Tags",
        accessor: "serviceTags",
        filterable: false,
        Cell: row => {
          return row.value.map(tagData => <Label theme={"MEDIUM_GRAYY"} size={"SMALL"} border={false}>{tagData}</Label>)
        }
      },
      {
        Header: "Service Check",
        accessor: "serviceChecksFilter",
        show: false,
        filterable: true
      },
      {
        Header: "Service Checks",
        accessor: "serviceChecks",
        filterable: false,
        width: 150,
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
        accessor: "serviceNamespace",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      }
    ]


    const HEADER_DETAILS = [
      {
        Header: "Endpoint",
        accessor: "endPointName",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      },
      {
        Header: "IP",
        accessor: "ip",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      },
      {
        Header: "Application Profile",
        accessor: "ap",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      },
      {
        Header: "EPG",
        accessor: "epgName",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      },
      {
        Header: "EPG Health",
        accessor: "epgHealth",
        filterType: 'number',
        sortMethod: (a, b) => Number(a)-Number(b),// sorting numerically
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
        accessor: "consulNode",
        filterType: "text",
        Cell: row => {
          return <span title={row.value}>{row.value}</span>
        }
      },
      {
        Header: "Node Check",
        accessor: "nodeChecksFilter",
        show: false,
        filterable: true
      },
      {
        Header: "Service Tag",
        accessor: "serviceTagFilter",
        show: false,
        filterable: true
      },
      {
        Header: "Any text",
        accessor: "anyText",
        show: false,
        filterable: false
      },
      {
        Header: "Node Checks",
        accessor: "nodeChecks",
        filterable: false,
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

  componentDidMount(){
    const node = this.myRef.current;
    node.filterFields.pop(); // remove anytext from filter
  }

  componentWillReceiveProps(newprops) {
    this.setState({ loading: newprops.loading })
    this.setState({ row: newprops.data })
  }

  render() {
    return (
      <div>
        <ToolBar onReload={() => this.props.onReload(true)} />

        <FilterableTable loading={this.state.loading}
          ref={this.myRef}
          className="-striped -highlight"
          noDataText="No endpoints found for the given Application in the given Tenant."
          data={this.state.row}
          columns={this.state.columns}
          getTrProps={(state, rowInfo) => {
              if (rowInfo && rowInfo.row) {
                return {
                  onClick: (e) => {
                    this.props.setSummaryDetail(rowInfo.original)
                  }
                }
              } else {
                return {}
              }
            }}
           />
      </div>
    )
  }
}
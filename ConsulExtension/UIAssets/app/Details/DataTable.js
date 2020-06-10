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
        filterType: "textoptions"
      },
      {
        Header: "Service Instance",
        accessor: "serviceInstance",
        filterType: "textoptions"
      },
      {
        Header: "Port",
        accessor: "port",
        filterType: "textoptions"
      },
      {
        Header: "Service Kind",
        accessor: "serviceKind",
        filterType: "textoptions"
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
        filterType: "textoptions"
      }
    ]


    const HEADER_DETAILS = [
      {
        Header: "Endpoint",
        accessor: "endPointName",
        filterType: "textoptions"
      },
      {
        Header: "IP",
        accessor: "ip",
        filterType: "textoptions"
      },
      {
        Header: "Application Profile",
        accessor: "ap",
        filterType: "textoptions"
      },
      {
        Header: "EPG",
        accessor: "epgName",
        filterType: "textoptions"
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
        filterType: "textoptions"
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

  // CONSUL_handleRowExpanded(newExpanded, index, event) {
  //   // we override newExpanded, keeping only current selected row expanded
  //   this.props.setExpand(index[0])
  // }

  render() {
    let thiss = this;
    return (
      <div>
        <ToolBar onReload={() => this.props.onReload(true)} />



        <FilterableTable loading={this.state.loading}
          ref={this.myRef}
          className="-striped -highlight"
          noDataText="No endpoints found for the given Application in the given Tenant."
          data={this.state.row}
          columns={this.state.columns}
          // onPageChange={() => this.props.resetExpanded()}
          // expanded={this.props.expanded}
          // onExpandedChange={(newExpanded, index, event) => this.CONSUL_handleRowExpanded(newExpanded, index, event)}
          getTrProps={(state, rowInfo) => {
            if (rowInfo && rowInfo.row) {
              return {
                onClick: (e) => {
                  thiss.props.setSummaryDetail(rowInfo.original)
                  // console.log("Select row on click ", rowInfo );
                }
              }
            } else {
              return {}
            }
          }} />
        {/* </FilterableTable> */}
      </div>
    )
  }
}
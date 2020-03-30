import React, { Component } from "react";
import { Table, Panel } from "blueprint-react";
import "./styleTabs.css";
export default class SubTable extends Component {
    constructor(props) {
        super(props);
        this.state = {
            data: this.props.data,

            columns: [
                {
                    Header: 'Violation Id',
                    accessor: 'Violation Id'
                },
{
                    Header: 'Status',
                    accessor: 'Status'
                },
                {
                    Header: 'Severity',
                    accessor: 'Severity'
                },
                {
                    Header: 'Affected Object',
                    accessor: 'Affected Object'
                },
                
                {
                    Header: 'Start Time',
                    accessor: 'Start Time'
                },
                {
                    Header: 'End Time',
                    accessor: 'End Time'
                },
                {
                    Header: 'Description',
                    accessor: 'Description'
                },
                {
                    Header: 'Evaluation States',
                    expander: true,
                    width: 100
                }
            ],
            subColumns: [

                {
                    Header: 'Severity',
                    accessor: 'Severity'
                },
                {
                    Header: 'Start Time',
                    accessor: 'Start Time'
                },
                {
                    Header: 'End Time',
                    accessor: 'End Time'
                },
                {
                    Header: 'Summary',
                    accessor: 'Summary',
					 key: 'summ',
                    Cell: row => {
                        return <div dangerouslySetInnerHTML={{ __html: row.value }}></div>
                    }
                },
                {
                    Header: 'Description',
                    accessor: 'Description',
                    key: 'desc1',
                    Cell: row => {
                        return <div dangerouslySetInnerHTML={{ __html: row.value }}></div>
                    }
                }
            ]

        }
    }
    render() {
        return (
            <Panel style={{ width: "100%" }} border="panel--bordered">
                <Table
                    data={this.state.data}
                    SubComponent={row => <div className="sub-table"><Table data={row.original["Evaluation States"]} defaultPageSize={5} columns={this.state.subColumns}></Table></div>}
                    columns={this.state.columns}

                />
            </Panel>
        );
    }
}
import React from "react";
import { Tab } from "blueprint-react";
import "../DetailsPage.css";

import clone from "clone";
import DataTable from "./DataTable.js";

export default class Operational extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            query: this.props.query,
            tabs: [
                {
                    label: "Client End-points",
                    key: "cep",
                    content: <div>Work In Progress</div>, //add your component here
                    gqlCall: "GetOperationalInfo",
                    list: "{operationalList}"

                },
                {
                    label: "Configured Access Policies",
                    key: "cap",
                    content: <div>Work In Progress</div>, //add your component here
                    gqlCall: "GetConfiguredAccessPolicies",
                    list: "{accessPoliciesList}"
                },
                {
                    label: "Contracts",
                    key: "contracts",
                    content: <div>Work In Progress</div>, //add your component here
                    gqlCall: "GetAuditLogs",
                    list: "{auditLogsList}"
                }
            ],
            nestedTabs: [
                {
                    label: "To EPG Traffic",
                    key: "tep",
                    content: <div>Work In Progress</div>, //add your component here
                    gqlCall: "GetToEpgTraffic",
                    list: "{toEpgTrafficList}"

                },
                {
                    label: "Subnets",
                    key: "subnets",
                    content: <div>Work In Progress</div>, //add your component here
                    gqlCall: "GetSubnets",
                    list: "{subnetsList}"

                }
            ]
        }
    }
    componentDidMount() {
        let temp = clone(this.state.tabs)
        let nestedTemp = clone(this.state.nestedTabs);

        let query = {
            param: this.state.query,
            type: temp[0]['gqlCall'],
            list: temp[0]['list']
        }
        let customQuery = {
            param: this.props.customQuery,
            type: temp[1]['gqlCall'],
            list: temp[1]['list']
        }
        let queryToEPG = {
            param: this.props.nomo,
            type: nestedTemp[0]['gqlCall'],
            list: nestedTemp[0]['list']
        }
		let querySubnets = {
			param: this.props.nomo,
            type: nestedTemp[1]['gqlCall'],
            list: nestedTemp[1]['list']
		}
        nestedTemp[0]['content'] = <DataTable key='toepg' defaultSorted={[{id:"to_epg"}]} query={queryToEPG} index="5"></DataTable>
		nestedTemp[1]['content'] = <DataTable key='subnets' query={querySubnets} index="6"></DataTable>
        this.setState({ nestedTabs: nestedTemp })

        temp[0]['content'] = <DataTable key="cep" query={query} index="3"></DataTable>
        temp[1]['content'] = <DataTable key="cap" query={query} customQuery={customQuery || false} index="4"></DataTable>
        console.log(this.state.nestedTabs);
        temp[2]['content'] = <Tab tabs={nestedTemp}></Tab>
        this.setState({ tabs: temp })
    }
    render() {
        return (
            <Tab type="secondary-tabs" tabs={this.state.tabs} />)
    }
}
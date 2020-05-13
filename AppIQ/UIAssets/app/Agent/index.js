import React from 'react';
import { Redirect } from 'react-router-dom';
import { Screen, Table } from 'blueprint-react';
// import './style.css'

export default class Agent extends React.Component {
    constructor(props) {
        console.log("Appb");
        super(props)
        this.closeAgent = this.closeAgent.bind(this)
        this.state = {
            redirectToMain: false,
        }
    }

    closeAgent() {
        this.props.handleAgent(false);

        this.setState({ redirectToMain: true });
    }

    render() {

        const tableColumns = [{
            Header: 'Protocol',
            accessor: 'protocol'
        },
        {
            Header: 'IP / DNS',
            accessor: 'ip'
        },
        {
            Header: 'Port',
            accessor: 'port'
        },
        {
            Header: 'Token',
            accessor: 'token',
        },
        {
            Header: 'Data Center',
            accessor: 'datacenter',
        },
        {
            Header: 'Status',
            accessor: 'status',
        },
        {
            Header: 'Action',
            accessor: '',
        }
        ]

        return (<div>
            {this.state.redirectToMain && <Redirect to="/" />}
            <Screen hideFooter={true} title={"Agent"} allowMinimize={false} onClose={this.closeAgent}>


                <Table key={"agentTable"}
                    loading={false}
                    // style={{width:"90%", maxHeight: "35%"}} 
                    data={[]}
                    columns={tableColumns}
                />

            </Screen>
        </div>)
    }

}
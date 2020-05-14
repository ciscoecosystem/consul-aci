import React from 'react';
import { Redirect } from 'react-router-dom';
import { Screen, Table, Button, Dropdown } from 'blueprint-react';
import Modal from '../commonComponent/Modal.js';
import "./index.css";


const dummylist = [
    { "protocol": "http", "ip": "10.0.0.0", "port": 8050, "token": "lnfeialilsacirvjlnlaial", "status": true, "datacenter": "datacenter1" },
    { "protocol": "https", "ip": "10.0.0.1", "port": 8051, "token": "lnfeialilsacirvjlglaial", "status": false, "datacenter": "datacenter1" },
    { "protocol": "http", "ip": "10.0.0.2", "port": 8051, "token": "lnfeialilsacirvjhnlaial", "status": true, "datacenter": "datacenter2" }
]

export default class Agent extends React.Component {
    constructor(props) {
        super(props)
        this.closeAgent = this.closeAgent.bind(this);
        this.handleModal = this.handleModal.bind(this);
        this.actionEvent = this.actionEvent.bind(this);
        this.state = {
            redirectToMain: false,
            addAgentModalIsOpen: false,
            actionItems: [
                { label: "Update", action: this.actionEvent },
                { label: "Delete", action: this.actionEvent }
            ]
        }
    }

    actionEvent() {
        console.log("Action called");
        // handle update or edit
    }

    closeAgent() {
        this.props.handleAgent(false);
        this.setState({ redirectToMain: true });
    }

    handleModal(addAgentModalIsOpen = false) {
        console.log("handleModal param ", addAgentModalIsOpen)
        this.setState({ addAgentModalIsOpen })
    }


    render() {
        console.log("Render ", this.state);
        let { addAgentModalIsOpen, redirectToMain } = this.state;

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
            Header: 'Datacenter',
            accessor: 'datacenter',
        },
        {
            Header: 'Status',
            accessor: 'status',
            Cell: row => {
                let { status } = row.original;
                return <div>
                    <span className={`health-bullet ${status ? 'healthy' : 'dead'}`}></span>
                    <span className='health-status'>
                        {status ? "Active" : "Not Active"}
                    </span>
                </div>
            }
        },
        {
            Header: 'Action',
            accessor: '',
            Cell: row => {
                return <div>
                    <Dropdown
                        label={<span className="icon-more btn--xsmall"></span>}
                        size="btn--xsmall"
                        items={this.state.actionItems}>
                    </Dropdown>
                </div>
            }
        }
        ]

        return (<div>
            {redirectToMain && <Redirect to="/" />}

            <Modal isOpen={addAgentModalIsOpen} title="Add Agent" onClose={this.handleModal}>
                <div>
                    Authentication
                        </div>
            </Modal>

            <Screen id="agents" key="agents" className="modal-layer-1" hideFooter={true} title={"Agents"} allowMinimize={false} onClose={this.closeAgent}>

                <div className="dialog-content">
                    <div className="screen-content">

                        <div className="panel  panel-with-header ">
                            <div className="panel-header with-config-group  ">
                                <div className="heading-container">
                                    {/* <div className="panel-label">Agents</div> */}
                                </div>
                                <div className="config-group">

                                    <Button key={"reddetail"}
                                        className="half-margin-left"
                                        size="btn--small"
                                        type="btn--primary-ghost"
                                        onClick={() => { this.handleModal(true) }}>Add Agent</Button>
                                </div>
                            </div>
                            <div className="panel-body ">
                                <Table key={"agentTable"}
                                    loading={false}
                                    className="-striped -highlight"
                                    noDataText="No Agent Found."
                                    data={dummylist}
                                    columns={tableColumns}
                                />
                            </div>
                        </div>

                    </div>
                </div>



            </Screen>
        </div>)
    }

}
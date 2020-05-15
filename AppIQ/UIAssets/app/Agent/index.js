import React from 'react';
import { Redirect } from 'react-router-dom';
import { Screen, Table, Button, Dropdown, Input, Select } from 'blueprint-react';
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
        this.handleFieldChange = this.handleFieldChange.bind(this);
        this.handleSelectChange = this.handleSelectChange.bind(this);
        this.validateField = this.validateField.bind(this);
        this.submitAgent = this.submitAgent.bind(this);

        this.state = {
            redirectToMain: false,
            addAgentModalIsOpen: false,
            actionItems: [
                { label: "Update", action: this.actionEvent },
                { label: "Delete", action: this.actionEvent }
            ],
            agentFields: [{ name: "Protocol", type: "select", mandatory: true },
            { name: "FQDNS", type: "text", mandatory: true },
            { name: "Port", type: "number", mandatory: true },
            { name: "Token", type: "password", mandatory: false }
            ],
            protocolOptions: [
                { label: 'HTTPS', value: 'https', selected: true },
                { label: 'HTTP', value: 'http' }
            ],
            Protocol: "https",
            FQDNS: null,
            Port: null,
            Token: null,
            errormsg: {
                FQDNS: null,
                Port: null
            }
        }
    }

    componentDidCatch(error, info) {
        console.log("ERRROR :===>> ", error, info)
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
        this.setState({ addAgentModalIsOpen })
    }

    validateField(fieldName, value) {
        if (fieldName === "FQDNS" || fieldName === "Port") {
            if (value === "" || value === null || value === undefined) {
                return {
                    isError: true,
                    msg: "Field Required"
                }
            }
        }
        if (fieldName === "FQDNS") {
            // CHEK REGEX
        }
        if (fieldName === "Port") {
            // check regex
        }
        return { isError: false, msg: null }
    }

    handleFieldChange(e) {
        console.log("handlefieldchange ", e.target);
        debugger
        let { name, value } = e.target;
        let validationStatus = this.validateField(name, value);

        let errormsg = this.state.errormsg;
        errormsg[name] = validationStatus.msg;

        this.setState({
            [name]: value,
            errormsg
        })
    }

    handleSelectChange(selected, options) {
        this.setState({
            Protocol: selected[0].value,
            protocolOptions: options
        })
    }

    submitAgent(event) {
        event.preventDefault();
        console.log("Submit agent: ", this.state);
    }

    render() {
        let thiss = this;
        console.log("Render ", this.state);
        let { addAgentModalIsOpen, redirectToMain, agentFields, protocolOptions, errormsg, Port, FQDNS } = this.state;

        const tableColumns = [{
            Header: 'Protocol',
            accessor: 'protocol'
        },
        {
            Header: 'FQDNS:Port',
            accessor: 'ip',
            Cell: row => {
                let { ip, port } = row.original;
                return <div>
                    {ip}:{port}
                </div>
            }
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
                        {status ? "Active" : "Inactive"}
                    </span>
                </div>
            }
        },
        {
            Header: 'Action',
            accessor: '',
            Cell: row => {
                return <div className="right-menu-icons action-btn">
                    <Dropdown
                        label={<span className="icon-more btn--xsmall"></span>}
                        size="btn--xsmall"
                        preferredPlacements={["left", "right"]}
                        items={this.state.actionItems}>
                    </Dropdown>
                </div>
            }
        }
        ]

        function FormField(props) {
            let { name, type, mandatory } = props;

            let labelComp = <span>{name}{mandatory && <span className="mandatory-symbol">*</span>}</span>
            let errorMsg = errormsg[name];

            return (<div className="form-field">
                {
                    (type === "select") ? <Select key={name} items={protocolOptions} onChange={thiss.handleSelectChange} label={labelComp} />
                        :
                        <Input label={labelComp}
                            type={type}
                            key={name}
                            name={name}
                            placeholder={name.toLowerCase()}
                            value={thiss.state[name]}
                            onBlur={thiss.handleFieldChange}
                            onChange={thiss.handleFieldChange}
                            className={errorMsg && "input-error"} />
                }

                {errorMsg && <div class="help-block text-danger"><span class="icon-error"></span><span>{errorMsg}</span></div>}

            </div>)
        }

        let saveAllow = errormsg["Port"] === null && errormsg["FQDNS"] === null && FQDNS && Port

        return (<div>
            {redirectToMain && <Redirect to="/" />}

            <Modal isOpen={addAgentModalIsOpen} title="Add Agent" onClose={this.handleModal}>
                <div>
                    <div className="panel">
                        <form onSubmit={this.submitAgent}>
                            <div className="integration-form">
                                {
                                    agentFields.map(function (elem) {
                                        return FormField(elem)
                                    })
                                }

                                <div className="form-action-buttons">
                                    <Button key={"addagentsave"}
                                        className={!saveAllow && "disabled"}
                                        size="btn--small"
                                        type="btn--primary"
                                    >Add</Button>

                                </div>
                            </div>
                        </form></div>
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
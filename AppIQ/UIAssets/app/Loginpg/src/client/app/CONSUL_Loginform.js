import React from 'react';
import './style.css';
// import { strictEqual } from 'assert';
// import { stringify } from 'querystring';
import {Table,Button, Icon, Input, Label, Radio, Tooltip} from "blueprint-react"
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


// Error messages
const FILL_DETAILS = 'Please fill the details';
const CANT_DELETE_AGENT_AS_SOME_BEEN_WRITTEN = "An agent is being written, can't process this!";


function getCookieVal(offset) {
    var endstr = document.cookie.indexOf(";", offset);
    if (endstr == -1) {
        endstr = document.cookie.length;
    }
    return unescape(document.cookie.substring(offset, endstr));
}

function getCookie(name) {
    var arg = name + "=";
    var alen = arg.length;
    var clen = document.cookie.length;
    var i = 0;
    var j = 0;
    while (i < clen) {
        j = i + alen;
        if (document.cookie.substring(i, j) == arg) {
            return getCookieVal(j);
        }
        i = document.cookie.indexOf(" ", i) + 1;
        if (i === 0) {
            break;
        }
    }
    return null;
}


/**
* @param {string} theUrl The URL of the REST API
*
* @return {string} The response received from portal
*/
function httpGet(theUrl, payload) {
    window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
    window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");
    var xmlHttp = new XMLHttpRequest();

    xmlHttp.open("POST", theUrl, false); // false for synchronous request
    xmlHttp.setRequestHeader("Content-type", "application/json");
    xmlHttp.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
    xmlHttp.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
    xmlHttp.send(JSON.stringify(payload));
    return xmlHttp.responseText;
}

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
    vars[key] = value;
    });
    return vars;
}

// Scroll the table to specific row mentioned @param indextable
function resetScrollInsideTable(indexTable) {
    let tableBody = document.getElementsByClassName('rt-tbody')[indexTable];
    tableBody.scrollTop = 0;
  }

class CONSUL_LoginForm extends React.Component {

    constructor(props) {
        super(props);

        /*
        // ** TEMPORARILY PURPOSE bypass
        const check_payload = {query: `query{
            Check{checkpoint}            
          }`}

        let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
        let checkData = httpGet(url, check_payload);
        try {
            if(JSON.parse(JSON.parse(checkData).data.Check.checkpoint).status_code == "200") {
                if(typeof getUrlVars()['reset'] == "undefined") {
                    window.location.href = "app.html";
                }
            }
        }
        catch(e) {
            console.log('Error collecting checkpoint');
        }
        */

        this.handleSignIn = this.handleSignIn.bind(this);
        this.notify = this.notify.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.removeAgent = this.removeAgent.bind(this);
        this.addAgent = this.addAgent.bind(this);

        this.state = {
                details : [{"protocol" : "http", "ip" : "10.0.0.0", "port" : 8050, "token" : "lnfeialilsacirvjlnlaial", "status" : false},
                {"protocol" : "https", "ip" : "10.0.0.1", "port" : 8051, "token" : "lnfeialilsacirvjlglaial", "status" : true},
                {"protocol" : "http", "ip" : "10.0.0.1", "port" : 8051, "token" : "lnfeialilsacirvjhnlaial", "status" : false}
                ],
            editAgentIndex: null, // [0,1,...n] indicates row number & [-1] indicates a row is added and being written
            editDetailCopy: undefined,
            isNewAgentAdded: false,
        }
    }

    notify(message) {
        toast.error(message, {
            position: toast.POSITION.BOTTOM_CENTER
          });
    }

    handleSignIn(e) {
        e.preventDefault()
        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");
        let username = this.refs.username.value;
        let password = this.refs.password.value;
        let account = this.refs.account.value;
        let ip = this.refs.ip.value;
        let port = this.refs.port.value;
        let signin = this.props.onSignIn;
        let signout = this.props.onSignOut;
        let modal_alert = this.props.alert;
        var payload = {
            query: `query{
  LoginApp(ip:"` + ip + `",port:"` + port + `",username:"` + username + `",account:"` + account + `",password:"` + password + `"){
    loginStatus
  }
}`}
        let xhr = new XMLHttpRequest();
        let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
        let thiss = this;
        try {
            xhr.open("POST", url, false);
            xhr.setRequestHeader("Content-type", "application/json");
            xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    let json = JSON.parse(xhr.responseText);
                    if ('errors' in json) {
                        thiss.notify("Could not login. The query may be invalid.");
                        signout();
                    }
                    else if ('loginStatus' in json.data.LoginApp) {
                        let resp = JSON.parse(json.data.LoginApp.loginStatus)
                        if(resp.status_code == 200) {
                            signin(username, password, account, port, ip);
                            window.location.href = "app.html";
                        }
                        else {
                            thiss.notify(resp.message);
                            signout();
                        }
                    }
                }
                else {
                    thiss.notify("Error while reaching the container.")
                    signout();
                }
            }
            xhr.send(JSON.stringify(payload));
        }
        catch(e) {
            this.notify("Error while logging in.");
        }
    }

    handleChange(index, target) {
        let newDetails = [...this.state.details];
        newDetails[index][target.name] = target.value;
        this.setState({
            details: newDetails
        })
    }
  
    // remove an agent
    removeAgent(index) {
        let {details, isNewAgentAdded} = this.state;
        if (isNewAgentAdded === true && index !== 0){ // new agent being written; while delete other agent
            this.notify(CANT_DELETE_AGENT_AS_SOME_BEEN_WRITTEN);
            return;
        }
        let newDetails = [...details];

        newDetails.splice(index, 1);
        this.setState({ details: newDetails, editAgentIndex: null, editDetailCopy: undefined, isNewAgentAdded: false  });
    }

    // edit an Agent
    editAgent(editAgentIndex) {
        console.log("editeagent");
        this.setState({ 
            editAgentIndex,
            editDetailCopy: Object.assign({}, this.state.details[editAgentIndex])
          });
    }

    // Abort editing Agent
    abortEditAgent(index){
        let newDetail = [...this.state.details];

        if (this.state.editDetailCopy === undefined){
            this.notify("Cant process this");
            return false;
        }
        newDetail[this.state.editAgentIndex] = this.state.editDetailCopy;

        this.setState({
            details: newDetail,
            editDetailCopy: undefined,
            editAgentIndex: null
        })
        return true;
    }

    // Accept the change made while editing
    updateAgent(index){
        let details = this.state.details[index];
        console.log("update agent", details);

        if (!details.ip || !details.port || !details.token ){ // cgeckung if all field added
            this.notify(FILL_DETAILS);
            return;
        }

        this.setState({
            editDetailCopy: undefined,
            editAgentIndex: null,
            isNewAgentAdded: false,
        })
    }

    addAgent() {
        console.log("Add agent");
        // Scroll to top
        resetScrollInsideTable(0);

        let {details} = this.state;
        details.unshift({
            ip: '',
            port: '',
            token: '',
            protocol: null,
            status: undefined
        })
        this.setState({ details, editAgentIndex: 0, isNewAgentAdded: true }); // isNewAgentAdded == true indicate a row has been written
    }

    render() {
    let { editAgentIndex } = this.state;
    console.log("Render state: ", this.state);

    const tableColumns = [  {
        header: 'protocol',
        accessor: 'protocol',
        Cell: props => <span className="radio-grp">
            <Radio name={"protocol"+props.index} value="http" checked={props.original.protocol==="http"} label="http" disabled={props.index!==editAgentIndex} onChange={(e)=> this.handleChange(props.index, { name: "protocol", value:"http"})} />
            <Radio name={"protocol"+props.index} value="https" checked={props.original.protocol==="https"} label="https" disabled={props.index!==editAgentIndex} onChange={(e)=> this.handleChange(props.index, { name: "protocol", value:"https"})} />
        </span>
    },
    {
        header: 'ip',
        accessor: 'ip',
        Cell: props => {
            return  <Input placeHolder="ip" disabled={props.index!==editAgentIndex} value={props.original.ip} name={"ip"} onChange={(e) => this.handleChange(props.index, e.target)} />
        }
    },
    {
        header: 'Port',
        accessor: 'port',
        Cell: props =>  <Input placeHolder="port" disabled={props.index!==editAgentIndex} value={props.original.port}  name={"port"} onChange={(e) => this.handleChange(props.index, e.target)} />
    },
    {
        header: 'Token',
        accessor: 'token',
        width:200,
        Cell: props =>  <Input placeHolder="token" disabled={props.index!==editAgentIndex} value={props.original.token}  name={"token"} onChange={(e) => this.handleChange(props.index, e.target)} />
    }, 
    {
        header: 'status',
        accessor: 'status',
        Cell: props => {
        let { status } = props.original;
        if (status === true) {
            return <span className="label-connection"> <Label theme={"label--success"} size={"MEDIUM"}>Connected</Label> </span> 
        } else if (status === false) {
            return <span className="label-connection"> <Label theme={"label--danger"} size={"MEDIUM"}>Disconnected</Label>  </span>
        }
        }
    },
    {
        accessor: '',
        Cell: props =>  {
            if (props.index === editAgentIndex) { // Update an agent; to show [Update, Abort, Delete]
                return <React.Fragment>
                <Icon style={{margin:"5px"}} className="no-link toggle pull-right" size="icon-small" type="icon-check" onClick={()=>this.updateAgent(props.index)}></Icon>

                {/* if new agent being written; dont show abort */}
                {(this.state.isNewAgentAdded === false) && <Icon style={{margin:"5px"}} className="no-link toggle pull-right" size="icon-small" type=" icon-exit-outline" onClick={()=>this.abortEditAgent(props.index)}></Icon> }

                <Tooltip key={"delete"} title={"title"} content={"Delete"} placement={"auto"}>
                        <Icon className="no-link toggle pull-right" size="icon-small" type="icon-delete" onClick={()=>this.removeAgent(props.index)}></Icon>
                    </Tooltip>
                 </React.Fragment>
            }
            else if (editAgentIndex === null){ // no action on row; to show [Edit, delete]
                return <React.Fragment>
                    <Tooltip key={"title"} title={"title"} content={"Edit"} placement={"auto"}>
                            <Icon className="no-link toggle pull-right" size="icon-small" type="icon-edit" onClick={()=>this.editAgent(props.index)}></Icon>
                    </Tooltip>
                    <Tooltip key={"delete"} title={"title"} content={"Delete"} placement={"auto"}>
                        <Icon className="no-link toggle pull-right" size="icon-small" type="icon-delete" onClick={()=>this.removeAgent(props.index)}></Icon>
                    </Tooltip>
                </React.Fragment>
            } else {    // only show delete
                return <Tooltip key={"delete"} title={"title"} content={"Delete"} placement={"auto"}>
                    <Icon className="no-link toggle pull-right" size="icon-small" type="icon-delete" onClick={()=>this.removeAgent(props.index)}></Icon>
                </Tooltip>
            }
        }
    }
    ]   

    return (
            <div className="login-form">
            <ToastContainer />
            <center>
                <Table style={{width:"90%", maxHeight: "35%"}} data={this.state.details} columns={tableColumns} minRows={0} showPagination={false} TheadComponent={props => null}>
                </Table>
            </center>
         
            <form onSubmit={(event)=> { event.preventDefault();}}>
                <center>
                    <br/>
                    <Button style={{ marginRight: "20px"}} disabled={editAgentIndex!==null} type="btn--success" size="btn--small" onClick={this.addAgent}>Add Agent</Button>
                    <input style={{color:"white"}} type="button" disabled={editAgentIndex!==null} value="Login" className="button view-button" onClick={()=> window.location.href = "app.html"}/>
                </center>
            </form>
            </div>
        )
    }
}

export default CONSUL_LoginForm;

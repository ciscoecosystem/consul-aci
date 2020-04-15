import React from 'react';
import './style.css';
// import { strictEqual } from 'assert';
// import { stringify } from 'querystring';
import {Table,Button, Icon, Input, Label, Radio, Tooltip, Loader} from "blueprint-react"
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


// Error messages
const FILL_DETAILS = 'Please fill the details';
const CANT_DELETE_AGENT_AS_SOME_BEEN_WRITTEN = "An agent is being written, can't process this!";
// const QUERY_URL="http://127.0.0.1:5000/graphql.json";
const QUERY_URL = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";


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
        console.log("In httpget request.......");
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

        this.notify = this.notify.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.removeAgent = this.removeAgent.bind(this);
        this.addAgent = this.addAgent.bind(this);
        this.readAgentsCall = this.readAgentsCall.bind(this);
        this.removeAgentCall = this.removeAgentCall.bind(this);
        this.addAgentCall = this.addAgentCall.bind(this);

        this.state = {
                details : [],
            editAgentIndex: null, // [0,1,...n] indicates row number & [-1] indicates a row is added and being written
            editDetailCopy: undefined,
            isNewAgentAdded: false,
            readAgentLoading: false
        }
    }

    componentDidMount() {
        console.log("Component Did mount loginform");  
        let thiss = this;  

        this.setState({ readAgentLoading: true});  
        setTimeout(function(){ thiss.readAgentsCall() }, 0 ); // making async function.. fix for now
    }

    notify(message) {
        toast.error(message, {
            position: toast.POSITION.BOTTOM_CENTER
          });
    }

    readAgentsCall() {
        this.setState({ readAgentLoading: true})
        const payload = {query: `query{
            ReadCreds{creds}
        }`}

        try {
            // let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
            let checkData = httpGet(QUERY_URL, payload);
            console.log("== > cehckdata", checkData );

            let credsData = JSON.parse(JSON.parse(checkData).data.ReadCreds.creds);
            if(credsData.status_code == "200") {
                this.setState({ details: credsData.payload })
            } else {
                this.notify("Something went wrong")
            }
        }
        catch(e) {
            console.log('Error getting agents');
        }
        finally {
            this.setState({ readAgentLoading: false})
        }

    }

    addAgentCall(agentDetail) {
        let { isNewAgentAdded } = this.state;
        
        delete agentDetail.status;
        agentDetail.port = parseInt(agentDetail.port);
        console.log("agentDetail", agentDetail);

        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");

        let payload = {};
        
        if (isNewAgentAdded){
            payload = { query: `query{
                WriteCreds(agentList: ${JSON.stringify(JSON.stringify([agentDetail]))} ){creds}
            }`}
        } else {
            let editDetailCopy  = Object.assign({}, this.state.editDetailCopy);
            delete editDetailCopy.status;
            delete editDetailCopy.token;
            editDetailCopy.port = parseInt(editDetailCopy.port);

            let dataInput = {
                "oldData" : editDetailCopy,
                "newData" : agentDetail
            }

            payload = { query: `query{
                UpdateCreds(updateInput: ${JSON.stringify(JSON.stringify(dataInput))}){creds}
            }`}
        }

        let xhr = new XMLHttpRequest();
        // let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
        let thiss = this;
        try {
            xhr.open("POST", QUERY_URL, false);
            xhr.setRequestHeader("Content-type", "application/json");
            xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    let json = JSON.parse(xhr.responseText);
                    console.log("response json ", json);

                    if ('errors' in json) {
                        thiss.notify("Could not Fetch. The query may be invalid.");  
                    }
                    else if ( ('WriteCreds' in json.data && 'creds' in json.data.WriteCreds ) ||
                                ('UpdateCreds' in json.data && 'creds' in json.data.UpdateCreds )
                    ) {
                        let resp = (isNewAgentAdded) ? JSON.parse(json.data.WriteCreds.creds) : JSON.parse(json.data.UpdateCreds.creds) ;

                        if(resp.status_code == 200) {
                            console.log("Its 200; alling readagentCalls");
                            toast.success("Agent added successfully", {
                                position: toast.POSITION.BOTTOM_CENTER
                            });
                            thiss.readAgentsCall();
                        }
                        else {
                            thiss.notify(resp.message);
                        }
                    }
                }
                else {
                    thiss.notify("Error while reaching the container.")
                }
            }
            xhr.send(JSON.stringify(payload));
        }
        catch(e) {
            this.notify("Error while logging in.");
            this.setState({ readAgentLoading: false})
        }
      
    }

    removeAgentCall(agentDetail) {
        delete agentDetail.status;
        agentDetail.port = parseInt(agentDetail.port);
        console.log("agentDetail", agentDetail);

        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");

        // let payload = { query: `query{
        //     WriteCreds(agentList: ${JSON.stringify(JSON.stringify([agentDetail]))} ){creds}
        // }`}
        // { "query": 'query{DeleteCreds(agentData:){message}}'}
        let payload = { query: `query{
            DeleteCreds(agentData: ${JSON.stringify(JSON.stringify(agentDetail))} ){message}
        }`}
        console.log("==> patload ", payload);

        let xhr = new XMLHttpRequest();
        // let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
        let thiss = this;
        try {
            xhr.open("POST", QUERY_URL, false);
            xhr.setRequestHeader("Content-type", "application/json");
            xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    let json = JSON.parse(xhr.responseText);
                    console.log("response json ", json);

                    if ('errors' in json) {
                        thiss.notify("Could not Fetch. The query may be invalid.");   
                    }
                    else if ('message' in json.data.DeleteCreds) {
                        let resp = JSON.parse(json.data.DeleteCreds.message)
                        if(resp.status_code == 200) {
                            console.log("Its 200; working delete call");
                            toast.success("Agent "+agentDetail.ip+" removed successfully", {
                                position: toast.POSITION.BOTTOM_CENTER
                            });
                            thiss.readAgentsCall();
                        }
                        else {
                            thiss.notify(resp.message);
                        }
                    }
                    else {
                        thiss.notify("Something went wrong!")
                    }
                }
                else {
                    thiss.notify("Error while reaching the container.")
                }
            }
            xhr.send(JSON.stringify(payload));
        }
        catch(e) {
            this.notify("Error while logging in.");
            this.setState({ readAgentLoading: false})
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
        if (isNewAgentAdded === true){
            newDetails.splice(index, 1);
            this.setState({ details: newDetails, editAgentIndex: null, editDetailCopy: undefined, isNewAgentAdded: false  });
        }
       
        this.setState({ readAgentLoading: true});
        let thiss = this;
        setTimeout(function(){ 
                thiss.removeAgentCall(Object.assign({}, newDetails.splice(index, 1)[0] ) ) 
        }, 0)

        // newDetails.splice(index, 1);
        // this.setState({ details: newDetails, editAgentIndex: null, editDetailCopy: undefined, isNewAgentAdded: false  });
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

        if (!details.ip || !details.port || !details.token || !details.protocol ){ // cgeckung if all field added
            this.notify(FILL_DETAILS);
            return;
        }

            let thiss = this;
            this.setState({ readAgentLoading: true}, function() {
                setTimeout(function(){ 
                    thiss.addAgentCall(Object.assign({}, details))
                    
                    thiss.setState({
                        editDetailCopy: undefined,
                        editAgentIndex: null,
                        isNewAgentAdded: false,
                    })
                }, 0)
            });       
    }

    addAgent() {
        console.log("Add agent");
        // Scroll to top
        resetScrollInsideTable(0);

        let {details} = this.state;
        details.unshift({
            ip: '',
            port: 'http',
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
        Cell: props => {
            let { protocol } = props.original;
            console.log("protocol of "+props.index + "is ", protocol)
        return <span className="radio-grp">
            <Radio key={"protocol"+props.index} name={"protocol"+props.index} value="http" label="http" 
                   checked={protocol === "http"} disabled={props.index!==editAgentIndex} onChange={(e)=> this.handleChange(props.index, { name: "protocol", value:"http"})} />
   
            <Radio key={"protocol"+props.index} name={"protocol"+props.index} value="https" label="https"
                   checked={protocol === "https"} disabled={props.index!==editAgentIndex} onChange={(e)=> this.handleChange(props.index, { name: "protocol", value:"https"})} />
        </span>
        }
    },
    {
        header: 'ip',
        accessor: 'ip',
        Cell: props => {
            return  <Input key={"ip"+props.index} placeHolder="ip" disabled={props.index!==editAgentIndex} value={props.original.ip} name={"ip"} onChange={(e) => this.handleChange(props.index, e.target)} />
        }
    },
    {
        header: 'Port',
        accessor: 'port',
        Cell: props =>  <Input key={"port"+props.index} placeHolder="port" disabled={props.index!==editAgentIndex} value={props.original.port}  name={"port"} onChange={(e) => this.handleChange(props.index, e.target)} />
    },
    {
        header: 'Token',
        accessor: 'token',
        width:200,
        Cell: props =>  <Input key={"token"+props.index} placeHolder="token" type={(props.index!==editAgentIndex) ? "password":"text"} disabled={props.index!==editAgentIndex} value={props.original.token}  name={"token"} onChange={(e) => this.handleChange(props.index, e.target)} />
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
                <Icon key={"updateagent"} style={{margin:"5px"}} className="no-link toggle pull-right" size="icon-small" type="icon-check" onClick={()=>this.updateAgent(props.index)}></Icon>

                {/* if new agent being written; dont show abort */}
                {(this.state.isNewAgentAdded === false) && <Icon key={"abortagent"} style={{margin:"5px"}} className="no-link toggle pull-right" size="icon-small" type=" icon-exit-outline" onClick={()=>this.abortEditAgent(props.index)}></Icon> }

                    <Icon key={"removeagent"} className="no-link toggle pull-right" size="icon-small" type="icon-delete" onClick={()=>this.removeAgent(props.index)}></Icon>
                 </React.Fragment>
            }
            else if (editAgentIndex === null){ // no action on row; to show [Edit, delete]
                return <React.Fragment>
                        <Icon key={"editagent"} className="no-link toggle pull-right" size="icon-small" type="icon-edit" onClick={()=>this.editAgent(props.index)}></Icon>
                        <Icon key={"removeagent2"} className="no-link toggle pull-right" size="icon-small" type="icon-delete" onClick={()=>this.removeAgent(props.index)}></Icon>
                </React.Fragment>
            } else {    // only show delete
                return <Icon key={"removeagent3"} className="no-link toggle pull-right" size="icon-small" type="icon-delete" onClick={()=>this.removeAgent(props.index)}></Icon>
            }
        }
    }
    ]   

    return (
            <div className="login-form">
            <ToastContainer />
            <center>
                {(this.state.readAgentLoading) ? <span>loading.. <Loader> loading </Loader>  </span>:
                <Table key={"agentTable"} loading={this.state.readAgentLoading} style={{width:"90%", maxHeight: "35%"}} data={this.state.details} columns={tableColumns} minRows={3} showPagination={false} TheadComponent={props => null}>
                </Table>}
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

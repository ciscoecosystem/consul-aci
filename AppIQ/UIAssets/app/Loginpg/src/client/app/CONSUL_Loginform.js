import React from 'react';
import './style.css';
import {Table,Button, Icon, Input, Label, Loader, IconButton} from "blueprint-react"
import { ToastContainer, toast } from 'react-toastify';
import { PROFILE_NAME } from '../../../../../constants.js';
import 'react-toastify/dist/ReactToastify.css';


// Error messages
const FILL_DETAILS = 'Please fill the details';
const CANT_DELETE_AGENT_AS_SOME_BEEN_WRITTEN = "An agent is being written, can't process this!";
// const QUERY_URL="http://127.0.0.1:5000/graphql.json";
const QUERY_URL = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";

const dummylist = [
    {"protocol" : "http", "ip" : "10.0.0.0", "port" : 8050, "token" : "lnfeialilsacirvjlnlaial", "status" : true, "datacenter" : "datacenter1"},
    {"protocol" : "https", "ip" : "10.0.0.1", "port" : 8051, "token" : "lnfeialilsacirvjlglaial", "status" : false, "datacenter" : "datacenter1"},
    {"protocol" : "http", "ip" : "10.0.0.2", "port" : 8051, "token" : "lnfeialilsacirvjhnlaial", "status" : true, "datacenter" : "datacenter2"}
]

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

// Scroll the table to specific row mentioned @param indextable
function resetScrollInsideTable(indexTable) {
    let tableBody = document.getElementsByClassName('rt-tbody')[indexTable];
    tableBody.scrollTop = 0;
  }

class CONSUL_LoginForm extends React.Component {

    constructor(props) {
        super(props);

        this.notify = this.notify.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.removeAgent = this.removeAgent.bind(this);
        this.addAgent = this.addAgent.bind(this);
        this.readAgentsCall = this.readAgentsCall.bind(this);
        this.removeAgentCall = this.removeAgentCall.bind(this);
        this.addAgentCall = this.addAgentCall.bind(this);
        this.abortEditAgent = this.abortEditAgent.bind(this);
        this.abortUpdateAgentAction = this.abortUpdateAgentAction.bind(this);
        this.loadAgentList = this.loadAgentList.bind(this);

        this.state = {
            details : [],
            editAgentIndex: null, // [0,1,...n] indicates row number & [-1] indicates a row is added and being written
            editDetailCopy: undefined,
            isNewAgentAdded: false,
            readAgentLoading: false,
            tenantName: this.props.tenantName
        }
    }

    componentDidMount() {
        console.log("Component Did mount loginform");  
        this.loadAgentList();
    }

    loadAgentList(){
        let thiss = this;
        this.setState({ readAgentLoading: true});  
        setTimeout(function(){ thiss.readAgentsCall() }, 0 ); // making async function.. fix for now
    }

    notify(message, isSuccess = false, isWarning = false) {
        isWarning ?  toast.warn(message, {
            position: toast.POSITION.BOTTOM_CENTER
            }) :
        isSuccess ?  toast.success(message, {
            position: toast.POSITION.BOTTOM_CENTER
            }) :
            toast.error(message, {
            position: toast.POSITION.BOTTOM_CENTER
          });
    }

    handleChange(index, target) {
        let newDetails = [...this.state.details];
        newDetails[index][target.name] = target.value;
        this.setState({
            details: newDetails
        })
    }

    abortUpdateAgentAction() {
        let { isNewAgentAdded , details} = this.state;

        if (isNewAgentAdded){ // new agent being added
            // remove first element from details
            details.shift();
            this.setState({ details });
        } 
        else {  // existing agent being updated
            // abort edit and show exsising data 
            this.abortEditAgent();
        }
    }

    readAgentsCall() {
        this.setState({ readAgentLoading: true})
        const payload = {query: `query{
            ReadCreds{creds}
        }`}
        let isDetail = false;
        try {
            let checkData = httpGet(QUERY_URL, payload);
            console.log("== > data", checkData );

            let credsData = JSON.parse(JSON.parse(checkData).data.ReadCreds.creds);
            if(credsData.status_code == "200") {
                this.setState({ details: credsData.payload })

                // to check if more than 1 detail exists
                if (credsData.payload.length > 0){
                    isDetail = true;
                }
            } else {
                this.notify("Error while fetching agent information please refresh")
            }
        }
        catch(e) {
            this.notify("Error while fetching agent information please refresh")
            console.error('Error getting agents',e);
        }
        finally {
            this.setState({ readAgentLoading: false});
            // if no data found then initial add agent form
            if (!isDetail) {
                this.addAgent();
            }
        }

    }

    // make sure everytim it updates
    shouldComponentUpdate(nextProps, nextState){
        console.log("Shouldcomponentupdate ", nextProps, nextState);
        return true;
    }

    addAgentCall(agentDetail, updateIndex) {
        if (JSON.stringify(this.state.editDetailCopy) === JSON.stringify(agentDetail)) { // no change in copy
            console.log("no change");
            return;
        }
        console.log("updateIndex = ", updateIndex );
        let { isNewAgentAdded, details } = this.state;
        
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

                            if (isNewAgentAdded){ // new agent added
                                console.log("In write response ", resp);
                                if (resp.payload && resp.payload.length > 0){
                                    details[updateIndex] = resp.payload[0];
                                    thiss.setState({ details });

                                     // connection is not true
                                    if (resp.payload.status !== true && resp.message){
                                        this.notify(resp.message, false, true);
                                        // thiss.notify("Connection could not be established for "+ details[updateIndex].ip +":" + details[updateIndex].port ,false, true)
                                    }
                                } else {
                                    thiss.abortUpdateAgentAction();
                                    thiss.notify("Some technical glitch!");
                                }

                            } else { // updated an agent
                                // thiss.notify("Agent updated successfully", true);

                                if (resp.payload){
                                    details[updateIndex] = resp.payload;
                                    thiss.setState({ details });

                                    // connection is not true
                                    if (resp.payload.status !== true && resp.message){
                                        this.notify(resp.message, true);
                                        // thiss.notify("Connection could not be established for "+ resp.payload.ip +":" + resp.payload.port, false, true)
                                    }
                                } else {
                                    thiss.abortUpdateAgentAction();
                                    thiss.notify("Some technical glitch!");
                                }
                            }
                        }
                        else {
                            thiss.abortUpdateAgentAction();
                            thiss.notify(resp.message);
                        }
                    }
                }
                else {
                    thiss.abortUpdateAgentAction();
                    thiss.notify("Error while reaching the container.")
                }
            }
            xhr.send(JSON.stringify(payload));
        }
        catch(e) {
            console.error("Error api addAgentCall", e);
            // this.notify("Error while logging in.");
            this.abortUpdateAgentAction();
        }
        finally {
            this.setState({ readAgentLoading: false})
        }
      
    }

    removeAgentCall(agentDetail, deleteIndex) {
        delete agentDetail.status;
        agentDetail.port = parseInt(agentDetail.port);
        console.log("agentDetail", agentDetail);

        let { details } = this.state;

        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");

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
                            // thiss.notify("Agent "+agentDetail.ip+" removed successfully", true);

                            details.splice(deleteIndex, 1);
                            thiss.setState({ details });
                        }
                        else {
                            thiss.notify(resp.message);
                        }
                    }
                    else {
                        thiss.notify("Something went wrong!")
                        console.log("DelCrefs: response structure invalid")
                    }
                }
                else {
                    thiss.notify("Error while reaching the container.")
                }
            }
            xhr.send(JSON.stringify(payload));
        }
        catch(e) {
            console.error("Error api removeagent", e);
        }
        finally {
            this.setState({ readAgentLoading: false, editAgentIndex: null, editDetailCopy: undefined, isNewAgentAdded: false })
        }
    }
  
    // remove an agent
    removeAgent(index) {
        let {details, isNewAgentAdded} = this.state;

        if (isNewAgentAdded === true && index !== 0){ // new agent being written; while delete other agent
            this.notify(CANT_DELETE_AGENT_AS_SOME_BEEN_WRITTEN);
            return;
        }
        
        let newDetails = [...details];
        if (isNewAgentAdded === true){ // its internal to delete, no api call so clear state and return 
            newDetails.splice(index, 1);
            this.setState({ details: newDetails, editAgentIndex: null, editDetailCopy: undefined, isNewAgentAdded: false  });
            return; 
        }
       
        this.setState({ readAgentLoading: true});
        let thiss = this;
        setTimeout(function(){ 
                thiss.removeAgentCall(Object.assign({}, newDetails.splice(index, 1)[0] ), index ) 
        }, 0)

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
    abortEditAgent(){
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
        let { details } = this.state;
        let updatingAgentDetail = details[index];
        console.log("update agent", updatingAgentDetail);

        if (!updatingAgentDetail.protocol) { this.notify("Protocol required, please select."); return; }
        if (!updatingAgentDetail.ip) { this.notify("Ip / Dns required, please enter."); return; }
        if (!updatingAgentDetail.port) { this.notify("Port required, please enter."); return; }

         // check if Details in Index is not same as others in [...Details] as per port and ip
        for (let ind=0; ind < details.length; ind++) {
            if (index === ind) continue;
            if (details[ind].ip === updatingAgentDetail.ip && parseInt(details[ind].port) === parseInt(updatingAgentDetail.port) ){
                console.log("same as @", ind);
                this.notify("Agent already exists.")
                return;
            }
        }
        
        let thiss = this;
        this.setState({ readAgentLoading: true}, function() {
            setTimeout(function(){ 
                thiss.addAgentCall(Object.assign({}, updatingAgentDetail), index)
                   
                thiss.setState({
                    editDetailCopy: undefined,
                    editAgentIndex: null,
                    isNewAgentAdded: false,
                    readAgentLoading: false
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
            port: '',
            token: '',
            datacenter: null,
            protocol: "http",
            status: undefined
        })
        this.setState({ details, editAgentIndex: 0, isNewAgentAdded: true }); // isNewAgentAdded == true indicate a row has been written
    }

    render() {
    let { editAgentIndex, tenantName, readAgentLoading } = this.state;

    // Handle redirection to page 
    function handleMapClick(profileNameValue) {
        localStorage.setItem(PROFILE_NAME, profileNameValue);
        window.location.href = `mapping.html?&${PROFILE_NAME}=` + encodeURIComponent(profileNameValue) + "&tn=" + encodeURIComponent(tenantName);
    }
    function handleViewClick(profileNameValue) {
        window.location.href = `tree.html?${PROFILE_NAME}=` + encodeURIComponent(profileNameValue) + "&tn=" + encodeURIComponent(tenantName);
    }
    function handleDetailsClick(profileNameValue) {
        window.location.href = `details.html?${PROFILE_NAME}=` + encodeURIComponent(profileNameValue) + "&tn=" + encodeURIComponent(tenantName);
    }

    const tableColumns = [  {
        header: 'protocol',
        accessor: 'protocol',
        Cell: props => {
            let { protocol } = props.original;
            return <span className="radio-grp">
            <label>
              <input
              id={"http"+props.index}
              id={"http"+props.index}
              type="radio"
              value="http"
              disabled={props.index!==editAgentIndex}
              checked={protocol === "http"}
              onChange={(e)=> {
                  this.handleChange(props.index, { name: "protocol", value:"http"}) 
                }
              } 
            />
                http
            </label>&nbsp;&nbsp;
            <label>
              <input
              id={"http"+props.index}
              name={"http"+props.index}
              type="radio"
              value="https"
              disabled={props.index!==editAgentIndex}
              checked={protocol === "https"}
              onChange={(e)=> this.handleChange(props.index, { name: "protocol", value:"https"})}
            />
                https
            </label>
         </span>
        }
    },
    {
        header: 'ip',
        accessor: 'ip',
        Cell: props => {
            return  <Input key={"ip"+props.index} placeHolder="ip / dns" disabled={props.index!==editAgentIndex} value={props.original.ip} name={"ip"} onChange={(e) => this.handleChange(props.index, e.target)} />
        }
    },
    {
        header: 'Port',
        accessor: 'port',
        Cell: props =>  <Input key={"port"+props.index} type="number" placeHolder="port" disabled={props.index!==editAgentIndex} value={props.original.port} name={"port"} onChange={(e) => this.handleChange(props.index, e.target)} />
    },
    {
        header: 'Token',
        accessor: 'token',
        width:200,
        Cell: props =>  <Input key={"token"+props.index} placeHolder="token" type={(props.index!==editAgentIndex) ? "password":"text"} disabled={props.index!==editAgentIndex} value={props.original.token}  name={"token"} onChange={(e) => this.handleChange(props.index, e.target)} />
    }, 
    {
        header: 'Datacenter',
        accessor: 'datacenter',
        Cell: props => (props.original.datacenter === null) ? (<i>datacenter</i>) : props.original.datacenter
    },
    {
        header: 'status',
        accessor: 'status',
        width: 70,
        Cell: props => {
        let { status } = props.original;
        if (status === true) {
            return <Label theme={"label--success label--circle"} size={"MEDIUM"}></Label> 
        } else if (status === false) {
            return <Label theme={"label--danger label--circle"} size={"MEDIUM"}></Label>
        } else {
            return <Label theme={"label--ltgray label--circle"} size={"MEDIUM"}></Label>
        }
        }
    },
    {
        accessor: '',
        Cell: props =>  {
            let isSomeAgentInEditMode = (editAgentIndex !== null && props.index !== editAgentIndex);

            if (props.index === editAgentIndex) { // Update an agent; to show [Update, Abort, Delete]
                return <React.Fragment>
                <Icon key={"updateagent"} style={{margin:"5px"}} className="no-link toggle pull-right" size="icon-small" type="icon-check" onClick={()=>this.updateAgent(props.index)}></Icon>

                {/* if new agent being written; dont show abort */}
                {(this.state.isNewAgentAdded === false) && <Icon key={"abortagent"} style={{margin:"5px"}} className="no-link toggle pull-right" size="icon-small" type=" icon-exit-outline" onClick={()=>this.abortEditAgent()}></Icon> }

                    <Icon key={"removeagent"} className="no-link toggle pull-right" size="icon-small" type="icon-delete" onClick={()=>this.removeAgent(props.index)}></Icon>
                 </React.Fragment>
            }
            else { // no action on row; to show [Edit, delete]
                return <React.Fragment>
                        <Icon key={"editagent"} disabled={isSomeAgentInEditMode} className="no-link toggle pull-right" size="icon-small" type="icon-edit" onClick={()=>this.editAgent(props.index)}></Icon>
                        <Icon key={"removeagent2"} disabled={isSomeAgentInEditMode} className="no-link toggle pull-right" size="icon-small" type="icon-delete" onClick={()=>this.removeAgent(props.index)}></Icon>
                </React.Fragment>
            }
        }
    }
    ]

    return (
            <div className="login-form">
            <ToastContainer />
            <center>
            <div className="row toolbar" style={{width: "90%", background: "unset", marginBottom: "10px"}}>
                <div className="col-md-12" style={{textAlign:"center"}}>

                  {/* <Button style={{ marginRight: "20px"}} disabled={editAgentIndex!==null} type="btn--success" size="btn--small" onClick={this.addAgent}>Add Agent</Button> */}
             
                <span className="pull-right">
                    <IconButton
                        type="btn--icon btn--gray-ghost"
                        size="btn--small"
                        icon="icon-plus"
                        disabled={editAgentIndex!==null || readAgentLoading === true} 
                        onClick={this.addAgent}
                   />
                     <IconButton
                        type="btn--icon btn--gray-ghost"
                        size="btn--small"
                        icon="icon-refresh"
                        disabled={editAgentIndex!==null || readAgentLoading === true} 
                        onClick={this.loadAgentList}
                   />
                </span>
                  
                </div>
            </div>
            </center> 

            <div>
            <center>
                {(this.state.readAgentLoading) ? <span>loading.. <Loader> loading </Loader>  </span>:
                <Table key={"agentTable"} 
                loading={this.state.readAgentLoading} style={{width:"90%", maxHeight: "35%"}} 
                data={this.state.details} 
                columns={tableColumns} 
                minRows={1} 
                showPagination={false} 
                SubComponent={row => {
                    let { datacenter, status } = row.original;
                    /* Dont show [Detail, operations And Map] 
                        when connection not true &
                             agent in edit state
                    */
                    if (status !== true || editAgentIndex === row.index) return undefined; 
                    return (
                      <Table
                        data={[{spaceCol:"",btnCol:""}]}
                        columns={[
                                { 
                                     accessor:"spaceCol"
                                },
                                { 
                                      accessor:"btnCol",
                                       Cell: props => {
                                        return <div>
                                            <Button key={"reddetail"} className="half-margin-left" size="btn--small" type="btn--secondary" onClick={()=>{ handleDetailsClick(datacenter) }}>Details</Button>
                                            <Button key={"redmap"} className="half-margin-left" size="btn--small" type="btn--secondary" onClick={()=>{ handleMapClick(datacenter) }}>Map</Button>
                                            <Button key={"redview"} className="half-margin-left" size="btn--small" type="btn--secondary" onClick={()=>{ handleViewClick(datacenter) }}>Operational</Button>
                                           </div>
                                        } 
                                }
                        ]}
                        noDataText={"No services found"}
                        defaultPageSize={100}
                        minRows={0}
                        showPagination={false}
                        TheadComponent={props => null} />
                    )
                  }}
                TheadComponent={props => null}>
                </Table>}
            </center>
            </div>
            </div>
        )
    }
}

export default CONSUL_LoginForm;

import React, { Component } from 'react'
import Header from './Header'
import DetailsTable from './DetailsTable'
import './style.css'
import DataTable from "./DataTable"
import { PROFILE_NAME, DC_DETAILS_QUERY_PAYLOAD } from "../../constants.js";

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

var params_appid;
var params_tn;
var details_raw;

var urlToParse = location.search;
var urlParams = {};
urlToParse.replace(
    new RegExp("([^?=&]+)(=([^&]*))?", "g"),
    function ($0, $1, $2, $3) {
        urlParams[$1] = $3;
    }
);
var result = urlParams;

var headerInstanceName;

class Container extends Component {
    constructor(props) {
        super(props);

        this.getData = this.getData.bind(this);
        this.reload = this.reload.bind(this);
        this.fetchData = this.fetchData.bind(this);
    
        params_tn = result['tn'];



        this.state = {
            "data": [],
            loading: true,
            expanded: {}
        };

        this.handleBackClick = this.handleBackClick.bind(this);
        this.CONSUL_setExpand = this.CONSUL_setExpand.bind(this);
        this.CONSUL_resetExpanded = this.CONSUL_resetExpanded.bind(this);

        let reloader = setInterval(this.reload, 30000);
    }
    componentDidMount() {
        this.fetchData();
    }

    getData() {
        /**
        * Use this.httpGet to get data from REST API
        */
       let payload = DC_DETAILS_QUERY_PAYLOAD(result['tn']);
        // let payload = {
        //     query: 'query{Details(tn:"' + result['tn'] + '",appId:"' + result['appId'] + '"){details}}'
        // }

        details_raw = "[]";
        try {
            let main_data_raw = this.httpGet(document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json", payload);
            let rawJsonData = JSON.parse(JSON.parse(main_data_raw).data.Details.details)
            let main_data_json = JSON.parse(main_data_raw);

            if ('errors' in main_data_json) {
                // Error related to query
                localStorage.setItem('message', JSON.stringify(main_data_json.errors));
                const message_set = true;
                window.location.href = "app.html?gqlerror=1";
            }
            else {
                if (rawJsonData.status_code != "200") {
                    // Problem with backend fetching data
                    const message = {
                        "errors": [{
                            "message": rawJsonData.message
                        }]
                    }
                    localStorage.setItem('message', JSON.stringify(message.errors));
                    const message_set = true;
                    window.location.href = "app.html?gqlerror=1";
                }
                else {
                    // Success
                    headerInstanceName = rawJsonData.agentIP; // CONSUL change :replacing instanceName with agent ip
                    this.setState({ loading: false })
                    details_raw = JSON.parse(main_data_raw).data.Details.details;
                    this.setState({
                        "data": JSON.parse(details_raw).payload
                    });
                }
            }
        }
        catch (e) {
            // Problem fetching data
            if (typeof message_set == 'undefined') {
                const message = {
                    "errors": [{
                        "message": "Error while fetching data for details."
                    }]
                }
                localStorage.setItem('message', JSON.stringify(message.errors));
            }
            window.location.href = "app.html?gqlerror=1";
        }
    }


    /**
    * @param {string} theUrl The URL of the REST API
    *
    * @return {string} The response received from portal
    */
    httpGet(theUrl, payload) {
        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");
        var xmlHttp = new XMLHttpRequest();

        xmlHttp.open("POST", theUrl, true); // false for synchronous request
        xmlHttp.setRequestHeader("Content-type", "application/json");
        xmlHttp.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
        xmlHttp.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
        xmlHttp.send(JSON.stringify(payload));
        return xmlHttp.responseText;
    }

    fetchData() {
    
        let payload = DC_DETAILS_QUERY_PAYLOAD(result['tn']);
        // let payload = {
        //     query: 'query{Details(tn:"' + result['tn'] + '",appId:"' + result['appId'] + '"){details}}'
        // }
        console.log(payload);
        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");
    
        let xhr = new XMLHttpRequest();
        let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
        try {
          xhr.open("POST", url, true);
    
          xhr.setRequestHeader("Content-type", "application/json");
          xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
          xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
    
          xhr.onreadystatechange = () => {
            
            console.log("Sending req");
            if (xhr.readyState == 4) {
              if (xhr.status == 200) {
                let json = JSON.parse(xhr.responseText);

                console.log(json);
                if ("errors" in json) {
                  // Error related to query
                  localStorage.setItem('message', JSON.stringify(main_data_json.errors));
                  const message_set = true;
                  window.location.href = "app.html?gqlerror=1";
                } else {
                  // Response successful
                  let response = JSON.parse(json.data.Details.details)
    
                  if (response.status_code != "200") {
                    // Problem with backend fetching data
                    const message = {
                        "errors": [{
                            "message": response.message
                        }]
                    }
                    localStorage.setItem('message', JSON.stringify(message.errors));
                    const message_set = true;
                    window.location.href = "app.html?gqlerror=1";
                  } else {
                    // Success
                    headerInstanceName = response.instanceName;
                  
                    
                    this.setState({
                        "data": response.payload
                    });
                    this.setState({ loading: false })
                  }
                }
              } else {
                // Status code of XHR request not 200
                  if (typeof message_set == 'undefined') {
                const message = {
                    "errors": [{
                        "message": "Error while fetching data for details."
                    }]
                }
                localStorage.setItem('message', JSON.stringify(message.errors));
            }
            window.location.href = "app.html?gqlerror=1";
              }
            }
          };
          xhr.send(JSON.stringify(payload));
        } catch (except) {
            if (typeof message_set == 'undefined') {
                const message = {
                    "errors": [{
                        "message": "Error while fetching data for details."
                    }]
                }
                localStorage.setItem('message', JSON.stringify(message.errors));
            }
            window.location.href = "app.html?gqlerror=1";
        }
        
      }

    handleBackClick() {
        window.location.href = "app.html";
    }

    CONSUL_setExpand(index) {    
        let { expanded } = this.state;
        let newExpanded = Object.assign( expanded, { [ index ]: (expanded[index] === true) ? false : true} )
        this.setState({ expanded: newExpanded })
    }

    CONSUL_resetExpanded() {
        this.setState({ expanded: {} })
    }

    reload(loading) {
        if(!this.state.loading){
        if(loading){
            this.setState({loading:true})
        }
        this.fetchData();
        }
    }

    render() {
        console.log("[render] Container"  );
        let title = " | Details";
        let apptext = " " + result[PROFILE_NAME];

        let noEndpointsElement = null;
        if (this.state.data.length) {
            noEndpointsElement = <div></div>
        } else {
            noEndpointsElement = <div className="no-element-found">No endpoints found for the given Application in the given Tenant.</div>
        }


        return (
            <div>
                <Header polling={true} text={title} applinktext={apptext} instanceName={headerInstanceName} />
                <div className="scroll">
                    {/* <DetailsTable data={this.state.data} appId={params_appid} tn={params_tn} onReload={this.reload} /> */}
                    {/* <button className="button view-button" onClick={this.handleBackClick}> Back </button> */}
                    {/* {noEndpointsElement} */}
                    <DataTable 
                        expanded={this.state.expanded} 
                        setExpand={this.CONSUL_setExpand} 
                        resetExpanded={this.CONSUL_resetExpanded} 
                        loading={this.state.loading} 
                        data={this.state.data} 
                        onReload={this.reload}>
                    </DataTable>
                </div>
            </div>
        )
    }
}

export default Container

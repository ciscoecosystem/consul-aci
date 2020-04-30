import React from 'react';
import { render } from 'react-dom';
import { Loader } from "blueprint-react"
import TestComponent from './TestComponent.js';
import Header from './Header.js'
import { TREE_VIEW_QUERY_PAYLOAD, PROFILE_NAME, INTERVAL_API_CALL } from "../../../../../constants.js"
// import { dummyData } from './dummydata.js';

const QUERY_URL="http://127.0.0.1:5000/graphql.json";
// const QUERY_URL = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";

var key = 0;
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

window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");

var headerInstanceName;

function loadingBoxShow() {
let health = document.getElementById("health-indicators")
if(health){
health.style.display= "none";
}
  document.getElementById("loading-box").style.display = "block";
  console.log(document.getElementById("loading-box").style.display)
}

function loadingBoxHide() {
	let health = document.getElementById("health-indicators")
if(health){
health.style.display= "block";
}
  document.getElementById("loading-box").style.display = "none";
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            result: {},
            treedata : undefined,

            detailsPane: {
                visible: false,
                data: {}
              },
        
            detailsPage: {
                visible: false,
                data: {}
              },
            treeApiLoading: false
        }

        this.reload = this.reload.bind(this);
        this.getData = this.getData.bind(this);
        this.getStaticData = this.getStaticData.bind(this);
        this.toggleDetailsPane = this.toggleDetailsPane.bind(this);
        this.toggleeDetailsPage = this.toggleeDetailsPage.bind(this);
    }

    componentWillMount(){
      document.body.style.overflow = "scroll"
    }

    componentDidMount() { 
      this.getData();
      setInterval(this.getData, INTERVAL_API_CALL);
      console.log("Tree index [ Component Did mount ]")
    }

    reload() {
        // alert("Reloading");
        loadingBoxShow("block");
        this.getData(true);
    }

    toggleDetailsPane(nodeData = undefined){ // if no argument that means details pane to be closed
        let isOpen = (nodeData !== undefined);
        this.setState({
            detailsPane: {
              visible: isOpen,
              data : isOpen ? nodeData : {}
            }
        })
    }

    toggleeDetailsPage(nodeData = undefined){ // if no argument that means details pane to be closed
        let isOpen = (nodeData !== undefined);
        this.setState({
            detailsPage: {
              visible: isOpen,
              data : isOpen ? nodeData : {}
            }
        })
    }

    getStaticData(fullyReload = false) {
        let thiss = this;
        console.log("GetData of tree;");
        let { detailsPage, detailsPane, treeApiLoading } = this.state;
  
        console.log("= detailsPage ", detailsPage);
        console.log("= detailsPane ", detailsPane);
  
        if (detailsPage.visible || detailsPane.visible) return;
        let xhr = new XMLHttpRequest();
        // let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
      
        try {
          console.log("opening post")
          //   xhr.open("POST", QUERY_URL,true);
            xhr.open('GET', 'treeData.json' , true)
            xhr.responseType = 'json';  
            xhr.setRequestHeader("Content-type", "application/json");

            xhr.onreadystatechange = function () {
                console.log("Response ====> ", xhr)
                if (xhr.readyState == 4){
                    if(xhr.status == 200 || xhr.status == 304) {
                        console.log("In 200 or 304 resposnse")
                        console.log("Tree data", xhr.response, typeof(xhr.response));
                        let treedata = xhr.response;

                        if ((JSON.stringify(thiss.state.treedata) !== JSON.stringify(treedata) || fullyReload) && !treeApiLoading){
                            console.log("Tree data taking ");
                            thiss.setState({ treeApiLoading: true}, function() {
                                setTimeout(function() { thiss.setState({ treedata, treeApiLoading: false }) } , 10 );
                            })
                        } else {
                           console.log("Didnt change as before");
                        }

                    }
                    else {
                        // Status code of XHR request not 200
                        console.log("Api fail");
                    }
                }
            }
            console.log("sending post")
            xhr.send(null);
        }
        catch(except) {
            console.log("Cannot fetch data to fetch Tree data.", except)
            thiss.setState({ treeApiLoading: false})
        }
    }

    getData(fullyReload = false) { 
      console.log("GetData of tree;");
      let { detailsPage, detailsPane, treeApiLoading } = this.state;

      if (detailsPage.visible || detailsPane.visible) return; // IF any popup is open dont call api

      let thiss = this;
      var urlToParse = location.search;
      let urlParams = {};
      urlToParse.replace(
          new RegExp("([^?=&]+)(=([^&]*))?", "g"),
          function ($0, $1, $2, $3) {
              urlParams[$1] = $3;
          }
      );
      let result = urlParams;

      try{
        result && this.setState({ result });
      } catch(err){
        console.error("set state error", err);
      }
  
      let payload = TREE_VIEW_QUERY_PAYLOAD(result['tn'], result[PROFILE_NAME])
      let xhr = new XMLHttpRequest();
    
      try {
        console.log("opening post")
          xhr.open("POST", QUERY_URL,true); 
          xhr.setRequestHeader("Content-type", "application/json");
          xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
          xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
          console.log("header set")
          xhr.onreadystatechange = function () {
              if (xhr.readyState == 4){
                  if(xhr.status == 200) {
                      let json = JSON.parse(xhr.responseText);
                      if('errors' in json) {
                          // Error related to query
                          localStorage.setItem('message', JSON.stringify(json.errors));
                          const message_set = true;
                          window.location.href = "index.html?gqlerror=1";
                      }
                      else {
                          // Response successful
                          const response = JSON.parse(json.data.Run.response);
                          if(response.status_code != "200") {
                              // Problem with backend fetching data
                              const message = {"errors": [{
                                  "message": response.message
                              }]}
                              localStorage.setItem('message', JSON.stringify(message.errors));
                              const message_set = true;
                              window.location.href = "index.html?gqlerror=1";
                          }
                          else {
                              // Success
                              var treedata_raw = JSON.parse(json.data.Run.response).payload;
                              headerInstanceName = JSON.parse(json.data.Run.response).agentIP; //  CONSUL : change from instanceName to agentIp

                              if ((JSON.stringify(thiss.state.treedata) !== JSON.stringify(JSON.parse(treedata_raw)) || fullyReload) 
                                   && !treeApiLoading){

                                console.log("Tree data taking ");

                                thiss.setState({ treeApiLoading: true}, function() {
                                    setTimeout(function() {
                                        thiss.setState({ treedata : JSON.parse(treedata_raw), treeApiLoading: false });
                                    } , 10 );
                                })

                              } else {
                                console.log("Didnt change as before");
                              }
                            }
                      }
                  }
                  else {
                      // Status code of XHR request not 200
                      console.log("Cannot fetch data to fetch Tree data.");
                      if(typeof message_set !== 'undefined') {
                          const message = {"errors": [{"message": "Error while fetching data for Tree. Status code" + xhr.status}]}
                          localStorage.setItem('message', JSON.stringify(message.errors));
                      }
                      window.location.href = "index.html?gqlerror=1";
                  }
              }
          }
          console.log("sending post")
          xhr.send(JSON.stringify(payload));
      }
      catch(except) {
          console.log("Cannot fetch data to fetch Tree data.", except)
          if(typeof message_set == 'undefined') {
              const message = {"errors": [{
                  "message": "Error while fetching data for Tree"
                }]}
              localStorage.setItem('message', JSON.stringify(message.errors));
          }
          thiss.setState({ treeApiLoading: false})
          window.location.href = "index.html?gqlerror=1";
      }
      key = key + 1;
      return true;
  }

    render() {
        let { treedata, treeApiLoading } = this.state;
      loadingBoxHide();
      console.log("Render tree index", this.state);
      let apptext = " " + this.state.result[PROFILE_NAME]; // CONSUL changes
      let title = " | View"
      
        return (
            <div>
                <Header text={title} applinktext={apptext} instanceName={headerInstanceName}/>
                {(treedata === undefined || treeApiLoading) ? <Loader> loading </Loader> : <TestComponent key={key} 
                    detailsPage={this.state.detailsPage}
                    detailsPane={this.state.detailsPane}
                    toggleDetailsPane = {this.toggleDetailsPane}
                    toggleeDetailsPage = {this.toggleeDetailsPage}
                    data={this.state.treedata} 
                    reloadController={this.reload} 
                    datacenterName={this.state.result[PROFILE_NAME]}/> }
            </div>
        );
    }
}

render(<App />, document.getElementById('app'));


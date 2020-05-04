import React from 'react';
import { render } from 'react-dom';
import TestComponent from './TestComponent.js';
import Header from './Header.js'
import { TREE_VIEW_QUERY_PAYLOAD, PROFILE_NAME } from "../../../../../constants.js"

var treedata;
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

function getStaticData() {
    let rawData = [
        {
          "name": "AppProf",
          "level": "seagreen",
          "sub_label": "AppD-AppProfile1", 
          "label": "EComm-NPM-Demo", 
          "attributes": {
            "App-Health": "CRITICAL"
          },
          "type": "#581552", 
          "children": [
            {
              "name": "EPG",
              "level": "seagreen", 
              "sub_label": "AppD-Ord", 
              "label": "Order-Tier", 
              "fraction": 2, 
              "attributes": {
                "BD": "AppD-BD1",
                "Contracts": [
                  {
                    "Provider": "controller"
                  },
                  {
                    "Provider": "default"
                  },
                  {
                    "Consumer": "controller"
                  },
                  {
                    "Consumer": "default"
                  },
                  {
                    "Consumer": "test"
                  }
                ],
                "VMM-Domain": "ESX0-leaf102",
                "Tier-Health": "NORMAL",
                "VRF": "AppDynamics/AppD-VRF",
                "Nodes": [
                  "ORD-N1_0",
                  "ORD-N1_1"
                ]
              },
              "type": "#085A87",
              "children": [
                {
                  "name": "EP",
                  "level": "seagreen",
                  "sub_label": "AppD-Ord-1_1", 
                  "label": "Order-Tier", 
                  "attributes": {
                    "Tier-Health": "NORMAL",
                    "IP": "192.168.128.18",
                    "Interfaces": [
                      "topology/pod-1/paths-102/pathep-[     eth1/6   ]"
                    ],
                    "HealthRuleViolations": [
                      
                    ],
                    "ServiceEndpoints": [
                      {
                        "sepName": "/order/rest",
                        "sepId": 534,
                        "Errors/Min": "0.0",
                        "ErrorPercentage": "0.0",
                        "TotalErrors": "0",
                        "Type": "SERVLET"
                      }
                    ]
                  },
                  "type": "#2DBBAD",
                  "children": [
                    {
                      "attributes": {
                        "Node-Health": "NORMAL"
                      },
                      "label": "ORD-N1_0",
                      "type": "#C5D054",
                      "name": "Node",
                      "level": "seagreen"
                    },
                    {
                      "attributes": {
                        "Node-Health": "NORMAL"
                      },
                      "label": "ORD-N1_1",
                      "type": "#C5D054",
                      "name": "Node",
                      "level": "seagreen"
                    }
                  ]
                },
                {
                  "fractions": 2,
                  "name": "EP",
                  "level": "grey",
                  "sub_label": "",
                  "label": "",
                  "attributes": {
                    "00: 50: 56: 89: 2F: 28": "192.168.128.17",
                    "00: 50: 56: 89: E0: 1C": "192.168.128.20"
                  },
                  "type": "grey"
                }
              ]
            },
            {
              "name": "EPG",
              "level": "seagreen",
              "sub_label": "Appd-Inv-Data",
              "label": "Inv-Tier",
              "fraction": 0,
              "attributes": {
                "BD": "AppD-BD1",
                "Contracts": [
                  {
                    "Provider": "default"
                  },
                  {
                    "Provider": "controller"
                  },
                  {
                    "Consumer": "default"
                  },
                  {
                    "Consumer": "controller"
                  }
                ],
                "VMM-Domain": "ESX1-Leaf102",
                "Tier-Health": "NORMAL",
                "VRF": "AppDynamics/AppD-VRF",
                "Nodes": [
                  "INV-N1_0",
                  "INV-N1_1"
                ]
              },
              "type": "#085A87",
              "children": [
                {
                  "name": "EP",
                  "level": "seagreen",
                  "sub_label": "AppD-Inv",
                  "label": "Inv-Tier",
                  "attributes": {
                    "Tier-Health": "NORMAL",
                    "IP": "192.168.128.21",
                    "Interfaces": [
                      "topology/pod-1/paths-102/pathep-[     eth1/5   ]"
                    ],
                    "HealthRuleViolations": [
                      
                    ],
                    "ServiceEndpoints": [
                      {
                        "sepName": "/cart/services",
                        "sepId": 530,
                        "Errors/Min": "0.0",
                        "ErrorPercentage": "0.0",
                        "TotalErrors": "0",
                        "Type": "SERVLET"
                      }
                    ]
                  },
                  "type": "#2DBBAD",
                  "children": [
                    {
                      "attributes": {
                        "Node-Health": "NORMAL"
                      },
                      "label": "INV-N1_0",
                      "type": "#C5D054",
                      "name": "Node",
                      "level": "seagreen"
                    },
                    {
                      "attributes": {
                        "Node-Health": "NORMAL"
                      },
                      "label": "INV-N1_1",
                      "type": "#C5D054",
                      "name": "Node",
                      "level": "seagreen"
                    }
                  ]
                }
              ]
            },
            {
              "name": "EPG",
              "level": "seagreen",
              "sub_label": "AppD-Payment",
              "label": "Payment-Tier",
              "fraction": 1,
              "attributes": {
                "BD": "AppD-BD1",
                "Contracts": [
                  {
                    "Provider": "default"
                  }
                ],
                "VMM-Domain": "ESX0-leaf103",
                "Tier-Health": "NORMAL",
                "VRF": "AppDynamics/AppD-VRF",
                "Nodes": [
                  "PAY-N2_0"
                ]
              },
              "type": "#085A87",
              "children": [
                {
                  "name": "EP",
                  "level": "seagreen",
                  "sub_label": "AppD-Pay2",
                  "label": "Payment-Tier",
                  "attributes": {
                    "Tier-Health": "NORMAL",
                    "IP": "192.168.128.161",
                    "Interfaces": [
                      "topology/pod-1/paths-103/pathep-[     eth1/6   ]"
                    ],
                    "HealthRuleViolations": [
                      
                    ],
                    "ServiceEndpoints": [
                      {
                        "sepName": "/paymentgateway/store",
                        "sepId": 525,
                        "Errors/Min": "0.0",
                        "ErrorPercentage": "0.0",
                        "TotalErrors": "0",
                        "Type": "SERVLET"
                      }
                    ]
                  },
                  "type": "#2DBBAD",
                  "children": [
                    {
                      "attributes": {
                        "Node-Health": "NORMAL"
                      },
                      "label": "PAY-N2_0",
                      "type": "#C5D054",
                      "name": "Node",
                      "level": "seagreen"
                    }
                  ]
                },
                {
                  "fractions": 1,
                  "name": "EP",
                  "level": "grey",
                  "sub_label": "",
                  "label": "",
                  "attributes": {
                    "00: 50: 56: 89: A7: 8E": "192.168.128.15"
                  },
                  "type": "grey"
                }
              ]
            },
            {
              "name": "EPG",
              "level": "seagreen",
              "sub_label": "Appd-Ecom-Data",
              "label": "Ecom-Tier",
              "fraction": 0,
              "attributes": {
                "BD": "AppD-BD1",
                "Contracts": [
                  {
                    "Provider": "default"
                  },
                  {
                    "Provider": "controller"
                  },
                  {
                    "Consumer": "default"
                  },
                  {
                    "Consumer": "controller"
                  }
                ],
                "VMM-Domain": "ESX1-Leaf102",
                "Tier-Health": "NORMAL",
                "VRF": "AppDynamics/AppD-VRF",
                "Nodes": [
                  "ECOM-N1_0",
                  "ECOM-N1_1"
                ]
              },
              "type": "#085A87",
              "children": [
                {
                  "name": "EP",
                  "level": "seagreen",
                  "sub_label": "AppD-Ecom-1",
                  "label": "Ecom-Tier",
                  "attributes": {
                    "Tier-Health": "NORMAL",
                    "IP": "192.168.128.13",
                    "Interfaces": [
                      "topology/pod-1/paths-102/pathep-[     eth1/5   ]"
                    ],
                    "HealthRuleViolations": [
                      
                    ],
                    "ServiceEndpoints": [
                      {
                        "sepName": "/appdynamicspilot/rest",
                        "sepId": 526,
                        "Errors/Min": "0.0",
                        "ErrorPercentage": "0.0",
                        "TotalErrors": "0",
                        "Type": "SERVLET"
                      },
                      {
                        "sepName": "/",
                        "sepId": 591,
                        "Errors/Min": "0.0",
                        "ErrorPercentage": "0.0",
                        "TotalErrors": "0",
                        "Type": "SERVLET"
                      }
                    ]
                  },
                  "type": "#2DBBAD",
                  "children": [
                    {
                      "attributes": {
                        "Node-Health": "NORMAL"
                      },
                      "label": "ECOM-N1_1",
                      "type": "#C5D054",
                      "name": "Node",
                      "level": "seagreen"
                    },
                    {
                      "attributes": {
                        "Node-Health": "NORMAL"
                      },
                      "label": "ECOM-N1_0",
                      "type": "#C5D054",
                      "name": "Node",
                      "level": "seagreen"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ];
    treedata = rawData;
}

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
            result: {}
        }

        this.reload = this.reload.bind(this);
        this.getData = this.getData.bind(this);
    }

    componentWillMount(){
      document.body.style.overflow = "scroll"
    }

    componentDidMount() {
      this.getData();
    }

    reload() {
        // alert("Reloading");
        loadingBoxShow("block");
        this.getData();
    }

    getData() {  
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
      // let payload = { query: 'query{Run(tn:"' + result['tn'] + '",appId:"' + result['appId'] + '"){response}}' }
      let xhr = new XMLHttpRequest();
      let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
    
      try {
        console.log("opening post")
          xhr.open("POST", url,false);
  
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
                          const response = JSON.parse(json.data.OperationalTree.response);
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
                              var treedata_raw = JSON.parse(json.data.OperationalTree.response).payload;
                              headerInstanceName = JSON.parse(json.data.OperationalTree.response).agentIP; //  CONSUL : change from instanceName to agentIp
                              treedata = JSON.parse(treedata_raw);
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
          console.log("Cannot fetch data to fetch Tree data.")
          if(typeof message_set == 'undefined') {
              const message = {"errors": [{
                  "message": "Error while fetching data for Tree"
                }]}
              localStorage.setItem('message', JSON.stringify(message.errors));
          }
  
          window.location.href = "index.html?gqlerror=1";
      }
      key = key + 1;
      return true;
  }

    render() {
      loadingBoxHide();

      let apptext = " " + this.state.result[PROFILE_NAME]; // CONSUL changes
      let title = " | Operational"
      
        return (
            <div>
                <Header text={title} applinktext={apptext} instanceName={headerInstanceName}/>
                <TestComponent key={key} data={treedata} reloadController={this.reload} datacenterName={this.state.result[PROFILE_NAME]}/>
            </div>
        );
    }
}

render(<App />, document.getElementById('app'));


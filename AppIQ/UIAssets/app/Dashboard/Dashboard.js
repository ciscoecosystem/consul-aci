import React from 'react';
import './Dashboard.css';
import {Button, Icon} from 'blueprint-react';
import PieChartAndCounter from "../commonComponent/PieChartAndCounter.js";

export default class Dashboard extends React.Component{

  constructor(props)
  {
    super(props);
    this.state ={
        
    }
    this.xhrCred = new XMLHttpRequest();
    this.loadDashBoardData = this.loadDashBoardData.bind(this);
    this.formateDataToChartData = this.formateDataToChartData.bind(this);
    this.nFormatter = this.nFormatter.bind(this);
  }

  
  componentDidMount(){
    console.log("In component Did")
    this.getDashboardData()
  }

  loadDashBoardData(data){
      this.setState({agents: data.agents, endpoints:data.service_endpoint, services: data.service, nodes: data.nodes})
  }

  nFormatter(num) {
    if (num >= 1000000000) {
       return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'G';
    }
    if (num >= 1000000) {
       return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    }
    if (num >= 1000) {
       return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
    }
    return num;
}

  formateDataToChartData(data){
    let totalCnt = 0;
    let formattedData = [];
    console.log(this.nFormatter)
    let datakeys = Object.keys(data);
    datakeys.forEach(function (elem) {
        let dataElem = {};
        dataElem.label = elem;
        dataElem.value = data[elem];
        totalCnt += data[elem];

        if (elem === "passing") {
            dataElem.color = "rgb(108, 192, 74)";
        } else if (elem === "warning") {
            dataElem.color = "rgb(255, 204, 0)";
        } else if (elem === "failing") {
            dataElem.color = "rgb(226, 35, 26)";
        }
        formattedData.push(dataElem)
    })
    console.log(formattedData)
    return {
        formattedData, // format as per chart
        totalCnt    // total count of all (passing,warning,failing)
    }
}

  getDashboardData(){
    console.log("In Get Dashboard Data!")
    // const payload = {
    //     query: `query{
    //     ReadCreds{creds}
    // }`}
    try {
        this.xhrCred.open("GET", "http://localhost:5050/GetPerformanceDashboard");
        console.log("In Get Dashboard Data!")
        // this.xhrCred.setRequestHeader("Content-type", "application/json");
        // console.log("In Get Dashboard Data!")
        // this.window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
        // window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
        // this.xhrCred.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
        // this.xhrCred.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            this.xhrCred.send();
            console.log("chr== state ", this.xhrCred.readyState);
            console.log(this.xhrCred)
            console.log(this.xhrCred.status)
            this.xhrCred.onreadystatechange =  () =>{
              // console.log("chr== state ", xhrCred.readyState);
              if (this.xhrCred.status == 200) {
                  let checkData = JSON.parse(this.xhrCred.responseText);
                  console.log(checkData)
                  this.loadDashBoardData(checkData)
                  this.setState({chartLoaded:true})
                  // let credsData = JSON.parse(checkData.data.ReadCreds.creds);

                  // if (parseInt(credsData.status_code) === 200) {
                      // thiss.setDetails(credsData.payload, isReloaded);
                      // thiss.setState({ details: credsData.payload })
                  // } else if (parseInt(credsData.status_code) === 300) {
                      // try {
                      //     thiss.notify(credsData.message)
                      // } catch (e) {
                      //     console.log("message error", e)
                      // }
                  // }
              }
              else {
                  console.log("Not fetching");
              }
            }

        
    }
    catch (e) {
        // thiss.notify("Error while fetching agent information please refresh");
        console.error('Error getting agents', e);
    }
  }

  render(){
    return(
        <React.Fragment>
            <div style={{marginBottom:"1%"}}><h4>Dashboard</h4></div>
            <div className="overview">
                {/* <ExamplesHeader title="Charts"/> */}
                <h5 style={{"padding":"5px", "marginBottom":"10px"}}><b>Overview</b></h5>
                    <div style={{"float":"left"}}>
                        <h6 style={{textAlign:"center", paddingLeft:"70%"}}>Agents</h6>
                        <div className="agent" >
                            <div style={{marginLeft:"30%"}}><span className="green-dot"></span><span>Up({this.state.agents?this.nFormatter(this.state.agents.up):0})</span></div>
                        </div>
                        <div className="agent">
                            <div style={{marginLeft:"30%"}}><span className="red-dot"></span><span>Down({this.state.agents?this.nFormatter(this.state.agents.down):0})</span></div>
                        </div>
                    </div>
                    <div style={{"float":"right"}}>
                        <h6 style={{textAlign:"center"}}>Endpoints</h6>
                        <div className="endpoint">
                            <span className="green-dot"></span><span>Service Endpoints({this.state.endpoints?this.nFormatter(this.state.endpoints.service):0})</span>
                        </div>
                        <div className="endpoint">
                            <span className="grey-dot"></span><span>Non-Service Endpoints({this.state.endpoints?this.nFormatter(this.state.endpoints.non_service):0})</span>
                        </div>
                    </div>
                    {this.state.services && this.state.nodes?
                        <div style={{textAlign:"center"}}>
                            <div style={{float:"left", "margin-left":"15%", "width":"15%"}}>
                                <h6>Services</h6>
                                <PieChartAndCounter  data={this.formateDataToChartData(this.state.services).formattedData} totalCount={this.nFormatter(this.formateDataToChartData(this.state.services).totalCnt)} />
                            </div>
                            <div style={{float:"right", "margin-right":"15%", "width":"15%"}}>
                                <h6>Nodes</h6>
                                <PieChartAndCounter  data={this.formateDataToChartData(this.state.nodes).formattedData} totalCount={this.nFormatter(this.formateDataToChartData(this.state.nodes).totalCnt)}/>
                            </div>
                        </div>
                    :null}

            </div>
        </React.Fragment>

    )
  }
}

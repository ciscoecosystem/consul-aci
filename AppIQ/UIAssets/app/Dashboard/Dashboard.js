import React from 'react';
import './Dashboard.css';
import {Loader, Button, Icon} from 'blueprint-react';
import PieChartAndCounter from "../commonComponent/PieChartAndCounter.js";
import {QUERY_URL, getCookie, DEV_TOKEN, URL_TOKEN} from '../../constants.js';
import {  toast } from 'react-toastify';

// const dummydata = {'nodes': {'passing': 6, 'warning': 0, 'failing': 0}, 'agents': {'down': 0, 'up': 2}, 'service': {'passing': 1, 'warning': 0, 'failing': 0}, 'service_endpoint': {'non_service': 21, 'service': 11}}

export default class Dashboard extends React.Component{

  constructor(props)
  {
    super(props);
    this.state ={
        loadingDashBoard: false
    }
    // console.log("==> props ", this.props);
    this.xhrReadDashboard = new XMLHttpRequest();
    this.loadDashBoardData = this.loadDashBoardData.bind(this);
    this.formateDataToChartData = this.formateDataToChartData.bind(this);
    this.nFormatter = this.nFormatter.bind(this);
    this.getDashboardData = this.getDashboardData.bind(this);
    this.notify = this.notify.bind(this);
  }

  
  componentDidMount(){
    console.log("In component Did")
    this.setState({loadingDashBoard: true}, this.getDashboardData)
    // this.loadDashBoardData(dummydata);
    // this.getDashboardData()
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

notify(message, isSuccess = false, isWarning = false) {
    isWarning ? toast.warn(message, {
        position: toast.POSITION.TOP_RIGHT,
        delay: 1500
    }) :
        isSuccess ? toast.success(message, {
            position: toast.POSITION.TOP_RIGHT,
            delay: 1500
        }) :
            toast.error(message, {
                position: toast.POSITION.TOP_RIGHT,
                delay: 1500
            });
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

    const payload = {
        query: 'query{GetPerformanceDashboard(tn:"' + this.props.tenantName + '"){response}}'
    }

    try {
        this.xhrReadDashboard.open("POST", QUERY_URL, false);
        this.xhrReadDashboard.setRequestHeader("Content-type", "application/json");
        // window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
        // window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
        this.xhrReadDashboard.setRequestHeader("DevCookie", getCookie(DEV_TOKEN));
        this.xhrReadDashboard.setRequestHeader("APIC-challenge", getCookie(URL_TOKEN));

        this.xhrReadDashboard.onreadystatechange = () => {
            // debugger
            console.log("xhr== state ", this.xhrReadDashboard);
            if (this.xhrReadDashboard.readyState == 4 && this.xhrReadDashboard.status == 200) {
                console.log("reponse data =>  ", this.xhrReadDashboard);
                let checkData = JSON.parse(this.xhrReadDashboard.responseText);
                console.log("checkdata ", checkData, typeof(checkData));
                let dashoardData = JSON.parse(checkData.data.GetPerformanceDashboard.response);
                console.log("dashoardData data", dashoardData);

                if (parseInt(dashoardData.status) === 200) {
                    this.loadDashBoardData(dashoardData.payload)
                } else if (parseInt(dashoardData.status) === 300) {
                    try {
                        this.notify(dashoardData.message)
                    } catch (e) {
                        console.log("message error", e)
                    }
                }

            }
            else {
                this.notify("something went wrong");
                console.log("Not fetching");
            }
            this.setState({loadingDashBoard:false})
        }
        this.xhrReadDashboard.send(JSON.stringify(payload));
    }
    catch (e) {
        console.error('Error While Fetching Dashboard', e);
    }
  }

  render(){
    return(
        <React.Fragment>
                <div style={{ margin:"10px"}}><h4>Dashboard</h4></div>
                <div className="overview">
                    {/* <ExamplesHeader title="Charts"/> */}
                    <h5 style={{"padding":"5px", "marginBottom":"10px"}}><b>Overview</b></h5>
                        {this.state.loadingDashBoard?<Loader></Loader>:
                        <React.Fragment>
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
                                    <div className="service-chart">
                                        <h6>Services</h6>
                                        <PieChartAndCounter  data={this.formateDataToChartData(this.state.services).formattedData} totalCount={this.nFormatter(this.formateDataToChartData(this.state.services).totalCnt)} />
                                    </div>
                                    <div className="node-chart">
                                        <h6>Nodes</h6>
                                        <PieChartAndCounter  data={this.formateDataToChartData(this.state.nodes).formattedData} totalCount={this.nFormatter(this.formateDataToChartData(this.state.nodes).totalCnt)}/>
                                    </div>
                                </div>
                            :null}
                        </React.Fragment>
                        }
                </div>
        </React.Fragment>

    )
  }
}

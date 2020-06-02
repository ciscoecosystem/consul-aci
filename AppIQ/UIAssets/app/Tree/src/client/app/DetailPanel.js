import React from 'react'
import { CollapsiblePanel, Label } from "blueprint-react"
import SummaryPane from "./Components/SummaryPane.js";
import PieChartAndCounter from "./commonComponent/PieChartAndCounter.js";
import "./DetailPanel.css";

const NODE_EP_NAME = "EP";
const NODE_SERVICE_NAME = "Service";
const NODE_EPG_NAME = "EPG"

function formateDataToChartData(data) {
    let totalCnt = 0;
    let formattedData = [];

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

    return {
        formattedData, // format as per chart
        totalCnt    // total count of all (passing,warning,failing)
    }
}

export default function DetailPanel(props) {
    
    let { summaryPaneIsOpen, summaryDetail } = props;
    let title = summaryDetail.name;
    console.log("==> Detail pane mounted", summaryDetail);

    // let apicInfoOrder = [
    // { name: "interface", label: "Interface" },
    // { name: "ip", label: "ip" },
    // { name: "mac", label: "mac" },
    // { name: "epgName", label: "epg" },
    // { name: "epgHealth", label: "epg Health" },
    // { name: "ap", label: "Application profile" },
    // { name: "vrf", label: "Vrf" },
    // { name: "bd", label: "bd" },
    // { name: "learningSource", label: "Learning Source" },
    // { name: "reportingController", label: "reporting Controller" },
    // { name: "hostingServer", label: "hosting Server" }];

    // let nodeInfoOrder = [{ name: "consulNode", label: "consul Node" },
    // { name: "nodeChecks", label: "node Checks" }];

    // let serviceInfoOrder = [{ name: "service", label: "service" },
    // { name: "serviceChecks", label: "service Checks" },
    // { name: "serviceInstance", label: "service Instance" },
    // { name: "Port", label: "port" },
    // { name: "serviceTags", label: "service Tags" },
    // { name: "serviceKind", label: "service Kind" },
    // { name: "serviceNamespace", label: "Namespace" }];

    let appProfileOrder=[{name:"name", label:"Name"},
                        { name:"App-Health", label:"App-Health"}]

                        // {name:"name", label:"Name"},
    let epgInfoOrder=[{name:"name", label:"Name"},
                    { name:"VRF", label:"vrf"},
                        { name:"BD", label:"bd"}]

    let constractInfoOrder=[ { name:"Consumer", label:"consumer"},
                            { name:"Provider", label:"Provider"}]

    let consulNodeOrder = [  { name:"Node", label:"node"}, 
                            { name:"Node Checks", label:"Node Checks"},
                                { name:"Reporting Node IP", label:"Reporting Node IP"}]

    let consulServiceOrder = [  { name:"Service", label:"Service"}, 
                            { name:"Address", label:"Address"},
                            { name:"Service Checks", label:"Service Checks"}]



    function CollapsePane(title, infoOrder, values=undefined, nodeElem = undefined) {
        let details = values ? values : summaryDetail;

        function allDetailRender(showDetails) {
            return infoOrder.map(function (elem) {
            let { name, label } = elem
            let detailValue = showDetails[name];

            if (name === "nodeChecks" || name === "serviceChecks" || name === "Node Checks" || name==="Service Checks") {
                let { formattedData, totalCnt } = formateDataToChartData(showDetails[name])
                detailValue = <PieChartAndCounter data={formattedData} totalCount={totalCnt} />
            }
            else if (name === "serviceTags") {
                detailValue = showDetails[name].map(function (tags) {
                    return <Label theme={"MEDIUM_GRAYY"} size={"MEDIUM"} border={false}>{tags}</Label>
                })
            } else if (name === "interface" || name === "Consumer" || name==="Provider") {
                detailValue = <ul style={{ listStyleType: "none", paddingLeft: "0px" }}>
                    {showDetails[name].map(function (infcs) {
                        return <li>{infcs}</li>
                    })}
                </ul>
            }

            return <PropertyItem propertyLabel={label} propertyValue={detailValue} />
            })
        }

        return <CollapsiblePanel id="ccpid1" key="ccpkey1" title={title}>
            
            {(nodeElem) ? nodeElem : (Array.isArray(details)) ? 
                details.map((elemData,ind) => <React.Fragment> {allDetailRender(elemData)} 
                                    {(details.length-1 !== ind) && <hr/>}
                                     </React.Fragment> ) : 
                allDetailRender(details)  
            }
            
        </CollapsiblePanel>
    }

    function panelToShow() {
        summaryDetail.attributes["name"] = summaryDetail["sub_label"];
        switch (summaryDetail.name) {

        case NODE_SERVICE_NAME:
          return (
            <React.Fragment>
                {CollapsePane(summaryDetail.name + " Information", [])}
                {CollapsePane("service info", [])}
            </React.Fragment>)

        case NODE_EP_NAME:
          return (
            <React.Fragment>
               {CollapsePane(summaryDetail.name + " Information", [])}
               {CollapsePane("ep info", [])}
            </React.Fragment>)

        case NODE_EPG_NAME:
            console.log("Epg info ", summaryDetail)
          return (
            <React.Fragment>
              {CollapsePane(summaryDetail.name + " Information", epgInfoOrder, summaryDetail.attributes )}

            {('Contracts' in summaryDetail.attributes) &&
                CollapsePane("Contracts Information", constractInfoOrder, summaryDetail.attributes.Contracts )}
              
              {CollapsePane("Consul Nodes", consulNodeOrder, summaryDetail.attributes.Nodes)}

            {/* {('Nodes' in summaryDetail.attributes && summaryDetail.attributes.Nodes.length > 0) &&
                summaryDetail.attributes.Nodes.map(nodeData => CollapsePane("Consul Nodes", consulNodeOrder, nodeData) )} */}

              {CollapsePane("Consul Services", consulServiceOrder, summaryDetail.attributes.Services_List)}

            {/* {('Services_List' in summaryDetail.attributes && summaryDetail.attributes.Services_List.length > 0) &&
                summaryDetail.attributes.Services_List.map(serviceData => CollapsePane("Consul Services", consulServiceOrder, serviceData) )} */}
            
            </React.Fragment>)

        default:
          return (
            <React.Fragment>
              {CollapsePane(summaryDetail.name + " Information", appProfileOrder)}
            </React.Fragment>)

        }
    }

    return (summaryPaneIsOpen) ? <SummaryPane
        subTitle={""}
        title={summaryDetail["sub_label"]}
        closeSummaryPane={() => props.setSummaryIsOpen(false)}
        isOpenScreen={true}
        openScreen={() => props.openDetailsPage(summaryDetail)}
    >
        <div className="" style={{ marginBottom: "80%" }}>
    
            {/* {CollapsePane("APIC Information", apicInfoOrder)}
            {CollapsePane("Consul Node Information", nodeInfoOrder)}
            {CollapsePane("Consul Service Information", serviceInfoOrder)} */}

            {panelToShow()}
        </div>
    </SummaryPane> : <div></div>
}


function PropertyItem(props) {
    return (
        <div className="property-list-item">
            <div className="property-label">{props.propertyLabel}</div>
            <div className="property-value">{props.propertyValue ? props.propertyValue : "-"}</div>
        </div>
    )
}
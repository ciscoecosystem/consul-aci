import React from 'react'
import { CollapsiblePanel, Label } from "blueprint-react"
import SummaryPane from "../Components/SummaryPane";
import PieChartAndCounter from "../commonComponent/PieChartAndCounter";
import { showShortName, isString } from '../Utility/utils.js' ;
import "./DetailPanel.css";



const VALUE_LENGTH = 35;


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
    console.log("==> Detail pane mounted");
    let { summaryPaneIsOpen, summaryDetail, title } = props;
    let apicInfoOrder = [
    { name: "interface", label: "Interface" },
    { name: "pod_name", label: "POD"},
    { name: "ip", label: "ip" },
    { name: "mac", label: "mac" },
    { name: "epgName", label: "epg" },
    { name: "epgHealth", label: "epg Health" },
    { name: "ap", label: "Application profile" },
    { name: "vrf", label: "Vrf" },
    { name: "bd", label: "bd" },
    { name: "learningSource", label: "Learning Source" },
    { name: "reportingController", label: "reporting Controller" },
    { name: "hostingServer", label: "hosting Server" }];

    let nodeInfoOrder = [{ name: "consulNode", label: "consul Node" },
    { name: "nodeChecks", label: "node Checks" }];

    let serviceInfoOrder = [{ name: "service", label: "service" },
    { name: "serviceChecks", label: "service Checks" },
    { name: "serviceInstance", label: "service Instance" },
    { name: "port", label: "port" },
    { name: "serviceTags", label: "service Tags" },
    { name: "serviceKind", label: "service Kind" },
    { name: "serviceNamespace", label: "Namespace" }];


    function CollapsePane(title, infoOrder) {
        return <CollapsiblePanel id="ccpid1" key="ccpkey1" title={title}>
            {
                infoOrder.map(function (elem) {
                    let { name, label } = elem
                    let detailValue = summaryDetail[name];

                    if (name === "nodeChecks" || name === "serviceChecks") {
                        let { formattedData, totalCnt } = formateDataToChartData(summaryDetail[name])
                        detailValue = <PieChartAndCounter data={formattedData} totalCount={totalCnt} />
                    }
                    else if (name === "serviceTags" || name === "pod_name") {
                        detailValue = summaryDetail[name].map(function (tags) {
                            return <Label theme={"MEDIUM_GRAYY"} size={"MEDIUM"} border={false}>{tags}</Label>
                        })
                    } else if (name === "interface") {
                        detailValue = <ul style={{ listStyleType: "none", paddingLeft: "0px" }}>
                            {summaryDetail[name].map(function (infcs) {
                                return <li title={infcs}>{infcs}</li>
                            })}
                        </ul>
                    }

                    return <PropertyItem propertyLabel={label} propertyValue={detailValue} />
                })
            }
        </CollapsiblePanel>
    }



    return (summaryPaneIsOpen) ? <SummaryPane
        subTitle={"ENDPOINT"}
        title={title}
        closeSummaryPane={() => props.setSummaryIsOpen(false)}
        openScreen={()=>props.setExpansionViewOpen()}
    >
        <div className="" style={{ marginBottom: "80%" }}>
            {CollapsePane("APIC Information", apicInfoOrder)}
            {CollapsePane("Consul Node Information", nodeInfoOrder)}
            {CollapsePane("Consul Service Information", serviceInfoOrder)}
        </div>
    </SummaryPane> : <div></div>
}


function PropertyItem(props) {
    return (
        <div className="property-list-item">
            <div className="property-label">{props.propertyLabel}</div>
            <div className="property-value" title={ isString(props.propertyValue) && props.propertyValue}>
                {props.propertyValue ? 
                    isString(props.propertyValue) ? showShortName(props.propertyValue, VALUE_LENGTH): props.propertyValue 
                    : "-"}
            </div>
        </div>
    )
}
import React from 'react'
import { CollapsiblePanel, Label } from "blueprint-react"
import SummaryPane from "../Components/SummaryPane";
import PieChartAndCounter from "../commonComponent/PieChartAndCounter";
import "./DetailPanel.css";

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
    let { summaryPaneIsOpen, summaryDetail, title } = props;
    let apicInfoOrder = ["endPointName", "interface", "ip", "mac", "epgName", "epgHealth", "vrf", "bd", "learningSource", "reportingController", "hostingServer"];
    let nodeInfoOrder = ["consulNode", "nodeChecks"];
    let serviceInfoOrder = ["service", "serviceChecks", "serviceInstance", "Port", "serviceTags", "serviceKind"];


    function CollapsePane(title, infoOrder) {
        return <CollapsiblePanel id="ccpid1" key="ccpkey1" title={title}>
            {
                infoOrder.map(function (elem) {
                    let detailValue = summaryDetail[elem];

                    if (elem === "nodeChecks" || elem === "serviceChecks") {
                        let { formattedData, totalCnt } = formateDataToChartData(summaryDetail[elem])
                        detailValue = <PieChartAndCounter data={formattedData} totalCount={totalCnt} />
                    }
                    else if (elem === "serviceTags") {
                        detailValue = summaryDetail[elem].map(function (tags) {
                            return <Label theme={"MEDIUM_GRAYY"} size={"MEDIUM"} border={false}>{tags}</Label>
                        })
                    } else if (elem === "interface") {
                        detailValue = <ul style={{ listStyleType: "none", paddingLeft: "0px" }}>
                            {summaryDetail[elem].map(function (infcs) {
                                return <li>{infcs}</li>
                            })}
                        </ul>
                    }

                    return <PropertyItem propertyLabel={elem} propertyValue={detailValue} />
                })
            }
        </CollapsiblePanel>
    }



    return (summaryPaneIsOpen) ? <SummaryPane
        title={title}
        closeSummaryPane={() => props.setSummaryIsOpen(false)}
        openScreen={function () { console.log("Here open detail it") }}
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
            <div className="property-value">{props.propertyValue ? props.propertyValue : "-"}</div>
        </div>
    )
}
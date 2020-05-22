import React, { Component } from 'react'

import { CollapsiblePanel } from "blueprint-react"
import SummaryPane from "../Components/SummaryPane";
import "./DetailPanel.css";

export default function DetailPanel(props) {
    let { summaryPaneIsOpen, summaryDetail, title } = props;

    let detailOrder = ["endPointName", "ip", "port", "mac", "epgName", "consulNode", "vrf", "service", "serviceInstance"]

    return (summaryPaneIsOpen) ? <SummaryPane
        title={title}
        closeSummaryPane={() => props.setSummaryIsOpen(false)}
        openScreen={function () { console.log("Here open detail it") }}
    >
        <CollapsiblePanel id="ccpid1" key="ccpkey1" title="General Information">
            {
                detailOrder.map(function (elem) {
                    return <PropertyItem propertyLabel={elem} propertyValue={summaryDetail[elem]} />
                })
            }
        </CollapsiblePanel>

    </SummaryPane> : <div></div>
}


function PropertyItem(props) {
    return (
        <div className="property-list-item">
            <div className="property-label">{props.propertyLabel}</div>
            <div className="property-value">{props.propertyValue}</div>
        </div>
    )
}
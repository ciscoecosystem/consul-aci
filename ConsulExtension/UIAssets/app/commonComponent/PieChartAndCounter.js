
import React from 'react';
import { Charts } from 'blueprint-react';
import "./PieChartAndCounter.css";
import {nFormatter} from "../Utility/utils.js";

function renderLabels(count = 0) {
    return (
        <div className="pie-labels">
            <div className="pie-total-label">
                {count}
            </div>
        </div>
    );
};

function FormatToLabel(label) {
    if (label && typeof (label) === "string" && label.length > 1) {
        return label[0].toUpperCase() + label.slice(1);
    }
    return label;
}

export default function PieChartAndCounter(props) {
    let { data, totalCount } = props;
        data = [{
            color: "#bebec1",
            value: (totalCount === 0) ? 1 : 0,
            label: "none"
        }, ...data]
    
    return (<div className="d-flex">
        <div className="piechart-wrapper">
            <Charts.ResponsiveContainer width="100%" height={100}>
                <Charts.PieChart height={100}>
                    <Charts.Pie
                        data={data}
                        dataKey="value"
                        innerRadius={36}
                        outerRadius={40}
                        paddingAngle={1}
                        isAnimationActive={true}
                    >
                        {
                            data.map((entry, index) => {
                                return <Charts.Cell key={index} fill={entry.color} />
                            })
                        }
                    </Charts.Pie>
                </Charts.PieChart>
            </Charts.ResponsiveContainer>
            {renderLabels(nFormatter(totalCount))}
        </div>

        <div class="counters " style={{ maxHeight: "270px" }}>
            {data.slice(1).map(function (elem, key) {
                let label = (elem.label === "failing") ? "Critical" : elem.label;
                return (<div class="info-container  zero-values NORMAL">
                    <div onClick={props.clickable?()=>{props.onClick(label.toLowerCase())}:null} style={props.clickable?{display: "flex", cursor: "pointer"}:{display: "flex"}}>
                    <div class="info-title">
                        <span class="info-bullet NORMAL" style={{ backgroundColor: `${elem.color}` }}></span>
                        <span class="info-label NORMAL"> {FormatToLabel(label)} </span>
                    </div>
                     <div class="info-count">({elem.value})</div>
                </div>
                </div>)
            })
            }
        </div>

    </div>)
}
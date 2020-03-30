import LegendNode from './LegendNode.js';
import React from 'react';
import uuid from 'uuid';
import { layout, select, behavior, event } from 'd3';
import './style.css';


var legend = [{
    "name": "EPG",
    "level": "#085A87",
    "label": "EPG",
    "type": "#085A87",
    "trans": 0
}, {
    "name": "EP",
    "level": "#2DBBAD",
    "label": "EndPoint",
    "type": "#2DBBAD",
    "trans": 1.2
}]


export default class Legend extends React.Component {
    render() {
        return (
            <div>
                <svg width="100%" height="16%" style={{ backgroundColor: "rgb(224,224,226)" }}>
                    {legend.map(legend => (
                        <LegendNode
                            key={uuid.v4()}
                            nodeSvgShape={{ shape: 'circle', shapeProps: { r: 20 } }}
                            orientation='vertical'
                            transitionDuration={500}
                            nodeData={legend}
                            name={legend.name}
                            translate={{ x: 60 + legend.trans * 50, y: 25 }}
                            textLayout={{ textAnchor: "middle", y: 0 }}
                            styles={{ leafNode: { circle: { fill: "#DFF" } } }}
                        />
                    ))}
                </svg>
            </div>
        );
    }
}


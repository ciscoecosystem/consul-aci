import LegendNode from './LegendNode.js';
import React from 'react';
import uuid from 'uuid';
import { layout, select, behavior, event } from 'd3';
import './style.css';

const svgSquare = {
    shape: 'rect',
    shapeProps: {
        width: 20,
        height: 20,
        x: -10,
        y: -10,
    }
}

const svgCircle = { shape: 'circle', shapeProps: { r: 20 } }


var legend = [{
    "name": "",
    "level": "seagreen",
    "type": "seagreen",
    "label": "Normal",
    "trans": 8,
    "shape": svgSquare
}, {
    "name": "",
    "level": "orange",
    "type": "orange",
    "label": "Normal",
    "trans": 10,
    "shape": svgSquare
}, {
    "name": "",
    "level": "red",
    "type": "red",
    "label": "Normal",
    "trans": 12,
    "shape": svgSquare
}]


export default class HealthLegend extends React.Component {
    render() {
        return (
            <div width="20%">
                {/* <svg width="20%" height="16%" style={{ backgroundColor: "rgb(224,224,226)", float : "right", zIndex : "-1000"}}>
                    {legend.map(legend => (
                        <LegendNode
                            key={uuid.v4()}
                            nodeSvgShape={legend.shape}
                            orientation='vertical'
                            transitionDuration={500}
                            nodeData={legend}
                            name={legend.name}
                            translate={{ x: 60 + legend.trans * 50, y: 25 }}
                            textLayout={{ textAnchor: "middle", y: 0 }}
                            styles={{ leafNode: { circle: { fill: "#DFF" } } }}
                        />
                    ))}
                </svg> */}
            </div>
        );
    }
}
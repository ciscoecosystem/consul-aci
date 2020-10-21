import React from "react";
import uuid from "uuid";
import { IconButton } from "blueprint-react";
import LegendNode from "./LegendNode.js";

import "./style.css";

var legend = [
  {
    name: "AppProf",
    level: "#581552",
    label: "Application",
    sub_label: "profile",
    type: "#581552",
    trans: 0
  },
  {
    name: "EPG",
    level: "#025e91",
    label: "End Point",
    sub_label: "Group",
    type: "#025e91",
    trans: 1
  },
  {
    name: "EP",
    level: "#2DBBAD",
    label: "End Point",
    type: "#2DBBAD",
    trans: 2
  },
  {
    name: "Service",
    level: "#C5D054",
    label: "Service",
    type: "#C5D054",
    trans: 2.9
  },
  {
    name: "EP",
    level: "grey",
    label: "Non-Service",
    sub_label: "End Points",
    type: "grey",
    trans: 3.9
  }
];

function zoomIn() {
  window.treeComponent.zoomInTree();
}

function zoomOut() {
  window.treeComponent.zoomOutTree();
}

export default class Legend extends React.Component {
  render() {
    return (
      <div className="row no-gutters" style={{ width: "100%", background: "rgb(224,224,226)" }}>
        <div className="col-md-12">
          {" "}
          <svg
            width="70%"
            height="80px"
            style={{ backgroundColor: "rgb(224,224,226)" }}
          >
            {legend.map(legend => (
              <LegendNode
                key={uuid.v4()}
                nodeSvgShape={{ shape: "circle", shapeProps: { r: 15 } }}
                orientation="vertical"
                transitionDuration={500}
                nodeData={legend}
                name={legend.name}
                translate={{ x: 60 + legend.trans * 85, y: 25 }}
                textLayout={{ textAnchor: "middle", y: 0 }}
                styles={{ leafNode: { circle: { fill: "#DFF" } } }}
              />
            ))}

            <symbol id="icon-zoom-in" viewBox="0 0 5 5">
              <title>cog</title>
              <path d="M14.59 9.535c-0.839-1.454-0.335-3.317 1.127-4.164l-1.572-2.723c-0.449 0.263-0.972 0.414-1.529 0.414-1.68 0-3.042-1.371-3.042-3.062h-3.145c0.004 0.522-0.126 1.051-0.406 1.535-0.839 1.454-2.706 1.948-4.17 1.106l-1.572 2.723c0.453 0.257 0.845 0.634 1.123 1.117 0.838 1.452 0.336 3.311-1.12 4.16l1.572 2.723c0.448-0.261 0.967-0.41 1.522-0.41 1.675 0 3.033 1.362 3.042 3.046h3.145c-0.001-0.517 0.129-1.040 0.406-1.519 0.838-1.452 2.7-1.947 4.163-1.11l1.572-2.723c-0.45-0.257-0.839-0.633-1.116-1.113zM8 11.24c-1.789 0-3.24-1.45-3.24-3.24s1.45-3.24 3.24-3.24c1.789 0 3.24 1.45 3.24 3.24s-1.45 3.24-3.24 3.24z" />
            </symbol>
          </svg>
          <IconButton
            className="pull-right half-margin-left base-margin-top qtr-margin-right"
            type="btn--icon btn--gray-ghost"
            size="btn--small"
            icon="icon-zoom-in"
            onClick={zoomIn}
          />
          <IconButton
            className="pull-right base-margin-top"
            type="btn--icon btn--gray-ghost"
            size="btn--small"
            icon="icon-zoom-out"
            onClick={zoomOut}
          />
          &nbsp;
             <IconButton
            className="pull-right base-margin-top "
            type="btn--icon btn--gray-ghost"
            size="btn--small"
            icon="icon-refresh"
            onClick={this.props.reloadController}
          />
        </div>

      </div>
    );
  }
}

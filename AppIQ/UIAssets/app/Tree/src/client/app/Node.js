import React from "react";
import PropTypes from "prop-types";
import uuid from "uuid";
import { select } from "d3";
import "./style.css";
import "react-tippy/dist/tippy.css";
import d3Tip from "d3-tip";
d3.tip = d3Tip;

// var qtip;
var d;

export default class Node extends React.Component {
  constructor(props) {
    super(props);
    const {
      nodeData: { parent },
      orientation
    } = props;
    const originX = parent ? parent.x : 0;
    const originY = parent ? parent.y : 0;

    this.qtip = null;

    this.state = {
      transform: this.setTransformOrientation(originX, originY, orientation),
      initialStyle: {
        opacity: 0
      }
    };

    this.handleClick = this.handleClick.bind(this);
    this.handleMouseIn = this.handleMouseIn.bind(this);
    this.handleMouseOut = this.handleMouseOut.bind(this);
    // this.createtip = this.createtip.bind(this);
  }

  componentDidMount() {
    const {
      nodeData: { x, y },
      orientation,
      transitionDuration
    } = this.props;
    const transform = this.setTransformOrientation(x, y, orientation);

    this.applyTransform(transform, transitionDuration);
  }

  componentWillUpdate(nextProps) {
    const transform = this.setTransformOrientation(
      nextProps.nodeData.x,
      nextProps.nodeData.y,
      nextProps.orientation
    );
    this.applyTransform(transform, nextProps.transitionDuration);
  }

  shouldComponentUpdate(nextProps) {
    return this.shouldNodeTransform(this.props, nextProps);
  }

  shouldNodeTransform(ownProps, nextProps) {
    return (
      nextProps.subscriptions !== ownProps.subscriptions ||
      nextProps.nodeData.x !== ownProps.nodeData.x ||
      nextProps.nodeData.y !== ownProps.nodeData.y ||
      nextProps.orientation !== ownProps.orientation
    );
  }

  setTransformOrientation(x, y, orientation) {
    return orientation === "horizontal"
      ? `translate(${y},${x})`
      : `translate(${x},${y})`;
  }

  applyTransform(transform, transitionDuration, opacity = 1, done = () => {}) {
    if (transitionDuration === 0) {
      select(this.node)
        .attr("transform", transform)
        .style("opacity", opacity);
      done();
    } else {
      select(this.node)
        .transition()
        .duration(transitionDuration)
        .attr("transform", transform)
        .style("opacity", opacity)
        .each("end", done);
    }
  }

  handleClick() {
    this.props.onClick(this.props.nodeData.id);
  }

  handleMouseIn(event) {
    const titleMap = {
      AppProf: "Application Profile",
      EP: "End Point",
      EPG: "End Point Group",
      Node: "Node"
    };
    d = this.props.nodeData;
    this.qtip = d3
      .tip()
      .attr("class", "d3-tip")
      .direction("se")
      .html(function() {
        var title =
          "<strong>" + titleMap[d.name] + " Information</strong></br>";
        var htmlstring = "<table>";
        if (
          d.name != "Node" &&
          d.name != "AppProf" &&
          d.label != "App Unmapped EPs"
        ) {
          htmlstring =
            htmlstring +
            "<tr><td><div class='nodeAttributesBase'>Tiers</div></td><td><div class='nodeAttributesBase'>: " +
            d.sub_label +
            "</div></td></tr>";
        }
        Object.keys(d.attributes).map(function(key, index) {
          if (
            key != "ServiceEndpoints" &&
            key != "HealthRuleViolations" &&
            key != "Contracts"
          ) {
            htmlstring =
              htmlstring +
              "<tr><td><div class='nodeAttributesBase'>" +
              key +
              "</div></td><td><div class='nodeAttributesBase'>: " +
              d.attributes[key] +
              "</div></td></tr>";
          }
        });
        var htmlstring = htmlstring + "</table>";
        if (d.attributes.hasOwnProperty("ServiceEndpoints")) {
          htmlstring =
            htmlstring +
            "<table></br></br><strong>Service Endpoints:</strong></br>";
          var i;
          for (i = 0; i < d.attributes.ServiceEndpoints.length; ++i) {
            Object.keys(d.attributes.ServiceEndpoints[i]).map(function(
              key,
              index
            ) {
              if (key != "Service Endpoints:") {
                htmlstring =
                  htmlstring +
                  "<tr><td><div class='nodeAttributesBase'>" +
                  key +
                  "</div></td><td><div class='nodeAttributesBase'>: " +
                  d.attributes.ServiceEndpoints[i][key] +
                  "</div></td></tr>";
              }
            });
          }
        }
        var htmlstring = htmlstring + "</table>";
        if (d.attributes.hasOwnProperty("HealthRuleViolations")) {
          htmlstring =
            htmlstring +
            "<table></br></br><strong>Health Rule Violations:</strong></br>";
          var i;
          for (i = 0; i < d.attributes.HealthRuleViolations.length; ++i) {
            Object.keys(d.attributes.HealthRuleViolations[i]).map(function(
              key,
              index
            ) {
              if (key != "HealthRuleViolations:") {
                htmlstring =
                  htmlstring +
                  "<tr><td><div class='nodeAttributesBase'>" +
                  key +
                  "</div></td><td><div class='nodeAttributesBase'>: " +
                  d.attributes.HealthRuleViolations[i][key] +
                  "</div></td></tr>";
              }
            });
          }
        }
        var htmlstring = htmlstring + "</table>";
        if (d.attributes.hasOwnProperty("Contracts")) {
          htmlstring =
            htmlstring + "<table></br></br><strong>Contracts:</strong></br>";
          var i;
          for (i = 0; i < d.attributes.Contracts.length; ++i) {
            Object.keys(d.attributes.Contracts[i]).map(function(key, index) {
              if (key != "Contracts:") {
                htmlstring =
                  htmlstring +
                  "<tr><td><div class='nodeAttributesBase'>" +
                  key +
                  "</div></td><td><div class='nodeAttributesBase'>: " +
                  d.attributes.Contracts[i][key] +
                  "</div></td></tr>";
              }
            });
          }
        }
        var htmlstring = htmlstring + "</table>";
        return title + htmlstring;
      });
    var svg = select(this.node).call(this.qtip);

    window.qtip = this.qtip;

    if (window.tipAvailable) {
      this.qtip.show("d", event.target);
    } else {
      console.log("AppD : Tooltip display locked.");
    }
  }

  handleMouseOut() {
    this.qtip.hide();
  }

  componentWillLeave(done) {
    const {
      nodeData: { parent },
      orientation,
      transitionDuration
    } = this.props;
    const originX = parent ? parent.x : 0;
    const originY = parent ? parent.y : 0;
    const transform = this.setTransformOrientation(
      originX,
      originY,
      orientation
    );

    this.applyTransform(transform, transitionDuration, 0, done);
  }

  render() {
    const { nodeData, nodeSvgShape, textLayout, styles } = this.props;
    const nodeStyle = nodeData._children
      ? { ...styles.node }
      : { ...styles.leafNode };

    //onClick={this.handleClick}

    return (
      <g
        id={nodeData.id}
        ref={n => {
          this.node = n;
        }}
        style={this.state.initialStyle}
        className={nodeData._children ? "nodeBase" : "leafNodeBase"}
        transform={this.state.transform}
        onClick={this.handleClick}
      
      >
        {(nodeStyle.circle.stroke = nodeData.level)}
        {(nodeStyle.circle.fill = nodeData.type)}

        {this.props.circleRadius ? (
          <circle r={this.props.circleRadius} style={nodeStyle.circle} />
        ) : (
          React.createElement(nodeSvgShape.shape, {
            ...nodeSvgShape.shapeProps,
            ...nodeStyle.circle
          })
        )}

        <text
          className="nodeNameBase"
          style={nodeStyle.name}
          textAnchor={textLayout.textAnchor}
          x={textLayout.x}
          y={textLayout.y}
          transform={textLayout.transform}
          dy={this.props.name == "EPG" ? "0.35em" : ".35em"}
        >
          {this.props.name == "EP" ? "EP" : this.props.name.charAt(0)}
        </text>

        {/* <text
          className="nodeNameBase"
          style={{fontSize : "10px"}}
          textAnchor={textLayout.textAnchor}
          x={textLayout.x}
          y={textLayout.y}
          transform={textLayout.transform}
          dy="1.3em"
        >
          {this.props.fraction ? this.props.fraction :  ""}
        </text> */}

        <text
          className="nodeNameBase"
          style={{ fontSize: "10px" }}
          textAnchor={textLayout.textAnchor}
          x={textLayout.x}
          y={textLayout.y}
          transform={textLayout.transform}
          dy="1.3em"
        >
          {this.props.totalUnmapped ? this.props.totalUnmapped : ""}
        </text>

        {this.props.label ? (
          <text
            className="nodeSubLabel"
            y={textLayout.y + 35}
            textAnchor={textLayout.textAnchor}
            transform={textLayout.transform}
            //style={nodeStyle.attributes}
            dy="10"
          >
            {"(" + this.props.label +")"}
          </text>
        ) : (
          ""
        )}
        {this.props.sub_label ? (
          <text
            className="nodeAttributesBase"
            y={textLayout.y + 23}
            textAnchor={textLayout.textAnchor}
            transform={textLayout.transform}
            //style={nodeStyle.attributes}
            dy="10"
          >
            {
              this.props.sub_label.replace(/([^,]*),.*/, "$1 + ") +
              " " +
              (this.props.sub_label.split(",").length > 1
                ? this.props.sub_label.split(",").length - 1
                : "") }
          </text>
        ) : (
          ""
        )}
      </g>
    );
  }
}

Node.defaultProps = {
  textAnchor: "start",
  attributes: undefined,
  circleRadius: undefined,
  styles: {
    node: {
      circle: {},
      name: {},
      attributes: {}
    },
    leafNode: {
      circle: {},
      name: {},
      attributes: {}
    }
  }
};

Node.propTypes = {
  nodeData: PropTypes.object.isRequired,
  nodeSvgShape: PropTypes.object.isRequired,
  orientation: PropTypes.oneOf(["horizontal", "vertical"]).isRequired,
  transitionDuration: PropTypes.number.isRequired,
  onClick: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  attributes: PropTypes.object,
  textLayout: PropTypes.object.isRequired,
  subscriptions: PropTypes.object.isRequired, // eslint-disable-line react/no-unused-prop-types
  circleRadius: PropTypes.number,
  styles: PropTypes.object
};

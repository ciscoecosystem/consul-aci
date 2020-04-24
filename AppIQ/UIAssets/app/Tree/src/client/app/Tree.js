import React from "react";
import PropTypes from "prop-types";
import { TransitionGroup } from "react-transition-group";
import { layout, select, behavior, event } from "d3";
import d3 from "d3";
import clone from "clone";
import deepEqual from "deep-equal";
import uuid from "uuid";

import Node from "./Node.js";
import Link from "./Link.js";
import "./style.css";

import DetailsPane from "./DetailsPane";
import DetailsPage from "./DetailsPage";

const svgSquare = {
  shape: "rect",
  shapeProps: {
    width: 20,
    height: 7,
    x: -10,
    y: -10
  }
};

const svgSquareButton = {
  shape: "rect",
  shapeProps: {
    width: 40,
    height: 20,
    x: -10,
    y: -10
  }
};

const svgCircle = { shape: "circle", shapeProps: { r: 20 } };

var legend = [
  {
    name: "",
    level: "seagreen",
    type: "seagreen",
    label: "Normal",
    trans: 8,
    shape: svgSquare
  },
  {
    name: "",
    level: "orange",
    type: "orange",
    label: "Warning",
    trans: 9,
    shape: svgSquare
  },
  {
    name: "",
    level: "red",
    type: "red",
    label: "Critical",
    trans: 10,
    shape: svgSquare
  }
];

var legendButton = {
  name: "",
  level: "grey",
  type: "grey",
  trans: 8,
  shape: svgSquare
};

var boundEvent;

export default class Tree extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      initialRender: true,
      data: this.assignInternalProperties(clone(props.data)),

      detailsPane: {
        visible: false,
        data: {}
      },

      detailsPage: {
        visible: false,
        data: {}
      }
    };
    this.findNodesById = this.findNodesById.bind(this);
    this.collapseNode = this.collapseNode.bind(this);
    this.handleNodeToggle = this.handleNodeToggle.bind(this);
    this.handleOnClickCb = this.handleOnClickCb.bind(this);
    this.handleMouseOver = this.handleMouseOver.bind(this);

    this.handleNodeClick = this.handleNodeClick.bind(this);
    this.openDetailsPane = this.openDetailsPane.bind(this);
    this.closeDetailsPane = this.closeDetailsPane.bind(this);
    this.openDetailsPage = this.openDetailsPage.bind(this);
    this.closeDetailsPage = this.closeDetailsPage.bind(this);

    window.treeComponent = this;
    window.tipAvailable = true;
  }

  zoomOutTree() {
    const svg = select(".rd3t-svg");
    const g = select(".rd3t-g");
    svg.call(boundEvent.event);
    boundEvent.scale(boundEvent.scale() - 0.2);
    svg
      .transition()
      .duration(550)
      .call(boundEvent.event);
  }

  zoomInTree() {
    const svg = select(".rd3t-svg");
    const g = select(".rd3t-g");
    svg.call(boundEvent.event);
    boundEvent.scale(boundEvent.scale() + 0.2);
    svg
      .transition()
      .duration(550)
      .call(boundEvent.event);
  }

  componentDidMount() {
    this.bindZoomListener(this.props);
    this.zoomOutTree = this.zoomOutTree.bind(this);
    this.zoomInTree = this.zoomInTree.bind(this);

    // TODO find better way of setting initialDepth, re-render here is suboptimal
    this.setState({ initialRender: false }); // eslint-disable-line

    select(".linkBase").attr("marker-end", "url(#arrow)");
    //test
  }

  componentWillReceiveProps(nextProps) {
    // Clone new data & assign internal properties
    if (!deepEqual(this.props.data, nextProps.data)) {
      this.setState({
        data: this.assignInternalProperties(clone(nextProps.data))
      });
    }

    // If zoom-specific props change -> rebind listener with new values
    if (
      !deepEqual(this.props.translate, nextProps.translate) ||
      !deepEqual(this.props.scaleExtent, nextProps.scaleExtent)
    ) {
      this.bindZoomListener(nextProps);
    }
  }

  /**
   * setInitialTreeDepth - Description
   *
   * @param {array} nodeSet Array of nodes generated by `generateTree`
   * @param {number} initialDepth Maximum initial depth the tree should render
   *
   * @return {void}
   */
  setInitialTreeDepth(nodeSet, initialDepth) {
    nodeSet.forEach(n => {
      n._collapsed = n.depth >= initialDepth;
    });
  }

  /**
   * bindZoomListener - If `props.zoomable`, binds a listener for
   * "zoom" events to the SVG and sets scaleExtent to min/max
   * specified in `props.scaleExtent`.
   *
   * @return {void}
   */
  bindZoomListener(props) {
    const { zoomable, scaleExtent, translate } = props;
    boundEvent = behavior
      .zoom()
      .scaleExtent([scaleExtent.min, scaleExtent.max])
      .on("zoom", () => {
        g.attr(
          "transform",
          `translate(${event.translate}) scale(${event.scale})`
        );
      })
      // Offset so that first pan and zoom does not jump back to [0,0] coords
      .translate([translate.x, translate.y]);
    const svg = select(".rd3t-svg");
    const g = select(".rd3t-g");

    if (zoomable) {
      svg.call(boundEvent);
    }
  }

  /**
   * assignInternalProperties - Assigns internal properties to each node in the
   * `data` set that are required for tree manipulation and returns
   * a new `data` array.
   *
   * @param {array} data Hierarchical tree data
   *
   * @return {array} `data` array with internal properties added
   */
  assignInternalProperties(data) {
    return data.map(node => {
      node.id = uuid.v4();
      node._collapsed = false;
      // if there are children, recursively assign properties to them too
      if (node.children && node.children.length > 0) {
        node.children = this.assignInternalProperties(node.children);
        node._children = node.children;
      }
      return node;
    });
  }

  /**
   * findNodesById - Description
   *
   * @param {string} nodeId The `node.id` being searched for
   * @param {array} nodeSet Array of `node` objects
   * @param {array} hits Accumulator for matches, passed between recursive calls
   *
   * @return {array} Set of nodes matching `nodeId`
   */
  // TODO Refactor this into a more readable/reasonable recursive depth-first walk.
  findNodesById(nodeId, nodeSet, hits) {
    if (hits.length > 0) {
      return hits;
    }

    hits = hits.concat(nodeSet.filter(node => node.id === nodeId));

    nodeSet.forEach(node => {
      if (node._children && node._children.length > 0) {
        hits = this.findNodesById(nodeId, node._children, hits);
        return hits;
      }
      return hits;
    });

    return hits;
  }

  /**
   * collapseNode - Recursively sets the `_collapsed` property of
   * the passed `node` object and its children to `true`.
   *
   * @param {object} node Node object with custom properties
   *
   * @return {void}
   */
  collapseNode(node) {
    node._collapsed = true;
    if (node._children && node._children.length > 0) {
      node._children.forEach(child => {
        this.collapseNode(child);
      });
    }
  }

  /**
   * expandNode - Sets the `_collapsed` property of
   * the passed `node` object to `false`.
   *
   * @param {type} node Node object with custom properties
   *
   * @return {void}
   */
  expandNode(node) {
    node._collapsed = false;
  }

  /**
   * TODO: Remove this function
   * handleNodeToggle - Finds the node matching `nodeId` and
   * expands/collapses it, depending on the current state of
   * its `_collapsed` property.
   * `setState` callback receives targetNode and handles
   * `props.onClick` if defined.
   *
   * @param {string} nodeId A node object's `id` field.
   *
   * @return {void}
   */
  handleNodeToggle(nodeId) {
    const data = clone(this.state.data);
    const matches = this.findNodesById(nodeId, data, []);
    const targetNode = matches[0];

    window.tipAvailable = false;
    let tipPermission = setTimeout(() => {
      window.tipAvailable = true;
    }, 700);

    if (this.props.collapsible) {
      targetNode._collapsed
        ? this.expandNode(targetNode)
        : this.collapseNode(targetNode);
      this.setState({ data }, () => this.handleOnClickCb(targetNode));
    } else {
      this.handleOnClickCb(targetNode);
    }
  }

  handleMouseOver(attrs) {
    const data = clone(this.state.data);
    const matches = this.findNodesById(nodeId, data, []);
    const targetNode = matches[0];
    tip = d3
      .tip()
      .attr("class", "d3-tip")
      .html(function(d) {
        return (
          d.attributes &&
          Object.keys(this.props.attributes).map(labelKey => (
            <tspan x={textLayout.x} key={uuid.v4()}>
              {labelKey + " : " + this.props.attributes[labelKey]}
            </tspan>
          ))
        );
      });
  }

  handleMouseOut(attrs) {}

  /**
   * handleOnClickCb - Handles the user-defined `onClick` function
   *
   * @param {object} targetNode Description
   *
   * @return {void}
   */
  handleOnClickCb(targetNode) {
    const { onClick } = this.props;
    if (onClick && typeof onClick === "function") {
      onClick(clone(targetNode));
    }
  }

  /**
   * Handles the event when user clicks a node
   */
  handleNodeClick(nodeId) {
    const data = clone(this.state.data);
    const matches = this.findNodesById(nodeId, data, []);
    const targetNode = matches[0];
    this.openDetailsPane(targetNode);
  }


   /**
   * Opens a Right panel with data of clicked node
   */
  openDetailsPane(nodeData) {
    this.setState({
      detailsPane: {
        visible: true,
        data: nodeData
      }
    });
   // this.openDetailsPage(nodeData);
  }

 /**
   * Closes a right panel
   */
  closeDetailsPane() {
    
    this.setState({
      detailsPane: {
        visible: false,
        data : {}
       
      }
    });
  }

   /**
   * Opens a details page with data (more details) of clicked node
   */
  openDetailsPage(nodeData) {
   console.log("open deatails")
   console.log(nodeData)
    this.setState({
      detailsPage: {
        visible: true,
        data: nodeData
      }
    });
  }

   /**
   * Closes details page
   */
  closeDetailsPage() {

    this.setState({
      detailsPage: {
        visible: false,
         data:{}
      }
    });
  }

  /**
   * generateTree - Generates tree elements (`nodes` and `links`) by
   * grabbing the rootNode from `this.state.data[0]`.
   * Restricts tree depth to `props.initialDepth` if defined and if this is
   * the initial render of the tree.
   *
   * @return {object} Object containing `nodes` and `links`.
   */
  generateTree() {
    if (this.props.data.length == 0) {
      const nodes = [];
      const links = [];
      return { nodes, links };
    }
    const {
      initialDepth,
      depthFactor,
      separation,
      nodeSize,
      orientation
    } = this.props;

    const tree = layout
      .tree()
      .nodeSize(
        orientation === "horizontal"
          ? [nodeSize.y - 25, nodeSize.x]
          : [nodeSize.x - 25, nodeSize.y]
      )
      .separation((a, b) =>
        deepEqual(a.parent, b.parent)
          ? separation.siblings
          : separation.nonSiblings
      )
      .children(d => (d._collapsed ? null : d._children));

    const rootNode = this.state.data[0];
    const nodes = tree.nodes(rootNode);
    const links = tree.links(nodes);

    // set `initialDepth` on first render if specified
    if (initialDepth !== undefined && this.state.initialRender) {
      this.setInitialTreeDepth(nodes, initialDepth);
    }

    if (depthFactor) {
      nodes.forEach(node => {
        node.y = node.depth * depthFactor;
      });
    }

    return { nodes, links };
  }

  render() {
    const { nodes, links } = this.generateTree();
    const {
      nodeSvgShape,
      orientation,
      translate,
      pathFunc,
      transitionDuration,
      zoomable,
      textLayout,
      nodeSize,
      depthFactor,
      initialDepth,
      separation,
      circleRadius,
      styles
    } = this.props;

    const subscriptions = {
      ...nodeSize,
      ...separation,
      depthFactor,
      initialDepth
    };

    const windowHeight = parseFloat(window.innerHeight) / 2;
    const windowWidth = parseFloat(window.innerWidth) / 2 - 80;

    // alert(windowHeight + " : " + windowWidth)

    if (nodes.length == 0) {
      return (
        <div
          className={`rd3t-tree-container ${
            zoomable ? "rd3t-grabbable" : undefined
          }`}
        >
          <svg width="100%" height="100%">
            <text
              x={windowWidth/2}
              y={windowHeight}
              font-family="sans-serif"
              font-size="20px"
              fill="grey"
            >
              No Endpoints Found for the given Application in the given Tenant.
            </text>
          </svg>
        </div>
      );
    }

    return (
      <div>
        <div
          className={`rd3t-tree-container ${
            zoomable ? "rd3t-grabbable" : undefined
          }`}
        >
          <svg className="rd3t-svg" width="100%" height="100%">
            <defs>
              <marker
                id="arrow"
                markerUnits="strokeWidth"
                markerWidth="8"
                markerHeight="8"
                viewBox="0 0 12 12"
                refX="6"
                refY="6"
                orient="auto"
              >
                <path
                  d="M 0 0 12 6 0 12 0 3"
                  style={{ fill: "rgb(54, 126, 233)" }}
                />
              </marker>
            </defs>
            <TransitionGroup
              component="g"
              className="rd3t-g"
              transform={`translate(${translate.x},${translate.y})`}
            >
               {/* the links under root node is avoided */}
              {links.slice(this.props.totApps).map(linkData => (
                <Link
                  key={uuid.v4()}
                  orientation={orientation}
                  pathFunc={pathFunc}
                  linkData={linkData}
                  transitionDuration={transitionDuration}
                  styles={styles.links}
                />
              ))}

              {/* root node is avoided */}
              {nodes.slice(1).map(nodeData => (
                <Node
                  key={nodeData.id}
                  nodeSvgShape={nodeSvgShape}
                  orientation={orientation}
                  transitionDuration={transitionDuration}
                  nodeData={nodeData}
                  name={nodeData.name}
                  sub_label={nodeData.sub_label}
                  fraction={nodeData.fraction}
                  totalUnmapped={nodeData.totalUnmapped}
                  label={nodeData.label}
                  attributes={nodeData.attributes}
                  // onClick={this.handleNodeToggle}
                  onClick={this.handleNodeClick}
                  closeDetailsPane={this.closeDetailsPane}
                  textLayout={textLayout}
                  circleRadius={circleRadius}
                  subscriptions={subscriptions}
                  styles={styles.nodes}
                />
              ))}
            </TransitionGroup>
          </svg>
        </div>

        <div>
          {this.state.detailsPane.visible ? (
            <DetailsPane
              closeDetailsPane={this.closeDetailsPane}
              openDetailsPage={this.openDetailsPage}
              data={this.state.detailsPane.data}
            />
          ) : null}   
          {this.state.detailsPage.visible ? (
            <DetailsPage
              data = {this.state.detailsPage.data}
              closeDetailsPage={this.closeDetailsPage}
              datacenterName={this.props.datacenterName}
            />
          ) : null}
        </div>
      </div>
    );
  }
}

Tree.defaultProps = {
  nodeSvgShape: {
    shape: "circle",
    shapeProps: {
      r: 10
    }
  },
  onClick: undefined,
  orientation: "horizontal",
  translate: { x: 0, y: 0 },
  pathFunc: "diagonal",
  transitionDuration: 500,
  depthFactor: undefined,
  collapsible: true,
  initialDepth: undefined,
  zoomable: true,
  scaleExtent: { min: 0.1, max: 1 },
  nodeSize: { x: 140, y: 140 },
  separation: { siblings: 0.9, nonSiblings: 1 },
  textLayout: {
    textAnchor: "start",
    x: 10,
    y: -10,
    transform: undefined
  },
  circleRadius: undefined, // TODO: DEPRECATE
  styles: {}
};

Tree.propTypes = {
  data: PropTypes.array.isRequired,
  datacenterName: PropTypes.string,
  nodeSvgShape: PropTypes.shape({
    shape: PropTypes.string,
    shapeProps: PropTypes.object
  }),
  onClick: PropTypes.func,
  orientation: PropTypes.oneOf(["horizontal", "vertical"]),
  translate: PropTypes.shape({
    x: PropTypes.number,
    y: PropTypes.number
  }),
  pathFunc: PropTypes.oneOfType([
    PropTypes.oneOf(["diagonal", "elbow", "straight"]),
    PropTypes.func
  ]),
  transitionDuration: PropTypes.number,
  depthFactor: PropTypes.number,
  collapsible: PropTypes.bool,
  initialDepth: PropTypes.number,
  zoomable: PropTypes.bool,
  scaleExtent: PropTypes.shape({
    min: PropTypes.number,
    max: PropTypes.number
  }),
  nodeSize: PropTypes.shape({
    x: PropTypes.number,
    y: PropTypes.number
  }),
  separation: PropTypes.shape({
    siblings: PropTypes.number,
    nonSiblings: PropTypes.number
  }),
  textLayout: PropTypes.object,
  circleRadius: PropTypes.number,
  styles: PropTypes.shape({
    nodes: PropTypes.object,
    links: PropTypes.object
  })
};

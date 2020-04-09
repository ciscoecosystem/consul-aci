import React from "react";
import { Icon } from "blueprint-react";
import "./DetailsPane.css";

const successColor = "#6ebe4a";
const failColor = "#e2231a";
const warningColor = "#f49141";

const NODE_EP_NAME = "EP";
const NODE_SERVICE_NAME = "Service";
const NODE_EPG_NAME = "EPG"

function NoInformation() {
  return <div className="no-info" >No Infomation</div>;
}

function CONSUL_ServiceCard(props) {
  let attributeOrder = ["Service", "Address", "Service Instance", "Service Checks", "Service Tag", "Service Kind"]

  return CardData(props, attributeOrder);
}

function CONSUL_EPCard(props) {
  let { attributes } = props;

  if (props.level === "grey") { // leat node of EP when it has no service under it
    return CardData(props)
  }

  let attributeOrder = ["IP", "Interfaces", "VMM-Domain"];
  let nodeDetailOrder = ["Node", "Node Checks", "Reporting Node IP"];
  let serviceOrder = ["Service", "Address", "Service Checks"]

  return (<React.Fragment>
    {CardData(props, attributeOrder)}

    {('Node' in attributes) &&
      <span>
        Consul Node
      {CardData(Object.assign(props, { name: undefined }), nodeDetailOrder)}
      </span>}

    {('Services_List' in attributes) &&
      <span className="mt-2">
        Consul Services
     {(attributes.Services_List.length > 0) ? attributes.Services_List.map(serviceData => CardData(Object.assign({}, { attributes: serviceData }), serviceOrder))
          : NoInformation()}
      </span>}

  </React.Fragment>
  )

}

function CONSUL_EPGCard(props) {
  const { attributes } = props;

  const infoOrder = ["VRF", "BD"];
  const nodeDetailOrder = ["Node", "Node Checks", "Reporting Node IP"];
  const serviceOrder = ["Service", "Address", "Service Checks"]

  return (<React.Fragment>
    {/* 1. epg information */}
    {CardData(props, infoOrder)}

    {/* 2. contract information */}
    {('Contracts' in attributes) &&
      <span>
        Contracts Information
        <ContractDetails
          attributes={attributes.Contracts}
        />
      </span>}

    {/* 3. consul node */}
    {('Nodes' in attributes) &&
      <span>
        Node Services
        {(attributes.Nodes.length > 0) ?
          attributes.Nodes.map(nodeData => CardData(Object.assign({}, { attributes: nodeData }), nodeDetailOrder))
          : NoInformation()}
      </span>}

    {/* 4. service list  */}
    {('Services_List' in attributes) &&
      <span className="mt-2">
        Consul Services
      {(attributes.Services_List.length > 0) ? attributes.Services_List.map(serviceData => CardData(Object.assign({}, { attributes: serviceData }), serviceOrder))
          : NoInformation()}
      </span>}

  </React.Fragment>
  )

}

function CardData(props, attributeOrder = undefined) {
  let { attributes, name } = props;

  if (attributeOrder === undefined || Object.keys(attributeOrder).length === 0) {
    attributeOrder = Object.keys(props.attributes);
  }

  return (
    <table className="info-table">
      {name ?
        <tr>
          <td width="30%">Name</td>
          <td width="70%">{name}</td>
        </tr> : null
      }
      {props.level == "grey" ?
        (
          <tr>
            <td width="30%" className="bold-font">MAC</td>
            <td width="70%" className="bold-font">IP</td>
          </tr>
        ) : null
      }
      {attributeOrder.map(key => {
        // when value is simply string/number
        if (typeof attributes[key] == "string" || typeof attributes[key] == "number") {
          return (
            <tr>
              <td width="30%">{key}</td>
              <td width="70%">{attributes[key]}</td>
            </tr>
          );
          // when value is list
        } else if (
          Array.isArray(attributes[key]) &&
          typeof attributes[key][0] == "string"
        ) {
          return (
            <tr>
              <td width="30%"> {key} </td>
              <td width="70%">{attributes[key].join(", ")}</td>
            </tr>
          );
        }
        // special case for service checks
        else if (key === "Service Checks" || key === "Node Checks") {
          let checks = attributes[key];
          return (checks) ? (
            <tr>
              <td width="30%">{key}</td>
              <td width="70%">
                <span>
                  {(checks.passing !== undefined) && (<span> <Icon size="icon-small" type=" icon-check-square" style={{ color: successColor }}></Icon>&nbsp;{checks.passing}&nbsp;&nbsp;</span>)}
                  {(checks.warning !== undefined) && (<span> <Icon size="icon-small" type=" icon-warning" style={{ color: warningColor }}></Icon>&nbsp;{checks.warning}&nbsp;&nbsp;</span>)}
                  {(checks.failing !== undefined) && (<span> <Icon size="icon-small" type=" icon-exit-contain" style={{ color: failColor }}></Icon>&nbsp;{checks.failing} </span>)}
                </span>
              </td>
            </tr>) : (null)
        }
      })}
    </table>
  );
}

function ContractDetails(props) {
  if (props.attributes && props.attributes.constructor == Array && props.attributes.length > 0) {
    return (
      <table className="info-table">
        {props.attributes.map(key => {
          return (
            <tr>
              <td width="30%">{Object.keys(key)[0]}</td>
              <td width="70%">{key[Object.keys(key)[0]]}</td>
            </tr>
          );
        })}
      </table>
    );
  }
  return NoInformation();
}

class DetailsPane extends React.Component {
  constructor(props) {
    super(props);
    this.healthColor = this.healthColor.bind(this);
    this.state = {
      data: this.props.data,
      color: {
        NORMAL: "#2e8b57",
        WARNING: "orange",
        CRITICAL: "red"
      }
    };
  }
  componentWillReceiveProps(newData) {
    this.setState({ data: newData.data });
  }
  healthColor() {
    const health =
      this.state.data.attributes["App-Health"] ||
      this.state.data.attributes["Tier-Health"] ||
      this.state.data.attributes["Node-Health"] ||
      false;
    if (health) {
      return this.state.color[health];
    } else {
      return "gray";
    }
  }

  render() {
    let { data } = this.state;

    const CardRender = () => {
      switch (data.name) {
        case NODE_SERVICE_NAME:
          return (
            <React.Fragment>
              {data.name} Information
              <CONSUL_ServiceCard
                name={data.sub_label || false}
                level={data.level || false}
                attributes={data.attributes}
              />
            </React.Fragment>)

        case NODE_EP_NAME:
          return (
            <React.Fragment>
              {data.name} Information
            <CONSUL_EPCard
                name={(data.level === "grey") ? undefined : (data.sub_label || false)}
                level={data.level || false}
                attributes={data.attributes}
              />
            </React.Fragment>)

        case NODE_EPG_NAME:
          return (
            <React.Fragment>
              {data.name} Information
              <CONSUL_EPGCard
                name={data.sub_label || false}
                level={data.level || false}
                attributes={data.attributes}
              />
            </React.Fragment>)

        default:
          return (
            <React.Fragment>
              {data.name} Information
             <CardData
                name={data.sub_label || false}
                level={data.level || false}
                attributes={data.attributes}
              />
            </React.Fragment>)

      }
    }

    return (
      <div>
        <div id="myNav" className="overlay-pane">
          <div className="pane-header">

            <span style={{ verticalAlign: "super", fontSize: "1.3em", fontWeight: 550 }}>
              {data.attributes.Service || data.sub_label || data.label || "Non-service endpoint"}
            </span>

            <Icon className="no-link toggle pull-right" size="icon-medium-small" type="icon-exit-contain" onClick={this.props.closeDetailsPane}>&nbsp;</Icon>

            {data.name !== "Node" ? <Icon className="no-link toggle pull-right" size="icon-medium-small" type="icon-jump-out" onClick={() => this.props.openDetailsPage(data)}>&nbsp;</Icon> : null}
          </div>

          <div className="panel-body">
            <div className="info-div">
              {data.level == "grey" ?
                <React.Fragment>
                  <div>EP Count : {Object.keys(data.attributes).length}</div>

                </React.Fragment>
                : null
              }
              {CardRender()}
            </div>
          </div>
        </div>
      </div>
    );
  }
}
export default DetailsPane;

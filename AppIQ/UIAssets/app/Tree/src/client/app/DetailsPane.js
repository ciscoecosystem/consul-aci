import React from "react";
import "./DetailsPane.css";
import { Icon } from "blueprint-react";

const successColor = "#6ebe4a";
const failColor = "#e2231a";
const warningColor = "#f49141";

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
    return (
      <div>
        <div id="myNav" className="overlay-pane">
          <div className="pane-header">

            <span style={{ verticalAlign: "super", fontSize: "1.3em", fontWeight: 550 }}>
              {this.props.data.name}
            </span>

            <Icon className="no-link toggle pull-right" size="icon-medium-small" type="icon-exit-contain" onClick={this.props.closeDetailsPane}>&nbsp;</Icon>

            {this.state.data.name !== "Node" ? <Icon className="no-link toggle pull-right" size="icon-medium-small" type="icon-jump-out" onClick={() => this.props.openDetailsPage(this.state.data)}>&nbsp;</Icon> : null}
          </div>
          <div className="panel-body">
            <div className="info-div">
              {this.state.data.level == "grey" ?
                <div>EP Count : {Object.keys(this.state.data.attributes).length}</div> : null
              }
              {this.state.data.name} Information
              <CardData
                name={this.state.data.sub_label || false}
                level={this.state.data.level || false}
                attributes={this.state.data.attributes}

              />
            </div>

            {this.state.data.attributes.hasOwnProperty("Contracts") && this.state.data.attributes["Contracts"] !== [] ? (
              <div className="info-div">
                Contracts Information
                <ContractDetails
                  attributes={this.state.data.attributes.Contracts}
                />
              </div>
            ) : null}

            {this.state.data.attributes.hasOwnProperty("ServiceEndpoints") ? (
              <div className="info-div">
                ServiceEndpoints Information
                <ServiceEndpoints
                  data={this.state.data.attributes["ServiceEndpoints"]}
                />
              </div>
            ) : null}

            {this.state.data.attributes.hasOwnProperty("HealthRuleViolations") ? (
              <div className="info-div">
                HealthRuleViolations Information
                <HealthRuleViolations
                  data={this.state.data.attributes["HealthRuleViolations"]}
                />
              </div>
            ) : null}
          </div>
        </div>
      </div>
    );
  }
}

function NoInformation() {
  return <div className="no-info" >No Infomation</div>;
}


function CONSUL_serviceCard(props) {
  let attributeOrder = ["Service", "Port", "Service Instance", "Service Checks", "Service Tag", "Service Kind"]

  return (
    <table className="info-table">
      {props.name ?
        <tr>
          <td width="30%">Name</td>
          <td width="70%">{props.name}</td>
        </tr> : null
      }

      {attributeOrder.map(key => {

        // when value is simply string/number
        if (
          typeof props.attributes[key] == "string" ||
          typeof props.attributes[key] == "number"
        ) {
          return (
            <tr>
              <td width="30%">{key}</td>
              <td width="70%">{props.attributes[key]}</td>
            </tr>
          );
          // when value is list
        } else if (
          Array.isArray(props.attributes[key]) &&
          typeof props.attributes[key][0] == "string"
        ) {
              return (
                <tr>
                  <td width="30%"> {key} </td>
                  <td width="70%">{props.attributes[key].join(", ")}</td>
                </tr>
              );
        }
        // special case for service checks
        else if (key === "Service Checks") {
          let checks = props.attributes[key];
          return (
            <tr>
              <td width="30%">{key}</td>
              <td width="70%">
                <span>
                  {(checks.passing !== undefined) && (<span> <Icon size="icon-small" type=" icon-check-square" style={{ color: successColor }}></Icon>&nbsp;{checks.passing}&nbsp;&nbsp;</span>)}
                  {(checks.warning !== undefined) && (<span> <Icon size="icon-small" type=" icon-warning" style={{ color: warningColor }}></Icon>&nbsp;{checks.warning}&nbsp;&nbsp;</span>)}
                  {(checks.failing !== undefined) && (<span> <Icon size="icon-small" type=" icon-exit-contain" style={{ color: failColor }}></Icon>&nbsp;{checks.failing} </span>)}
                </span>
              </td>
            </tr>)
        }
      })}
    </table>
  );
}


function CardData(props) {
  console.log("Inside card");

  if ("Service" in props.attributes) {
    return CONSUL_serviceCard(props);
  }

  return (
    <table className="info-table">
      {props.name ?
        <tr>
          <td width="30%">Name</td>
          <td width="70%">{props.name}</td>
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
      {Object.keys(props.attributes).map(key => {
        if (key == "App-Health" || key == "Tier-Health") {
          return null;
        }
        else if (
          typeof props.attributes[key] == "string" ||
          typeof props.attributes[key] == "number"
        ) {
          return (
            <tr>
              <td width="30%">{key}</td>
              <td width="70%">{props.attributes[key]}</td>
            </tr>
          );
        } else if (
          Array.isArray(props.attributes[key]) &&
          typeof props.attributes[key][0] == "string"
        ) {
          return props.attributes[key].map((element, index) => {
            if (index == 0) {
              return (
                <tr>
                  <td rowSpan={props.attributes[key].length} width="30%">
                    {key}
                  </td>
                  <td width="70%">{element}</td>
                </tr>
              );
            }

            return (
              <tr>
                <td width="70%">{element}</td>
              </tr>
            );
          });
        }
      })}
    </table>
  );
}
function HealthRuleViolations(props) {
  if (props.data && props.data.constructor == Array && props.data.length > 0) {
    let keys = [
      "Violation Id",
      "Status",
      "Severity",
      "Affected Object",
      "Start Time",
      "End Time",
      "Description"
    ]
    return props.data.map(endPoint => {
      return (
        <table className="info-table">
          {keys.map(key => {
            if (
              typeof endPoint[key] == "string" ||
              typeof endPoint[key] == "number"
            ) {
              return (
                <tr>
                  <td width="30%">{key}</td>
                  <td width="70%">{endPoint[key]}</td>
                </tr>
              );
            }
          })}
        </table>
      );
    });
  }
  return NoInformation();
}

function ServiceEndpoints(props) {
  if (props.data && props.data.constructor == Array && props.data.length > 0) {
    return props.data.map(endPoint => {
      return (
        <table className="info-table">
          {Object.keys(endPoint).map(key => {
            if (
              typeof endPoint[key] == "string" ||
              typeof endPoint[key] == "number"
            ) {
              return (
                <tr>
                  <td width="30%">{key}</td>
                  <td width="70%">{endPoint[key]}</td>
                </tr>
              );
            }
          })}
        </table>
      );
    });
  }
  return NoInformation();
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
export default DetailsPane;

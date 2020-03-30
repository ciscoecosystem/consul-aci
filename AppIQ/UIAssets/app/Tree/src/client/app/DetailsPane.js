import React from "react";
import "./DetailsPane.css";
import {Icon} from "blueprint-react";
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
    console.log(this.state.data)
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
         
              <span className="health-icon">
                <svg
                  width="26"
                  height="26"
                  viewBox="0 0 20 20"
                  style={{ fontSize: "26px" }}
                >
                  <path
                    fill={this.healthColor()}
                    d="M18 3C18 3 18 3 18 3 18 6 18 10 16 13 15 15 13 18 10 20 10 20 10 20 10 20 10 20 10 20 10 20 7 18 5 15 4 13 2 10 2 6 2 3 2 3 2 3 2 3L10 0C10 0 10 0 10 0L18 3ZM10 14C10 14 10 14 10 14L14 11C15 10 15 9 15 9 15 8 15 7 14 7 14 7 13 6 12 6 12 6 12 6 12 6 11 6 11 7 11 7 11 7 11 7 11 7 10 7 10 7 10 7 10 7 10 7 10 7 10 7 9 7 9 7 9 7 9 6 8 6 8 6 8 6 8 6 7 6 6 7 6 7 5 7 5 8 5 9 5 9 5 9 5 9 5 10 5 10 5 10 6 10 6 10 6 10 6 11 6 11 6 11 6 11 6 11 6 11L10 14C10 14 10 14 10 14Z"
                    id="path-1"
                  />
                </svg>
              </span>
           
            <span style={{ verticalAlign: "super", fontSize:"1.3em",fontWeight:550 }}>
               {this.props.data.sub_label || this.props.data.label || this.props.data.name + " Information"}
            </span>
              
              <Icon className="no-link toggle pull-right" size="icon-medium-small" type="icon-exit-contain" onClick={this.props.closeDetailsPane}>&nbsp;</Icon>
              
              {this.state.data.name !== "Node" ? <Icon className="no-link toggle pull-right" size="icon-medium-small" type="icon-jump-out" onClick={() => this.props.openDetailsPage(this.state.data)}>&nbsp;</Icon> : null}
          </div>
          <div className="panel-body">
		  <AppdData data={this.state.data}></AppdData>
            <div className="info-div">
			{this.state.data.level == "grey" ? 
			<div>EP Count : {Object.keys(this.state.data.attributes).length}</div> : null
			}
              {this.state.data.name} Information
              <CardData
			   name = {this.state.data.sub_label || false}
			  level = {this.state.data.level || false}
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
function AppdData(props){
	if(props.data.level == "grey"){
	return null;
	}
	else if(props.data.name == "Node"){
	return null;
	}
	else{
		let rows = []
		
		if(props.data.name == "AppProf"){
			 rows = (
			[<tr>
		<td width="30%">Name</td><td width="70%">{props.data.label}</td>
		</tr>,
		<tr>
		<td width="30%">App-Health</td><td width="70%">{props.data.attributes["App-Health"]}</td>
		</tr>,
		
		]
			)
		}
		else{
			 rows = (
			[<tr>
		<td width="30%">Tier</td><td width="70%">{props.data.label}</td>
		</tr>,
		<tr>
		<td width="30%">Tier-Health</td><td width="70%">{props.data.attributes["Tier-Health"]}</td>
		</tr>,
		
		]
			)
		}
		return (
		<div className="info-div">AppDynamics Information
		<table className="info-table">
		{
		rows
		}
		</table>
		</div>
		)
	}
}
function CardData(props) {
  console.log("Inside card");
  let newCard = [];
  return (
    <table className="info-table">
{props.name ?
        <tr>
          <td width="30%">Name</td>
          <td width="70%">{props.name}</td>
        </tr> : null
      }     
	 {	props.level == "grey" ? 
	
			(
			
			
				<tr>
				<td width="30%" className="bold-font">MAC</td>
				<td width="70%" className="bold-font">IP</td>
				
				</tr>
			) : null
		
	}
      {Object.keys(props.attributes).map(key => {
		  if(key == "App-Health" || key == "Tier-Health"){
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
  if (props.data && props.data.constructor == Array && props.data.length>0) {
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

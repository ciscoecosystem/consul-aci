import React from "react";
import { Tab, Card, CardBody, Label } from "blueprint-react";
import CONSUL_ChecksTable from "./CONSUL_ChecksTable";
import PieChartAndCounter from "../../commonComponent/PieChartAndCounter.js";

function formateDataToChartData(data) {
  let totalCnt = 0;
  let formattedData = [];

  let datakeys = Object.keys(data);
  datakeys.forEach(function (elem) {
    let dataElem = {};
    dataElem.label = elem;
    dataElem.value = data[elem];
    totalCnt += data[elem];

    if (elem === "passing") {
      dataElem.color = "rgb(108, 192, 74)";
    } else if (elem === "warning") {
      dataElem.color = "rgb(255, 204, 0)";
    } else if (elem === "failing") {
      dataElem.color = "rgb(226, 35, 26)";
    }
    formattedData.push(dataElem);
  });

  return {
    formattedData, // format as per chart
    totalCnt, // total count of all (passing,warning,failing)
  };
}

function PropertyItem(props) {
  return (
    <div className="property-list-item">
      <div
        className="property-label"
        style={props.propertyLabel === "Checks" ? { marginLeft: "10px" } : {}}
      >
        {props.propertyLabel}
      </div>
      <div
        className="property-value"
        title={typeof props.propertyValue === "string" && props.propertyValue}
      >
        {props.propertyValue ? props.propertyValue : "-"}
      </div>
    </div>
  );
}

function ServiceList(props) {
  console.log(props);
  return (
    <div style={{ marginBottom: "50px" }}>
      {!props[0].Service ? (
        <div
          style={{
            height: "50vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <div
            style={{
              padding: "20px",
              backgroundColor: "rgba(255, 255, 255, 0.8)",
              fontWeight: "bold",
              color: "rgba(26, 26, 26, 0.5)",
            }}
          >
            No data found
          </div>
        </div>
      ) : null}
      <div>
        <div
          className="service-cards"
          style={{ display: "grid", gridTemplateColumns: "1fr 1fr" }}
        >
          {props[0].Service
            ? props.map((item, index) => {
                return (
                  <div style={{ margin: "10px" }}>
                    <Card style={{ height: "46vh" }}>
                      <CardBody>
                        <div
                          style={{
                            display: "grid",
                            gridTemplateColumns: "1fr 1fr",
                          }}
                        >
                          <div style={{ maxWidth: "30vh" }}>
                            <PropertyItem
                              propertyLabel={"Service"}
                              propertyValue={item.Service}
                            />
                            <PropertyItem
                              propertyLabel={"Service Address"}
                              propertyValue={item.Address}
                            />
                            <PropertyItem
                              propertyLabel={"Service Tags"}
                              propertyValue={
                                item.ServiceTags &&
                                item.ServiceTags.map((tagData) => (
                                  <Label
                                    theme={"MEDIUM_GRAYY"}
                                    size={"SMALL"}
                                    border={false}
                                  >
                                    {tagData}
                                  </Label>
                                ))
                              }
                            />
                            <PropertyItem
                              propertyLabel={"Service Kind"}
                              propertyValue={item.ServiceKind}
                            />
                            <PropertyItem
                              propertyLabel={"Service Namespace"}
                              propertyValue={item.NameSpace}
                            />
                          </div>
                          <div>
                            <div class="col">
                              <PropertyItem
                                propertyLabel={"Checks"}
                                propertyValue={
                                  <PieChartAndCounter
                                    totalCount={
                                      formateDataToChartData(
                                        item["Service Checks"]
                                      ).totalCnt
                                    }
                                    data={
                                      formateDataToChartData(
                                        item["Service Checks"]
                                      ).formattedData
                                    }
                                  />
                                }
                              />
                            </div>
                          </div>
                        </div>
                      </CardBody>
                    </Card>
                  </div>
                );
              })
            : null}
        </div>
      </div>
    </div>
  );
}

// Containes subtabs: nodechecks and service checks
export default class CONSUL_ConsulTab extends React.Component {
  constructor(props) {
    super(props);
    let { NodeCheckQuery, ServiceCheckQuery } = props;

    this.state = {
      tabs: [
        {
          label: "Services",
          key: "Services",
          content: ServiceList(props.serviceList),
        },
        {
          label: "Node Checks",
          key: "Node Checks",
          content: (
            <CONSUL_ChecksTable
              key={"nodeChecks"}
              extraColumn={{
                index: 1,
                value: { Header: "Node", accessor: "NodeName" },
              }}
              query={NodeCheckQuery}
            />
          ),
        },
        {
          label: "Service Checks",
          key: "Service Checks",
          content: (
            <CONSUL_ChecksTable
              key={"serviceChecks"}
              query={ServiceCheckQuery}
            />
          ),
        },
      ],
    };
  }
  render() {
    return <Tab type="secondary-tabs" tabs={this.state.tabs} />;
  }
}

import React from "react";
import { CollapsiblePanel, Label, Table } from "blueprint-react";
import SummaryPane from "./Components/SummaryPane.js";
import PieChartAndCounter from "./commonComponent/PieChartAndCounter.js";
import { showShortName, isString } from "./utils.js";
import "./DetailPanel.css";

const NODE_EP_NAME = "EP";
const NODE_SERVICE_NAME = "Service";
const NODE_EPG_NAME = "EPG";
const VALUE_LENGTH = 35;
const IP_LENGTH = 22;
const MAC_LENGTH = 20;

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

function nonServiceEndPointEP(data) {
  const NON_SERVICE_ENPOINT_HEADER = [
    {
      Header: "MAC",
      accessor: "mac",
    },
    {
      Header: "IP",
      accessor: "ip",
    },
  ];
  console.log("DEBUG", data);
  let row = [];
  Object.keys(data).forEach((item) => {
    row.push({ mac: item, ip: data[item] });
  });

  return Object.keys(data).length > 0 ? (
    <div>
      <div className="mac-ip-table">
        {/* <Table
          data={row}
          columns={NON_SERVICE_ENPOINT_HEADER}
          defaultPageSize={row.length}
        /> */}
        <div className={"ReactTable -striped"}>
          <div className="rt-table" role="grid">
            <div className="rt-thead -header" style= {{minWidth: "200px"}}>
              <div className="rt-tr" role="row">
                <div
                  className="rt-th rt-resizable-header -cursor-pointer"
                  role="columnheader"
                  // tabindex="-1"
                  style={{flex: "100 0 auto", width: "100px"}}
                >
                  <div className="rt-resizable-header-content">MAC</div>
                  <div className="rt-resizer"></div>
                </div>
                <div
                  className="rt-th rt-resizable-header -cursor-pointer"
                  role="columnheader"
                  // tabindex="-1"
                  style={{flex: "100 0 auto", width: "100px"}}
                >
                  <div className="rt-resizable-header-content">IP</div>
                  <div className="rt-resizer"></div>
                </div>
              </div>
            </div>
            <div className="rt-tbody" style= {{minWidth: "200px"}}>
              {row.map((item, index) => (
                <div className="rt-tr-group" role="rowgroup">
                  <div
                    className={"rt-tr" + ((index % 2) ? " -even" : " -odd")}
                    role="row"
                  >
                    <div
                      className="rt-td"
                      role="gridcell"
                      style={{flex: "100 0 auto", width: "100px"}}
                    >
                      {item.mac}
                    </div>
                    <div
                      className="rt-td"
                      role="gridcell"
                      style={{flex: "100 0 auto", width: "100px"}}
                    >
                      {item.ip}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  ) : (
    <React.Fragment></React.Fragment>
  );
}

export default function DetailPanel(props) {
  let { summaryPaneIsOpen, summaryDetail } = props;
  console.log("==> Detail pane mounted", summaryDetail);

  // { name: "App-Health", label: "App-Health" }
  let appProfileOrder = [{ name: "sub_label", label: "Name" }];

  // {name:"name", label:"Name"},
  let epgInfoOrder = [
    { name: "name", label: "Name" },
    { name: "VRF", label: "vrf" },
    { name: "BD", label: "bd" },
  ];

  let constractInfoOrder =
    "Contracts" in summaryDetail.attributes
      ? Object.keys(summaryDetail.attributes.Contracts).map((item) => ({
          name: item,
          label: item,
        }))
      : [];

  let consulNodeOrder = [
    { name: "Node", label: "node" },
    { name: "Node Checks", label: "Node Checks" },
    { name: "Reporting Node IP", label: "Reporting Node IP" },
  ];

  let consulServiceOrder = [
    { name: "Service", label: "Service" },
    { name: "Address", label: "Address" },
    { name: "Service Checks", label: "Service Checks" },
    { name: "ServiceTags", label: "Service Tags" },
    { name: "ServiceKind", label: "Service Kind" },
    { name: "NameSpace", label: "Service Namespace" },
  ];

  let epInfoOrder = [
    { name: "name", label: "Name" },
    { name: "IP", label: "IP" },
    { name: "Interfaces", label: "Interfaces" },
    { name: "VMM-Domain", label: "VMM-Domain" },
  ];

  let serviceInfoOrder = [
    { name: "Service", label: "Service" },
    { name: "Address", label: "Address" },
    { name: "Service Instance", label: "Service Instance" },
    { name: "Service Checks", label: "Service Checks" },
    { name: "Namespace", label: "Namespace" },
    { name: "Service Tags", label: "Service Tags" },
    { name: "Service Kinds", label: "Service Kinds" },
  ];

  function CollapsePane(
    title,
    infoOrder,
    values = undefined,
    nodeElem = undefined
  ) {
    let details = values ? values : summaryDetail;

    function allDetailRender(showDetails) {
      return infoOrder.map(function (elem) {
        let { name, label } = elem;
        let detailValue = showDetails[name];

        if (
          name === "nodeChecks" ||
          name === "serviceChecks" ||
          name === "Node Checks" ||
          name === "Service Checks"
        ) {
          let { formattedData, totalCnt } = formateDataToChartData(
            showDetails[name]
          );
          detailValue = (
            <PieChartAndCounter data={formattedData} totalCount={totalCnt} />
          );
        } else if (
          name === "serviceTags" ||
          name === "Service Tags" ||
          name === "ServiceTags"
        ) {
          if (!Array.isArray(showDetails[name])) {
            console.warn("Service Tags format invalid");
            detailValue = "";
          } else {
            detailValue = showDetails[name].length
              ? showDetails[name].map(function (tags) {
                  return (
                    <Label
                      theme={"MEDIUM_GRAYY"}
                      size={"MEDIUM"}
                      border={false}
                    >
                      {tags}
                    </Label>
                  );
                })
              : "";
          }
        } else if (
          name === "interface" ||
          name === "Consumer" ||
          name === "Provider" ||
          name === "Interfaces" ||
          name === "Consumer Interface" ||
          name === "Taboo" ||
          name === "Intra EPG" ||
          name === "Consumer Interface"
        ) {
          if (detailValue && Array.isArray(detailValue)) {
            detailValue = (
              <ul
                style={{
                  listStyleType: "none",
                  paddingLeft: "0px",
                  paddingBottom: "3px",
                }}
              >
                {showDetails[name].map(function (infcs) {
                  return <li title={infcs}>{infcs}</li>;
                })}
              </ul>
            );
          } else {
            console.warn("Invalid format", name);
            detailValue = "";
          }
        }

        return (
          <PropertyItem propertyLabel={label} propertyValue={detailValue} />
        );
      });
    }

    return (
      <CollapsiblePanel id="ccpid1" key="ccpkey1" title={title}>
        {nodeElem
          ? nodeElem
          : Array.isArray(details)
          ? details.map((elemData, ind) => (
              <React.Fragment>
                {" "}
                {allDetailRender(elemData)}
                {details.length - 1 !== ind && <hr />}
              </React.Fragment>
            ))
          : allDetailRender(details)}
      </CollapsiblePanel>
    );
  }

  function panelToShow() {
    summaryDetail.attributes["name"] = summaryDetail["sub_label"];
    switch (summaryDetail.name) {
      case NODE_SERVICE_NAME:
        return (
          <React.Fragment>
            {CollapsePane(
              summaryDetail.name + " Information",
              serviceInfoOrder,
              summaryDetail.attributes
            )}
          </React.Fragment>
        );

      case NODE_EP_NAME:
        if (summaryDetail.level === "grey") {
          delete summaryDetail.attributes.name; // delete name as it does have any
          return (
            <React.Fragment key="ep-ns">
              <PropertyItem
                propertyLabel={"EP Count"}
                propertyValue={Object.keys(summaryDetail.attributes).length}
              />
              <PropertyItem
                propertyLabel={"EP Information"}
                propertyValue={nonServiceEndPointEP(summaryDetail.attributes)}
              />
            </React.Fragment>
          );
        } else {
          return (
            <React.Fragment key="ep">
              {CollapsePane(
                summaryDetail.name + " Information",
                epInfoOrder,
                summaryDetail.attributes
              )}
              {CollapsePane(
                "Consul Nodes",
                consulNodeOrder,
                summaryDetail.attributes
              )}
              {CollapsePane(
                "Consul Services",
                consulServiceOrder,
                summaryDetail.attributes.Services_List
              )}
            </React.Fragment>
          );
        }

      case NODE_EPG_NAME:
        console.log("Epg info ", summaryDetail);
        return (
          <React.Fragment>
            {CollapsePane(
              summaryDetail.name + " Information",
              epgInfoOrder,
              summaryDetail.attributes
            )}

            {"Contracts" in summaryDetail.attributes &&
              CollapsePane(
                "Contracts Information",
                constractInfoOrder,
                summaryDetail.attributes.Contracts
              )}

            {CollapsePane(
              "Consul Nodes",
              consulNodeOrder,
              summaryDetail.attributes.Nodes
            )}

            {CollapsePane(
              "Consul Services",
              consulServiceOrder,
              summaryDetail.attributes.Services_List
            )}
          </React.Fragment>
        );

      default:
        return (
          <React.Fragment>
            {CollapsePane(summaryDetail.name + " Information", appProfileOrder)}
          </React.Fragment>
        );
    }
  }

  let title = "";
  if (summaryDetail.name === "Service") {
    title = summaryDetail.attributes["Service Instance"];
  } else {
    title =
      summaryDetail.sub_label || summaryDetail.label || "Non-Service Endpoints";
  }

  return summaryPaneIsOpen ? (
    <SummaryPane
      subTitle={""}
      title={title}
      closeSummaryPane={() => props.setSummaryIsOpen(false)}
      isOpenScreen={true}
      openScreen={() => props.openDetailsPage(summaryDetail)}
    >
      <div className="" style={{ marginBottom: "80%" }}>
        {panelToShow()}
      </div>
    </SummaryPane>
  ) : (
    <div></div>
  );
}

function PropertyItem(props) {
  return (
    <div className="property-list-item">
      <div className="property-label">{props.propertyLabel}</div>
      <div
        className="property-value"
        title={isString(props.propertyValue) && props.propertyValue}
      >
        {props.propertyValue
          ? isString(props.propertyValue)
            ? showShortName(props.propertyValue, VALUE_LENGTH)
            : props.propertyValue
          : ""}
      </div>
    </div>
  );
}

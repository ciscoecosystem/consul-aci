import React from "react";
import { Button, Icon, Label } from "blueprint-react";

const successColor = "#6ebe4a";
const failColor = "#e2231a";
const warningColor = "#f49141";

const SERVICE_HEADER = [
  {
    Header: "Data Center",
    accessor: "datacenter",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "IP",
    accessor: "ip",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Pod",
    accessor: "pod_name",
    show: true,
    Cell: (row) => {
      return <div>{row.value !== "N/A" ? row.value : ""}</div>;
    },
  },
  {
    Header: "Consul Node",
    accessor: "consulNode",
    filterType: "text",
    Cell: (row) => {
      return <div>{row.value !== "N/A" ? row.value : ""}</div>;
    },
  },
  {
    Header: "Service",
    accessor: "service",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Service Instance",
    accessor: "serviceInstance",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Port",
    accessor: "port",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Service Kind",
    accessor: "serviceKind",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Service Tags",
    accessor: "serviceTags",
    filterable: false,
    Cell: (row) => {
      return (
        <div>
          {row.value.map((tagData) => (
            <Label theme={"MEDIUM_GRAYY"} size={"SMALL"} border={false}>
              {tagData}
            </Label>
          ))}
        </div>
      );
    },
  },
  {
    Header: "Service Check(s)",
    accessor: "serviceChecksFilter",
    show: false,
    filterable: true,
  },
  {
    Header: "Service Checks",
    accessor: "serviceChecks",
    filterable: false,
    width: 150,
    sortable: false,
    Cell: (row) => {
      return (
        <span>
          {row.value.passing !== undefined && (
            <span title="passing">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-check-square"
                style={{ color: successColor }}
              ></Icon>
              &nbsp;{row.value.passing}&nbsp;&nbsp;
            </span>
          )}
          {row.value.warning !== undefined && (
            <span title="warning">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-warning"
                style={{ color: warningColor }}
              ></Icon>
              &nbsp;{row.value.warning}&nbsp;&nbsp;
            </span>
          )}
          {row.value.failing !== undefined && (
            <span title="critical">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-exit-contain"
                style={{ color: failColor }}
              ></Icon>
              &nbsp;{row.value.failing}{" "}
            </span>
          )}
        </span>
      );
    },
  },
];

const NODE_COLUMNS = [
  {
    Header: "Data Center",
    accessor: "datacenter",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "IP",
    accessor: "ip",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Pod",
    accessor: "pod_name",
    show: true,
    Cell: (row) => {
      return <div>{row.value !== "N/A" ? row.value : ""}</div>;
    },
  },
  {
    Header: "Consul Node",
    accessor: "consulNode",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Node Check(s)",
    accessor: "nodeChecksFilter",
    show: false,
    filterable: true,
  },
  {
    Header: "Node Checks",
    accessor: "nodeChecks",
    filterable: false,
    width: 150,
    sortable: false,
    Cell: (row) => {
      return (
        <span>
          {row.value.passing !== undefined && (
            <span title="passing">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-check-square"
                style={{ color: successColor }}
              ></Icon>
              &nbsp;{row.value.passing}&nbsp;&nbsp;
            </span>
          )}
          {row.value.warning !== undefined && (
            <span title="warning">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-warning"
                style={{ color: warningColor }}
              ></Icon>
              &nbsp;{row.value.warning}&nbsp;&nbsp;
            </span>
          )}
          {row.value.failing !== undefined && (
            <span title="critical">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-exit-contain"
                style={{ color: failColor }}
              ></Icon>
              &nbsp;{row.value.failing}{" "}
            </span>
          )}
        </span>
      );
    },
  },
];

const NON_SERVICE_ENDPOINT_COLUMNS = [
  {
    Header: "IP",
    accessor: "IP",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "MAC",
    accessor: "CEP-Mac",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Pod",
    accessor: "pod",
    show: true,
    Cell: (row) => {
      return <div>{row.value !== "N/A" ? row.value : ""}</div>;
    },
  },
  {
    Header: "Application Profile",
    accessor: "AppProfile",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "EPG",
    accessor: "EPG",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
];

const SERVICE_ENDPOINT_COLUMNS = [
  {
    Header: "Data Center",
    accessor: "datacenter",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Endpoint",
    accessor: "endPointName",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Pod",
    accessor: "pod_name",
    show: true,
    Cell: (row) => {
      return <div>{row.value !== "N/A" ? row.value : ""}</div>;
    },
  },
  {
    Header: "IP",
    accessor: "ip",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Application Profile",
    accessor: "ap",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "EPG",
    accessor: "epgName",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "EPG Health",
    accessor: "epgHealth",
    filterType: "number",
    sortMethod: (a, b) => Number(a) - Number(b), // sorting numerically
    Cell: (row) => {
      let epgcolor = "#56b72a";
      if (row.value < 70) {
        epgcolor = "#ffcc00";
      }
      if (row.value < 40) {
        epgcolor = "#FF6666";
      }
      return (
        <Button
          style={{ width: "66px", backgroundColor: epgcolor, opacity: "1" }}
          disabled={true}
          key="dd"
          type="btn--success"
          size="btn--small"
        >
          {row.value}
        </Button>
      );
    },
  },
  {
    Header: "Consul Node",
    accessor: "consulNode",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Node Check(s)",
    accessor: "nodeChecksFilter",
    show: false,
    filterable: true,
  },
  {
    Header: "Service Tag(s)",
    accessor: "serviceTagFilter",
    show: false,
    filterable: true,
  },
  {
    Header: "Any text",
    accessor: "anyText",
    show: false,
    filterable: false,
  },
  {
    Header: "Node Checks",
    accessor: "nodeChecks",
    filterable: false,
    width: 150,
    sortable: false,
    Cell: (row) => {
      return (
        <span>
          {row.value.passing !== undefined && (
            <span title="passing">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-check-square"
                style={{ color: successColor }}
              ></Icon>
              &nbsp;{row.value.passing}&nbsp;&nbsp;
            </span>
          )}
          {row.value.warning !== undefined && (
            <span title="warning">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-warning"
                style={{ color: warningColor }}
              ></Icon>
              &nbsp;{row.value.warning}&nbsp;&nbsp;
            </span>
          )}
          {row.value.failing !== undefined && (
            <span title="critical">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-exit-contain"
                style={{ color: failColor }}
              ></Icon>
              &nbsp;{row.value.failing}{" "}
            </span>
          )}
        </span>
      );
    },
  },
  {
    Header: "Service",
    accessor: "service",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Service Instance",
    accessor: "serviceInstance",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Port",
    accessor: "port",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Service Kind",
    accessor: "serviceKind",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
  {
    Header: "Service Tags",
    accessor: "serviceTags",
    filterable: false,
    Cell: (row) => {
      return (
        <div>
          {row.value.map((tagData) => (
            <Label theme={"MEDIUM_GRAYY"} size={"SMALL"} border={false}>
              {tagData}
            </Label>
          ))}
        </div>
      );
    },
  },
  {
    Header: "Service Check(s)",
    accessor: "serviceChecksFilter",
    show: false,
    filterable: true,
  },
  {
    Header: "Service Checks",
    accessor: "serviceChecks",
    filterable: false,
    width: 150,
    sortable: false,
    Cell: (row) => {
      return (
        <span>
          {row.value.passing !== undefined && (
            <span title="passing">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-check-square"
                style={{ color: successColor }}
              ></Icon>
              &nbsp;{row.value.passing}&nbsp;&nbsp;
            </span>
          )}
          {row.value.warning !== undefined && (
            <span title="warning">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-warning"
                style={{ color: warningColor }}
              ></Icon>
              &nbsp;{row.value.warning}&nbsp;&nbsp;
            </span>
          )}
          {row.value.failing !== undefined && (
            <span title="critical">
              {" "}
              <Icon
                size="icon-small"
                type=" icon-exit-contain"
                style={{ color: failColor }}
              ></Icon>
              &nbsp;{row.value.failing}{" "}
            </span>
          )}
        </span>
      );
    },
  },
  {
    Header: "Namespace",
    accessor: "serviceNamespace",
    filterType: "text",
    Cell: (row) => {
      return (
        <span title={row.value !== "N/A" ? row.value : ""}>
          {row.value !== "N/A" ? row.value : ""}
        </span>
      );
    },
  },
];

export {
  SERVICE_HEADER,
  NODE_COLUMNS,
  NON_SERVICE_ENDPOINT_COLUMNS,
  SERVICE_ENDPOINT_COLUMNS,
};

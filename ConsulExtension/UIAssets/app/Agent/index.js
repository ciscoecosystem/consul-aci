import React from "react";
import { Redirect } from "react-router-dom";
import { toast } from "react-toastify";
import {
  Screen,
  Button,
  Input,
  Select,
  Icon,
  IconButton,
  Spinner,
  FilterableTable
} from "blueprint-react";
import { isIP } from "validator";
import isValidDomain from "is-valid-domain";
import Modal from "../commonComponent/Modal.js";
import {
  QUERY_URL,
  getCookie,
  INTERVAL_API_CALL,
  AGENTS,
  URL_TOKEN,
  DEV_TOKEN,
} from "../../constants.js";
import "./index.css";
import { tree } from "d3";

// const dummylist = [
//     { "protocol": "http", "ip": "10.0.0.0", "port": 8050, "token": "lnfeialilsacirvjlnlaial", "status": true, "datacenter": "datacenter1" },
//     { "protocol": "https", "ip": "10.0.0.1", "port": 8051, "token": "lnfeialilsacirvjlglaial", "status": false, "datacenter": "datacenter1" },
//     { "protocol": "http", "ip": "10.0.0.2", "port": 8051, "token": "lnfeialilsacirvjhnlaial", "status": true, "datacenter": "datacenter2" }
// ]
// const ipRegex = RegExp('((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))');
// const dnsRegex = RegExp('(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]');
const portRegex = RegExp("^[0-9]*$");

const defaultFieldState = {
  protocolOptions: [
    { label: "HTTPS", value: "https", selected: true },
    { label: "HTTP", value: "http", selected: false },
  ],
  editAgentIndex: null, // [0,1,...n] indicates row number & [-1] indicates a row is added and being written
  isNewAgentAdded: false,
  Protocol: "https",
  Address: null,
  Port: null,
  Token: null,
  VRF: null,
  errormsg: {
    Address: null,
    Port: null,
  },
};
export default class Agent extends React.Component {
  constructor(props) {
    super(props);
    // this.xhrCred = new XMLHttpRequest();
    this.xhrCred = new XMLHttpRequest();
    this.intervalCall = null;
    this.setDetails = this.setDetails.bind(this);
    this.closeAgent = this.closeAgent.bind(this);
    this.handleModal = this.handleModal.bind(this);
    this.actionEvent = this.actionEvent.bind(this);
    this.handleFieldChange = this.handleFieldChange.bind(this);
    this.handleSelectChange = this.handleSelectChange.bind(this);
    this.validateField = this.validateField.bind(this);
    this.submitAgent = this.submitAgent.bind(this);
    this.readAgents = this.readAgents.bind(this);
    this.readAgentsCall = this.readAgentsCall.bind(this);
    this.notify = this.notify.bind(this);
    this.addAgentCall = this.addAgentCall.bind(this);
    this.removeAgent = this.removeAgent.bind(this);
    this.removeAgentCall = this.removeAgentCall.bind(this);
    this.editAgent = this.editAgent.bind(this);
    this.refreshField = this.refreshField.bind(this);
    this.configureData = this.configureData.bind(this);
    // this.FormField = this.FormField.bind(this);
    console.log("Agent index props", props);
    this.state = {
      details: [],
      tenantName: this.props.tenantName,
      readAgentLoading: false,
      redirectToMain: false,
      addAgentModalIsOpen: false,
      loadingText: "Loading seed agents...",
      vrfOptions: [
        ...[{ label: "None", value: "None", selected: true }],
        ...this.props.vrfOptions.map((item) => ({ ...item })),
      ],
      isVRFLoading: false,
      actionItems: [
        { label: "Update", action: this.actionEvent },
        { label: "Delete", action: this.actionEvent },
      ],
      agentFields: [
        { name: "Protocol", type: "select", mandatory: true },
        {
          name: "Address",
          type: "text",
          mandatory: true,
          placeholder: "e.g 197.168.0.1",
        },
        {
          name: "Port",
          type: "number",
          mandatory: true,
          placeholder: "e.g. 8000",
        },
        { name: "VRF", type: "select", mandatory: false },
        {
          name: "Token",
          type: "password",
          mandatory: false,
          placeholder: "token",
        },
      ],
      ...defaultFieldState,
    };
  }

  componentDidMount() {
    // let thiss = this;
    this.readAgents();
    this.intervalCall = setInterval(
      () => this.readAgents(true),
      INTERVAL_API_CALL
    );
  }

  componentWillUnmount() {
    console.log("Component will unmount; intervalcall");
    clearInterval(this.intervalCall); // this clears the interval calls
    this.xhrCred.abort(); // cancel all apis
  }

  componentDidCatch(error, info) {
    console.log("ERRROR :===>> ", error, info);
  }

  refreshField() {
    this.setState({
      ...defaultFieldState,
      errormsg: {
        Address: null,
        Port: null,
      },

      vrfOptions: [
        ...[{ label: "None", value: "None", selected: true }],
        ...this.props.vrfOptions.map((item) => ({ ...item })),
      ],
    });
  }

  setDetails(details, isReloaded = false) {
    this.setState({ details: [...details] });
    isReloaded && this.props.updateDetails();
  }

  /**  readAgents @params
   * isRepeatedCall: true indicate read agent called in interval
   * isReloaded: true indicate, user reloaded the agent, its also reloads update dc api.
   */
  readAgents(isRepeatedCall = false, isReloaded = false) {
    let thiss = this;
    console.log("readagent:= isrepeatcall ", isRepeatedCall);
    if (isRepeatedCall === true) {
      let { addAgentModalIsOpen, readAgentLoading } = this.state;

      // if agent is being written or edit then dont read
      if (addAgentModalIsOpen || readAgentLoading) {
        console.log("Read agent abort");
        return;
      }
      this.readAgentsCall(isReloaded);
    } else {
      this.setState(
        { readAgentLoading: true, loadingText: "Loading seed agents..." },
        function () {
          console.log("LOading----");
          thiss.readAgentsCall(isReloaded);
        }
      );
    }
  }

  actionEvent() {
    console.log("Action called");
    // handle update or edit
  }

  closeAgent() {
    this.props.handleAgent(false);
    this.setState({ redirectToMain: true });
  }

  handleModal(addAgentModalIsOpen = false) {
    this.setState({ addAgentModalIsOpen });
  }

  validateField(fieldName, value) {
    if (fieldName === "Address" || fieldName === "Port") {
      if (value === "" || value === null || value === undefined) {
        return {
          isError: true,
          msg: "Field Required",
        };
      }
    }
    if (fieldName === "Address") {
      // CHEK REGEX
      if (!(isIP(value) || isValidDomain(value))) {
        return {
          isError: true,
          msg: "Address invalid.",
        };
      }
    }
    if (fieldName === "Port") {
      // check regex and range
      if (
        !(
          portRegex.test(value) &&
          parseInt(value) > 0 &&
          parseInt(value) <= 65535
        )
      ) {
        // port should be only betwn 1 - 65535
        return {
          isError: true,
          msg: "Port invalid.",
        };
      }
    }
    return { isError: false, msg: null };
  }

  handleFieldChange(e) {
    console.log("handlefieldchange ", e.target);
    let { name, value } = e.target;
    let validationStatus = this.validateField(name, value);

    let errormsg = this.state.errormsg;
    errormsg[name] = validationStatus.msg;

    this.setState({
      [name]: value,
      errormsg,
    });
  }

  handleSelectChange(selected, options, type) {
    if (type !== "VRF") {
      if (selected[0]) {
        this.setState({
          Protocol: selected[0].value,
          protocolOptions: options,
        });
      }
    } else {
      this.setState({
        VRF: selected[0].value,
        vrfOptions: options,
      });
    }
  }

  notify(message, isSuccess = false, isWarning = false) {
    isWarning
      ? toast.warn(message, {
          position: toast.POSITION.BOTTOM_CENTER,
        })
      : isSuccess
      ? toast.success(message, {
          position: toast.POSITION.BOTTOM_CENTER,
        })
      : toast.error(message, {
          position: toast.POSITION.BOTTOM_CENTER,
        });
  }

  readAgentsCall(isReloaded) {
    let thiss = this;
    const payload = {
      query: `query{
            ReadCreds(tn: ${JSON.stringify(this.state.tenantName)}){creds}
        }`,
    };
    let xhrCred = this.xhrCred;
    try {
      xhrCred.open("POST", QUERY_URL, true);
      xhrCred.setRequestHeader("Content-type", "application/json");
      window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
      window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
      xhrCred.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
      xhrCred.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
      xhrCred.onreadystatechange = function () {
        console.log("chr== state ", xhrCred.readyState);

        if (xhrCred.readyState == 4 && xhrCred.status == 200) {
          let checkData = JSON.parse(xhrCred.responseText);
          let credsData = JSON.parse(checkData.data.ReadCreds.creds);

          if (parseInt(credsData.status_code) === 200) {
            thiss.setDetails(credsData.payload, isReloaded);
            // thiss.setState({ details: credsData.payload })
          } else if (parseInt(credsData.status_code) === 300) {
            try {
              thiss.setDetails(credsData.payload, isReloaded);
              thiss.notify(credsData.message);
            } catch (e) {
              console.log("message error", e);
            }
          }
          thiss.refreshField();
          thiss.setState({ readAgentLoading: false });
        } else {
          console.log("Not fetching");
        }
      };
      xhrCred.send(JSON.stringify(payload));
    } catch (e) {
      thiss.notify("Error while fetching agent information please refresh");
      console.error("Error getting agents", e);
    }
  }

  submitAgent(event) {
    event.preventDefault();
    let thiss = this;
    let {
      details,
      Address,
      Port,
      Protocol,
      isNewAgentAdded,
      Token,
      VRF,
    } = this.state;
    console.log("Submit agent; detaios ", details);
    console.log("Address and port ", Address, Port);
    // check if Details in Index is not same as others in [...Details] as per port and ip
    for (let ind = 0; ind < details.length; ind++) {
      if (
        details[ind].ip === Address &&
        parseInt(details[ind].port) === parseInt(Port) &&
        details[ind].protocol === Protocol &&
        details[ind].token === Token &&
        details[ind].vrf === VRF
      ) {
        this.notify("Agent already exists.");
        return;
      }
    }

    this.handleModal(false);
    this.setState(
      {
        readAgentLoading: true,
        loadingText: isNewAgentAdded ? "Adding agent..." : "Updating agent...",
      },
      function () {
        console.log("Writing agents, so load:", thiss.state.readAgentLoading);
        thiss.addAgentCall();
      }
    );
  }

  addAgentCall() {
    let { details, isNewAgentAdded, editAgentIndex, VRF } = this.state;

    console.log(" ====================== Addagent call;  ");
    console.log(" IisNewAgentAdded ", isNewAgentAdded);

    let agentDetail = {
      protocol: this.state.Protocol,
      vrf: VRF !== "None" ? VRF : null,
      port: this.state.Port,
      ip: this.state.Address,
      token: this.state.Token,
    };

    agentDetail.port = parseInt(agentDetail.port);

    let payload = {};

    if (isNewAgentAdded) {
      payload = {
        query: `query{
                WriteCreds(tn: ${JSON.stringify(
                  this.state.tenantName
                )}, agentList: ${JSON.stringify(
          JSON.stringify([agentDetail])
        )}){creds}
            }`,
      };
    } else {
      let editDetailCopy = details[editAgentIndex];
      delete editDetailCopy.status;
      delete editDetailCopy.token;
      editDetailCopy.port = parseInt(editDetailCopy.port);

      let dataInput = {
        oldData: editDetailCopy,
        newData: agentDetail,
      };

      payload = {
        query: `query{
                UpdateCreds(tn: ${JSON.stringify(
                  this.state.tenantName
                )},updateInput: ${JSON.stringify(
          JSON.stringify(dataInput)
        )}){creds}
            }`,
      };
    }

    let xhr = this.xhrCred;
    //  new XMLHttpRequest();
    let thiss = this;
    try {
      xhr.open("POST", QUERY_URL, true);
      xhr.setRequestHeader("Content-type", "application/json");
      window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
      window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
      xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
      xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);

      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          let json = JSON.parse(xhr.responseText);
          console.log("Add agent response ", json);

          if ("errors" in json) {
            thiss.notify("Could not Fetch. The query may be invalid.");
          } else if (
            ("WriteCreds" in json.data && "creds" in json.data.WriteCreds) ||
            ("UpdateCreds" in json.data && "creds" in json.data.UpdateCreds)
          ) {
            let resp = isNewAgentAdded
              ? JSON.parse(json.data.WriteCreds.creds)
              : JSON.parse(json.data.UpdateCreds.creds);
            console.log("Add agentresponse ", resp);

            if (resp.status_code == 200) {
              if (resp.payload) {
                if (isNewAgentAdded) {
                  details.unshift(resp.payload);
                } else {
                  details[editAgentIndex] = resp.payload;
                }

                thiss.setDetails(details, true);
                localStorage.setItem("dashboardPollingInterval", "true");

                // connection is not true
                if (resp.payload.status !== true && resp.message) {
                  thiss.notify(resp.message, false, true);
                  // thiss.notify("Connection could not be established for "+ resp.payload.ip +":" + resp.payload.port, false, true)
                }
              } else {
                // thiss.abortUpdateAgentAction();
                thiss.notify("Some technical glitch!");
              }
              // }
            } else if (resp.status_code == 300) {
              console.log("ERROR Revert changes----");
              try {
                thiss.notify(resp.message);
              } catch (e) {
                console.log("message error", e);
              }
            } else if (resp.status_code == 301) {
              // detail updated but some server error
              console.log("Response 301 ", resp.payload);
              thiss.notify(resp.message); // error message
              if (resp.payload) {
                if (isNewAgentAdded) {
                  details.unshift(resp.payload);
                } else {
                  details[editAgentIndex] = resp.payload;
                }

                thiss.setDetails(details, true);
                localStorage.setItem("dashboardPollingInterval", "true");
              } else {
                thiss.notify("Some technical glitch!");
              }
              // }
            } else {
              console.log("ERROR Revert changes----");
              console.error("Invalid status code");
            }
          } else {
            console.log("ERROR Revert changes----");
            console.error("Invalid response strcture");
          }
          thiss.refreshField();
          thiss.setState({ readAgentLoading: false });
        } else {
          console.log("ERROR Revert changes----");
        }
      };
      xhr.send(JSON.stringify(payload));
    } catch (e) {
      console.error("Error api addAgentCall", e);
    } finally {
      this.setState({
        Protocol: "https",
        Address: null,
        Port: null,
        Token: null,
      });
    }
  }

  // remove an agent
  removeAgent(index) {
    console.log("rem Index", index);
    let thiss = this;
    let { details } = this.state;
    let newDetails = [...details];

    this.setState(
      { readAgentLoading: true, loadingText: "Removing agent..." },
      function () {
        thiss.removeAgentCall(
          Object.assign({}, newDetails.splice(index, 1)[0]),
          index
        );
      }
    );
  }

  removeAgentCall(agentDetail, deleteIndex) {
    delete agentDetail.status;
    agentDetail.port = parseInt(agentDetail.port);

    let { details } = this.state;

    let payload = {
      query: `query{
            DeleteCreds(tn: ${JSON.stringify(
              this.state.tenantName
            )}, agentData: ${JSON.stringify(
        JSON.stringify(agentDetail)
      )} ){message}
        }`,
    };

    let xhr = this.xhrCred;

    let thiss = this;
    try {
      xhr.open("POST", QUERY_URL, true);
      xhr.setRequestHeader("Content-type", "application/json");
      window.APIC_DEV_COOKIE = getCookie(DEV_TOKEN); // fetch for loginform
      window.APIC_URL_TOKEN = getCookie(URL_TOKEN); // fetch for loginform
      xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
      xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          let json = JSON.parse(xhr.responseText);

          console.log("del json ", json);

          if ("errors" in json) {
            thiss.notify("Could not Fetch. The query may be invalid.");
          } else if ("message" in json.data.DeleteCreds) {
            let resp = JSON.parse(json.data.DeleteCreds.message);
            console.log("Response del", resp);

            if (resp.status_code == 200) {
              details.splice(deleteIndex, 1);
              localStorage.setItem("dashboardPollingInterval", "true");
              // thiss.setState({ details });
              thiss.setDetails(details, true);
            } else {
              thiss.notify(resp.message);
            }
          } else {
            thiss.notify("Something went wrong!");
            console.error("DeleteCreds: response structure invalid");
          }
          thiss.refreshField();
          thiss.setState({ readAgentLoading: false });
        } else {
          // thiss.notify("Error while reaching the container.")
        }
      };
      xhr.send(JSON.stringify(payload));
    } catch (e) {
      console.error("Error api removeagent", e);
    }
  }

  // edit an Agent
  editAgent(editAgentIndex) {
    let thiss = this;
    // get required detail and put in Port, Protocol ,etc
    let agentDetail = this.state.details[editAgentIndex];
    let protocolOptions = JSON.parse(
      JSON.stringify(this.state.protocolOptions)
    );

    let protocolOptionsNew = protocolOptions.map(function (elem) {
      return Object.assign(elem, {
        selected: elem.value === agentDetail.protocol,
      });
    });

    let { vrfOptions } = this.state;
    let vrf = agentDetail.vrf ? agentDetail.vrf : "None";

    vrfOptions.forEach((item, index) => {
      if (item.value === vrf) vrfOptions[index].selected = true;
      else vrfOptions[index].selected = false;
    });

    // open Modal box and show the same
    this.setState(
      {
        editAgentIndex: editAgentIndex,
        isNewAgentAdded: false,
        Port: agentDetail.port,
        Protocol: agentDetail.protocol,
        protocolOptions: protocolOptionsNew,
        Address: agentDetail.ip,
        Token: agentDetail.token,
        VRF: vrf,
        vrfOptions: vrfOptions,
      },
      function () {
        thiss.handleModal(true);
      }
    );
  }

  configureData(data){

    return data.map(item => {
      let ip = item.ip+":"+item.port
      let status = item.status?"Connected":"Disconnected"
      let vrf = item.vrf?item.vrf:"N/A"
      let datacenter = item.datacenter?item.datacenter:"N/A"
      return {...item, ip, status, datacenter, vrf }
    })

  }

  render() {
    let thiss = this;
    console.log("Render ", this.state);
    let {
      addAgentModalIsOpen,
      redirectToMain,
      agentFields,
      protocolOptions,
      errormsg,
      readAgentLoading,
      Port,
      Address,
      vrfOptions,
    } = this.state;

    console.log(vrfOptions);
    const tableColumns = [
      {
        Header: "Protocol",
        accessor: "protocol",
        Cell: (row) => {
          return (
              <span>
              {row.value}
              </span>
          );
        },
      },
      {
        Header: "Address",
        accessor: "ip",
        Cell: (row) => {
          return (
              <span>
              {row.value}
              </span>
          );
        },
        // Cell: (row) => {
        //   let { ip, port } = row.original;
        //   return (
        //     <div>
        //       {ip}:{port}
        //     </div>
        //   );
        // },
      },
      {
        Header: "Datacenter",
        accessor: "datacenter",
        Cell: (row) => {
          return (
              <div>
              {row.value !== "N/A"? row.value : ""}
              </div>
          );
        },
      },
      {
        Header: "VRF",
        accessor: "vrf",
        Cell: (row) => {
          return (
              <div>
              {row.value !== "N/A"? row.value : ""}
              </div>
          );
        },
        // Cell: (row) => {
        //   let { vrf } = row.original;
        //   return <div>{vrf}</div>;
        // },
      },
      {
        Header: "Status",
        accessor: "status",
        filterType: "text",
        Cell: (row) => {
          let { status } = row.original;
          return (
            <div>
              <span
                className={`health-bullet ${status === "Connected" ? "healthy" : "dead"}`}
              ></span>
              <span className="health-status">
                {status}
              </span>
            </div>
          );
        },
      },
      {
        Header: "Action",
        accessor: "",
        Cell: (row) => {
          return (
            <div className="right-menu-icons action-btn">
              <Icon
                key={"editagent"}
                className="no-link toggle"
                size="icon-small"
                type="icon-edit"
                style={{ marginRight: "18px", marginLeft: "11px" }}
                onClick={() => {
                  this.editAgent(row.index);
                }}
              ></Icon>
              <Icon
                key={"removeagent2"}
                className="no-link toggle"
                size="icon-small"
                type="icon-delete"
                onClick={() => this.removeAgent(row.index)}
              ></Icon>
            </div>
          );
        },
      },
    ];

    function FormField(props, state) {
      let { name, type, mandatory, placeholder } = props;
      let { isVRFLoading } = state;

      let labelComp = (
        <span>
          {name}
          {mandatory && <span className="mandatory-symbol">*</span>}
        </span>
      );
      let errorMsg = errormsg[name];

      return (
        <div className="form-field">
          {type === "select" ? (
            name === "Protocol" ? (
              <Select
                key={name}
                items={protocolOptions}
                onChange={thiss.handleSelectChange}
                label={labelComp}
              />
            ) : null
          ) : (
            <Input
              label={labelComp}
              type={type}
              key={name}
              name={name}
              placeholder={placeholder}
              value={thiss.state[name]}
              onBlur={thiss.handleFieldChange}
              onChange={thiss.handleFieldChange}
              className={"agent-input" || (errorMsg && "input-error")}
            />
          )}
          {name === "VRF" ? (
            <div className="vrf-dropdown">
              <Select
                key={name}
                items={vrfOptions}
                onChange={(selected, options) =>
                  thiss.handleSelectChange(selected, options, "VRF")
                }
                label={labelComp}
                // disabled={isVRFLoading}
              />
              {isVRFLoading ? (
                <div className={"vrf-spinner"}>
                  <Spinner loading={true} />
                </div>
              ) : null}
            </div>
          ) : null}

          {errorMsg && (
            <div class="help-block text-danger">
              <span class="icon-error"></span>
              <span>{errorMsg}</span>
            </div>
          )}
        </div>
      );
    }

    let saveAllow =
      errormsg["Port"] === null &&
      errormsg["Address"] === null &&
      Address &&
      Port;

    return (
      <div>
        {redirectToMain && <Redirect to="/" />}
        <Modal
          isOpen={addAgentModalIsOpen}
          title={"Add " + AGENTS}
          onClose={function () {
            thiss.refreshField();
            thiss.handleModal();
          }}
        >
          <div>
            <div className="panel">
              <form>
                <div className="integration-form">
                  {agentFields.map((elem) => {
                    return FormField(elem, this.state);
                  })}
                  <div
                    style={{
                      color: "gre",
                      fontSize: "12px",
                      margin: "10px 0px",
                      lineHeight: "12px",
                    }}
                  >
                    Notes:
                    <ul style={{width: "200%"}}>
                      <li>
                      If you have overlapping IP spaces in VRF's , please
                      map it with this seed agent.
                      </li>
                      <li>
                      The data on Dashboard screen would be eventually consistent in case of any configuration changes in the app.
                      </li>
                    </ul>
                  </div>
                  <div className="form-action-buttons">
                    <Button
                      key={"addagentsave"}
                      className={!saveAllow && "disabled"}
                      size="btn--small"
                      type="btn--primary"
                      onClick={this.submitAgent}
                    >
                      Save
                    </Button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </Modal>

        <Screen
          id="agents"
          key="agents"
          className="modal-layer-1"
          hideFooter={true}
          title={AGENTS}
          allowMinimize={false}
          onClose={this.closeAgent}
        >
          <div className="dialog-content">
            <div className="screen-content">
              <div className="panel  panel-with-header ">
                <div className="panel-header with-config-group  ">
                  <div className="heading-container">
                    {/* <div className="panel-label">Agents</div> */}
                  </div>
                  <div className="config-group">
                    <Button
                      key={"reddetail"}
                      className={`half-margin-left ${
                        readAgentLoading && "disabled"
                      }`}
                      size="btn--small"
                      type="btn--primary-ghost"
                      onClick={() => {
                        this.setState(
                          {
                            isNewAgentAdded: true,
                            vrfOptions: [
                              ...[
                                {
                                  label: "None",
                                  value: "None",
                                  selected: true,
                                },
                              ],
                              ...this.props.vrfOptions.map((item) => ({
                                ...item,
                              })),
                            ],
                          },
                          () => {
                            this.handleModal(true);
                          }
                        );
                      }}
                      style={{ marginRight: "10px" }}
                    >
                      {" "}
                      {"Add " + AGENTS}{" "}
                    </Button>

                    <IconButton
                      className={`pull-right ${readAgentLoading && "disabled"}`}
                      type="btn--icon btn--gray-ghost"
                      size="btn--small"
                      icon="icon-refresh"
                      onClick={() => this.readAgents(false, true)}
                    />
                    {/* This recalls agent api and also updatedc call */}
                  </div>
                </div>
                <div className="panel-body ">
                  <FilterableTable
                    // ref={this.myRef}
                    loading={this.state.readAgentLoading}
                    loadingText={this.state.loadingText}
                    className="-striped -highlight"
                    noDataText="No Agent Found."
                    data={this.configureData(this.state.details)}
                    columns={tableColumns}
                    defaultFilters={this.props.defaultFilters || []}
                    />
                </div>
              </div>
            </div>
          </div>
        </Screen>
      </div>
    );
  }
}

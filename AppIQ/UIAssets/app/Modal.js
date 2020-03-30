import React from 'react'
import { Button, Input, Loader, SuccessAlert, DangerAlert, Select } from "blueprint-react"
import "./modelstyle.css"


function getCookieVal(offset) {
  var endstr = document.cookie.indexOf(";", offset);
  if (endstr == -1) {
    endstr = document.cookie.length;
  }
  return unescape(document.cookie.substring(offset, endstr));
}

function getCookie(name) {
  var arg = name + "=";
  var alen = arg.length;
  var clen = document.cookie.length;
  var i = 0;
  var j = 0;
  while (i < clen) {
    j = i + alen;
    if (document.cookie.substring(i, j) == arg) {
      return getCookieVal(j);
    }
    i = document.cookie.indexOf(" ", i) + 1;
    if (i === 0) {
      break;
    }
  }
  return null;
}

export default class Modal extends React.Component {



  constructor(props) {
    super(props)

    this.state = {
      time: 1,
      error: false,
      loading: false,
      message: "",
      status: 0,
      items: [{ label: "1", selected: true, value: 1 }, { label: "2", value: 2 }, { label: "3", value: 3 }
        , { label: "4", value: 4 }
        , { label: "5", value: 5 }
        , { label: "6", value: 6 }
        , { label: "7", value: 7 }
        , { label: "8", value: 8 }
        , { label: "9", value: 9 }
        , { label: "10", value: 10 }

      ]
    }
    this.setPollingInterval = this.setPollingInterval.bind(this);
    this.submitInterval = this.submitInterval.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }



  setPollingInterval(time) {

    let payload = { "query": 'query{SetPollingInterval(interval:"' + time + '" ){status, message}}' }
    let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json"
    window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
    window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");
    var xmlHttp = new XMLHttpRequest();
    try {
      xmlHttp.open("POST", url, true); // false for synchronous request
      xmlHttp.setRequestHeader("Content-type", "application/json");
      xmlHttp.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
      xmlHttp.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
      xmlHttp.send(JSON.stringify(payload));
      xmlHttp.onreadystatechange = () => {

        console.log(xmlHttp);
        if (xmlHttp.readyState == 4) {
          if (xmlHttp.status == 200) {
            let json = JSON.parse(xmlHttp.responseText);
            console.log(json);
            if ("errors" in json) {
              // Error related to query
              this.handleError(json.errors[0]["message"]);
            } else {
              // Response successful
              const response = json.data["SetPollingInterval"]

              if (response.status != "200") {
                // Problem with backend fetching data
                this.handleError(response.message);
              } else {
                // Success
                this.handleError(response.message, true)
              }
            }
          } else {
            // Status code of XHR request not 200

            if (xmlHttp.responseText.includes("errors")) {
              let jsonError = JSON.parse(xmlHttp.responseText)

              this.handleError(jsonError.errors[0]["message"]);
            }
            else {
              this.handleError("Error- " + xmlHttp.status + ": " + xmlHttp.statusText)
            }

          }
        }
      };
    }
    catch (excp) {
      this.handleError("Error: Please check query parameters")
      this.setState({ loading: true })
    }
  }

  handleError(message, successful) {
    console.log(message)
    if (successful) {
      this.setState({ status: 1 })
    }
    else {
      this.setState({ status: 2 })
    }
    this.setState({ message: message })
    this.setState({ loading: false })
  }

  submitInterval() {
    if (this.state.time) {
      this.setState({ loading: true })
      this.setPollingInterval(this.state.time)
    }
    else {
      this.setState({ error: true })
    }
  }

  handleChange(event) {
    console.log(event[0].value)
    this.setState({ time: event[0].value })

  }
  render() {

    return (
      <div className="modal-wrap active" style={{overflow:"scroll"}}>
        <div className="about modal-container new-modal">
          <header><h4 className="pull-left">Polling Interval</h4><div className="close-button" title="Close">
            <span disabled={this.state.loading} className="icon-close icon-medium" onClick={this.props.close}></span></div></header>
          {this.state.loading ?

            <main>
              <Loader></Loader>
            </main> :
            <main>
              <div className="row ">
                {this.state.status == 0 ? null :

                  <div className="modal-wrap active">
                    <div style={{margin: "0px 0px 16px -16px"}} className="about modal-container new-modal after-info">

                      <main >
                        <div>
                          {this.state.status == 1 ? <SuccessAlert key="14" children={this.state.message} /> :
                            <DangerAlert key="1" children={this.state.message}></DangerAlert>

                          }

                          <Button className="submit-btn" onClick={this.props.close} type="btn--primary" size="btn--small">Ok</Button>
                        </div> </main>
                    </div>
                  </div>

                }
                <div className="col-md-12">
                  <Select onChange={this.handleChange} items={this.state.items} size="input-default" placeholder="select interval in minutes"></Select>
                  {/* <Input onChange={this.handleChange} value={this.state.time} maxLength="2" placeholder="In Minutes"  ></Input> */}</div>
              </div>
              {this.state.error ? <div className="col-md-12 text-danger">
                *Please Enter Polling Interval
</div> : null}
              <Button className="submit-btn" onClick={this.submitInterval} type="btn--primary" size="btn--small">Save</Button>
            </main>

          }




        </div>
      </div>
    )

  }


}
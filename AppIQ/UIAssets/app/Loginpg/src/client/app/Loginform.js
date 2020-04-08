import React from 'react';
import './style.css';
import { strictEqual } from 'assert';
import { stringify } from 'querystring';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

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


/**
* @param {string} theUrl The URL of the REST API
*
* @return {string} The response received from portal
*/
function httpGet(theUrl, payload) {
    window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
    window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");
    var xmlHttp = new XMLHttpRequest();

    xmlHttp.open("POST", theUrl, false); // false for synchronous request
    xmlHttp.setRequestHeader("Content-type", "application/json");
    xmlHttp.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
    xmlHttp.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
    xmlHttp.send(JSON.stringify(payload));
    return xmlHttp.responseText;
}

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
    vars[key] = value;
    });
    return vars;
}

class LoginForm extends React.Component {

    constructor(props) {
        super(props);

        const check_payload = {query: `query{
            Check{checkpoint}            
          }`}

        let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
        let checkData = httpGet(url, check_payload);
        try {
            if(JSON.parse(JSON.parse(checkData).data.Check.checkpoint).status_code == "200") {
                if(typeof getUrlVars()['reset'] == "undefined") {
                    window.location.href = "app.html";
                }
            }
        }
        catch(e) {
            console.log('Error collecting checkpoint');
        }
        
        this.handleSignIn = this.handleSignIn.bind(this);
        this.notify = this.notify.bind(this);
    }

    notify(message) {
        toast.error(message, {
            position: toast.POSITION.BOTTOM_CENTER
          });
    }

    handleSignIn(e) {
        e.preventDefault()
        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");
        let username = this.refs.username.value;
        let password = this.refs.password.value;
        let account = this.refs.account.value;
        let ip = this.refs.ip.value;
        let port = this.refs.port.value;
        let signin = this.props.onSignIn;
        let signout = this.props.onSignOut;
        let modal_alert = this.props.alert;
        var payload = {
            query: `query{
  LoginApp(ip:"` + ip + `",port:"` + port + `",username:"` + username + `",account:"` + account + `",password:"` + password + `"){
    loginStatus
  }
}`}
        let xhr = new XMLHttpRequest();
        let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";
        let thiss = this;
        try {
            xhr.open("POST", url, false);
            xhr.setRequestHeader("Content-type", "application/json");
            xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
            xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    let json = JSON.parse(xhr.responseText);
                    if ('errors' in json) {
                        thiss.notify("Could not login. The query may be invalid.");
                        signout();
                    }
                    else if ('loginStatus' in json.data.LoginApp) {
                        let resp = JSON.parse(json.data.LoginApp.loginStatus)
                        if(resp.status_code == 200) {
                            signin(username, password, account, port, ip);
                            window.location.href = "app.html";
                        }
                        else {
                            thiss.notify(resp.message);
                            signout();
                        }
                    }
                }
                else {
                    thiss.notify("Error while reaching the container.")
                    signout();
                }
            }
            xhr.send(JSON.stringify(payload));
        }
        catch(e) {
            this.notify("Error while logging in.");
        }
    }

    render() {
        return (
            <div>
            <ToastContainer />
            {/* Temporarily commented --- 
            <form onSubmit={this.handleSignIn}>
                <center>
                    <table>
                        <tbody>
                            <tr>
                                <th>
                                    Appdynamics Controller
                                </th>
                                <th>
                                    Controller Port
                                </th>
                                <th>
                                    User
                                </th>
                                <th>
                                    Account
                                </th>
                                <th>
                                    Password
                                </th>
                            </tr>
                            <tr>
                                <td>
                                    <input type="text" ref="ip" placeholder="Controller" className="input-textbox" />
                                </td>
                                <td>
                                    <input type="text" ref="port" placeholder="Port" className="input-textbox" />
                                </td>
                                <td>
                                    <input type="text" ref="username" placeholder="User" className="input-textbox" />
                                </td>
                                <td>
                                    <input type="text" ref="account" placeholder="Account" className="input-textbox" />
                                </td>
                                <td>
                                    <input type="password" ref="password" placeholder="Password" className="input-textbox" />
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    <br/>
                    <input type="submit" value="Login" className="button view-button" />
                </center>
            </form>
            */}

            {/* for Temporary bypass purpose */}
            <form>
                <center>
                    <br/>
                    <input type="button" value="Login" className="button view-button" onClick={()=> window.location.href = "app.html"}/>
                </center>
            </form>
            </div>
        )
    }
}

export default LoginForm;

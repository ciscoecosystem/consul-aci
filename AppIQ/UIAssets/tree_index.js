import React from 'react';
import { render } from 'react-dom';
import TestComponent from './app/Tree/src/client/app/TestComponent.js';

var treedata;

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

window.APIC_DEV_COOKIE = getCookie("app_Cisco_TestAppIQ_token");
window.APIC_URL_TOKEN = getCookie("app_Cisco_TestAppIQ_urlToken");

function getData() {
    var apicHeaders = new Headers();
    // apicHeaders.append("DevCookie", window.APIC_DEV_COOKIE);
    // apicHeaders.append("APIC-challenge", window.APIC_URL_TOKEN);
    // fetch(document.location.origin + '/appcenter/Cisco/TestAppIQ/run.json?' + filter, {
    //     method: 'GET',
    //     headers: apicHeaders
    // })
    //     .then(function (response) {
    //         return response.json()
    //     }).then(function (body) {
    //         console.log(body);
    //         treedata = body;
    //         render(<App />, document.getElementById('app'));
    //     });

    var urlToParse = location.search;
    let urlParams = {};
    urlToParse.replace(
        new RegExp("([^?=&]+)(=([^&]*))?", "g"),
        function ($0, $1, $2, $3) {
            urlParams[$1] = $3;
        }
    );
    let result = urlParams;


    let payload = { query: 'query{Run(tn:"AppDynamics",appId:"' + result['appId'] + '"){details}}' }

    let xhr = new XMLHttpRequest();
    let url = "http://127.0.0.1:80/graphql.json";

    try {
        xhr.open("POST", url, false);
    }
    catch (e) {
        localStorage.setItem('message', "Network error while fetching data for tree.");
        window.location.href = "app.html?gqlerror=1";
    }

    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
    xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log(xhr.responseText);
            let json = JSON.parse(xhr.responseText);

            if ('errors' in json) {
                localStorage.setItem('message', JSON.stringify(json.errors));
                window.location.href = "app.html?gqlerror=1";
            }
            treedata = JSON.parse(json.data.Run.response);
            render(<App />, document.getElementById('app'));
        }
        else {
            console.log("Cannot fetch data to fetch Tree data.")
            localStorage.setItem('message', "Error while fetching data for tree.");
            window.location.href = "app.html?gqlerror=1";
        }
    }
    try {
        xhr.send(JSON.stringify(payload));
    }
    catch (e) {
        localStorage.setItem('message', "Network error while fetching data for tree.");
        window.location.href = "app.html?gqlerror=1";
    }
}

// var req = new XMLHttpRequest();
// req.open('GET', document.location.origin + '/appcenter/Cisco/TestAppIQ/run.json?' + filter, false);
// req.onreadystatechange = function () {
//     if (req.readyState == 4 && req.status == 200) {
//         var jsonResponse = JSON.parse(req.responseText);
//         treedata = jsonResponse;
//         render(<App />, document.getElementById('app'));
//     }
// }
// req.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
// req.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
// req.send(null);


class App extends React.Component {
    render() {
        return (
            <div>
                <TestComponent data={treedata} />
            </div>
        );
    }
}

// render(<App />, document.getElementById('app'));

getData();

window.addEventListener('message', function (e) {
    if (e.source === window.parent) {
        try {
            var tokenObj = JSON.parse(e.data);
            if (tokenObj) {
                window.APIC_DEV_COOKIE = tokenObj.token;
                window.APIC_URL_TOKEN = tokenObj.urlToken;
                getData();
            }
        }
        catch (e) {
            console.log(e)
        }
    }
});

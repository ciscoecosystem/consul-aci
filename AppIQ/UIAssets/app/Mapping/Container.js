import React from 'react'
import Header from './Header'
import { PROFILE_NAME, QUERY_URL, getCookie } from '../../constants.js';
import ClusterList from './ClusterList'
import './style.css'

var headerInstanceName;

class Container extends React.Component {
    constructor(props) {
        super(props);

        var urlToParse = location.search;
        let urlParams = {};
        urlToParse.replace(
            new RegExp("([^?=&]+)(=([^&]*))?", "g"),
            function ($0, $1, $2, $3) {
                urlParams[$1] = $3;
            }
        );
        let result = urlParams;

        /**
        * Use this.httpGet to get data from REST API
        */
        let payload = { query: 'query{Mapping(tn:"' + result['tn'] + '",datacenter:"' + result[PROFILE_NAME] + '"){mappings}}' }

        let mappings_json_data = {
            target_cluster: [],
            source_cluster: []
        }

        try {
            let main_data_raw = this.httpGet(QUERY_URL, payload);

            let rawJsonData = JSON.parse(JSON.parse(main_data_raw).data.Mapping.mappings)

            if ('errors' in JSON.parse(main_data_raw)) {
                // Error related to query
                localStorage.setItem('message', JSON.stringify(JSON.parse(main_data_raw).errors));
                window.location.href = "index.html?gqlerror=1";
            }
            else {
                if (rawJsonData.status_code != "200") {
                    // Problem with backend fetching data
                    const message = {
                        "errors": [{
                            "message": rawJsonData.message
                        }]
                    }
                    localStorage.setItem('message', JSON.stringify(message.errors));
                    window.location.href = "index.html?gqlerror=1";
                }
                else {
                    // Success
                    headerInstanceName = rawJsonData.instanceName;
                    mappings_json_data = rawJsonData.payload;
                }
            }
        }
        catch (e) {
            // Problem fetching data
            if (typeof message_set == 'undefined') {
                const message = {
                    "errors": [{
                        "message": "Error while fetching data for Mappings."
                    }]
                }
                localStorage.setItem('message', JSON.stringify(message.errors));
            }
            window.location.href = "index.html?gqlerror=1";
        }

        let sourceJsonData = mappings_json_data.source_cluster;
        let targetJsonData = mappings_json_data.target_cluster;

        sourceJsonData.forEach(item => {
            if ("ipaddress" in item) {
                item["macaddress"] = "";
            } else {
                item["ipaddress"] = "";
            }
        });

        let newTargetJsonData = targetJsonData.map(item => {
            let ipaddress = '';
            if ("ipaddress" in item) {
                ipaddress = item.ipaddress;
            }
            let domainName = item.domainName;
            let macaddress = '';
            if ("macaddress" in item) {
                macaddress = item.macaddress;
            }
            let newObject = {
                "ipaddress": ipaddress,
                "macaddress": macaddress,
                "domains": [
                    {
                        "domainName": domainName
                    }
                ]
            };

            return newObject
        });

        targetJsonData = newTargetJsonData;

        this.state = {
            "sourceClusterList": sourceJsonData,
            "targetClusterList": targetJsonData,
            "sourceSelected": null,
            "targetSelected": null,
            datacenterName: result[PROFILE_NAME]
        };

        this.insertIntoTarget = this.insertIntoTarget.bind(this);
        this.removeFromTarget = this.removeFromTarget.bind(this);
        this.sourceSelectionChanged = this.sourceSelectionChanged.bind(this);
        this.targetSelectionChanged = this.targetSelectionChanged.bind(this);
        this.saveMapping = this.saveMapping.bind(this);
    }

    /**
    * @param {string} theUrl The URL of the REST API
    *
    * @return {string} The response received from portal
    */
    httpGet(theUrl, payload) {
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

    /**
    * Insert the item selected in source, to target list
    */
    insertIntoTarget() {
        let newItem = this.state.sourceSelected;
        let oldList = this.state.targetClusterList;

        if (this.state.sourceSelected == null) {
            return;
        }

        let newIPaddress = newItem.ipaddress ? newItem.ipaddress : '';
        let newDomainName = newItem.domainName;
        let newMacaddress = newItem.macaddress ? newItem.macaddress : '';

        let newObjectString = '{"ipaddress" : "' + newIPaddress + '","macaddress" : "' + newMacaddress + '" ,"domains" : [{"domainName" : "' + newDomainName + '","recommended" : true}]}'
        const newObject = JSON.parse(newObjectString);

        //check if element already exist
        //append if not
        let existingTargetList = this.state.targetClusterList.map(item => {
            return item.ipaddress
        });
        if (existingTargetList.indexOf(newIPaddress) > -1) {
            return;
        }

        oldList.push(newObject);
        this.setState({
            "targetCLusterList": oldList,
            "sourceSelected": null
        });
    }

    /**
    * Remove an element from list when 'remove' is clicked
    */
    removeFromTarget() {
        let itemToRemove = this.state.targetSelected;

        //nothing to do if no item is selected
        if (itemToRemove == null) {
            return;
        }

        //locate the item to remove
        let oldList = this.state.targetClusterList;
        let index = -1;
        let i = 0;
        for (i = 0; i < oldList.length; i++) {
            index += 1;
            if (itemToRemove.ipaddress == oldList[i].ipaddress) {
                break;
            }
        }

        //remove if found
        if (index > -1) {
            oldList.splice(index, 1);
        }

        this.setState({
            "targetCLusterList": oldList,
            'targetSelected': null
        });
    }

    /**
    * @param {object} ipaddress
    * @return none
    *
    * Update state when a new item in source is selected
    */
    sourceSelectionChanged(ipaddress) {
        let existingTargetList = this.state.targetClusterList.map(item => {
            return item.ipaddress
        });
        if (existingTargetList.indexOf(JSON.parse(ipaddress.target.getAttribute("value")).ipaddress) > -1) {
            return;
        }
        this.setState({
            "sourceSelected": JSON.parse(ipaddress.target.getAttribute("value"))
        });
    }

    /**
    * @param {object} ipaddress
    * @returns none
    *
    * Update state when a new item in target is selected
    */
    targetSelectionChanged(ipaddress) {
        this.setState({
            "targetSelected": JSON.parse(ipaddress.target.getAttribute("value"))
        });
    }

    /**
     * Callback when the 'save mapping' operation is called
     */
    saveMapping() {

        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");

        let xhr = new XMLHttpRequest();

        let mappingList = JSON.stringify(this.state.targetClusterList);
        let payload = { query: 'query{SaveMapping(datacenter:"' + this.state.datacenterName + '",tn:"' + this.props.tenantName + '",data:"' + mappingList.replace(/"/g, '\'') + '"){savemapping}}' }

        xhr.open("POST", QUERY_URL, false);
        xhr.setRequestHeader("Content-type", "application/json");
        xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
        xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                window.location.href = "index.html";
            }
        }
        xhr.send(JSON.stringify(payload));
    }

    backToIndex() {
        window.location.href = "index.html";
    }

    render() {
        let existingTargetList = this.state.targetClusterList.map(item => {
            if (item.ipaddress != '') {
                return item.ipaddress;
            } else if (item.macaddress != '') {
                return item.macaddress;
            }
        });

        let addEnabled = (this.state.sourceSelected == null) ? "button-disabled" : "";
        let removeEnabled = (this.state.targetSelected == null) ? "button-disabled" : "";

        return (
            <div>
                <Header text={this.props.headertext} applinktext={this.props.applinktext} instanceName={headerInstanceName} />
                <div className="container">
                    <div className="cluster-list">
                        <ClusterList type="source" listData={this.state.sourceClusterList} targetList={existingTargetList} onSelectionChanged={this.sourceSelectionChanged} selectedItem={this.state.sourceSelected} />
                    </div>

                    <div className="control-button-panel">
                        <button onClick={this.insertIntoTarget} className={addEnabled} style={{ "backgroundColor": "#6ABE45", "display": "inline-block", "height": "2em", "line-height": "1.5em", "padding-top": "0.1em", "padding-left": "1%", "border-radius": "15px" }}>Add <svg class="svg-icon" viewBox="0 -3 20 20">
                            <path fill="none" d="M1.729,9.212h14.656l-4.184-4.184c-0.307-0.306-0.307-0.801,0-1.107c0.305-0.306,0.801-0.306,1.106,0
                            l5.481,5.482c0.018,0.014,0.037,0.019,0.053,0.034c0.181,0.181,0.242,0.425,0.209,0.66c-0.004,0.038-0.012,0.071-0.021,0.109
                            c-0.028,0.098-0.075,0.188-0.143,0.271c-0.021,0.026-0.021,0.061-0.045,0.085c-0.015,0.016-0.034,0.02-0.051,0.033l-5.483,5.483
                            c-0.306,0.307-0.802,0.307-1.106,0c-0.307-0.305-0.307-0.801,0-1.105l4.184-4.185H1.729c-0.436,0-0.788-0.353-0.788-0.788
                            S1.293,9.212,1.729,9.212z"></path>
                        </svg>
                        </button>
                        <br /> <br />
                        <button onClick={this.removeFromTarget} className={removeEnabled} style={{ "backgroundColor": "Transparent", "color": "#5092fb", "whiteSpace": "nowrap", "display": "inline-block", "height": "2em", "line-height": "1.5em", "padding-top": "0.1em", "padding-left": "1%", "border-radius": "15px" }}><svg class="svg-iconr" viewBox="0 -3 20 20">
                            <path fill="none" d="M18.271,9.212H3.615l4.184-4.184c0.306-0.306,0.306-0.801,0-1.107c-0.306-0.306-0.801-0.306-1.107,0
                            L1.21,9.403C1.194,9.417,1.174,9.421,1.158,9.437c-0.181,0.181-0.242,0.425-0.209,0.66c0.005,0.038,0.012,0.071,0.022,0.109
                            c0.028,0.098,0.075,0.188,0.142,0.271c0.021,0.026,0.021,0.061,0.045,0.085c0.015,0.016,0.034,0.02,0.05,0.033l5.484,5.483
                            c0.306,0.307,0.801,0.307,1.107,0c0.306-0.305,0.306-0.801,0-1.105l-4.184-4.185h14.656c0.436,0,0.788-0.353,0.788-0.788
                            S18.707,9.212,18.271,9.212z"></path>
                        </svg> Remove
                    </button>
                    </div>

                    <div className="cluster-list">
                        <ClusterList type="target" listData={this.state.targetClusterList} onSelectionChanged={this.targetSelectionChanged} selectedItem={this.state.targetSelected} />
                        <div>
                            <button className="submit-button" onClick={this.saveMapping}>Save</button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}

export default Container

import React from 'react'
import Button from './Button'
import { PROFILE_NAME } from "../constants.js";
import './style.css'

class AppInfo extends React.Component {
    constructor(props) {
        super(props)
        this.handleMapClick = this.handleMapClick.bind(this);
        this.handleViewClick = this.handleViewClick.bind(this);
        this.handleDetailsClick = this.handleDetailsClick.bind(this);

        this.tenantName = props.tenantName;
    }
    handleMapClick(event) {
        localStorage.setItem(PROFILE_NAME, event.target.getAttribute("value"));
        window.location.href = `mapping.html?${PROFILE_NAME}=` + encodeURIComponent(event.target.getAttribute(PROFILE_NAME)) + "&tn=" + encodeURIComponent(this.tenantName);
    }
    
    handleViewClick(event) {
        console.log("View : " + this.props.data[PROFILE_NAME] );
        window.location.href = `tree.html?${PROFILE_NAME}=` + encodeURIComponent(event.target.getAttribute(PROFILE_NAME)) + "&tn=" + encodeURIComponent(this.tenantName);
    }
    
    handleDetailsClick(event) {
        window.location.href = `details.html?${PROFILE_NAME}=` + encodeURIComponent(event.target.getAttribute(PROFILE_NAME)) + "&tn=" + encodeURIComponent(this.tenantName);
    }

    render() {
        const highlight = this.props.highlight;
        var sty = {};
        const health = this.props.data.health;
        let color = "56b72a";
        if(health == "WARNING") {
            color = "#ffcc00";
        }
        if(health == "CRITICAL") {
            color = "#ff6666";
        }
        let highlightClass = highlight==false ? "light" : "dark";
        let classes =  highlightClass + " app-name";

        let CONSUL_btnMoreProps = { [PROFILE_NAME] : this.props.data[PROFILE_NAME] }

        return (
                <tr className={highlightClass}>
                    <td className="app-name" width="55%">
                        {this.props.data[PROFILE_NAME]}
                    </td>
                    <td width="15%">  
                    <center>
                        <button className="health button" style={{"backgroundColor" : color}} disabled>{this.props.data.health}</button>
                    </center>                
                    </td>
                    <td width="10%">  
                        <center>
                        <Button onClicked={this.handleDetailsClick} type="Details" {...CONSUL_btnMoreProps}/> 
                        </center>                
                    </td>
                    <td width="10%">
                        <center>
                            <Button onClicked={this.handleMapClick} type="Map" {...CONSUL_btnMoreProps} appId={"123"}/> 
                        </center>               
                    </td>
                    <td width="10%">
                        <center>
                            <Button onClicked={this.handleViewClick} type="View" enable={this.props.data.isViewEnabled} {...CONSUL_btnMoreProps}/>
                        </center>
                    </td>
                </tr>
        )
    }
}

export default AppInfo
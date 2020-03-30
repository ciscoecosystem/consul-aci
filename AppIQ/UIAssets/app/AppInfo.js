import React from 'react'
import Button from './Button'
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
        localStorage.setItem("appProfileName", event.target.getAttribute("value"));
        window.location.href = "mapping.html?appId=" + encodeURIComponent(event.target.getAttribute("value")) + "&appProfileName=" + encodeURIComponent(event.target.getAttribute("appProfileName")) + "&tn=" + encodeURIComponent(this.tenantName);
    }
    
    handleViewClick(event) {
        console.log("View : " + this.props.data.appProfileName );
        window.location.href = "tree.html?appId=" + encodeURIComponent(event.target.getAttribute("value")) + "&tn=" + encodeURIComponent(this.tenantName);
    }
    
    handleDetailsClick(event) {
        window.location.href = "details.html?appId=" + encodeURIComponent(event.target.getAttribute("value")) + "&tn=" + encodeURIComponent(this.tenantName);
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
        return (
                <tr className={highlightClass}>
                    <td className="app-name" width="55%">
                        {this.props.data.appProfileName}
                    </td>
                    <td width="15%">  
                    <center>
                        <button className="health button" style={{"backgroundColor" : color}} disabled>{this.props.data.health}</button>
                    </center>                
                    </td>
                    <td width="10%">  
                        <center>
                        <Button onClicked={this.handleDetailsClick} type="Details" appProfileName={this.props.data.appProfileName} appId={this.props.data.appId}/> 
                        </center>                
                    </td>
                    <td width="10%">
                        <center>
                            <Button onClicked={this.handleMapClick} type="Map" appProfileName={this.props.data.appProfileName} appId={this.props.data.appId}/> 
                        </center>               
                    </td>
                    <td width="10%">
                        <center>
                            <Button onClicked={this.handleViewClick} type="View" enable={this.props.data.isViewEnabled} appProfileName={this.props.data.appProfileName} appId={this.props.data.appId}/>
                        </center>
                    </td>
                </tr>
        )
    }
}

export default AppInfo
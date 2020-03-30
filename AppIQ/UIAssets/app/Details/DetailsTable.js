import React from 'react'
import './style.css'
import ToolBar from './ToolBar'

class DetailsTable extends React.Component {
    constructor(props) {
        super(props);
        console.log("DetTab : " + props.onReload);
    }

    render() {
        const data = this.props.data;

        let lightDark = "light";
        let keyIter = -1;
        const rendereddata = data.map(item => {
            keyIter += 1;
            lightDark = (lightDark == "light") ? "dark" : "light";

            let tiercolor = "56b72a";
            if(item.tierHealth == "WARNING") {
                tiercolor = "#ffcc00";
            }
            if(item.tierHealth == "CRITICAL") {
                tiercolor = "#ff6666";
            }

            let epgcolor = "56b72a";
            if(item.epgHealth < 70) {
                epgcolor = "#ffcc00";
            }
            if(item.epgHealth < 40) {
                epgcolor = "#ff6666";
            }
            return (
                <tr key={keyIter} className={lightDark}>
                    <td className="app-name">
                        {item.IP}
                    </td>
                    <td className="app-name">
                        {item.endPointName}
                    </td>
                    <td className="app-name">
                        {item.epgName}
                    </td>
                    <td>
                        <span className="button" style={{backgroundColor : epgcolor}}>{item.epgHealth}</span>
                    </td>
                    <td className="app-name">
                        {item.tierName}
                    </td>
                    <td>
                    <span className="button" style={{backgroundColor : tiercolor}}>{item.tierHealth}</span>
                    </td>
                    {/* <td>
                        <button className="button view-button" onClick={()=>{window.location.href = "network.html?p_appid=" + encodeURIComponent(this.props.appId)+ "&p_tn=" + encodeURIComponent(this.props.tn) + "&endpointname=" + encodeURIComponent(item.endPointName)}}>App Flow</button>
                    </td> */}
                </tr>
            );
        })

        return (
            <div className="details-table-container">
                <ToolBar onReload={this.props.onReload} />
                <table border="0" width="100%">
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <tbody>
                    <tr className="th-header">
                        <td></td>
                        <td colSpan="3">
                            <center><div className="th-header-inside">EPG</div></center>
                        </td>
                        <td colSpan="2">
                            <center><div className="th-header-inside">Tier</div></center>
                        </td>
                    </tr>
                    <tr className="sub-header">
                        <td className="sub-header">IP</td>
                        <td className="sub-header">End point</td>
                        <td className="sub-header">Name</td>
                        <td className="sub-header">Health</td>
                        <td className="sub-header">Name</td>
                        <td className="sub-header">Health</td>
                    </tr>
                    {rendereddata}
                    </tbody>
                </table>
            </div>
        )
    }
}

export default DetailsTable

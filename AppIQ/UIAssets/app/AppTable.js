import React from "react"
import {Table,Button} from "blueprint-react"
export default class AppTable extends React.Component{
    constructor(props){
        super(props);
        this.handleMapClick = this.handleMapClick.bind(this);
        this.handleViewClick = this.handleViewClick.bind(this);
        this.handleDetailsClick = this.handleDetailsClick.bind(this);
        this.state = {
            tenantName : this.props.tenantName,
            jsonData : this.props.rows
        }
        this.columns = [
            { Header : "Application Name",
            accessor : "appProfileName"    
            },
            {
                Header : "Health",
                accessor : "health",
                Cell : row => {
                    let tiercolor = "#6ebe4a";
                    if(row.value == "WARNING") {
                        tiercolor = "#ffcc00";
                    }
                    if(row.value == "CRITICAL") {
                        tiercolor = "#FF6666";
                    }
                    return <Button  style={{backgroundColor:tiercolor,opacity:"1"}} disabled={true} key ="S"  size="btn--small">{row.value}</Button>
                }
            },
            {
                Header : "",
                id : "details",
                accessor : d => d,
                Cell : row => (
                    <div>
                    <Button className="half-margin-left" size="btn--small" type="btn--secondary" onClick={()=>this.handleDetailsClick(row.value)}>Details</Button>
                    <Button className="half-margin-left" size="btn--small"type="btn--secondary" onClick={()=>this.handleMapClick(row.value)}>Mapping</Button>
                    <Button className="half-margin-left" disabled={!row.value.isViewEnabled} size="btn--small" type="btn--secondary" onClick={()=>this.handleViewClick(row.value)}>View</Button>
                    </div>)
            }
        ]

      
    }
    handleMapClick(data) {
        localStorage.setItem("appProfileName", data.appId);
        window.location.href = "mapping.html?appId=" + encodeURIComponent(data.appId) + "&appProfileName=" + encodeURIComponent(data.appProfileName) + "&tn=" + encodeURIComponent(this.state.tenantName);
    }
    
    handleViewClick(data) {
     
        window.location.href = "tree.html?appId=" + encodeURIComponent(data.appId) + "&tn=" + encodeURIComponent(this.state.tenantName);
    }
    
    handleDetailsClick(data) {
        window.location.href = "details.html?appId=" + encodeURIComponent(data.appId) + "&tn=" + encodeURIComponent(this.state.tenantName);
    }
    render(){
      return  <Table data={this.props.rows} columns={this.columns}></Table>
    }

}
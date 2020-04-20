import React from "react"
import {Table,Button} from "blueprint-react"
import { PROFILE_NAME } from "../constants.js";

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
            {
                Header : "",
                accessor : PROFILE_NAME
            },
            {
                Header : "",
                id : "details",
                accessor : d => d,
                Cell : row => (
                    <div>
                    <Button className="half-margin-left" size="btn--small" type="btn--secondary" onClick={()=>this.handleDetailsClick(row.value)}>Details</Button>
                    <Button className="half-margin-left" size="btn--small"type="btn--secondary" onClick={()=>this.handleMapClick(row.value)}>Map</Button>
                    <Button className="half-margin-left" disabled={!row.value.isViewEnabled} size="btn--small" type="btn--secondary" onClick={()=>this.handleViewClick(row.value)}>Operational</Button>
                    </div>)
            }
        ]

      
    }
    handleMapClick(data) {
        localStorage.setItem(PROFILE_NAME, data[PROFILE_NAME]);
        window.location.href = `mapping.html?&${PROFILE_NAME}=` + encodeURIComponent(data[PROFILE_NAME]) + "&tn=" + encodeURIComponent(this.state.tenantName);
    }
    
    handleViewClick(data) {
     
        window.location.href = `tree.html?${PROFILE_NAME}=` + encodeURIComponent(data[PROFILE_NAME]) + "&tn=" + encodeURIComponent(this.state.tenantName);
    }
    
    handleDetailsClick(data) {
        window.location.href = `details.html?${PROFILE_NAME}=` + encodeURIComponent(data[PROFILE_NAME]) + "&tn=" + encodeURIComponent(this.state.tenantName);
    }
    render(){
      return  <Table noDataText="No data found" data={this.props.rows} columns={this.columns} TheadComponent={props => null}></Table>
    }

}
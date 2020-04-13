import React from 'react'
import './hstyle.css'
import {Dropdown,Icon,Table} from "blueprint-react"
import Modal from "./Modal"


class Header extends React.Component {
    constructor(props) {
        super(props)

        this.handleLogoutClick = this.handleLogoutClick.bind(this);
        this.closeModal = this.closeModal.bind(this);
        this.openModal = this.openModal.bind(this);
	
        this.state = {
            showModal : false,
            items : [
              { label: "Set Polling Interval", action:this.openModal},
              { label: "Logout", action:this.handleLogoutClick}
            ]
        }
  
    }
    openModal(){
        this.setState({showModal:true})
    }
	
    closeModal(){
        this.setState({showModal:false})
    }
    handleLogoutClick() {
        window.location.href = "index.html?reset=1"; //TEMPORARY change to login.html
    }

    render() {
   
        return (
            <div className="clearfix">
                {this.state.showModal ? <Modal close={this.closeModal}></Modal> : null}
                <a href="index.html" className="sub-header floal">{this.props.applinktext}</a>
                <div className="sub-header floal">{this.props.text}</div>
             
			
                <div className="floar">
               
                <div className="instancetext">{this.props.instanceName}</div>
                <div className="dropdown-setting pull-right">
 
                <Dropdown 
                label={<span class="icon-cog icon-small"></span>}
                  style={{overflow:"visible"}}
                   size="btn--small"  items={this.state.items}></Dropdown>
                </div>
                </div>
					</div>
           
        )
    }
}


export default Header

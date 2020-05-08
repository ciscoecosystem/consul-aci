import React from 'react';
import { Dropdown } from "blueprint-react";
import './style.css';

class Header extends React.Component {
    constructor(props) {
        super(props);
        this.handleLogoutClick = this.handleLogoutClick.bind(this);
        this.state = {
            items: [
                { label: "Logout", action: this.handleLogoutClick }
            ]
        }
    }

    handleLogoutClick() {
        window.location.href = "index.html?reset=1";
    }

    render() {

        return (
            <div className="clearfix">
                <a href="index.html" className="sub-header floal">{this.props.applinktext}</a>
                <div className="sub-header floal">{this.props.text}</div>

                <div className="floar">

                    <div className="instancetext">{this.props.instanceName}</div>
                    <div className="dropdown-setting pull-right">

                        <Dropdown
                            label={<span class="icon-cog icon-small"></span>}
                            style={{ overflow: "visible" }}
                            size="btn--small" items={this.state.items}></Dropdown>
                    </div>
                </div>
            </div>

        )
    }
}

export default Header

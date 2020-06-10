import React from 'react';
import CONSUL_LoginForm from "./CONSUL_Loginform";
import './style.css';

class LoginComponent extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            user: null
        }

        // Fetching TenantName 'tn' from url
        try {
            const rx = /Tenants:(.*)\|/g;
            const topUrl = window.top.location;
            const tenantNames = rx.exec(topUrl);

            this.tenantName = tenantNames[1];
        } catch (err) {
            console.error("error in getting tenants ", err);
        }
    }

    render() {
        return (
            <div>
                <CONSUL_LoginForm tenantName={this.tenantName} />
            </div>
        )
    }
}

export default LoginComponent;

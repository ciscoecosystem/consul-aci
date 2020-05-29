import React from 'react'
import { Screen } from "blueprint-react";
import CONSUL_Container from "./CONSUL_Container";
import { PROFILE_NAME, getParamObject } from "../../constants.js";

class Mapping extends React.Component {
    constructor(props) {
        super(props);

        this.closeAgent = this.closeAgent.bind(this);
    }

    closeAgent() {
        this.props.handleMapping(false);
    }

    render() {

        let result = getParamObject(window.location);
        // let dcName = result[PROFILE_NAME];

        return (
            <div>
                <Screen id="agents" key="agents" className="modal-layer-1" hideFooter={true} title={"Mapping | " + this.props.mappingDcname} allowMinimize={false} onClose={this.closeAgent}>
                    <CONSUL_Container tenantName={result['tn']} datacenterName={this.props.mappingDcname} onClose={this.closeAgent}/>
                </Screen>
            </div>
        )
    }
}

export default Mapping

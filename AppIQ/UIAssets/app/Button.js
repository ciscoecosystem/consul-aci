import React from 'react'
import { PROFILE_NAME } from "../constants.js";

class Button extends React.Component {
    constructor(props) {
        super(props)
    }
    
    render() {
        let btnProps = { "onClick": this.props.onClicked, [PROFILE_NAME]: this.props[PROFILE_NAME] }

        if(this.props.type == "Map") {
            return <button {...btnProps} className="button map-button">Mapping</button>
        }
        if(this.props.type == "Details") {
            return <button {...btnProps}  className="button map-button">Details</button>
        }
        
        if(this.props.type == "View") {
            if(this.props.enable == true) {
                return <button  {...btnProps} className="button view-button">View</button>
            }
            else {
                return <button onClick={this.props.onClicked} className="button view-button view-button-disabled" disabled>View</button>
            }
        }
        
        
    }
}

export default Button
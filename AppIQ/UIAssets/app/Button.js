import React from 'react'

class Button extends React.Component {
    constructor(props) {
        super(props)
    }
    
    render() {
        if(this.props.type == "Map") {
            return <button onClick={this.props.onClicked} appProfileName={this.props.appProfileName} value={this.props.appId} className="button map-button">Mapping</button>
        }
        if(this.props.type == "Details") {
            return <button onClick={this.props.onClicked} appProfileName={this.props.appProfileName} value={this.props.appId} className="button map-button">Details</button>
        }
        
        if(this.props.type == "View") {
            if(this.props.enable == true) {
                return <button onClick={this.props.onClicked} appProfileName={this.props.appProfileName} value={this.props.appId} className="button view-button">View</button>
            }
            else {
                return <button onClick={this.props.onClicked} className="button view-button view-button-disabled" disabled>View</button>
            }
        }
        
        
    }
}

export default Button
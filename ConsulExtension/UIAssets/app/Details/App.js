import React, { Component } from 'react'
import Container from './Container'

class App extends Component {
    constructor(props) {
        super(props)
    }
    render() {
        return (
            <div>
                <Container tenantName={this.props.tenantName} dcName={this.props.dcName}/>
            </div>
        )
    }
}

export default App

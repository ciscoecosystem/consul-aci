import React, { Component } from 'react'
import Container from './Container'
import './style.css'

class App extends Component {
    constructor(props) {
        super(props)
    }
    render() {
        return (
            <div className="detail-container">
                <Container tenantName={this.props.tenantName} dcName={this.props.dcName} isDeleted={this.props.isDeleted}/>
            </div>
        )
    }
}

export default App

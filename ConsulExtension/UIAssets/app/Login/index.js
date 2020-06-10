import React from 'react';
import ReactDOM from 'react-dom';
import LoginComponent from './LoginComponent.js';
import './style.css'


class LoginApp extends React.Component {
    constructor(props) {
        super(props)
    }
    render() {
        return (
            <div>
                <LoginComponent />
            </div>
        );
    }
}

ReactDOM.render(<LoginApp />, document.getElementById("app"))

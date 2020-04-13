import React from 'react';
import LoginForm from "./Loginform";
import './style.css';

class LoginComponent extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            user: null
        }
    }

    signIn(username, password, account, port, ip) {
        this.setState({
            user: {
                username,
                account,
                password,
                port,
                ip
            }
        })
    }

    signOut() {
        this.setState({ user: null })
    }

    render() {
        return (
            <div>
                {
                    (this.state.user) ?
                        window.location.href = "app.html" //temporary
                        :
                            <LoginForm
                                onSignIn={this.signIn.bind(this)}
                                onSignOut={this.signOut.bind(this)}
                            />
                }
            </div>
        )
    }
}

export default LoginComponent;

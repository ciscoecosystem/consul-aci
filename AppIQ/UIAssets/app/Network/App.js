import React from 'react';
import Container from './Container';
import Legend from './Legend.js'

export default class App extends React.Component {
    render() {
        return (
            <div>
                <Legend />
                <Container />
            </div>
        );
    }
}

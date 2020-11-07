import React from 'react'
import Container from './Container'

class App extends React.Component {
    constructor(props) {
       super(props)
    }

    render() {
        var urlToParse = location.search;
        let urlParams = {};
        urlToParse.replace(
          new RegExp("([^?=&]+)(=([^&]*))?", "g"),
          function($0, $1, $2, $3) {
            urlParams[$1] = $3;
          }
        );
        let result = urlParams;
        let apptext = " List of Applications";
        let title = " | Application Mapping - " + result['appProfileName'];
        return (
            <div>
                <Container appId={result['appId']} tenantName={result['tn']} applinktext={apptext} headertext={title}/>
            </div>
        )
    }
}

export default App

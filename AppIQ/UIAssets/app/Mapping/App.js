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
      function ($0, $1, $2, $3) {
        urlParams[$1] = $3;
      }
    );
    let result = urlParams;
    let apptext = " " + result['datacenterName'];
    let title = " | Consul Mapping ";
    return (
      <div>
        <Container tenantName={result['tn']} applinktext={apptext} headertext={title} />
      </div>
    )
  }
}

export default App

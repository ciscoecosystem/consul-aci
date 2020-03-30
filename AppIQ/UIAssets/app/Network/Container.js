import React from 'react';
import Graph from "react-graph-vis";
import './style.css'

var endpointName;

const data = {
    "AppD-Pay" : {
        nodes: [
            { id: 1, label: "AppD-Ord_1\n\n<i>10.10.10.18:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
            { id: 2, label: "AppD-Ord_2\n\n<i>10.10.10.19:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
            { id: 3, label: "AppD-Ord", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 4, label: "AppD-Pay", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 5, group: "root", label: "AppD-Pay\n\n<i>10.10.10.21:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" }
          ],
          edges: [{ from: 1, to: 3}, { from: 2, to: 3}, { from: 3, to: 4}, { from: 4, to: 5}]
    },
    "AppD-Inv1_2" :{
        nodes: [
            { id: 1, group: "root", label: "AppD-Inv1_2\n\n<i>10.10.10.17:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
            { id: 2, label: "AppD-Misc\nAppVMs", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 3, label: "AppD-Inv", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 4, label: "AppD-Inv1_1\n\n<i>10.10.10.16:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
            { id: 5, label: "AppD-Ord", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 6, label: "AppD-Ord_1\n\n<i>10.10.10.18:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
            { id: 7, label: "AppD-Ord_2\n\n<i>10.10.10.19:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" }
          ],
          edges: [{ from: 1, to: 2}, { from: 2, to: 3},{ from: 3, to: 4},  { from: 2, to: 5}, { from: 5, to: 6}, { from: 5, to: 7}]
    },
    "AppD-Inv1_1" :{
        nodes: [
            { id: 1, label: "AppD-Inv1_2\n\n<i>10.10.10.17:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
            { id: 2, label: "AppD-Misc\nAppVMs", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 3, label: "AppD-Inv", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 4,  group: "root", label: "AppD-Inv1_1\n\n<i>10.10.10.16:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
          ],
          edges: [{ from: 1, to: 2}, { from: 2, to: 3}, { from: 3, to: 4}]
    },
    "AppD-Ord_2" :{
        nodes: [
            { id: 1, group: "root", label: "AppD-Ord_2\n\n<i>10.10.10.19:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
            { id: 2, label: "AppD-Ord", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 3, label: "AppD-Pay", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 4, label: "AppD-Pay\n\n<i>10.10.10.21:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
          ],
          edges: [{ from: 1, to: 2}, { from: 2, to: 3}, { from: 3, to: 4}]
    },
    "AppD-Ord_1" :{
        nodes: [
            { id: 1, group: "root", label: "AppD-Ord_1\n\n<i>10.10.10.18:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
            { id: 2, label: "AppD-Ord", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 3, label: "AppD-Pay", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
            { id: 4, label: "AppD-Pay_1\n\n<i>10.10.10.21:8080</i>", font : {color : "white", multi: 'html'}, color: "#2DBBAD", shape: "circle" },
          ],
          edges: [{ from: 1, to: 2}, { from: 2, to: 3}, { from: 3, to: 4}]
    }
}

// const graph = {
//     nodes: [
//       { id: 1, label: "AppD-Inv1_1", font : {color : "white"}, color: "#2DBBAD", shape: "circle" },
//       { id: 2, label: "AppD-Inv", font : {color : "white", multi: 'html'}, color: "#085A87", shape: "circle" },
//       { id: 3, label: "AppD-Ord", font : {color : "white"}, color: "#085A87", shape: "circle" },
//       { id: 4, label: "AppD-Ord_1", font : {color : "white"}, color: "#2DBBAD", shape: "circle" },
//       { id: 5, label: "AppD-Ord_2", font : {color : "white"}, color: "#2DBBAD", shape: "circle" }
//     ],
//     edges: [{ from: 1, to: 2}, { from: 2, to: 3}, { from: 3, to: 4}, { from: 3, to: 5}]
// };

const options = {
    layout: {
        hierarchical: false
    },
    edges: {
        color: "#000000"
    },
    groups: {
        root: {color:{background: 'rgb(189, 30, 30)'}}
    },
    physics:{
        enabled: false
    }

};

const events = {
    select: function(event) {
        var { nodes, edges } = event;
        console.log("Selected nodes:");
        console.log(nodes);
        console.log("Selected edges:");
        console.log(edges);
    }
};

var p_appId = null;
var p_tn = null;

export default class App extends React.Component {
    constructor(props) {
        super(props);

        var urlToParse = location.search;
        let urlParams = {};
        urlToParse.replace(
            new RegExp("([^?=&]+)(=([^&]*))?", "g"),
            function ($0, $1, $2, $3) {
                urlParams[$1] = $3;
            }
        );
        let result = urlParams;
        p_appId = result['p_appid'];
        p_tn = result['p_tn'];

        endpointName = result['endpointname']
    }

    render() {
        return (
            <div>
                <button className="button back-button" onClick={()=>{window.location = "details.html?appId=" + encodeURIComponent(p_appId)+ "&tn=" + encodeURIComponent(p_tn)}}> Back </button>
                <Graph graph={data[endpointName]} options={options} events={events} style={{ height: "640px" }} />
            </div>
        );
    }
}

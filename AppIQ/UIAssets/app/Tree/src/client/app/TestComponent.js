import React from 'react';
import Tree from './Tree.js';
import Legend from './Legend.js'
// import { dummyData } from './dummydata.js';
import './style.css';

let treeNumber = 0
export default class TestComponent extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        let nodeData = (this.props.data === undefined) ? [] : this.props.data
        // let nodeData = dummyData;
        let totApps = nodeData.length;
        /*
        nodeWrapper act as a root node and under it would be all nodes, but the root node (ie nodewrapper) is avoided tobe shown
        */

        let nodeWrapper = (totApps === 0) ? [] : [{
            "name": "allNodes",
            "children": nodeData
        }]

        return (
            <div>
                <Legend reloadController={this.props.reloadController} />
                <div id="treeWrapper">
                    <Tree
                        data={nodeWrapper} // nodeWrapper contains 1 array element which further contains multiple node
                        treeNum={treeNumber + 1}
                        totApps={totApps} // signifies total root node (ie total tree)
                        orientation='vertical'
                        textLayout={{ textAnchor: "middle", y: 0 }}
                        nodeSvgShape={{ shape: 'circle', shapeProps: { r: 20 } }}
                        styles={{
                            nodes: {
                                node: {
                                    circle: { fill: "#DFF" },
                                    attributes: { fill: "#000" }
                                },
                                leafNode: { circle: { fill: "#DFF" } }
                            }
                        }}
                        translate={{ x: 400, y: -60 }}  // as root node wont be show (alignment fix)
                    />

                </div >
            </div>
        );
    }
}


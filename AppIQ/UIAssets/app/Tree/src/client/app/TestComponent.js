import React from 'react';
import Tree from './Tree.js';
import Legend from './Legend.js'
import './style.css';

import clone from 'clone';
import request from 'request';

var treeNumber = 0
export default class TestComponent extends React.Component {

    constructor(props) {
        super(props);
        this.getInList = this.getInList.bind(this);
    }

    getInList(item) {
        let list = [];
        list.push(item);
        return list;
    }

    render() {

        let legend = {
            "name": "AppProf",
            "level": "#27AAE1",
            "label": "Application Profile",
            "type": "#27AAE1",
            "trans": 0
        }
        let nodeData = (this.props.data === undefined) ? [] : this.props.data
        console.log("NodeData ", nodeData);
        return (
            <div>
                <Legend  reloadController={this.props.reloadController}/>
                <div id="treeWrapper">
                    <Tree 
                        data={nodeData}
                        treeNum={treeNumber+1}
                        orientation='vertical'
                        textLayout={{ textAnchor: "middle", y: 0 }}
                        nodeSvgShape={{ shape: 'circle', shapeProps: { r: 20 } }}
                        styles={{ 
                            nodes: { 
                                node: { circle: { fill: "#DFF" }, 
                                attributes: { fill: "#000" } }, 
                                leafNode: { circle: { fill: "#DFF" } } 
                            } 
                        }} 
                        translate={{ x: 400, y: 60}} 
                    />

                </div >
            </div>
        );
    }
}


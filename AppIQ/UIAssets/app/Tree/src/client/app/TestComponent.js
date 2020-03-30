import React from 'react';
import Tree from './Tree.js';
import Legend from './Legend.js'
import './style.css';

import clone from 'clone';
import request from 'request';

var dataList;
var treeNumber = 0
export default class TestComponent extends React.Component {

    constructor(props) {
        super(props);
        this.getInList = this.getInList.bind(this);
        this.newData = clone(props.data)
        dataList = this.newData.map(item=>{
            return [item];
        })
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

        return (
            <div>
                <Legend  reloadController={this.props.reloadController}/>
                <div id="treeWrapper">
                    <Tree 
                        data={this.props.data}
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

                <div className="health-indicators" id="health-indicators">
                    <h4 style={{marginTop : "50px"}}>Health Legend</h4>
                    <hr/>
                    <div className="health-indicators-table" width="100%">
                        <table width="90%" style={{margin : "5%"}}>
                            <tr className="health-row">
                                <td width="80%" className="legend-title" style={{padding : "1em"}}> Normal </td>
                                <td width="19%">
                                    <div className="health-normal" style={{height : "2em", width: "2em"}}>&nbsp;</div>
                                </td>
                            </tr>
                            <tr className="health-row">
                                <td width="80%" className="legend-title" style={{padding : "1em"}}> Warning </td>
                                <td width="19%">
                                    <div className="health-warning_" style={{height : "2em", width: "2em"}}>&nbsp;</div>
                                </td>
                            </tr>
                            <tr className="health-row" style={{border : "0px"}}>
                                <td width="80%" className="legend-title" style={{padding : "1em"}}> Critical </td>
                                <td width="19%">
                                    <div className="health-critical_" style={{height : "2em", width: "2em"}}>&nbsp;</div>
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        );
    }
}


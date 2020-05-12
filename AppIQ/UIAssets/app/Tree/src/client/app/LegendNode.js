import React from 'react';
import './style.css';

export default class LegendNode extends React.Component {
    constructor(props) {
        super(props);
        // const { nodeData: { parent } } = props;
        this.state = {
            initialStyle: {
                opacity: 1,
            },
        };
    }

    render() {
        const { nodeData, nodeSvgShape, textLayout, styles } = this.props;
        const nodeStyle = { ...styles.leafNode };
        return (
            <g
                id={nodeData.id}
                ref={n => {
                    this.node = n;
                }}
                style={this.state.initialStyle}
                className={'leafNodeBase1'}
                onClick={this.props.onClick}
                transform={"translate(" + this.props.translate.x + "," + this.props.translate.y + ")"}
            >

                {nodeStyle.circle.stroke = nodeData.level}
                {nodeStyle.circle.fill = nodeData.type}


                {this.props.circleRadius ? (
                    <circle r={this.props.circleRadius} style={nodeStyle.circle} />
                ) : (
                        React.createElement(nodeSvgShape.shape, {
                            ...nodeSvgShape.shapeProps,
                            ...nodeStyle.circle,
                        })
                    )}

                <text
                    className="nodeNameBase"
                    style={nodeStyle.name}
                    textAnchor={textLayout.textAnchor}
                    x={textLayout.x}
                    y={textLayout.y}
                    transform={textLayout.transform}
                    dy=".35em"
                >
                    {(this.props.name == "EP") ? "EP" : this.props.name.charAt(0)}
                </text>

                {this.props.nodeData.label ?
                    <text
                        className="nodeAttributesBase"
                        y={textLayout.y + 23}
                        textAnchor={textLayout.textAnchor}
                        transform={textLayout.transform}
                        //style={nodeStyle.attributes}
                        dy='10'
                    >
                        {this.props.nodeData.label}
                    </text> : ""}

                {this.props.nodeData.sub_label ?
                    <text
                        className="nodeAttributesBase"
                        y={textLayout.y + 35}
                        textAnchor={textLayout.textAnchor}
                        transform={textLayout.transform}
                        //style={nodeStyle.attributes}
                        dy='10'
                    >
                        {this.props.nodeData.sub_label}
                    </text> : ""}

            </g>
        );
    }
}

Node.defaultProps = {
    textAnchor: 'start',
    attributes: undefined,
    circleRadius: undefined,
    styles: {
        node: {
            circle: {},
            name: {},
            attributes: {},
        },
        leafNode: {
            circle: {},
            name: {},
            attributes: {},
        },
    },
};


import React from 'react';
import { Screen } from 'blueprint-react';
import "./Modal.css";

export default function Modal(props) {
    return (props.isOpen === true) ? (
        <div>
            <div className="modal-overlay"> </div>
            <Screen className="modal-layout" hideFooter={true} title={props.title} allowMinimize={false} onClose={props.onClose}>
                <div>
                    {props.children}
                </div>
            </Screen>
        </div>
    ) : (<span></span>)
}
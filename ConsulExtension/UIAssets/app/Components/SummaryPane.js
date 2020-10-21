import React from "react";
import { Icon } from "blueprint-react";
import { showShortName } from "../Utility/utils";
import "./SummaryPane.css";

const HEADER_LENGTH = 25;

class SummaryPane extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
        <div id="myNav" className="overlay-pane summary-pane">
          <header>
            <div className="summary-pane-header">

              <div class="summary-pane-title-value">
                <div class="title" title={this.props.subTitle}>{showShortName(this.props.subTitle, HEADER_LENGTH)}</div>
                <div class="value" title={this.props.title}>{showShortName(this.props.title, HEADER_LENGTH)}</div>
              </div>


              <div class="header-action-buttons">

                <Icon className="link toggle" size="icon-small" type="icon-jump-out" onClick={this.props.openScreen}>&nbsp;</Icon>
                <Icon className="link toggle" size="icon-small" type="icon-close" onClick={this.props.closeSummaryPane}>&nbsp;</Icon>

              </div>
            </div>
          </header>
          <main>
            {this.props.children}
          </main>
        </div>
      </div>
    );
  }
}
export default SummaryPane;

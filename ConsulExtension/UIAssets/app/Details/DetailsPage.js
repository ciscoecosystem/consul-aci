import React, { Component } from "react";
import { Loader, Tab, Screen } from "blueprint-react";
import CONSUL_ConsulTab from "./DetailsPageChild/CONSUL_ConsulTab.js";
import Operational from "./DetailsPageChild/Operational.js";
import "./DetailsPage.css";

export default class DetailsPage extends Component {
  constructor(props) {
    super(props);
    let { data } = props;
    let NodeCheckQuery = {
      query:
        'query{NodeChecks(nodeName:"' +
        data.consulNode +
        '", datacenter:"' +
        props.dataCenter +
        '"){response}}',
    };
    let serviceListForQuery = [
      { Service: data.service, ServiceID: data.serviceInstance },
    ];
    let serviceList = [
      {
        Address: data.ip + ":" + data.port,
        Service: data.service,
        "Service Checks": data.serviceChecks,
        ServiceKind: data.serviceKind,
        ServiceTags: data.serviceTags,
        NameSpace: data.serviceNamespace,
      },
    ];
    let ServiceCheckQuery = {
      query:
        "query{ MultiServiceChecks(serviceList:" +
        JSON.stringify(JSON.stringify(serviceListForQuery)) +
        ', datacenter:"' +
        props.dataCenter +
        '"){response}}',
    };

    this.state = {
      tabs: [
        {
          label: "Operational",
          key: "Operational",
          content: (
            <Operational
              domainName={"uni/tn-"+ this.props.tenantName + "/ap-" + data.ap + "/epg-" + data.epgName }
              moType={"ep"}
              macList={data.mac}
              ipList={[]}
              ip={data.ip}
            />
          ),
        },
        {
          label: "Consul",
          key: "Consul",
          content: (
            <CONSUL_ConsulTab
              NodeCheckQuery={NodeCheckQuery}
              ServiceCheckQuery={ServiceCheckQuery}
              serviceList={serviceList}
            />
          ),
        },
      ],
    };
  }

  render() {
    return (
      <Screen
        class="details-view"
        hideFooter={true}
        title={this.props.title}
        allowMinimize={false}
        onClose={this.props.closeDetailsPage}
      >
        {this.state.tabs.length > 0 ? (
          <Tab type="secondary-tabs" tabs={this.state.tabs} />
        ) : (
          <Loader> loading </Loader>
        )}
      </Screen>
    );
  }
}

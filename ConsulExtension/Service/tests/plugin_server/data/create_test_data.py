import os
import json

val = ["get_to_epg_traffic"]

data =[
([{
            "vzFromEPg": {
                "children": [{
                    "vzToEPg": {
                        "attributes": {
                            "epgDefDn": "uni/tn-DummyTn/brc-DummyBrc/dummy/cons-dummy",
                            "epgDn": "uni/tn-DummyTn/ap-DummyAp/epg-DummyEpg"
                        },
                        "children": [{
                            "vzRsRFltAtt": {
                                "attributes": {
                                    "tDn": "uni/tn-common/fp-default",
                                },
                                "children": [{
                                    "vzCreatedBy": {
                                        "attributes": {
                                            "ownerDn": "uni/tn-DummyTn/brc-DummyBrc/subj-DummySubj/rssubjFiltAtt-DummyFilt"
                                        }
                                    }
                                }]
                            }
                        }]
                    }
                }]
            }
        }],
        {
        "status_code": "200",
        "message": "",
        "payload": [{
            "to_epg": "DummyTn/DummyAp/DummyEpg",
            "contract_subj": "DummyTn/DummyBrc/DummySubj",
            "filter_list": ["flt1", "flt1"],
            "ingr_pkts": "1",
            "egr_pkts": "1",
            "alias": "DummyAlias",
            "contract_type": "",
            "type": "Consumer"
        }]
    })
]

dir = "get_to_epg_traffic"

try:
    os.mkdir(dir)
except OSError:
    print("Error")

for x in range(len(data)):

    with open("{}/{}_input.json".format(dir, val[x]), "w") as f:
        json.dump(data[x][0], f)

    with open("{}/{}_output.json".format(dir, val[x]), "w") as f:
        json.dump(data[x][1], f)

    # with open("{}/{}_ip.json".format(dir, val[x]), "w") as f:
    #     json.dump(data[x][4], f)

    # with open("{}/{}_input.json".format(direct[x], "empty"), "w") as f:
    #     json.dump(data[x][1][0], f)

    # with open("{}/{}_output.json".format(direct[x], "empty"), "w") as f:
    #     json.dump(data[x][1][1], f)

    print("(\"/plugin_server/data/{}/{}_input.json\",".format(dir, val[x]))
    print("\"/plugin_server/data/{}/{}_output.json\"),".format(dir, val[x]))
    # print("(\"/data/{}/empty_input.json\",".format(direct[x], direct[x]))
    # print("\"/data/{}/empty_output.json\")".format(direct[x], direct[x]))
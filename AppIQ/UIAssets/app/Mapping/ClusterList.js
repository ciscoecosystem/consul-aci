import React from 'react'
import SearchBar from './SearchBar.js'
import './style.css'


class ClusterList extends React.Component {
    constructor(props) {
        super(props);
        if (props.selectedItem != null) {
            // console.log(props.selectedItem);
        }
        this.searchValueChanged = this.searchValueChanged.bind(this);
        this.filterList = this.filterList.bind(this);
    }

    /**
    * @param {HTMLObject} e
    */
    searchValueChanged(e) {
        this.forceUpdate();
    }

    /**
    * Filter the list acc to the value in search bar
    * @return {list} filtered list
    */
    filterList() {
        if (this.inputSource == undefined) {
            this.searchValue = "";
        }
        else {
            this.searchValue = this.inputSource.value;
        }

        /**
        * List of elements matching the search string
        */
        let filteredList = [];
        this.props.listData.forEach(item => {

            /**
             * <SUBTASK>
             * Show recommended domain first
             */
            let i = 0;
            let marker = false;
            for (i = 0; i < item.domains.length; i++) {
                if (item.domains[i].recommended) {
                    marker = true;
                    break;
                }
            }
            if (marker) {
                let recommendedDomain = item.domains[i];
                item.domains.splice(i, 1);
                item.domains = [recommendedDomain].concat(item.domains)
            }
            /** </SUBTASK> */

            if ('ipaddress' in item && item.ipaddress !== '') {
                if (item.ipaddress.indexOf(this.searchValue) > -1) {
                    filteredList.push(item);
                }
            } else {
                if (item.macaddress.indexOf(this.searchValue) > -1) {
                    filteredList.push(item);
                }                
            }
        });

        return filteredList;
    }

    render() {
        /**
        * Process props data into a list
        */
        let rawListRaw = this.props.listData;
        rawListRaw = this.filterList()

        let processedList = []

        /**
         * Generate the li elements of each ip-address
         */
        rawListRaw.forEach(ip => {
            let listOfDomains = [];
            listOfDomains = ip.domains.map(item => {
                let sourceToTarget = { "ipaddress": ip.ipaddress, "domainName": item.domainName, 'macaddress': ip.macaddress };
                let classes = (this.props.selectedItem != null && this.props.selectedItem.domainName == item.domainName && this.props.selectedItem.ipaddress == ip.ipaddress) ? "selected" : "";
                let recommendClass = (this.props.type == "source" && item.recommended != undefined && item.recommended == true) ? "recommended" : "not-recommended";
                let tooltip = item.domainName;
                let oldName = item.domainName;
                if (item.domainName.length > 30) {
                    oldName = item.domainName.slice(0, 30) + "...";
                }
                return (<li title={tooltip} key={item.domainName} onClick={this.props.onSelectionChanged} value={JSON.stringify(sourceToTarget)} className={classes}>
                    &nbsp;&nbsp;{oldName}
                    <span onClick={this.props.onSelectionChanged} value={JSON.stringify(sourceToTarget)} className={recommendClass}>
                        <svg class="svg-icont" viewBox="0 0 20 20">
                            <path d="M10.219,1.688c-4.471,0-8.094,3.623-8.094,8.094s3.623,8.094,8.094,8.094s8.094-3.623,8.094-8.094S14.689,1.688,10.219,1.688 M10.219,17.022c-3.994,0-7.242-3.247-7.242-7.241c0-3.994,3.248-7.242,7.242-7.242c3.994,0,7.241,3.248,7.241,7.242C17.46,13.775,14.213,17.022,10.219,17.022 M15.099,7.03c-0.167-0.167-0.438-0.167-0.604,0.002L9.062,12.48l-2.269-2.277c-0.166-0.167-0.437-0.167-0.603,0c-0.166,0.166-0.168,0.437-0.002,0.603l2.573,2.578c0.079,0.08,0.188,0.125,0.3,0.125s0.222-0.045,0.303-0.125l5.736-5.751C15.268,7.466,15.265,7.196,15.099,7.03"></path>
                        </svg>&nbsp;&nbsp;
                            </span>
                </li>
                )
            });

            let classes = "li-item";
            if (this.props.type == "source") {
                classes = (this.props.targetList.indexOf(ip.ipaddress !== ''? ip.ipaddress: ip.macaddress) > -1) ? "disabled li-item" : "li-item";
            }
            processedList.push(
                <li className={classes} key={ip.ipaddress !== ''? ip.ipaddress: ip.macaddress}>
                    <div className="ipaddress">
                        {ip.ipaddress !== ''? ip.ipaddress: ip.macaddress}
                    </div>
                    <div className="domain-list">
                        <ul>
                            {listOfDomains}
                        </ul>
                    </div>
                </li>
            )
        })



        const clusterType = (this.props.type == "source") ? "Source Endpoints" : "Target Endpoints";
        const isSourceRecommended = (this.props.type == "source") ? ' - Recommended' : "";

        let listElement = null;
        if(processedList.length == 0) {
            if(this.props.type == "source") {
                listElement = <center><br/><div className = "ul-out"><div className="no-element-found">No Endpoints found for the given Application in the given Tenant.</div></div></center>
            } else {
                listElement = <div className = "ul-out"></div>;
            }
        } else {
            listElement = <ul className="ul-out">
                    {processedList}
                </ul>
        }

        return (
            <div>
                <div className="cluster-header">{clusterType}</div>

                <SearchBar onChanged={this.searchValueChanged} inputRef={el => this.inputSource = el} />
                { isSourceRecommended ?
                <p>Displaying <b>{processedList.length}</b> out of {this.props.listData.length} clusters <div className={"recommended-t"}><svg class="svg-icont" viewBox="-2 -4 22 22">
                    <path d="M10.219,1.688c-4.471,0-8.094,3.623-8.094,8.094s3.623,8.094,8.094,8.094s8.094-3.623,8.094-8.094S14.689,1.688,10.219,1.688 M10.219,17.022c-3.994,0-7.242-3.247-7.242-7.241c0-3.994,3.248-7.242,7.242-7.242c3.994,0,7.241,3.248,7.241,7.242C17.46,13.775,14.213,17.022,10.219,17.022 M15.099,7.03c-0.167-0.167-0.438-0.167-0.604,0.002L9.062,12.48l-2.269-2.277c-0.166-0.167-0.437-0.167-0.603,0c-0.166,0.166-0.168,0.437-0.002,0.603l2.573,2.578c0.079,0.08,0.188,0.125,0.3,0.125s0.222-0.045,0.303-0.125l5.736-5.751C15.268,7.466,15.265,7.196,15.099,7.03"></path>
                </svg></div> {isSourceRecommended}</p>
                :
                <p>Displaying <b>{processedList.length}</b> out of {this.props.listData.length} clusters {isSourceRecommended}</p>
                }

                {listElement}

            </div>
        );
    }
}

export default ClusterList

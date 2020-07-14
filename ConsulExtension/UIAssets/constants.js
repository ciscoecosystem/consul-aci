/*
* for appcenter: ConsulExtensionforACI
*/
export const APPID = "ConsulExtensionforACI"; // this resembles App name

/*
* for appcenter: CiscoHashiCorp
* for normal: Cisco
*/
export const VENDORNAME = "CiscoHashiCorp"; 
export const PROFILE_NAME = "datacenterName";
export const INTERVAL_API_CALL = 30000; // in milliseconds

// export const QUERY_URL = "http://127.0.0.1:5000/graphql.json"; // for Local
export const QUERY_URL = document.location.origin + "/appcenter/"+VENDORNAME+"/"+APPID+"/graphql.json"; // for Production

export const DEV_TOKEN = "app_"+VENDORNAME+"_"+APPID+"_token";
export const URL_TOKEN = "app_"+VENDORNAME+"_"+APPID+"_urlToken";

// cookie handler
export function getCookieVal(offset) {
    var endstr = document.cookie.indexOf(";", offset);
    if (endstr == -1) {
        endstr = document.cookie.length;
    }
    return unescape(document.cookie.substring(offset, endstr));
}

export function getCookie(name) {
    var arg = name + "=";
    var alen = arg.length;
    var clen = document.cookie.length;
    var i = 0;
    var j = 0;
    while (i < clen) {
        j = i + alen;
        if (document.cookie.substring(i, j) == arg) {
            return getCookieVal(j);
        }
        i = document.cookie.indexOf(" ", i) + 1;
        if (i === 0) {
            break;
        }
    }
    return null;
}

export function getParamObject(location) {
    let urlToParse = location.search;
    let urlParams = {};
    urlToParse.replace(
        new RegExp("([^?=&]+)(=([^&]*))?", "g"),
        function ($0, $1, $2, $3) {
            urlParams[$1] = $3;
        });
    return urlParams
}

export function DC_DETAILS_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{DetailsFlattened(tn:"' + tn + '", datacenter: "' + datacenter + '"){details}}' }
}

export function TREE_VIEW_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{OperationalTree(tn:"' + tn + '", datacenter: "' + datacenter + '"){response}}' }
}

export function READ_DATACENTER_QUERY(tn){
    return { query: 'query{GetDatacenters(tn:"' +tn + '"){datacenters}}'
}
export function POST_TENANT_QUERY(tn) {
    return { query: 'query{PostTenant(tn:"' + tn + '"){tenant}}' }
}


// naming 
export const AGENTS = "Seed Agents";
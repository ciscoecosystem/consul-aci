export const PROFILE_NAME = "datacenterName";
export const INTERVAL_API_CALL = 30000; // in milliseconds

// export const QUERY_URL="http://127.0.0.1:5000/graphql.json"; // for Local
export const QUERY_URL = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json"; // for Production

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


export function DC_DETAILS_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{Details(tn:"' + tn + '", datacenter: "' + datacenter + '"){details}}' }
}

export function TREE_VIEW_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{OperationalTree(tn:"' + tn + '", datacenter: "' + datacenter + '"){response}}' }
}
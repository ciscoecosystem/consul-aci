export const PROFILE_NAME = "datacenterName";
export const INTERVAL_API_CALL = 30000; // in milliseconds

// export const QUERY_URL="http://127.0.0.1:5000/graphql.json"; // for Local
export const QUERY_URL = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json"; // for Production

export function DC_DETAILS_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{Details(tn:"' + tn + '", datacenter: "' + datacenter + '"){details}}' }
}

export function TREE_VIEW_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{OperationalTree(tn:"' + tn + '", datacenter: "' + datacenter + '"){response}}' }
}
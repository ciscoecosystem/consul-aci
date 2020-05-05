export const PROFILE_NAME = "datacenterName";
export const INTERVAL_API_CALL = 30000; // in milliseconds

export function DC_DETAILS_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{Details(tn:"' + tn + '", datacenter: "' + datacenter + '"){details}}' }
}

export function TREE_VIEW_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{OperationalTree(tn:"' + tn + '", datacenter: "' + datacenter + '"){response}}' }
}
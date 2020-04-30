export const PROFILE_NAME = "datacenterName";

export function DC_DETAILS_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{Details(tn:"' + tn + '", datacenter: "' + datacenter + '"){details}}' }
}

export function TREE_VIEW_QUERY_PAYLOAD(tn, datacenter) {
    return { query: 'query{OperationalTree(tn:"' + tn + '", datacenter: "' + datacenter + '"){response}}' }
}
export const PROFILE_NAME = "datacenterName";

export function DC_DETAILS_QUERY_PAYLOAD(tn) {
    return { query: 'query{Details(tn:"' + tn + '"){details}}' }
}

export function TREE_VIEW_QUERY_PAYLOAD(tn) {
    return { query: 'query{Run(tn:"' + tn + '"){response}}' }
}
// A fragment as an id (the table of contents, links into folds, the manual's drawer). A malformed one ("#%")
// is used as it is: decodeURIComponent would throw.
export const leadFragment = (hash) => { try { return decodeURIComponent(hash); } catch { return hash; } };

# utility functions
import pysolr


# config params
solr_url = "http://localhost:8983/solr/"
kw_collection = "clusterkw"
doc_collection = "abstracts"
row_cnt = 10
# limit clusters used in filter to 500 - linked to maxBooleanClauses param in Solr
max_clauses = 500


def fetch_group_query_results(search_term):
    """
    find and return clusters of documents that contain search_term
    clustered PubMed documents are indexed in Solr. search_term is used to get the cluster numbers, which are then used
    to filter documents to be returned.
    documents are returned in groups, with each group corresponding to a cluster
    :param search_term: keyword to be searched in Solr
    :return: list of documents that match the query filter in Solr index
    """
    # set default query if search_term is empty
    if search_term == '':
        search_term = '*:*'
        filter_req = False
    else:
        filter_req = True
    # first query clusterkw collection to get clusterNum
    complete_url = solr_url + kw_collection
    solr_client = pysolr.Solr(complete_url)
    # query params for first level query
    q_params = {'rows': 10000,
                'fl': "clusterNum"}
    res = solr_client.search(search_term, **q_params)
    # empty search queries are too broad and don't require a filter
    # add a filter only if the first query yielded any result
    if filter_req and int(res.hits) > 0:
        cluster_num_filter = " or ".join([str(i['clusterNum'][0]) for i in res.docs[:max_clauses]])
        cluster_num_filter = "clusterNum: " + cluster_num_filter
    else:
        cluster_num_filter = ''

    # query docs collections filtered by clusterNum - (variable names are re-used)
    complete_url = solr_url + doc_collection
    solr_client = pysolr.Solr(complete_url)
    # query params for second & final query
    q_params = {'fq': cluster_num_filter,
                'rows': row_cnt,
                'facet': 'on',
                'facet.field': 'clusterNum',
                'group': 'true',
                'group.field': 'clusterNum',
                'group.limit': 7}
    results = solr_client.search(search_term, **q_params)
    # clean up the results for display
    return _cleanup(results)


def fetch_simple_query_results(search_term, cluster_id, page_num):
    """
    find and return documents from a given cluster that match search_term
    :param search_term: keyword to be searched in Solr
    :param cluster_id: cluster to which the results must be limited to
    :param page_num: start of results page
    :return: list of documents(within a single cluster) that match the query filter in Solr index
    """
    # set default query if search_term is empty
    if search_term == '':
        search_term = '*:*'
    cluster_num_filter = 'clusterNum: ' + cluster_id
    # query docs collections filtered by clusterNum
    q_params = {'rows': row_cnt,
                'start': page_num,
                'fq': cluster_num_filter}
    complete_url = solr_url + doc_collection
    solr_client = pysolr.Solr(complete_url)
    results = solr_client.search(search_term, **q_params)
    return _cleanup(results)


def _cleanup(results):
    """
    cleanup input by removing non-alphanumeric characters
    :param results: raw result set
    :return: cleaned result set
    """
    for result in results:
        result['title'] = "".join(result['title']).replace("[", "")
        result['title'] = "".join(result['title']).replace("]", "")
    return results


def format_facets(facets):
    """
    extract facet fields and zip each field with its facet count
    :param facets: unformatted facet
    :return: zipped list facet fields and corresponding counts
    """
    facet_counts = facets['facet_fields']['clusterNum']
    return zip(facet_counts[::2], facet_counts[1::2])


def format_groups(groups):
    """
    format grouped query results
    :param groups: unformatted groups
    :return: extracted and formatted groups
    """
    # print(groups['clusterNum']['groups'])
    def sort_by_size(group):
        return group['doclist']['numFound']
    return sorted(groups['clusterNum']['groups'], key=sort_by_size, reverse=True)
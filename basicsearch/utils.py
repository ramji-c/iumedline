# utility functions
import pysolr
import os
from django.conf import settings

# config params
# TODO needs to be put in a separate file
solr_url = "http://localhost:8983/solr/"
kw_collection = "clusterkw"
doc_collection = "abstracts"
row_cnt = 200
max_cluster_cnt = 10000
# limit clusters used in filter to 500 - linked to maxBooleanClauses param in Solr
max_clauses = 500
stopwords = []
mesh_terms = []
mesh_file = os.path.join(settings.PROJECT_ROOT, '2017MeshTree.txt')
stopwords_file = os.path.join(settings.PROJECT_ROOT, 'stopwords.txt')


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

    # query params for first level query
    q_params = {'rows': max_cluster_cnt,
                'fl': "clusterNum"}
    res = _query_solr(solr_url, kw_collection, search_term, q_params)
    # empty search queries are too broad and don't require a filter
    # add a filter only if the first query yielded any result
    if filter_req and int(res.hits) > 0:
        cluster_num_filter = " or ".join([str(i['clusterNum']) for i in res.docs[:max_clauses]])
        cluster_num_filter = "clusterNum: " + cluster_num_filter
    else:
        cluster_num_filter = ''

    # query docs collections filtered by clusterNum - (variable names are re-used)
    # query params for second & final query
    q_params = {'fq': cluster_num_filter,
                'rows': row_cnt,
                'facet': 'on',
                'facet.field': 'clusterNum',
                'group': 'true',
                'group.field': 'clusterNum',
                'group.limit': 7}
    results = _query_solr(solr_url, doc_collection, search_term, q_params)
    # clean up the results for display
    return _cleanup(results)


def fetch_simple_query_results(search_term, cluster_id, page_num, num_items=row_cnt):
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
    q_params = {'rows': num_items,
                'start': (page_num * num_items),
                'fq': cluster_num_filter}
    return _cleanup(_query_solr(solr_url, doc_collection, search_term, q_params))


def fetch_cluster_keywords(search_term):
    """
    find and return keywords(centroids) of clusters that contain search_term
    :param search_term: keyword to be searched in Solr
    :return: sorted list of keywords that correspond to cluster centroids
    """
    # set default query if search_term is empty
    if search_term == '':
        search_term = '*:*'
    # query clusterkw collection
    q_params = {'rows': max_cluster_cnt}
    return _query_solr(solr_url, kw_collection, search_term, q_params)


def fetch_highlighted_results(search_term, cluster_id):
    """
    find documents that match query criteria and return highlighted portions of each document
    :param search_term: keyword to be searched in Solr
    :param cluster_id: cluster to which search results should be restricted
    :return: highlighted snippets of search results
    """
    # set default query if search_term is empty
    if search_term == '':
        search_term = '*:*'
    # query params
    q_params = {'fq': 'clusterNum: ' + str(cluster_id),
                'rows': row_cnt,
                'hl': 'true',
                'hl.fl': 'title',
                'hl.snippets': 2,
                'hl.method': 'unified',
                'hl.fragsize': 50}
    return _query_solr(solr_url, doc_collection, search_term, q_params)


def filter_keywords(keywords):
    """
    compute and return set intersection of keywords and titles; keywords and Mesh terms
    :param keywords: unfiltered set of cluster keywords
    :return: filtered set of keywords
    """
    kw_set = set()
    for kw in keywords[0].split(", ")[:100]:
        # if kw not in _load_stopwords():
        kw_set.add(kw)
    return kw_set


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


def _query_solr(url_, col, q, q_params):
    """
    helper function to query Solr
    :param url_: Solr instance URL
    :param col: collection to be queried
    :param q: query term
    :param q_params: query parameters (dict)
    :return: search results from Solr
    """
    complete_url = url_ + col
    solr_client = pysolr.Solr(url=complete_url)
    return solr_client.search(q, **q_params)


def _load_stopwords():
    # load stopwords from file if stopwords list is empty
    if len(stopwords) == 0:
        with open(stopwords_file) as file:
            line = file.readline()
            while line:
                stopwords.append(line.strip())
                line = file.readline()
    return stopwords


def _load_meshterms():
    # load flattened MeSH terms tree
    if len(mesh_terms) == 0:
        with open(mesh_file, encoding='utf-8') as file:
            line = file.readline()
            while line:
                mesh_terms.append(line.strip().split())
                line = file.readline()
    print(mesh_terms)
    return mesh_terms

from django.shortcuts import render
from .forms import SearchForm
from .utils import fetch_group_query_results, fetch_simple_query_results, fetch_cluster_keywords
from .utils import format_facets, format_groups


# index page
def index(request):
    """
    landing page with a search box
    :param request: incoming HTTP request
    :return: index page
    """
    return render(request, 'basicsearch/index.html')


# grouped search results page
def groupedresults(request):
    """
    clustered search results page for input query
    :param request: incoming HTTP request
    :return: grouped search results page
    """
    form = SearchForm(request.GET)
    # get the search terms
    search_term = request.GET.get('search_term')
    results = fetch_group_query_results(search_term)
    return render(request, 'basicsearch/grouped_results.html', {'form': form,
                                                                'results': results,
                                                                'facets': format_facets(results.facets),
                                                                'groups': format_groups(results.grouped),
                                                                'n_matches': results.grouped['clusterNum']['matches'],
                                                                'search_term': search_term,
                                                                'page_num': 0})


# detailed search results page
def detailedresults(request, cluster_id):
    """
    detailed results of a single cluster of documents
    :param request: incoming HTTP request
    :param cluster_id: cluster number to filter documents by
    :return: detailed search results page
    """
    form = SearchForm(request.GET)
    search_term = request.GET.get('search_term')
    page_num = int(request.GET.get('page_num'))
    results = fetch_simple_query_results(search_term=search_term,
                                         cluster_id=cluster_id,
                                         page_num=page_num)
    return render(request, 'basicsearch/detailed_results.html', {'form': form,
                                                                 'cluster_id': cluster_id,
                                                                 'results': results,
                                                                 'n_matches': results.hits,
                                                                 'permalink': "https://www.ncbi.nlm.nih.gov/pubmed/",
                                                                 'search_term': search_term,
                                                                 'page_num': page_num})


# keyword results page - alternate to grouped results
def keywordresults(request):
    """
    grouped results of cluster keywords for each cluster that matches input query
    :param request: incoming HTTP request
    :return: set of keywords for each cluster
    """
    form = SearchForm(request.GET)
    search_term = request.GET.get('search_term')
    results = fetch_cluster_keywords(search_term)
    return render(request, 'basicsearch/keyword_results.html', {'form': form,
                                                                'results': results,
                                                                'n_matches': results.hits,
                                                                'search_term': search_term,
                                                                'page_num': 0})
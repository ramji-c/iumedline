from django.shortcuts import render
from .forms import SearchForm
from .utils import fetch_group_query_results, fetch_simple_query_results
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
                                                                'search_term': search_term})


# detailed search results page
def detailedresults(request, cluster_id):
    """
    detailed results of a single cluster of documents
    :param request: incoming HTTP request
    :return: detailed search results page
    """
    form = SearchForm(request.GET)
    results = fetch_simple_query_results(search_term=request.GET.get('search_term'), cluster_id=cluster_id)
    return render(request, 'basicsearch/detailed_results.html', {'form': form,
                                                                 'cluster_id': cluster_id,
                                                                 'results': results,
                                                                 'n_matches': results.hits,
                                                                 'permalink': "https://www.ncbi.nlm.nih.gov/pubmed/"})

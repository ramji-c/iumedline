from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from .forms import SearchForm
from .utils import fetch_group_query_results, fetch_simple_query_results, fetch_cluster_keywords
from .utils import fetch_highlighted_results, filter_keywords
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
                                         page_num=page_num,
                                         num_items=10)
    return render(request, 'basicsearch/detailed_results.html', {'form': form,
                                                                 'cluster_id': cluster_id,
                                                                 'results': results,
                                                                 'n_matches': results.hits,
                                                                 'n_docs': len(results.docs),
                                                                 'limit': 10,
                                                                 'permalink': "https://www.ncbi.nlm.nih.gov/pubmed/",
                                                                 'search_term': search_term,
                                                                 'page_num': page_num})


# keyword results page - alternate to grouped results
def keywordresults(request):
    """
    grouped results of cluster keywords for each cluster that matches input query
    keywords are filtered - only the intersection of keywords and select titles are shown
    :param request: incoming HTTP request
    :return: set(filtered) of keywords for each cluster
    """
    results = []
    if request.is_ajax():
        print("Yas")
    form = SearchForm(request.GET)
    search_term = request.GET.get('search_term')
    clusters = fetch_cluster_keywords(search_term)
    for cluster in clusters:
        docs_ = fetch_simple_query_results(search_term, str(cluster['clusterNum']), 0, num_items=10)
        if docs_.hits > 0:
            results.append((str(cluster['clusterNum']),
                            filter_keywords(keywords=cluster['keywords']),
                            docs_,
                            docs_.hits))
    return render(request, 'basicsearch/keyword_results.html', {'form': form,
                                                                'results': sorted(results,
                                                                                  key=lambda x: x[3],
                                                                                  reverse=True),
                                                                'n_matches': clusters.hits,
                                                                'search_term': search_term,
                                                                'page_num': 0})


# highlighted search results page - alternate to grouped and keyword results page
def highlightedresults(request):
    """
    highlighted snippets of search results for each cluster that matches input query
    :param request: incoming HTTP request
    :return: highlighted results of snippets
    """
    form = SearchForm(request.GET)
    search_term = request.GET.get('search_term')
    results = []
    clusters = fetch_cluster_keywords(search_term)
    for cluster in clusters:
        results.append(fetch_highlighted_results(search_term, cluster['clusterNum']))
    return render(request, 'basicsearch/highlighted_results.html', {'form': form,
                                                                    'results': results,
                                                                    'n_matches': clusters.hits,
                                                                    'search_term': search_term,
                                                                    'page_num': 0})


@csrf_exempt
# view to remove keyword and add it to stopword list
def removekeyword(request):
    """
    get the POSTed keyword and add it to stopwords list
    :param request: incoming HTTP request
    :return: True if update was successful, False otherwise
    """
    if request.is_ajax():
        print(request.POST.get('keyword'))
        return HttpResponse(request.POST.get('keyword'))

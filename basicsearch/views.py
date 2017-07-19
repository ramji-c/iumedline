from django.shortcuts import render
from .forms import SearchForm
import pysolr

# config params
solr_url = "http://ec2-13-58-230-241.us-east-2.compute.amazonaws.com:8983/solr/pubmed/"
row_cnt = 20

# index page
def index(request):
    return render(request, 'basicsearch/index.html')


# search results page
def searchresults(request):
    form = SearchForm(request.GET)
    solr = pysolr.Solr(solr_url)
    # get the search terms
    search_term = request.GET.get('search_term')
    # set default query if search_term is empty
    if search_term == '':
        search_term = '*:*'
    results = solr.search(search_term, rows=row_cnt)
    num_pages = int(results.hits / row_cnt)
    return render(request, 'basicsearch/results.html', {'form': form,
                                                        'results': results,
                                                        'n_pages': range(num_pages)})

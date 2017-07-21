from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^search/$', views.groupedresults, name="groupedresults"),
    url(r'^search/cluster/(?P<cluster_id>\d+)$', views.detailedresults, name="detailedresults")
]
from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.main, name='main'),
    url(r'^$', views.log, name='log'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^full_clustering/(?P<Id>[a-zA-Z0-9]*)/$', views.full_clustering_one, name='full_clustering_one'),
    url(r'^fast_clustering/(?P<Id>[a-zA-Z0-9]*)/$', views.fast_clustering_one, name='fast_clustering_one'),
    url(r'^fast_clustering/$', views.archive_fast_clustering, name='archive_fast_clustering'),
    url(r'^full_clustering/$', views.archive_full_clustering, name='archive_full_clustering'),

    url(r'^fast_clustering/(?P<id_>[a-zA-Z0-9]*)/cluster/(?P<number>[0-9]*)$', views.fast_cluster_page, name='fast_cluster'),
    url(r'^full_clustering/(?P<id_>[a-zA-Z0-9]*)/cluster/(?P<number>[0-9]*)$', views.full_cluster_page, name='full_cluster'),
    url(r'^edit/(?P<full>[0-9]*)/(?P<id_>[a-zA-Z0-9]*)/cluster/(?P<number>[0-9]*)$', views.edit_news, name='edit'),
    url(r'^save/(?P<full>[0-9]*)/(?P<id_>[a-zA-Z0-9]*)/cluster/(?P<number>[0-9]*)$', views.save_news, name='save'),
    url(r'^publish/(?P<full>[0-9]*)/(?P<id_>[a-zA-Z0-9]*)/cluster/(?P<number>[0-9]*)$', views.publish, name='publish'),
    url(r'^update/(?P<full>[0-9]*)/(?P<id_>[a-zA-Z0-9]*)/cluster/(?P<number>[0-9]*)$', views.update_status, name='update_status'),
    url(r'^full_clustering_list/(?P<Id>[a-zA-Z0-9]*)/$', views.full_clustering_list, name='full_cluster_list'),
    url(r'^fast_clustering_list/(?P<Id>[a-zA-Z0-9]*)/$', views.fast_clustering_list, name='fast_cluster_list'),

    # url(r'^accounts/profile$', 'my_admin.prof', name='prof'),
    #url(r'', ),
]
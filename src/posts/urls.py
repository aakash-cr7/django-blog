from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', 'posts.views.list_post', name = "list_post"),
    url(r'^create/$', 'posts.views.create_post', name = "create_post"),
    url(r'^(?P<slug>[\w-]+)/delete/$', 'posts.views.delete_post', name = "delete_post"),
    url(r'^(?P<slug>[\w-]+)/edit/$', 'posts.views.update_post', name = "update"),
    url(r'^(?P<slug>[\w-]+)/$', 'posts.views.detail_post', name = "detail"),
]

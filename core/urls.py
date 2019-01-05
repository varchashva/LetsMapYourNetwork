from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<project_id>[a-z0-9A-Z]+)/action$', views.action, name='action'),
    url(r'^(?P<project_id>[a-z0-9A-Z]+)/refresh', views.refresh, name='refresh'),

]
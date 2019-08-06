from django.conf.urls import url, handler400, handler500
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<project_id>[a-z0-9A-Z]+)/action$', views.action, name='action'),
    url(r'^(?P<project_id>[a-z0-9A-Z]+)/refresh', views.refresh, name='refresh'),
    url(r'task_state', views.task_state, name='task_state'),
    url(r'create', views.create, name='create'),
    url(r'settings', views.settings, name='settings'),
    url(r'statistics', views.statistics, name='statistics'),
    url(r'activities', views.activities, name='activities'),
]

handler404 = views.handler404
handler500 = views.handler404
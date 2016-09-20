"""kaigi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from kaigi import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.home, name='home'),
    url(r'^auth/$', views.auth, name='auth'),
    url(r'^gettoken/$', views.gettoken, name='gettoken'),
    url(r'^getcached/$', views.get_cached_meetings, name='getcached'),
    url(r'^api/getcached/$', views.get_cached_meetings, name='getcached'),
    url(r'^events/$', views.events, name='events'),
    url(r'^events/(?P<meeting_id>\w+)/$', views.meeting, name='meeting'),
    url(r'^events/(?P<meeting_id>\w+)/chat/$', views.chat, name='chat'),
    url(r'^events/(?P<meeting_id>\w+)/rate/$', views.rate, name='rate'),
    url(r'^api/events/$', views.events, name='events'),
    url(r'^api/events/(?P<meeting_id>\w+)/$', views.meeting, name='meeting'),
    url(r'^api/events/(?P<meeting_id>\w+)/chat/$', views.chat, name='chat'),
    url(r'^api/events/(?P<meeting_id>\w+)/rate/$', views.rate, name='rate'),
    url(r'^meeting/(?P<meeting_id>\w+)/$', views.viewMeeting, name='viewMeeting'),
    url(r'^info/$', views.info, name='info'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    url(r'^reflection/$', views.reflection, name='reflection'),
    url(r'^api/reflection/$', views.reflection, name='reflection'),
    url(r'^names/$', views.names, name='names'),
    url(r'band/$', views.band, name='band'),
]

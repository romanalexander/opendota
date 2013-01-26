from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'dotastats.views.home', name='home'),
    url(r'^matches/$', 'dotastats.views.matches_overview', name='matches_overview'),
    url(r'^matches/(?P<match_id>\d+)/$', 'dotastats.views.matches_id', name='matches_id'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^steam/', include('django_openid_auth.urls')),
    url(r'^about/', 'dotastats.views.about', name='about'),
    url(r'^news/', 'dotastats.views.news', name='news'),
    url(r'^leagues/', 'dotastats.views.leagues', name='leagues'),
)

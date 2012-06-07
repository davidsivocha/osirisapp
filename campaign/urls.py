from django.conf.urls.defaults import *

urlpatterns = patterns('campaign.views',
    url(r'^$', 'campaign_list', name="campaign-list"),
    url(r'^add/$', 'campaign_add', name="campaign-add"),
    url(r'^(?P<object_id>\d+)/$', 'campaign_view', name="campaign-view"),
    url(r'^(?P<object_id>\d+)/edit/$', 'campaign_edit', name="campaign-edit"),

    url(r'^(?P<object_id>\d+)/stats/$', 'campaign_stats', name="campaign-stats"),
    url(r'^(?P<object_id>\d+)/weekstats/$', 'campaign_weekly_stats', name="campaign-week-stats"),
)
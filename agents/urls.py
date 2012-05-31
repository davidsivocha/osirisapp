from django.conf.urls.defaults import *

urlpatterns = patterns('agents.views',
    url(r'^$', 'agent_select', name="agent-select"),

    url(r'^(?P<agent>[-\w]+)/$', 'agent_page', name="agent-page"),
    url(r'^(?P<agent>[-\w]+)/(?P<year>\d{4})/$', 'agent_year_review', name="agent-year-review"),
    url(r'^(?P<agent>[-\w]+)/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'agent_month_review', name="agent-month-review"),
)
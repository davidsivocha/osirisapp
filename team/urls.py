from django.conf.urls.defaults import *

urlpatterns = patterns('team.views',
    url(r'^$', 'team_select', name="team-select"),

    url(r'^(?P<team>[-\w]+)/$', 'team_page', name="team-page"),
    url(r'^(?P<team>[-\w]+)/info/$', 'team_page_info', name="team-page-info"),
    url(r'^(?P<team>[-\w]+)/(?P<year>\d{4})/$', 'team_year_review', name="team-year-review"),
    url(r'^(?P<team>[-\w]+)/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'team_month_review', name="team-month-review"),
)
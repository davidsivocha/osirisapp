from django.conf.urls.defaults import *

urlpatterns = patterns('reports.views',
    url(r'^$', 'report_select', name="report-select"),

    url(r'^agent/$', 'report_agent_list', name='report-agent-list'),
    url(r'^agent/floorlist/$', 'report_agent_floor', name='report-agent-list-floor'),
    url(r'^agent/academylist/$', 'report_agent_academy', name='report-agent-list-academy'),
    url(r'^agent/(?P<agent>[-\w]+)/(?P<year>\d{4})/$', 'report_agent_stat_year', name="report-agent-year"),
    url(r'^agent/excel/(?P<agent>[-\w]+)/(?P<year>\d{4})/$', 'report_agent_stat_year', {'excel': 1}, name="report-agent-year-excel"),
    url(r'^agent/(?P<agent>[-\w]+)/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'report_agent_stat_month', name="report-agent-month"),
    url(r'^agent/excel/(?P<agent>[-\w]+)/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'report_agent_stat_month', {'excel': 1}, name="report-agent-month-excel"),

    url(r'^team/(?P<team>[-\w]+)/(?P<year>\d{4})/$', 'report_team_stat_year', name="report-team-year"),
    url(r'^team/excel/(?P<team>[-\w]+)/(?P<year>\d{4})/$', 'report_team_stat_year', {'excel': 1}, name="report-team-year-excel"),
    url(r'^team/(?P<team>[-\w]+)/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'report_team_stat_month', name="report-team-month"),
    url(r'^team/excel/(?P<team>[-\w]+)/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'report_team_stat_month', {'excel': 1}, name="report-team-month-excel"),
    url(r'^team/(?P<team>[-\w]+)/(?P<year>\d{4})/(?P<week>\d{2})/$', 'report_team_stat_week', name="report-team-week"),
    url(r'^team/excel/(?P<team>[-\w]+)/(?P<year>\d{4})/(?P<week>\d{2})/$', 'report_team_stat_week', {'excel': 1}, name="report-team-week-excel"),
    url(r'^team/(?P<team>[-\w]+)/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/$', 'report_team_stat_day', name="report-team-day"),

    url(r'^hours/(?P<type>[-\w]+)/(?P<startdate>\d{4}-\d{2}-\d{2}.*)/(?P<enddate>\d{4}-\d{2}-\d{2}.*)/$', 'report_hours', name="report-hours"),
)
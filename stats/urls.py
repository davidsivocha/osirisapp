from django.conf.urls.defaults import *

urlpatterns = patterns('stats.views',
    url(r'^$', 'stats_today', name="stats-today"),
    url(r'^week/$', 'stats_this_week', name="stats-today"),
    url(r'^month/$', 'stats_this_month', name="stats-today"),
    url(r'^year/$', 'stats_this_year', name="stats-today"),
    
    url(r'^(?P<year>\d{4})/$', 'stats_year', name="stats-year"),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'stats_month', name="stats-month"),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/$', 'stats_day', name="stats-day"),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/print/$', 'stats_day_print', name="stats-day-print"),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/print/excel/$', 'stats_day_print_excel', name="stats-day-print-excel"),
    url(r'^(?P<year>\d{4})/(?P<week>\d{2})/$', 'stats_week', name="stats-week"),

    url(r'^team/(?P<year>\d{4})/$', 'stats_team_year', name="stats-team-year"),
    url(r'^team/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'stats_team_month', name="stats-team-month"),
    url(r'^team/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/$', 'stats_team_day', name="stats-team-day"),
    url(r'^team/(?P<year>\d{4})/(?P<week>\d{2})/$', 'stats_team_week', name="stats-team-week"),

    url(r'^input/$', 'stats_input', name='stats-input'),
    url(r'^input/europe/(?P<country>[a-z]{2})/$', 'stats_input_europe', name='stats-input-europe'),
    url(r'^input/qapps/$', 'stats_input_qualifiedapps', name='stats-input-qualifiedapps'),
    url(r'^input/week/$', 'stats_input_weeklystats', name='stats-input-weeklystats'),

)
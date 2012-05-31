from django.conf.urls.defaults import *

urlpatterns = patterns('academy.views',
    #url(r'^$', 'academy_current_winners', name="academy-current-winners"),
    url(r'^$', 'academyboardtemp', name="academy-current-winners"),
    url(r'^(?P<year>\d{4})/$', 'academy_year_winners', name="academy-year-winners"),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'academy_month_winners', name="academy-month-winners"),
    url(r'^(?P<year>\d{4})/(?P<quarter>\d{1})/$', 'academy_quarter_winners', name="academy-quarter-winners"),

    #url(r'^leaderboard/$', 'academy_current_leaderboard', name="academy-current-leaderboard"),
    url(r'^leaderboard/$', 'academyleaderboardtemp', name="academy-current-leaderboard"),
    url(r'^leaderboard/(?P<month>[a-z]{3})/$', 'academyleaderboardtempmonth', name="academy-current-leaderboard"),
    url(r'^leaderboard/(?P<year>\d{4})/$', 'academy_year_leaderboard', name="academy-year-leaderboard"),
    url(r'^leaderboard/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'academy_month_leaderboard', name="academy-month-leaderboard"),
    url(r'^leaderboard/(?P<year>\d{4})/(?P<quarter>\d{1})/$', 'academy_quarter_leaderboard', name="academy-quarter-leaderboard"),
    
    url(r'^calendar/$', 'academy_calendar_select', name="academy-calendar"),
)
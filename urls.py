from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from django.views.generic.simple import direct_to_template
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_error'

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),

    url(r'^', include('core.urls')),
    url(r'^planner/', include('planner.urls')),
    url(r'^academy/', include('academy.urls')),
    url(r'^agent/', include('agents.urls')),
    url(r'^team/', include('team.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^stats/', include('stats.urls')),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'core/login.html'}),

    url(r'^about/$', direct_to_template, {
        'template': 'general/about.html'
    }),
)


urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.STATIC_ROOT}),
    )
# if we're in DEBUG mode, allow django to serve media
# This is considered inefficient and isn't secure.
from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.STATIC_ROOT}),
    )
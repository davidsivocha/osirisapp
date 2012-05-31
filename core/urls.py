from django.conf.urls.defaults import patterns, include, url
from django.views.generic import DetailView, ListView
from django.views.generic.simple import direct_to_template
from models import FrontPage

urlpatterns = patterns('core.views',
    url(r'^$', ListView.as_view(queryset=FrontPage.objects.filter(team=None).order_by('title'), context_object_name='frontpage', template_name='core/index.html')),
    url(r'^logout/$', 'logout_view', name='logout'),
    url(r'^user/(?P<username>.*)/$', 'user_view', name='userview'),
    url(r'^saul/$', 'saul_dashboard', name='saul-dashboard'),
)

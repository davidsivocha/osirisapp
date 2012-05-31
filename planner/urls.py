from django.conf.urls.defaults import *

# import our Ticket model in models.py
from models import Ticket

# create a dictionary (key-value array) which will be
# additional parameters we pass to the view functions below.
info = {
    'queryset': Ticket.objects.all().order_by('-created_on'),
}

urlpatterns = patterns('planner.views',
    url(r'^$', 'get_planner_list', name='ticket-list'),
    url(R'^(?P<object_id>\d+)/$', 'ticket_detail', name='ticket-detail'),
    url(R'^(?P<object_id>\d+)/edit/$', 'object_detail_edit', name='ticket-detail'),
    url(R'^add/$', 'object_detail_add', name='ticket-detail'),
)
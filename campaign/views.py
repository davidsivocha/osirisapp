# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from django.db.models import Avg, Max, Min, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, UserManager
from campaign.models import campaign
from campaign.forms import CampaignForm
from datetime import datetime, timedelta, time

@login_required
def campaign_list(request): #done
	if request.user.has_perm('agents.super'):
		thedate = datetime.today()
		runningcampaigns = Campaign.objects.exclude(enddate__lt=thedate).order_by('startdate')
		finishedcampaigns = Campaign.objects.exclude(enddate__gt=thedate).order_by('startdate')
		
		template = 'campaign/list.html'
		context = RequestContext(request, {'runningcampaigns':runningcampaigns, 'finishedcampaigns':finishedcampaigns})

		response = render_to_response(template, context)

		return response
	else:
		currentUrl = request.get_full_path()
		template = 'general/badpermissions.html'
		context = RequestContext(request, {'currenturl':currentUrl})

		response = render_to_response(template, context)

		return response

@login_required
def campaign_add(request): #done
	if request.user.has_perm('agents.super'):
		if request.method == 'POST':
			form = CampaignForm(request.POST)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect('/campaign/')
		else:
			form = CampaignForm()

			template = 'campaign/add.html'
			context = RequestContext(request, {'form':form})

			response = render_to_response(template, context)

			return response
	else:
		currentUrl = request.get_full_path()
		template = 'general/badpermissions.html'
		context = RequestContext(request, {'currenturl':currentUrl})

		response = render_to_response(template, context)

		return response

@login_required
def campaign_view(request, object_id): #done
	if request.user.has_perm('agents.super'):
		campaign = Campaign.objects.get(pk=object_id)
		template = 'campaign/view.html'
		context = RequestContext(request, {'campaign':campaign})

		response = render_to_response(template, context)

		return response
	else:
		currentUrl = request.get_full_path()
		template = 'general/badpermissions.html'
		context = RequestContext(request, {'currenturl':currentUrl})

		response = render_to_response(template, context)

		return response

@login_required
def campaign_edit(request, object_id): #done
	if request.user.has_perm('agents.super'):
		campaign = Campaign.objects.get(pk=object_id)
		if request.method == 'POST':
			form = CampaignForm(request.POST, instance=campaign)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect('/campaign/'+object_id)
		else:
			form = CampaignForm(instance=campaign)

			template = 'campaign/edit.html'
			context = RequestContext(request, {'form':form, 'object_id':object_id})

			response = render_to_response(template, context)

			return response
	else:
		currentUrl = request.get_full_path()
		template = 'general/badpermissions.html'
		context = RequestContext(request, {'currenturl':currentUrl})

		response = render_to_response(template, context)

		return response

@login_required
def campaign_stats(request): #done
	if request.user.has_perm('agents.super'):
		template = 'campaign/input.html'
		context = RequestContext(request, {})

		response = render_to_response(template, context)

		return response
	else:
		currentUrl = request.get_full_path()
		template = 'general/badpermissions.html'
		context = RequestContext(request, {'currenturl':currentUrl})

		response = render_to_response(template, context)

		return response

@login_required
def campaign_weekly_stats(request): #done
	if request.user.has_perm('agents.super'):
		template = 'campaign/input.html'
		context = RequestContext(request, {})

		response = render_to_response(template, context)

		return response
	else:
		currentUrl = request.get_full_path()
		template = 'general/badpermissions.html'
		context = RequestContext(request, {'currenturl':currentUrl})

		response = render_to_response(template, context)

		return response

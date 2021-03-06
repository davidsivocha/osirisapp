# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from django.db.models import Avg, Max, Min, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, UserManager
from campaign.models import Campaign, CampaignStats
from campaign.forms import CampaignForm
from datetime import datetime, timedelta, time

"""
The campaign list generates a list of currently running and finished campaigns
"""
@login_required
def campaign_list(request): #done
	if request.user.has_perm('agents.super'):
		thedate = datetime.today().date()
		#gets two lists of objects. one of the running campaigns and one of the finished campaigns, determined by the current date
		runningcampaigns = Campaign.objects.exclude(enddate__lte=thedate).order_by('startdate')
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

"""
This generates a form to add a new campaign and save it.
"""
@login_required
def campaign_add(request): #done
	if request.user.has_perm('agents.super'):
		if request.method == 'POST':
			form = CampaignForm(request.POST)
			if form.is_valid():
				form.save() #saves the returned campaign add form
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

"""
This page generates a view for the campaign. Showing off the campaign stats
"""
@login_required
def campaign_view(request, object_id): #done
	if request.user.has_perm('agents.super'):
		campaign = Campaign.objects.get(pk=object_id)
		thedate = datetime.today().date()
		campaignstats = CampaignStats.objects.filter(campaign=campaign)
		records = campaignstats.count()

		# next section checks to see if there are any daily stats records and creates some stats based on the records found if any.

		if records == 0:
			cpa = "&infin;"
			appnum = 0
		else:
			aggregate = campaignstats.aggregate(Sum('numapps'))
			appnum = aggregate['numapps__sum']
			cpa = campaign.cost / appnum

		if campaign.enddate <= thedate:
			status = "Finished"
		else:
			status = "Running"

		template = 'campaign/view.html'
		context = RequestContext(request, {'campaign':campaign, 'status':status, 'cpa':cpa, 'appnum':appnum})

		response = render_to_response(template, context)

		return response
	else:
		currentUrl = request.get_full_path()
		template = 'general/badpermissions.html'
		context = RequestContext(request, {'currenturl':currentUrl})

		response = render_to_response(template, context)

		return response

"""
This is used to edit any campaign and save the changes that you have made
"""
@login_required
def campaign_edit(request, object_id): #done
	if request.user.has_perm('agents.super'):
		campaign = Campaign.objects.get(pk=object_id) # gets the campaign idea that you want to edit
		if request.method == 'POST': 
			form = CampaignForm(request.POST, instance=campaign)  # if the request method is post, gets the form data from the campaign and updates it with the new data
			if form.is_valid():
				form.save() # saves the form
				return HttpResponseRedirect('/campaign/'+object_id) # redirects back to the object that was juse edited
		else:
			form = CampaignForm(instance=campaign) # passes the campaign into the form maker

			template = 'campaign/edit.html'
			context = RequestContext(request, {'form':form, 'object_id':object_id, 'campaign':campaign})

			response = render_to_response(template, context)

			return response
	else:
		currentUrl = request.get_full_path()
		template = 'general/badpermissions.html'
		context = RequestContext(request, {'currenturl':currentUrl})

		response = render_to_response(template, context)

		return response

"""
This is used to manage and add campaign stats
TODO: add the campaign stats forms and form logic.
"""
@login_required
def campaign_stats(request, object_id): #done
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

"""
This is used to manage and add campaign stats
TODO: add the campaign stats forms and form logic.
"""
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

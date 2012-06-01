# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from agents.models import Agent
from stats.models import Dstats, QualifiedApps, WeeklyStats, MonthlyStats
from team.models import Teams, Targets
from datetime import datetime, timedelta, time
from django.db.models import Avg, Max, Min, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, UserManager
from collections import OrderedDict
from extras.views import month_display, month_number
from django.forms.formsets import formset_factory
from stats.forms import DstatsInput, DstatsGlobal, QAppsInput, WstatsInput, DstatsGlobalInternal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Group, Permission

def daily_stats(year, month, day): #done
	var = [year, month_number(month), day]
	date = '-'.join(var)
	dstats = Dstats.objects.filter(date=date).filter(agent__agenttype=0).exclude(team__teamtype=5).exclude(team__teamtype=4).order_by('team')
	return dstats

def weekly_stats(year, week): #done
	internal = Agent.objects.filter(agenttype=0).filter(haveleft=0).order_by('teamid')
	targets = Targets.objects.get(pk=1)
	tstats = []
	for agents in internal:
	    calltime = 0
	    totalcalltime = 0
	    callattempts = 0
	    totalcallattempts = 0
	    totalapps = 0
	    floortotalapps = 0
	    fteapps = 0
	    floorfteapps = 0
	    stats = Dstats.objects.filter(isoyear=year).filter(isoweek=week).filter(agent=agents).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
	    if stats['calltime__sum'] > 0 and stats['prodhours__sum'] > 0:
	        calltime = int(stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours))
	    if stats['callattempts__sum'] > 0 and stats['prodhours__sum'] > 0:
	        callattempts = int(stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours))
	    if stats['totalapps__sum'] > 0 and stats['prodhours__sum'] > 0:
	        totalapps = stats['totalapps__sum'] 
	    if stats['totalapps__sum'] > 0 and  stats['prodhours__sum'] > 0:
	        fteapps = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum'] + stats['innovhours__sum']) / targets.hours)
	    tstats.append([agents.name, calltime, callattempts, totalapps, fteapps])

	return tstats

def monthly_stats(year, month): #done
	internal = Agent.objects.filter(agenttype=0).filter(haveleft=0).order_by('teamid')
	targets = Targets.objects.get(pk=1)
	tstats = []
	for agents in internal:
	    calltime = 0
	    totalcalltime = 0
	    callattempts = 0
	    totalcallattempts = 0
	    totalapps = 0
	    floortotalapps = 0
	    fteapps = 0
	    floorfteapps = 0
	    stats = Dstats.objects.filter(isoyear=year).filter(month=month).filter(agent=agents).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
	    if stats['calltime__sum'] > 0 and stats['prodhours__sum'] > 0:
	        calltime = int(stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours))
	    if stats['callattempts__sum'] > 0 and stats['prodhours__sum'] > 0:
	        callattempts = int(stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours))
	    if stats['totalapps__sum'] > 0 and stats['prodhours__sum'] > 0:
	        totalapps = stats['totalapps__sum'] 
	    if stats['totalapps__sum'] > 0 and  stats['prodhours__sum'] > 0:
	        fteapps = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum'] + stats['innovhours__sum']) / targets.hours)
	    tstats.append([agents.name, calltime, callattempts, totalapps, fteapps])

	return tstats

def yearly_stats(year): #done
	internal = Agent.objects.filter(agenttype=0).filter(haveleft=0).order_by('teamid')
	targets = Targets.objects.get(pk=1)
	tstats = []
	for agents in internal:
	    calltime = 0
	    totalcalltime = 0
	    callattempts = 0
	    totalcallattempts = 0
	    totalapps = 0
	    floortotalapps = 0
	    fteapps = 0
	    floorfteapps = 0
	    stats = Dstats.objects.filter(isoyear=year).filter(agent=agents).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
	    if stats['calltime__sum'] > 0 and stats['prodhours__sum'] > 0:
	        calltime = int(stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours))
	    if stats['callattempts__sum'] > 0 and stats['prodhours__sum'] > 0:
	        callattempts = int(stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours))
	    if stats['totalapps__sum'] > 0 and stats['prodhours__sum'] > 0:
	        totalapps = stats['totalapps__sum'] 
	    if stats['totalapps__sum'] > 0 and  stats['prodhours__sum'] > 0:
	        fteapps = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum'] + stats['innovhours__sum']) / targets.hours)
	    tstats.append([agents.name, calltime, callattempts, totalapps, fteapps])

	return tstats
	
def team_daily_stats(year, month, day): #done
	var = [year, month_number(month), day]
	date = '-'.join(var)

	internal = Teams.objects.all()
	targets = Targets.objects.get(pk=1)

	fullstats = Dstats.objects.filter(date=date).filter(agent__agenttype=0)
	dstatstotals = fullstats.aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))

	tstats = []
	totals = []
	calltime = 0
	totalcalltime = 0
	callattempts = 0
	totalcallattempts = 0
	totalapps = 0
	floortotalapps = 0
	fteapps = 0
	floorfteapps = 0

	for teams in internal:
	    stats = fullstats.filter(team=teams).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
	    if stats['calltime__sum'] > 0 and stats['prodhours__sum'] > 0:
	        calltime = stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours)
	        calltime = int(calltime)
	    if stats['callattempts__sum'] > 0 and stats['prodhours__sum'] > 0:
	        callattempts = stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours)
	        callattemtps = int(callattempts)
	    if stats['totalapps__sum'] > 0:
	        totalapps = stats['totalapps__sum'] 
	    if stats['totalapps__sum'] > 0 and stats['prodhours__sum'] > 0:
	        fteapps = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum'] + stats['innovhours__sum']) / targets.hours)
	    tstats.append([teams.name, calltime, callattempts, totalapps, fteapps])
	    stats['calltime__sum'] = 0
	    stats['callattempts__sum'] = 0
	    stats['totalapps__sum'] = 0
	    stats['prodhours__sum'] = 0
	    stats['sickhours__sum'] = 0
	    calltime = 0
	    callattempts = 0
	    totalapps = 0
	    fteapps = 0

	if dstatstotals['calltime__sum'] > 0:
	    totalcalltime = int(dstatstotals['calltime__sum'] / (dstatstotals['prodhours__sum'] / targets.hours))
	else:
		totalcalltime = 0

	if dstatstotals['callattempts__sum'] > 0:
	    totalcallattempts = int(dstatstotals['callattempts__sum'] / (dstatstotals['prodhours__sum'] / targets.hours))
	else:
		totalcallattempts = 0

	if dstatstotals['totalapps__sum'] > 0:
	    floortotalapps = dstatstotals['totalapps__sum'] 
	    floorfteapps = dstatstotals['totalapps__sum'] / ((dstatstotals['prodhours__sum'] + dstatstotals['sickhours__sum'] + dstatstotals['innovhours__sum']) / targets.hours)
	else:
		floorfteapps = 0
		floortotalapps = 0

	totals.append(totalcalltime) 
	totals.append(totalcallattempts)
	totals.append(floortotalapps)
	totals.append(floorfteapps)

	teamstats = {"tstats":tstats, "totals":totals}

	return teamstats

def team_weekly_stats(year, week): #done
	internal = Teams.objects.all()
	targets = Targets.objects.get(pk=1)

	fullstats = Dstats.objects.filter(isoweek=week).filter(isoyear=year).filter(agent__agenttype=0)
	dstatstotals = fullstats.aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))

	tstats = []
	totals = []
	calltime = 0
	totalcalltime = 0
	callattempts = 0
	totalcallattempts = 0
	totalapps = 0
	floortotalapps = 0
	fteapps = 0
	floorfteapps = 0
	
	for teams in internal:
	    stats = fullstats.filter(team=teams).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
	    if stats['calltime__sum'] > 0 and stats['prodhours__sum'] > 0:
	        calltime = stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours)
	        calltime = int(calltime)
	    if stats['callattempts__sum'] > 0 and stats['prodhours__sum'] > 0:
	        callattempts = stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours)
	        callattemtps = int(callattempts)
	    if stats['totalapps__sum'] > 0:
	        totalapps = stats['totalapps__sum'] 
	    if stats['totalapps__sum'] > 0 and stats['prodhours__sum'] > 0:
	        fteapps = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum'] + dstatstotals['innovhours__sum']) / targets.hours)
	    tstats.append([teams.name, calltime, callattempts, totalapps, fteapps])
	    stats['calltime__sum'] = 0
	    stats['callattempts__sum'] = 0
	    stats['totalapps__sum'] = 0
	    stats['prodhours__sum'] = 0
	    stats['sickhours__sum'] = 0
	    calltime = 0
	    callattempts = 0
	    totalapps = 0
	    fteapps = 0

	if dstatstotals['calltime__sum'] > 0 and dstatstotals['prodhours__sum'] > 0:
	    totalcalltime = int(dstatstotals['calltime__sum'] / (dstatstotals['prodhours__sum'] / targets.hours))
	else:
		totalcalltime = 0

	if dstatstotals['callattempts__sum'] > 0  and dstatstotals['prodhours__sum'] > 0:
	    totalcallattempts = int(dstatstotals['callattempts__sum'] / (dstatstotals['prodhours__sum'] / targets.hours))
	else:
		totalcallattempts = 0

	if dstatstotals['totalapps__sum'] > 0:
	    floortotalapps = dstatstotals['totalapps__sum'] 
	    floorfteapps = dstatstotals['totalapps__sum'] / ((dstatstotals['prodhours__sum'] + dstatstotals['sickhours__sum']+dstatstotals['innovhours__sum']) / targets.hours)
	else:
		floortotalapps = 0
		floorfteapps = 0

	totals.append(totalcalltime) 
	totals.append(totalcallattempts)
	totals.append(floortotalapps)
	totals.append(floorfteapps)

	teamstats = {"tstats":tstats, "totals":totals}

	return teamstats

def team_monthly_stats(year, month): #done
	internal = Teams.objects.all()
	targets = Targets.objects.get(pk=1)

	fullstats = Dstats.objects.filter(month=month).filter(isoyear=year).filter(agent__agenttype=0)
	dstatstotals = fullstats.aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))

	tstats = []
	totals = []
	calltime = 0
	totalcalltime = 0
	callattempts = 0
	totalcallattempts = 0
	totalapps = 0
	floortotalapps = 0
	fteapps = 0
	floorfteapps = 0
	
	for teams in internal:
	    stats = fullstats.filter(team=teams).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
	    if stats['calltime__sum'] > 0:
	        calltime = stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours)
	        calltime = int(calltime)
	    if stats['callattempts__sum'] > 0:
	        callattempts = stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours)
	        callattemtps = int(callattempts)
	    if stats['totalapps__sum'] > 0:
	        totalapps = stats['totalapps__sum'] 
	    if stats['totalapps__sum'] > 0:
	        fteapps = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum']+stats['innovhours__sum']) / targets.hours)
	    tstats.append([teams.name, calltime, callattempts, totalapps, fteapps])
	    stats['calltime__sum'] = 0
	    stats['callattempts__sum'] = 0
	    stats['totalapps__sum'] = 0
	    stats['prodhours__sum'] = 0
	    stats['sickhours__sum'] = 0
	    calltime = 0
	    callattempts = 0
	    totalapps = 0
	    fteapps = 0

	if dstatstotals['calltime__sum'] > 0:
	    totalcalltime = int(dstatstotals['calltime__sum'] / (dstatstotals['prodhours__sum'] / targets.hours))
	else:
		totalcalltime = 0

	if dstatstotals['callattempts__sum'] > 0:
	    totalcallattempts = int(dstatstotals['callattempts__sum'] / (dstatstotals['prodhours__sum'] / targets.hours))
	else:
		totalcallattempts = 0

	if dstatstotals['totalapps__sum'] > 0:
	    floortotalapps = dstatstotals['totalapps__sum'] 
	    floorfteapps = dstatstotals['totalapps__sum'] / ((dstatstotals['prodhours__sum'] + dstatstotals['sickhours__sum']+dstatstotals['innovhours__sum']) / targets.hours)
	else:
		floortotalapps = 0
		floorfteapps = 0

	totals.append(totalcalltime) 
	totals.append(totalcallattempts)
	totals.append(floortotalapps)
	totals.append(floorfteapps)

	teamstats = {"tstats":tstats, "totals":totals}

	return teamstats

def team_yearly_stats(year): #done
	internal = Teams.objects.all()
	targets = Targets.objects.get(pk=1)

	fullstats = Dstats.objects.filter(isoyear=year).filter(agent__agenttype=0)
	dstatstotals = fullstats.aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))

	tstats = []
	totals = []
	calltime = 0
	totalcalltime = 0
	callattempts = 0
	totalcallattempts = 0
	totalapps = 0
	floortotalapps = 0
	fteapps = 0
	floorfteapps = 0
	
	for teams in internal:
	    stats = fullstats.filter(team=teams).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
	    if stats['calltime__sum'] > 0:
	        calltime = stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours)
	        calltime = int(calltime)
	    if stats['callattempts__sum'] > 0:
	        callattempts = stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours)
	        callattemtps = int(callattempts)
	    if stats['totalapps__sum'] > 0:
	        totalapps = stats['totalapps__sum'] 
	    if stats['totalapps__sum'] > 0:
	        fteapps = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum'] + stats['innovhours__sum']) / targets.hours)
	    tstats.append([teams.name, calltime, callattempts, totalapps, fteapps])
	    stats['calltime__sum'] = 0
	    stats['callattempts__sum'] = 0
	    stats['totalapps__sum'] = 0
	    stats['prodhours__sum'] = 0
	    stats['sickhours__sum'] = 0
	    calltime = 0
	    callattempts = 0
	    totalapps = 0
	    fteapps = 0

	if dstatstotals['calltime__sum'] > 0:
	    totalcalltime = int(dstatstotals['calltime__sum'] / (dstatstotals['prodhours__sum'] / targets.hours))
	else:
		totalcalltime = 0

	if dstatstotals['callattempts__sum'] > 0:
	    totalcallattempts = int(dstatstotals['callattempts__sum'] / (dstatstotals['prodhours__sum'] / targets.hours))
	else:
		totalcallattempts = 0

	if dstatstotals['totalapps__sum'] > 0:
	    floortotalapps = dstatstotals['totalapps__sum'] 
	    floorfteapps = dstatstotals['totalapps__sum'] / ((dstatstotals['prodhours__sum'] + dstatstotals['sickhours__sum'] + dstatstotals['innovhours__sum']) / targets.hours)
	else:
		floortotalapps = 0
		floorfteapps = 0

	totals.append(totalcalltime) 
	totals.append(totalcallattempts)
	totals.append(floortotalapps)
	totals.append(floorfteapps)

	teamstats = {"tstats":tstats, "totals":totals}

	return teamstats

@login_required
def stats_today(request): #done
	thedate = datetime.today()-timedelta(days=1)
	if thedate.isoweekday() == 7:
		thedate = datetime.today()-timedelta(days=3)

	day = str(thedate.strftime("%d"))
	month = thedate.strftime("%b").lower()
	year = str(thedate.strftime("%Y"))
		
	stat = daily_stats(year, month, day)

	date = '/'.join([day, month_display(thedate.strftime("%b").lower()), year])
	title = "Agent Stats: " + date
	switchtype = "Team"

	highcalls = []
	highattempts = []
	highapps = []

	targets = Targets.objects.get(pk=1)

	highest = 0
	highest2 = 0
	highest3 = 0
	highcall = stat.order_by('-calltime')
	for Dstat in highcall:
		if Dstat.calltime >= highest:
			highest = Dstat.calltime
			highcalls.append([Dstat.agent, Dstat.calltime])
		elif Dstat.calltime >= highest2:
			highest2 = Dstat.calltime
			highcalls.append([Dstat.agent, Dstat.calltime])
		elif Dstat.calltime >= highest3:
			highest3 = Dstat.calltime
			highcalls.append([Dstat.agent, Dstat.calltime])
	        
	        
	highest = 0
	highest2 = 0
	highest3 = 0
	highattempt = stat.order_by('-callattempts')
	for Dstat in highattempt:
	    if Dstat.callattempts >= highest:
	        highest = Dstat.callattempts
	        highattempts.append([Dstat.agent, Dstat.callattempts])
	    elif Dstat.callattempts >= highest2:
	        highest2 = Dstat.callattempts
	        highattempts.append([Dstat.agent, Dstat.callattempts])
	    elif Dstat.callattempts >= highest3:
	        highest3 = Dstat.callattempts
	        highattempts.append([Dstat.agent, Dstat.callattempts])
	        
	highest = 0
	highest2 = 0
	highest3 = 0
	highapp = stat.order_by('-totalapps')
	for Dstat in highapp:
	    if Dstat.totalapps >= highest:
	        highest = Dstat.totalapps
	        highapps.append([Dstat.agent, Dstat.totalapps])
	    elif Dstat.totalapps >= highest2:
	        highest2 = Dstat.totalapps
	        highapps.append([Dstat.agent, Dstat.totalapps])
	    elif Dstat.totalapps >= highest3:
	        highest3 = Dstat.totalapps
	        highapps.append([Dstat.agent, Dstat.totalapps])


	switch = "/stats/team/"+str(year)+"/"+month+"/"+day
	printdate = "/stats/"+year+"/"+month+"/"+day+"/print"

	template = 'stats/daily.html'
	context = RequestContext(request, {'print':printdate, 'switch':switch, 'targets':targets, 'highapps':highapps, 'highattempts':highattempts, 'highcall':highcalls, 'title':title, 'stat':stat, 'switchtype':switchtype})

	response = render_to_response(template, context)

	return response

@login_required
def stats_this_week(request): #done
	thedate = datetime.today()-timedelta(days=1)
	if thedate.isoweekday() == 7:
		thedate = datetime.today()-timedelta(days=3)

	week = int(thedate.isocalendar()[1])
	year = thedate.strftime("%Y")
		
	stat = weekly_stats(year, week)

	title = "Agent Stats: Week " + str(week) + " - " + year 
	switch = "/stats/team/"+str(year)+"/"+str(week)
	switchtype = "Team"

	template = 'stats/stats.html'
	context = RequestContext(request, {'title':title, 'tstats':stat, 'switch':switch, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_this_month(request): #done
	thedate = datetime.today()-timedelta(days=1)
	if thedate.isoweekday() == 7:
		thedate = datetime.today()-timedelta(days=3)

	month = month_number(thedate.strftime("%b").lower())
	year = thedate.strftime("%Y")

	stat = monthly_stats(year, thedate.strftime("%b").lower())

	title = "Agent Stats: " + month_display(thedate.strftime("%b").lower()) + " " + year
	switch = "/stats/team/"+str(year)+"/"+thedate.strftime("%b").lower()
	switchtype = "Team"

	template = 'stats/stats.html'
	context = RequestContext(request, {'title':title, 'tstats':stat, 'switch':switch, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_this_year(request): #done
	thedate = datetime.today()-timedelta(days=1)
	if thedate.isoweekday() == 7:
		thedate = datetime.today()-timedelta(days=3)

	year = thedate.strftime("%Y")

	stat = yearly_stats(year)

	title = "Agent Stats: " + year
	switch = "/stats/team/"+str(year)
	switchtype = "Team"

	template = 'stats/stats.html'
	context = RequestContext(request, {'title':title, 'tstats':stat, 'switch':switch, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_day(request, year, month, day): #done
	stat = daily_stats(year, month, day)

	date = '/'.join([day, month_display(month), year])
	title = "Agent Stats: " + date
	switchtype = "Team"

	highcalls = []
	highattempts = []
	highapps = []

	targets = Targets.objects.get(pk=1)

	highest = 0
	highest2 = 0
	highest3 = 0
	highcall = stat.order_by('-calltime')
	for Dstat in highcall:
		if Dstat.calltime >= highest:
			highest = Dstat.calltime
			highcalls.append([Dstat.agent, Dstat.calltime])
		elif Dstat.calltime >= highest2:
			highest2 = Dstat.calltime
			highcalls.append([Dstat.agent, Dstat.calltime])
		elif Dstat.calltime >= highest3:
			highest3 = Dstat.calltime
			highcalls.append([Dstat.agent, Dstat.calltime])
	        
	        
	highest = 0
	highest2 = 0
	highest3 = 0
	highattempt = stat.order_by('-callattempts')
	for Dstat in highattempt:
	    if Dstat.callattempts >= highest:
	        highest = Dstat.callattempts
	        highattempts.append([Dstat.agent, Dstat.callattempts])
	    elif Dstat.callattempts >= highest2:
	        highest2 = Dstat.callattempts
	        highattempts.append([Dstat.agent, Dstat.callattempts])
	    elif Dstat.callattempts >= highest3:
	        highest3 = Dstat.callattempts
	        highattempts.append([Dstat.agent, Dstat.callattempts])
	        
	highest = 0
	highest2 = 0
	highest3 = 0
	highapp = stat.order_by('-totalapps')
	for Dstat in highapp:
	    if Dstat.totalapps >= highest:
	        highest = Dstat.totalapps
	        highapps.append([Dstat.agent, Dstat.totalapps])
	    elif Dstat.totalapps >= highest2:
	        highest2 = Dstat.totalapps
	        highapps.append([Dstat.agent, Dstat.totalapps])
	    elif Dstat.totalapps >= highest3:
	        highest3 = Dstat.totalapps
	        highapps.append([Dstat.agent, Dstat.totalapps])

	switch = "/stats/team/"+year+"/"+month+"/"+day
	printdate = "/stats/"+year+"/"+month+"/"+day+"/print"
	switchtype = "Team"

	template = 'stats/daily.html'
	context = RequestContext(request, {'print':printdate, 'switch':switch, 'targets':targets, 'highapps':highapps, 'highattempts':highattempts, 'highcall':highcalls, 'title':title, 'stat':stat, 'switchtype':switchtype})

	response = render_to_response(template, context)

	return response

@login_required
def stats_day_print(request, year, month, day): 
	var = [year, month_number(month), day]
	date = '-'.join(var)
	thedate = datetime.strptime(date, '%Y-%m-%d')

	statteams = []
	eachteam = OrderedDict()
	teamcolours = {}
	allteams = Teams.objects.all()
	allteams = allteams.exclude(teamtype=4).order_by('teamtype')
	allteams = allteams.exclude(teamtype=5).order_by('teamtype')
	x = 0
	month = thedate.strftime("%b").lower()
	year = thedate.strftime("%Y")
	for teams in allteams:
		teamstat = 0
		targets = Targets.objects.get(name=teams.targets)
		teamagents = Agent.objects.filter(teamid__pk=teams.pk).filter(agenttype=0)
		teamstats = Dstats.objects.filter(date=thedate).filter(team=teams).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'))
		teamstat = Dstats.objects.filter(month=month).filter(isoyear=year).filter(team=teams).aggregate(Sum('totalapps'))
		mtdapps = teamstat['totalapps__sum']
		teamcolours[teams.name] = teams.button
		for agent in teamagents:
			agentstat = Dstats.objects.filter(date=thedate).filter(agent=agent)
			for stat in agentstat:
				month = stat.month
				if stat.sickhours == targets.hours:
					sick = 1
				else:
					sick = 0
				if stat.holhours == targets.hours:
					hol = 1
				else:
					hol = 0   
				if stat.prodhours == 0 and stat.otherhours == 0 and stat.innovhours == 0 and stat.sickhours == 0 and stat.holhours == 0:
					ptcheck = 1
				else:
					ptcheck = 0
				monthstat = Dstats.objects.filter(month=month).filter(isoyear=year).filter(agent=agent).aggregate(Sum('totalapps'))
				statteams.append([agent.name, stat.calltime, stat.callattempts, stat.totalapps, monthstat['totalapps__sum'], "", sick, hol, ptcheck, stat.prodhours, stat.otherhours, stat.innovhours, targets.hours])
		monthstat = 0
		teamstats = Dstats.objects.filter(date=thedate).filter(team=teams).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
		fteapps = 0

		if teamstats['calltime__sum'] > 0 and teamstats['prodhours__sum'] > 0:
			calltime = teamstats['calltime__sum'] / (teamstats['prodhours__sum'] / targets.hours)
			calltime = int(calltime)
		else:
			calltime = 0
		if teamstats['callattempts__sum'] > 0 and teamstats['prodhours__sum'] > 0:
			callattempts = teamstats['callattempts__sum'] / (teamstats['prodhours__sum'] / targets.hours)
			callattempts = int(callattempts)
		else:
			callattempts = 0
		if teamstats['totalapps__sum'] > 0 and teamstats['prodhours__sum'] > 0:
			totalapps = teamstats['totalapps__sum'] 
		else:
			totalapps = 0
		if teamstats['totalapps__sum'] > 0 and teamstats['prodhours__sum'] > 0 and teamstats['sickhours__sum'] > 0:
			fteapps = teamstats['totalapps__sum'] / ((teamstats['prodhours__sum'] + teamstats['sickhours__sum'] + teamstats['innovhours__sum']) / targets.hours)
		else:
			fteapps = 0
		statteams.append([teams.name, calltime, callattempts, totalapps, mtdapps, fteapps, "", "", 0, "", 1, 0])
		calltime = 0
		callattempts = 0
		totalapps = 0
		fteapps = 0
		eachteam[teams.name] = statteams
		statteams=[]

	allteams = Teams.objects.filter(teamtype=5).order_by('teamtype')
	for teams in allteams:
		targets = Targets.objects.get(name=teams.targets)
		targets = Targets.objects.get(name=teams.targets)
		teamagents = Agent.objects.filter(teamid__pk=teams.pk).filter(agenttype=0)
		teamcolours[teams.name] = teams.button
		for agent in teamagents:
			agentstat = Dstats.objects.filter(date=thedate).filter(agent=agent)
			for stat in agentstat:
				month = stat.month
				if stat.sickhours == targets.hours:
					sick = 1
				else:
					sick = 0
				if stat.holhours == targets.hours:
					hol = 1
				else:
					hol = 0   
				if stat.prodhours == 0 and stat.otherhours == 0 and stat.innovhours == 0 and stat.sickhours == 0 and stat.holhours == 0:
					ptcheck = 1
				else:
					ptcheck = 0
				monthstat = Dstats.objects.filter(month=month).filter(agent=agent).aggregate(Sum('totalapps'))
				statteams.append([agent.name, stat.calltime, stat.callattempts, stat.totalapps, monthstat['totalapps__sum'], "", sick, hol, ptcheck, stat.prodhours, stat.otherhours, stat.innovhours, targets.hours])

		stats = Dstats.objects.filter(date=thedate).filter(team=teams).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
		monthstat = Dstats.objects.filter(month=month).filter(team=teams).aggregate(Sum('totalapps'))
		if stats['calltime__sum'] > 0:
			calltime = stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours)
			calltime = int(calltime)
		else:
			calltime = 0
		if stats['callattempts__sum'] > 0:
			callattempts = stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours)
			callattempts = int(callattempts)
		else:
			callattempts = 0
		if stats['totalapps__sum'] > 0:
			totalapps = stats['totalapps__sum'] 
		else: 
			totalapps = 0
		if stats['totalapps__sum'] > 0:
			fteapps = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum'] + stats['innovhours__sum']) / targets.hours)
		else:
			fteapps = 0
		statteams.append([teams.name, calltime, callattempts, totalapps, monthstat['totalapps__sum'], fteapps, "", "", 0, "", 1, 0])
		calltime = 0
		callattempts = 0
		totalapps = 0
		fteapps = 0
		eachteam[teams.name] = statteams
		statteams=[]

	internal = Teams.objects.filter(teamtype=1)

	tstats = []
	totals = []
	calltime = 0
	totalcalltime = 0
	callattempts = 0
	totalcallattempts = 0
	totalapps = 0
	floortotalapps = 0
	fteapps = 0
	floorfteapps = 0
	for teams in internal:
		stats = Dstats.objects.filter(date=thedate).filter(team=teams).aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
		if stats['calltime__sum'] > 0 and stats['prodhours__sum'] > 0:
			calltime = stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours)
			calltime = int(calltime)
		else:
			calltime = 0
		if stats['callattempts__sum'] > 0 and stats['prodhours__sum'] > 0:
			callattempts = stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours)
			callattempts = int(callattempts)
		else:
			callattempts = 0
		if stats['totalapps__sum'] > 0:
			totalapps = stats['totalapps__sum'] 
		else:
			totalapps = 0
		if stats['totalapps__sum'] > 0 and stats['prodhours__sum'] > 0 and stats['sickhours__sum'] >= 0:
			fteapps = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum'] + stats['innovhours__sum']) / targets.hours)
		else:
			fteapps = 0
		tstats.append([teams.name, calltime, callattempts, totalapps, fteapps])
		calltime = 0
		callattempts = 0
		totalapps = 0
		fteapps = 0

	dstatstotals = Dstats.objects.all()
	dstatstotals = dstatstotals.filter(date=thedate)
	dstatstotals = dstatstotals.filter(agent__agenttype=0)
	dstatstotals = dstatstotals.filter(team__teamtype=1)
	dstatstotals = dstatstotals.aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'), Sum('innovhours'))
	if dstatstotals['calltime__sum'] > 0:
		totalcalltime = dstatstotals['calltime__sum'] / (dstatstotals['prodhours__sum'] / targets.hours)
		totalcalltime = int(totalcalltime)
	else:
		totalcalltime = 0
	if dstatstotals['callattempts__sum'] > 0:
		totalcallattempts = dstatstotals['callattempts__sum'] / (dstatstotals['prodhours__sum'] / targets.hours)
		totalcallattempts = int(totalcallattempts)
	else:
		totalcallattempts = 0
	if dstatstotals['totalapps__sum'] > 0:
		floortotalapps = dstatstotals['totalapps__sum'] 
	else:
		floortotalapps = 0
	if dstatstotals['totalapps__sum'] > 0:
		floorfteapps = dstatstotals['totalapps__sum'] / ((dstatstotals['prodhours__sum'] + dstatstotals['sickhours__sum'] + dstatstotals['innovhours__sum']) / targets.hours)
	else:
		floorfteapps = 0
	totals.append(totalcalltime) 
	totals.append(totalcallattempts)
	totals.append(floortotalapps)
	totals.append(floorfteapps)

	highcalls = []
	highattempts = []
	highapps = []
	highest = 0
	highest2 = 0
	highest3= 0
	x = 0
	dstats = Dstats.objects.filter(date=date).filter(agent__agenttype=0).exclude(team__teamtype=5).order_by('team')
	highcall = dstats.exclude(team__teamtype=5).order_by('-calltime')
	for Dstat in highcall:
		if Dstat.calltime >= highest:
			highest = Dstat.calltime
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			highcalls.append([Dstat.agent, Dstat.calltime, flag])
			x +=1
		elif Dstat.calltime >= highest2:
			highest2 = Dstat.calltime
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			highcalls.append([Dstat.agent, Dstat.calltime, flag])
			x +=1
		elif Dstat.calltime >= highest3:
			highest3 = Dstat.calltime
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			highcalls.append([Dstat.agent, Dstat.calltime, flag])
			x +=1
	        
	highest = 0
	highest2 = 0
	highest3 = 0
	x = 0
	highattempt = dstats.exclude(team__teamtype=5).order_by('-callattempts')
	for Dstat in highattempt:
		if Dstat.callattempts >= highest:
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			highest = Dstat.callattempts
			highattempts.append([Dstat.agent, Dstat.callattempts, flag])
			x +=1
		elif Dstat.callattempts >= highest2:
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			highest2 = Dstat.callattempts
			highattempts.append([Dstat.agent, Dstat.callattempts, flag])
			x +=1
		elif Dstat.callattempts >= highest3:
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			highest3 = Dstat.callattempts
			highattempts.append([Dstat.agent, Dstat.callattempts, flag])
			x +=1
	        
	highest = 0
	highest2 = 0
	highest3 = 0
	x = 0
	highapp = dstats.exclude(team__teamtype=5).order_by('-totalapps')
	for Dstat in highapp:
		if Dstat.totalapps >= highest:
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			highest = Dstat.totalapps
			highapps.append([Dstat.agent, Dstat.totalapps, flag])
			x +=1
		elif Dstat.totalapps >= highest2:
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			highest2 = Dstat.totalapps
			highapps.append([Dstat.agent, Dstat.totalapps, flag])
			x +=1
		elif Dstat.totalapps >= highest3:
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			highest3 = Dstat.totalapps
			highapps.append([Dstat.agent, Dstat.totalapps, flag])
			x +=1
	''''''''''''''''''''''''''''''''''''''''''''''''
	' Belgium Stats                                             '
	''''''''''''''''''''''''''''''''''''''''''''''''
	bhighcalls = []
	bhighattempts = []
	bhighapps = []
	bhighest = 0
	x = 0
	bdstats = Dstats.objects.filter(team__teamtype=5).filter(date=date).filter(agent__agenttype=0).order_by('team')
	bhighcall = bdstats.order_by('-calltime')
	for Dstat in bhighcall:
		if Dstat.calltime >= bhighest:
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			bhighest = Dstat.calltime
			bhighcalls.append([Dstat.agent, Dstat.calltime])
			highcalls.append([Dstat.agent, Dstat.calltime, flag])
			x +=1
	        
	bhighest = 0
	x = 0
	bhighattempt = bdstats.order_by('-callattempts')
	for Dstat in bhighattempt:
		if Dstat.callattempts >= bhighest:
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			bhighest = Dstat.callattempts
			bhighattempts.append([Dstat.agent, Dstat.callattempts])
			highattempts.append([Dstat.agent, Dstat.callattempts, flag])
			x +=1
	        
	bhighest = 0
	x = 0
	bhighapp = bdstats.order_by('-totalapps')
	for Dstat in bhighapp:
		if Dstat.totalapps >= bhighest:
			agent = Agent.objects.get(name=Dstat.agent)
			team = Teams.objects.get(name=agent.teamid)
			flag = team.country
			bhighest = Dstat.totalapps
			bhighapps.append([Dstat.agent, Dstat.totalapps])
			highapps.append([Dstat.agent, Dstat.totalapps, flag])

			x +=1

	def sort_inner(inner):
		"""
		inner is each inner list in the list of lists to be sorted
		(here item at index 1 of each inner list is to be sorted)
		"""
		return inner[1]

	highapps.sort(key=sort_inner, reverse=True)
	highcalls.sort(key=sort_inner, reverse=True)
	highattempts.sort(key=sort_inner, reverse=True)

	template = 'osiris/reports/printstats.html'
	context = RequestContext(request, {'colour':teamcolours, 'targets':targets, 'dtotals': dstatstotals, 'bhighapps':bhighapps, 'bhighattempts':bhighattempts, 'bhighcall':bhighcalls, 'highapps':highapps, 'highattempts':highattempts, 'highcall':highcalls, 'eachteam':eachteam ,'statteams':statteams, 'tstats':tstats, 'thedate':thedate, 'totals':totals})

	response = render_to_response(template, context)

	return response

@login_required
def stats_day_print_excel(request, year, month, day): 
	stat = daily_stats(year, month, day)

	template = ''
	context = RequestContext(request, {})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_year(request, year): #done
	stat = yearly_stats(year)

	title = "Agent Stats: " + year
	switch = "/stats/team/"+year
	switchtype = "Team"

	template = 'stats/stats.html'
	context = RequestContext(request, {'switch':switch, 'title':title, 'tstats':stat, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_month(request, year, month): #done
	stat = monthly_stats(year, month)

	title = "Agent Stats: " + month_display(month) + " " + year
	switch = "/stats/team/"+year+"/"+month
	switchtype = "Team"

	template = 'stats/stats.html'
	context = RequestContext(request, {'title':title, 'tstats':stat, 'switch':switch, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_week(request, year, week): #done
	stat = weekly_stats(year, week)

	title = "Agent Stats: Week " + week + " - " + year 
	switch = "/stats/team/"+year+"/"+week
	switchtype = "Team"

	template = 'stats/stats.html'
	context = RequestContext(request, {'title':title, 'tstats':stat, 'switch':switch, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_team_year(request, year): #done
	stats = team_yearly_stats(year)

	title = "Team Stats: " + year
	switch = "/stats/"+year
	switchtype = "Agent"

	template = 'stats/stats.html'
	context = RequestContext(request, {'switch':switch, 'tstats':stats['tstats'], 'totals':stats['totals'], 'title':title, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_team_month(request, year, month): #done
	stats = team_monthly_stats(year, month)

	title = "Team Stats: " + month_display(month) + " " + year
	switch = "/stats/"+year+"/"+month
	switchtype = "Agent"

	template = 'stats/stats.html'
	context = RequestContext(request, {'tstats':stats['tstats'], 'totals':stats['totals'], 'title':title, 'switch':switch, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_team_day(request, year, month, day): #done
	stats = team_daily_stats(year, month, day)

	date = '/'.join([day, month_display(month), year])
	title = "Team Stats: " + date
	switch = "/stats/"+year+"/"+month+"/"+day
	switchtype = "Agent"

	template = 'stats/stats.html'
	context = RequestContext(request, {'tstats':stats['tstats'], 'totals':stats['totals'], 'title':title, 'switch':switch, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_team_week(request, year, week): #done
	stats = team_weekly_stats(year, week)

	title = "Team Stats: Week " + week + " - " + year
	switch = "/stats/"+year+"/"+week
	switchtype = "Agent"

	template = 'stats/stats.html'
	context = RequestContext(request, {'tstats':stats['tstats'], 'totals':stats['totals'], 'title':title, 'switch':switch, 'switchtype':switchtype})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def stats_input(request):
	user = request.user.get_profile()
	type = int(user.agenttype)
	if not request.user.has_perm('stats.add_dstats'):
		url = "/stats/" 
		return HttpResponseRedirect(url)

	dstatsformset = formset_factory(DstatsInput, extra=0)
	globalformset = formset_factory(DstatsGlobalInternal)

	today = datetime.today()-timedelta(days=1)
	thedate = datetime.date(today)

	agentlist = []
	agents = Agent.objects.filter(haveleft=0).filter(agenttype=0).exclude(teamid__teamtype=4).exclude(teamid__teamtype=5).order_by('teamid__name', 'name')

	for agent in agents:
		agentlist.append({'pk':agent.pk, 'agent':agent.name, 'brandedcardapps':0, 'productivehours':7.5, 'innovationhours':0, 'sickhours':0, 'holidayhours':0, 'otherhours':0})

	if request.method == 'POST':
		inputformset = dstatsformset(request.POST, request.FILES, prefix='input')
		globals = globalformset(request.POST, request.FILES, prefix='global')
		if inputformset.is_valid() and globals.is_valid():
			# do something with the formset.cleaned_data
			thedate = 0
			isomonth = ""
			isoyear = 0
			for form in globals:
				thedate = form.cleaned_data['date']
				isomonth = form.cleaned_data['isomonth']
				isoyear = form.cleaned_data['isoyear']
				noapps = form.cleaned_data['noapps']

			totalapps = 0
			for form in inputformset:
				totalapps += form.cleaned_data['brandedcardapps']

			if totalapps == 0 and noapps == False:
				inputform = inputformset
				globalform = globals

				noappsmsg = "There are no apps logged for this day! If this is actually the case please check the noapps button!"

				template = 'stats/input.html'
				context = RequestContext(request, {'input_formset':inputform, 'global_formset':globalform, 'noappsmsg':noappsmsg})

				response = render_to_response(template, context)

				return response

			for form in inputformset:
				pk = form.cleaned_data['pk']
				agent = Agent.objects.get(pk=pk)
				callin = form.cleaned_data['callin']
				callout = form.cleaned_data['callout']
				callattempts = form.cleaned_data['callattempts']
				brandedcardapps = form.cleaned_data['brandedcardapps']
				productivehours = form.cleaned_data['productivehours']
				innovationhours = form.cleaned_data['innovationhours']
				otherhours = form.cleaned_data['otherhours']
				sickhours = form.cleaned_data['sickhours']
				holidayhours = form.cleaned_data['holidayhours']

				hours = 0
				minutes = 0
				calldigits = callin.split(':')
				hours = int(calldigits[0]) * 60
				minutes = int(calldigits[1])
				calltimemin = hours + minutes

				hours = 0
				minutes = 0
				calldigits = callout.split(':')
				hours = int(calldigits[0]) * 60
				minutes = int(calldigits[1])
				calltimemin = calltimemin + hours + minutes

				dstat = Dstats(agent=agent,date=thedate,isoyear=isoyear,month=isomonth,calltime=calltimemin,callattempts=callattempts,prodhours=productivehours, innovhours=innovationhours,sickhours=sickhours,holhours=holidayhours,otherhours=otherhours,brandedapps=brandedcardapps)
				dstat.save()
			    
			pass
			url = "/stats/"
			return HttpResponseRedirect(url)
		else:
			inputform = inputformset
			globalform = globals
	else:
		inputform = dstatsformset(initial=agentlist, prefix='input')
		globalform = globalformset(prefix='global')

	template = 'stats/input.html'
	context = RequestContext(request, {'input_formset':inputform, 'global_formset':globalform})

	response = render_to_response(template, context)

	return response

@login_required
def stats_input_europe(request, country):
	user = request.user.get_profile()
	type = int(user.agenttype)
	if not request.user.has_perm('stats.add_dstats'):
		url = "/stats/" 
		return HttpResponseRedirect(url)

	dstatsformset = formset_factory(DstatsInput, extra=0)
	globalformset = formset_factory(DstatsGlobal)

	today = datetime.today()-timedelta(days=1)
	thedate = datetime.date(today)

	agentlist = []
	agents = Agent.objects.filter(haveleft=0).filter(agenttype=0).filter(teamid__country=country).order_by('teamid__name')
	for agent in agents:
		team = Teams.objects.get(name=agent.teamid)
		targets = Targets.objects.get(name=team.targets)
		if thedate.weekday == 4:
			agentlist.append({'pk':agent.pk, 'agent':agent.name, 'brandedcardapps':0, 'productivehours':7, 'innovationhours':0, 'sickhours':0, 'holidayhours':0, 'otherhours':0})
		else:
			agentlist.append({'pk':agent.pk, 'agent':agent.name, 'brandedcardapps':0, 'productivehours':targets.hours, 'innovationhours':0, 'sickhours':0, 'holidayhours':0, 'otherhours':0})
        
	if request.method == 'POST':
		inputformset = dstatsformset(request.POST, request.FILES, prefix='input')
		globals = globalformset(request.POST, request.FILES, prefix='global')
		if inputformset.is_valid() and globals.is_valid():
			# do something with the formset.cleaned_data
			thedate = 0
			isomonth = ""
			isoyear = 0
			for form in globals:
				thedate = form.cleaned_data['date']
				isomonth = form.cleaned_data['isomonth']
				isoyear = form.cleaned_data['isoyear']

			for form in inputformset:
				pk = form.cleaned_data['pk']
				agent = Agent.objects.get(pk=pk)
				callin = form.cleaned_data['callin']
				callout = form.cleaned_data['callout']
				callattempts = form.cleaned_data['callattempts']
				brandedcardapps = form.cleaned_data['brandedcardapps']
				productivehours = form.cleaned_data['productivehours']
				innovationhours = form.cleaned_data['innovationhours']
				otherhours = form.cleaned_data['otherhours']
				sickhours = form.cleaned_data['sickhours']
				holidayhours = form.cleaned_data['holidayhours']

				hours = 0
				minutes = 0
				calldigits = callin.split(':')
				hours = int(calldigits[0]) * 60
				minutes = int(calldigits[1])
				calltimemin = hours + minutes

				hours = 0
				minutes = 0
				calldigits = callout.split(':')
				hours = int(calldigits[0]) * 60
				minutes = int(calldigits[1])
				calltimemin = calltimemin + hours + minutes

				dstat = Dstats(agent=agent,date=thedate,isoyear=isoyear,month=isomonth,calltime=calltimemin,callattempts=callattempts,prodhours=productivehours, innovhours=innovationhours,sickhours=sickhours,holhours=holidayhours,otherhours=otherhours,brandedapps=brandedcardapps)
				dstat.save()
			    
			pass
			url = "/stats/" 
			return HttpResponseRedirect(url)
		else:
			inputform = inputformset
			globalform = globals
	else:
		inputform = dstatsformset(initial=agentlist, prefix='input')
		globalform = globalformset(prefix='global')

	template = 'stats/input.html'
	context = RequestContext(request, {'input_formset':inputform, 'global_formset':globalform})

	response = render_to_response(template, context)

	return response

@login_required
def stats_input_qualifiedapps(request):
	user = request.user.get_profile()
	type = int(user.agenttype)
	if not request.user.has_perm('stats.add_dstats'):
		url = "/stats/"
		return HttpResponseRedirect(url)

	qstatsformset = formset_factory(QAppsInput, extra=0)
	globalformset = formset_factory(DstatsGlobal)
	today = datetime.today()-timedelta(days=1)
	thedate = datetime.date(today)
	agentlist = []
	agents = Agent.objects.filter(haveleft=0).filter(agenttype=0).exclude(teamid__teamtype=3).exclude(teamid__teamtype=4).order_by('name')
	for agent in agents:
	    agentlist.append({'pk':agent.pk, 'agent':agent.name, 'qapps':0})

	if request.method == 'POST':
		inputformset = qstatsformset(request.POST, request.FILES, prefix='input')
		globals = globalformset(request.POST, request.FILES, prefix='global')
		if inputformset.is_valid() and globals.is_valid():
			# do something with the formset.cleaned_data
			thedate = 0
			isomonth = ""
			isoyear = 0

			for form in globals:
				thedate = form.cleaned_data['date']
				isomonth = form.cleaned_data['isomonth']
				isoyear = form.cleaned_data['isoyear']
			    
			QualifiedApps.objects.filter(year=isoyear).filter(month=isomonth).delete()
			  
			for form in inputformset:
				pk = form.cleaned_data['pk']
				agent = Agent.objects.get(pk=pk)
				qapps = form.cleaned_data['qapps']

				qstat = QualifiedApps(agent=agent,year=isoyear,month=isomonth,qualifiedapps=qapps)
				qstat.save()

			pass
			url = "/stats/" 
			return HttpResponseRedirect(url)
		else:
			inputform = inputformset
			globalform = globals
	else:
		inputform = qstatsformset(initial=agentlist, prefix='input')
		globalform = globalformset(prefix='global')

	template = 'stats/qapps.html'
	context = RequestContext(request, {'input_formset':inputform, 'global_formset':globalform})

	response = render_to_response(template, context)

	return response

@login_required
def stats_input_weeklystats(request):
	user = request.user.get_profile()
	type = int(user.agenttype)
	if not request.user.has_perm('stats.add_dstats'):
		url = "/stats/"
		return HttpResponseRedirect(url)

	wstatsformset = formset_factory(WstatsInput, extra=0)
	globalformset = formset_factory(DstatsGlobal)
	today = datetime.today()-timedelta(days=1)
	thedate = datetime.date(today)
	agentlist = []
	agents = Agent.objects.filter(haveleft=0).filter(agenttype=0).exclude(teamid__teamtype=3).exclude(teamid__teamtype=4).exclude(teamid__teamtype=5).order_by('name')
	for agent in agents:
	    agentlist.append({'pk':agent.pk, 'agent':agent.name})

	if request.method == 'POST':
		inputformset = wstatsformset(request.POST, request.FILES, prefix='input')
		globals = globalformset(request.POST, request.FILES, prefix='global')
		if inputformset.is_valid() and globals.is_valid():
			# do something with the formset.cleaned_data
			thedate = 0
			isomonth = ""
			isoyear = 0

			for form in globals:
				thedate = form.cleaned_data['date']
				isomonth = form.cleaned_data['isomonth']
				isoyear = form.cleaned_data['isoyear']
				isoweek = int(thedate.isocalendar()[1])

			for form in inputformset:
				pk = form.cleaned_data['pk']
				agent = Agent.objects.get(pk=pk)
				volume = form.cleaned_data['volume']
				drawcust = form.cleaned_data['drawcust']

				wstat = WeeklyStats(agent=agent,isoyear=isoyear,isomonth=isomonth, isoweek=isoweek,volume=volume, drawcust=drawcust)
				wstat.save()

				#mstat = MonthlyStats.objects.filter(agent=agent).filter(isomonth=isomonth)
				#for stat in mstat:
				#	stat.volume += volume
				#	stat.save()

			pass
			url = "/stats/" 
			return HttpResponseRedirect(url)
		else:
			inputform = inputformset
			globalform = globals
	else:
		inputform = wstatsformset(initial=agentlist, prefix='input')
		globalform = globalformset(prefix='global')

	template = 'stats/wstats.html'
	context = RequestContext(request, {'input_formset':inputform, 'global_formset':globalform})

	response = render_to_response(template, context)

	return response
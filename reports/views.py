# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from agents.models import Agent
from team.models import Teams, Targets, Supers
from stats.models import Dstats, QualifiedApps
from datetime import datetime, timedelta, time
from django.db.models import Avg, Max, Min, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, UserManager
from collections import OrderedDict
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from extras.views import month_display, month_number, humantime
from decimal import *

def report_select(request): #done
	agentlist = Agent.objects.filter(haveleft=0).filter(agenttype=0).order_by('teamid')
	teamlist = Teams.objects.all()

	template = 'reports/select.html'
	context = RequestContext(request, {'agentlist':agentlist, 'teamlist':teamlist})
    
	response = render_to_response(template, context)
    
	return response

def report_agent_list(request): #done
	title = "Full Agent List"
	agentlist = Agent.objects.filter(haveleft=0).filter(agenttype=0).order_by('teamid__name', 'name')

	template = 'reports/list.html'
	context = RequestContext(request, {'agentlist':agentlist, 'title':title})
    
	response = render_to_response(template, context)
    
	return response

def report_agent_floor(request): #done
	title = "Floor Agent List"
	agentlist = Agent.objects.filter(haveleft=0).filter(agenttype=0).exclude(teamid__teamtype=5).exclude(teamid__teamtype=4).order_by('teamid__name')

	template = 'reports/list.html'
	context = RequestContext(request, {'agentlist':agentlist, 'title':title})
    
	response = render_to_response(template, context)
    
	return response

def report_agent_academy(request): #done
	title = "Academy Agent List"
	agentlist = Agent.objects.filter(haveleft=0).exclude(teamid__teamtype=3).exclude(teamid__teamtype=5).exclude(teamid__teamtype=4).order_by('teamid__name', 'name')
	template = 'reports/list.html'
	context = RequestContext(request, {'agentlist':agentlist, 'title':title})
    
	response = render_to_response(template, context)
    
	return response 

def report_team_stat_year(request, team, year, excel=0): #done
	team = get_object_or_404(Teams, slug=team)
	title = team.name + " Performance: " + year
	agentlist = Agent.objects.filter(haveleft=0).filter(teamid=team).filter(agenttype=0)
	supervisor = Supers.objects.get(name=team.supervisor)
	stats = Dstats.objects.filter(team=team).filter(isoyear=year)
	targets = Targets.objects.get(name=team.targets)
	totals = stats.aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'), Sum('innovhours'))
	average = {}
	agentaverage = {}

	if totals['prodhours__sum'] > 0:
		average['calltime'] = int(totals['calltime__sum'] / (totals['prodhours__sum'] / targets.hours))
		average['callattempts'] = int(totals['callattempts__sum'] / (totals['prodhours__sum'] / targets.hours))
		average['apps'] = totals['totalapps__sum'] / ((totals['prodhours__sum'] + totals['sickhours__sum'] + totals['innovhours__sum'])/ targets.hours)

	appstable = []
	for staff in agentlist:
		qapps = QualifiedApps.objects.filter(year=year).filter(agent=staff).aggregate(Sum('qualifiedapps'))
		appstable.append([staff.name, qapps['qualifiedapps__sum']])

	for agent in agentlist:
		statslist = []
		agentstats = stats.filter(agent=agent).aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'), Sum('innovhours'))
		if agentstats['prodhours__sum'] > 0:
			calltime = int(agentstats['calltime__sum'] / (agentstats['prodhours__sum'] / targets.hours))
			callattempts = int(agentstats['callattempts__sum'] / (agentstats['prodhours__sum'] / targets.hours))
			apps = agentstats['totalapps__sum'] / ((agentstats['prodhours__sum'] + agentstats['sickhours__sum'] + agentstats['innovhours__sum'])/ targets.hours)
			totalapps = agentstats['totalapps__sum']
			statslist.append([calltime, callattempts, apps, totalapps])
		agentaverage[agent.name] = statslist

	if excel > 0:
		template = 'reports/excel/teamreport.html'
		context = RequestContext(request, {'qapps':appstable, 'title':title, 'team':team, 'agentlist':agentlist, 'super':supervisor, 'totals':totals, 'average':average, 'agentaverage':agentaverage})

		response = render_to_response(template, context)

		filename = "%sperformancereport%s.xls" % (team.slug, year)
		response['Content-Disposition'] = 'attachment; filename='+filename
		response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'

		return response

	else:
		url = "/reports/team/excel/"+team.slug+"/"+year
		template = 'reports/teamreport.html'
		context = RequestContext(request, {'url':url, 'qapps':appstable, 'title':title, 'team':team, 'agentlist':agentlist, 'super':supervisor, 'totals':totals, 'average':average, 'agentaverage':agentaverage})
	    
		response = render_to_response(template, context)
	    
		return response

def report_team_stat_month(request, team, year, month, excel=0): #done
	team = get_object_or_404(Teams, slug=team)
	title = team.name + " Performance: " +month_display(month) + " "+ year
	agentlist = Agent.objects.filter(haveleft=0).filter(teamid=team).filter(agenttype=0)
	supervisor = Supers.objects.get(name=team.supervisor)
	stats = Dstats.objects.filter(team=team).filter(isoyear=year).filter(month=month)
	targets = Targets.objects.get(name=team.targets)
	totals = stats.aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'), Sum('innovhours'))
	average = {}
	agentaverage = {}

	if totals['prodhours__sum'] > 0:
		average['calltime'] = int(totals['calltime__sum'] / (totals['prodhours__sum'] / targets.hours))
		average['callattempts'] = int(totals['callattempts__sum'] / (totals['prodhours__sum'] / targets.hours))
		average['apps'] = totals['totalapps__sum'] / ((totals['prodhours__sum'] + totals['sickhours__sum'] + totals['innovhours__sum'])/ targets.hours)

	appstable = []
	for staff in agentlist:
		qapps = QualifiedApps.objects.filter(year=year).filter(agent=staff).filter(month=month).aggregate(Sum('qualifiedapps'))
		appstable.append([staff.name, qapps['qualifiedapps__sum']])

	for agent in agentlist:
		statslist = []
		agentstats = stats.filter(agent=agent).aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'), Sum('innovhours'))
		if agentstats['prodhours__sum'] > 0:
			calltime = int(agentstats['calltime__sum'] / (agentstats['prodhours__sum'] / targets.hours))
			callattempts = int(agentstats['callattempts__sum'] / (agentstats['prodhours__sum'] / targets.hours))
			apps = agentstats['totalapps__sum'] / ((agentstats['prodhours__sum'] + agentstats['sickhours__sum'] + agentstats['innovhours__sum'])/ targets.hours)
			totalapps = agentstats['totalapps__sum']
			statslist.append([calltime, callattempts, apps, totalapps])
		agentaverage[agent.name] = statslist

	if excel > 0:
		template = 'reports/excel/teamreport.html'
		context = RequestContext(request, {'qapps':appstable, 'title':title, 'team':team, 'agentlist':agentlist, 'super':supervisor, 'totals':totals, 'average':average, 'agentaverage':agentaverage})

		response = render_to_response(template, context)

		filename = "%sperformancereport%s%s.xls" % (team.slug, year, month)
		response['Content-Disposition'] = 'attachment; filename='+filename
		response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'

		return response

	else:
		url = "/reports/team/excel/"+team.slug+"/"+year+"/"+month
		template = 'reports/teamreport.html'
		context = RequestContext(request, {'url':url, 'qapps':appstable, 'title':title, 'team':team, 'agentlist':agentlist, 'super':supervisor, 'totals':totals, 'average':average, 'agentaverage':agentaverage})
	    
		response = render_to_response(template, context)
	    
		return response

def report_agent_stat_year(request, agent, year, excel=0): #done
	agent = get_object_or_404(Agent, slug=agent)
	title = agent.name + " Performance: "+ year
	team = Teams.objects.get(name=agent.teamid)
	targets = Targets.objects.get(name=team.targets)
	stats = Dstats.objects.filter(agent=agent).filter(isoyear=year).order_by('date')
	totals = stats.aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'), Sum('innovhours'))
	average = {}

	if totals['prodhours__sum'] > 0:
		average['calltime'] = int(totals['calltime__sum'] / (totals['prodhours__sum'] / targets.hours))
		average['callattempts'] = int(totals['callattempts__sum'] / (totals['prodhours__sum'] / targets.hours))
		average['apps'] = totals['totalapps__sum'] / ((totals['prodhours__sum'] + totals['sickhours__sum'] + totals['innovhours__sum'])/ targets.hours)

	if excel > 0:
		template = 'reports/excel/agentreport.html'
		context = RequestContext(request, {'title':title, 'average':average, 'totals':totals, 'stats':stats})

		response = render_to_response(template, context)

		filename = "%sagentperformancereport%s.xls" % (agent.slug, year)
		response['Content-Disposition'] = 'attachment; filename='+filename
		response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'

		return response
	else:
		url = "/reports/agent/excel/"+agent.slug+"/"+year
		template = 'reports/agentreport.html'
		context = RequestContext(request, {'url':url, 'title':title, 'average':average, 'totals':totals, 'stats':stats})
    
		response = render_to_response(template, context)
    
		return response

def report_agent_stat_month(request, agent, year, month, excel=0): #done
	agent = get_object_or_404(Agent, slug=agent)
	title = agent.name + " Performance: " +month_display(month) + " "+ year
	team = Teams.objects.get(name=agent.teamid)
	targets = Targets.objects.get(name=team.targets)
	stats = Dstats.objects.filter(agent=agent).filter(isoyear=year).filter(month=month)
	totals = stats.aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'), Sum('innovhours'))
	average = {}

	if totals['prodhours__sum'] > 0:
		average['calltime'] = int(totals['calltime__sum'] / (totals['prodhours__sum'] / targets.hours))
		average['callattempts'] = int(totals['callattempts__sum'] / (totals['prodhours__sum'] / targets.hours))
		average['apps'] = totals['totalapps__sum'] / ((totals['prodhours__sum'] + totals['sickhours__sum'] + totals['innovhours__sum'])/ targets.hours)

	if excel > 0:
		template = 'reports/excel/agentreport.html'
		context = RequestContext(request, {'title':title, 'average':average, 'totals':totals, 'stats':stats})

		response = render_to_response(template, context)

		filename = "%sagentperformancereport%s%s.xls" % (agent.slug, year, month)
		response['Content-Disposition'] = 'attachment; filename='+filename
		response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'

		return response
	else:
		url = "/reports/agent/excel/"+agent.slug+"/"+year+"/"+month
		template = 'reports/agentreport.html'
		context = RequestContext(request, {'url':url, 'title':title, 'average':average, 'totals':totals, 'stats':stats})
	    
		response = render_to_response(template, context)
	    
		return response

def report_hours(request, type, startdate, enddate): #done
	if type == "other":
		title = "Other Hours Report: " + startdate + " to " + enddate
	elif type == "sick":
		title = "Sick Hours Report: " + startdate + " to " + enddate
	elif type == "hol":
		title = "Holiday Hours Report: " + startdate + " to " + enddate

	eachteam = OrderedDict()
	sickstats = []
	startdate = datetime.strptime(startdate, '%Y-%m-%d')
	enddate = datetime.strptime(enddate, '%Y-%m-%d')
	teams = Teams.objects.all()
		
	for team in teams:
		sickstats=[]
		agents = Agent.objects.filter(haveleft=0).filter(teamid=team)
		for agent in agents:
			if type == "other":
				dstats = Dstats.objects.filter(agent=agent).filter(date__range=(startdate, enddate)).filter(otherhours__gt =  0)
			elif type == "sick":
				dstats = Dstats.objects.filter(agent=agent).filter(date__range=(startdate, enddate)).filter(sickhours__gt =  0)
			elif type == "hol":
				dstats = Dstats.objects.filter(agent=agent).filter(date__range=(startdate, enddate)).filter(holhours__gt =  0)

			for dstat in dstats:
				if type == "other":
					sickstats.append([agent.name, dstat.date, dstat.otherhours])
				elif type == "sick":
					sickstats.append([agent.name, dstat.date, dstat.sickhours])
				elif type == "hol":
					sickstats.append([agent.name, dstat.date, dstat.holhours])

		eachteam[team.name] = sickstats
        


	template = 'reports/hours.html'
	context = RequestContext(request, {'title':title, 'startdate':startdate, 'enddate':enddate, 'eachteam':eachteam})
    
	response = render_to_response(template, context)
    
	return response

def report_team_stat_week(request, team, year, week, excel=0): 
	team = get_object_or_404(Teams, slug=team)
	agents = Agent.objects.filter(teamid=team).filter(haveleft=0).filter(agenttype=0)
	targets = Targets.objects.get(name=team.targets)
	title = team.name + " Week Breakdown: Week " + week + " - " + year

	teams = {}
	stats = Dstats.objects.filter(team=team).filter(isoyear=year).filter(isoweek=week)
	teamtotals = stats.aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'), Sum('innovhours'))
	totalhours = teamtotals['prodhours__sum']+teamtotals['sickhours__sum']+teamtotals['innovhours__sum']
	if totalhours > 0:
		teamcalltime = teamtotals['calltime__sum'] / (teamtotals['prodhours__sum']/targets.hours)
		teamcallattempts = teamtotals['callattempts__sum'] / (teamtotals['prodhours__sum']/targets.hours)
		teamfte = teamtotals['totalapps__sum'] / ((teamtotals['prodhours__sum'] + teamtotals['sickhours__sum'])/targets.hours)

	teams['Totals'] = (teamtotals['totalapps__sum'], humantime(teamtotals['calltime__sum']), teamtotals['callattempts__sum'])
	teams['Average'] = (teamfte, humantime(int(teamcalltime)), int(teamcallattempts))

	agentstatlist = {}
	agentaveragelist = {}
	for agent in agents:
		daylist = []
		agentstats = stats.filter(agent=agent)
		totals = agentstats.aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'), Sum('holhours'), Sum('innovhours'))
		for stat in agentstats:
			daylist.append([stat.date, stat.calltime, stat.callattempts, stat.totalapps, stat.prodhours, stat.sickhours, stat.holhours])

		totalhours = 0
		if totals['prodhours__sum'] >= 0 and totals['sickhours__sum'] >= 0 and totals['innovhours__sum'] >= 0:
			totalhours = totals['prodhours__sum'] + totals['sickhours__sum'] + totals['innovhours__sum']
			calltime = 0
			callattempts = 0
			fteapplications = 0
			applications = 0

		if totalhours > 0 and totals['prodhours__sum'] > 0:
			calltime = totals['calltime__sum'] / (totals['prodhours__sum']/targets.hours)
			callattempts = totals['callattempts__sum'] / (totals['prodhours__sum']/targets.hours)
			fteapplications = totals['totalapps__sum'] / ((totals['prodhours__sum'] + totals['sickhours__sum'] + totals['innovhours__sum'])/targets.hours)
		else:
			calltime = 0
			callattempts = 0
			fteapplications = 0
		applications = totals['totalapps__sum']

		daylist.append(["Totals", int(calltime), callattempts, applications, fteapplications, "", "", "FTE"])
		agentaveragelist[agent.name] = (humantime(int(calltime)), int(callattempts), applications, fteapplications)

		agentstatlist[agent.name] = daylist

	if excel > 0:
		template = 'reports/excel/breakdown.html'
		context = RequestContext(request, {"title":title, 'agentstats':agentstatlist, 'team':teams, 'agentaveragelist':agentaveragelist})

		response = render_to_response(template, context)

		filename = "%sbreakdown%s%s.xls" % (team.slug, year, week)
		response['Content-Disposition'] = 'attachment; filename='+filename
		response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'

		return response
	else:
		url = "/reports/team/excel/"+team.slug+"/"+year+"/"+week
		template = 'reports/breakdown.html'
		context = RequestContext(request, {'url':url, "title":title, 'agentstats':agentstatlist, 'team':teams, 'agentaveragelist':agentaveragelist})
    
		response = render_to_response(template, context)
    
		return response

def report_team_stat_day(request, team, year, month, day): 
	team = get_object_or_404(Teams, slug=team)
	agents = Agent.objects.filter(teamid=team).filter(haveleft=0)
	title = team.name + " Day Breakdown: " + day + "/" + month_display(month) + "/"+ year

	var = [year, month_number(month), day]
	date = '-'.join(var)

	stats = Dstats.objects.filter(team=team).filter(date=date)
	teamtotals = stats.aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'))


	template = 'reports/breakdown.html'
	context = RequestContext(request, {"title":title, 'team':team, })
    
	response = render_to_response(template, context)
    
	return response
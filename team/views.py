# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from agents.models import Agent
from team.models import Teams, Targets, Supers
from stats.models import Dstats, WeeklyStats, QualifiedApps
from core.models import FrontPage
from datetime import datetime, timedelta, time
from django.db.models import Avg, Max, Min, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, UserManager
from collections import OrderedDict
from extras.views import month_display, number_month, month_number

@login_required
def team_select(request):
	user = request.user.get_profile()
	type = int(user.agenttype)
	if not request.user.has_perm('agents.super'):
		team = Teams.objects.get(name=user.teamid)
		slug = team.slug
		url = "/team/" + slug + "/info"
		return HttpResponseRedirect(url)

	team_list = Teams.objects.all()
	chart_list = Teams.objects.filter(teamtype=1)
	thedate = datetime.today()
	isoweek = thedate.isocalendar()[1]
	isoyear = thedate.isocalendar()[0]

	chartweeks = []

	ctweeks = OrderedDict()
	caweeks = OrderedDict()
	appweeks = OrderedDict()

	ctlist = []
	calist = []
	apps = []

	if isoweek > 1 :    
		startweek = 1 
		while startweek < isoweek:
			for teams in chart_list:
				targets = Targets.objects.get(name=teams.targets)
				statsum = Dstats.objects.filter(isoyear=isoyear).filter(isoweek=startweek).filter(team=teams).aggregate(Sum('totalapps'), Sum('callattempts'), Sum('calltime'), Sum('prodhours'), Sum('sickhours'))
				if statsum['prodhours__sum'] > 0:
					calltimeavg = statsum['calltime__sum'] / (statsum['prodhours__sum'] / targets.hours)
					callattemptsavg = statsum['callattempts__sum'] / (statsum['prodhours__sum'] / targets.hours)
					appsavg = statsum['totalapps__sum']
				else:
					calltimeavg = 0
					callattemptsavg = 0
					appsavg = 0

				ctlist.append(calltimeavg)
				calist.append(callattemptsavg)
				apps.append(appsavg)
			    
			ctweeks[startweek] = ctlist
			caweeks[startweek] = calist
			appweeks[startweek] = apps
			ctlist = []
			calist = []
			apps = []
			statsum = []
			startweek = startweek + 1

	months = OrderedDict()
	months['jan'] = 'January'
	months['feb'] = 'February'
	months['mar'] = 'March'
	months['apr'] = 'April'
	months['may'] = 'May'
	months['jun'] = 'June'
	months['jul'] = 'July'
	months['aug'] = 'August'
	months['sep'] = 'September'
	months['oct'] = 'October'
	months['nov'] = 'November'
	months['dec'] = 'December'
    
	volweeks = OrderedDict()
	vollist = []
    
	for key,value in months.iteritems():
		for team in chart_list:
			volsum = WeeklyStats.objects.filter(team=team).filter(isomonth=key).filter(isoyear=isoyear).aggregate(Sum('volume'),)
			volsum = volsum['volume__sum']
			if not volsum >= 0:
				volsum = 0
			vollist.append(volsum)
			volsum = 0

		volweeks[value] = vollist
		vollist = []


	template = 'team/select.html'
	context = RequestContext(request, {'voltable':volweeks, 'team_list':team_list, 'catable':caweeks, 'cttable':ctweeks, 'appstable':appweeks, 'chart_list':chart_list})
    
	response = render_to_response(template, context)
    
	return response

@login_required	
def team_page(request, team):
	user = request.user.get_profile()
	type = int(user.agenttype)
	if not request.user.has_perm('agents.super'):
		team = Teams.objects.get(name=user.teamid)
		slug = team.slug
		url = "/team/" + slug + "/info"
		return HttpResponseRedirect(url)

	team = get_object_or_404(Teams, slug=team)
	agent  = Agent.objects.filter(teamid__pk=team.pk).filter(agenttype=0).filter(haveleft=0)
	super = Supers.objects.get(pk=team.supervisor_id)
	targets =  Targets.objects.get(name=team.targets)

	thedate = datetime.today()-timedelta(days=1)
	if thedate.isoweekday() == 7:
		thedate = datetime.today()-timedelta(days=3)

	week = int(thedate.isocalendar()[1])
	month = thedate.strftime("%b").lower()
	year = str(thedate.strftime("%Y"))
	date = {'week':week, 'month':month_display(month), 'year':year}
	todaymonth = int(month_number(month))
	todayyear = int(thedate.strftime("%Y"))
	todaymonth = todaymonth - 1
	if todaymonth == 0:
		todaymonth = 12
		todayyear = todayyear-1
	todayreadmonth = number_month(todaymonth)

	today = [todayyear, todaymonth, todayreadmonth]

	stats = Dstats.objects.filter(team=team.id).filter(isoyear=year)

	appstable = []
	for staff in agent:
		qapps = QualifiedApps.objects.filter(year=year).filter(agent=staff).filter(month=month).aggregate(Sum('qualifiedapps'))
		appstable.append([staff.name, qapps['qualifiedapps__sum']])

	weektodate = stats.filter(isoweek=week).aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'))
	monthtodate = stats.filter(month=month).aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'))
	yeartodate = stats.aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'))

	weekfte = {}
	monthfte = {}
	yearfte = {}

	if yeartodate['prodhours__sum'] > 0:
		yearfte['calltime'] = int(yeartodate['calltime__sum'] / (yeartodate['prodhours__sum'] / targets.hours))
		yearfte['totalcalltime'] = yeartodate['calltime__sum']
		yearfte['callattempts'] = int(yeartodate['callattempts__sum'] / (yeartodate['prodhours__sum'] / targets.hours))
		yearfte['totalcallattempts'] = yeartodate['callattempts__sum']
		yearfte['totalapps'] = yeartodate['totalapps__sum']
		yearfte['fteapps'] = yeartodate['totalapps__sum'] / ((yeartodate['prodhours__sum']+yeartodate['sickhours__sum']) / targets.hours)
	if monthtodate['prodhours__sum'] > 0:
		monthfte['calltime'] = int(monthtodate['calltime__sum'] / (monthtodate['prodhours__sum'] / targets.hours))
		monthfte['totalcalltime'] = monthtodate['calltime__sum']
		monthfte['callattempts'] = int(monthtodate['callattempts__sum'] / (monthtodate['prodhours__sum'] / targets.hours))
		monthfte['totalcallattempts'] = monthtodate['callattempts__sum']
		monthfte['totalapps'] = monthtodate['totalapps__sum']
		monthfte['fteapps'] = monthtodate['totalapps__sum'] / ((monthtodate['prodhours__sum']+monthtodate['sickhours__sum']) / targets.hours)
	if weektodate['prodhours__sum'] > 0:
		weekfte['calltime'] = int(weektodate['calltime__sum'] / (weektodate['prodhours__sum'] / targets.hours))
		weekfte['totalcalltime'] = weektodate['calltime__sum']
		weekfte['callattempts'] = int(weektodate['callattempts__sum'] / (weektodate['prodhours__sum'] / targets.hours))
		weekfte['totalcallattempts'] = weektodate['callattempts__sum']
		weekfte['totalapps'] = weektodate['totalapps__sum']
		weekfte['fteapps'] = weektodate['totalapps__sum'] / ((weektodate['prodhours__sum']+weektodate['sickhours__sum']) / targets.hours)

	agentweek = OrderedDict()
	agentmonth = OrderedDict()
	agentyear = OrderedDict()
	agentavgvol = OrderedDict()

	for each in agent:
		volmonth = thedate.strftime("%b").lower()
		yearstats = []
		monthstats = []
		weekstats = []
		volume = []

		volsum = WeeklyStats.objects.filter(agent=each).filter(isomonth=today[2]).filter(isoyear=today[0]).aggregate(Sum('volume'))
		if volsum['volume__sum'] is None:
			volsum = 0
		else:
			volsum = int(volsum['volume__sum'])
		if not volsum > 0:
			volsum = 0

		startdate = each.startdate
		volmonth = startdate.strftime("%b").lower()
		volmonth = int(month_number(volmonth))
		year = int(startdate.strftime("%Y"))

		starting = [year, volmonth]

		diff = (today[0] - starting[0])*12 + (today[1]-starting[1])
		diff = diff - 3

		if diff > 0 :
			volavg = int(volsum) / diff
		else: 
			volavg = int(volsum)

		agentavgvol[each.name] = volavg

		weektodate = stats.filter(agent=each).filter(isoweek=week).aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'))
		monthtodate = stats.filter(agent=each).filter(month=month).aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'))
		yeartodate = stats.filter(agent=each).aggregate(Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('prodhours'), Sum('sickhours'))

		if yeartodate['prodhours__sum'] > 0:
			yearstats.append(int(yeartodate['calltime__sum'] / (yeartodate['prodhours__sum'] / targets.hours)))
			yearstats.append(yeartodate['calltime__sum'])
			yearstats.append(int(yeartodate['callattempts__sum'] / (yeartodate['prodhours__sum'] / targets.hours)))
			yearstats.append(yeartodate['callattempts__sum'])
			yearstats.append(yeartodate['totalapps__sum'])
			yearstats.append(yeartodate['totalapps__sum'] / ((yeartodate['prodhours__sum']+yeartodate['sickhours__sum']) / targets.hours))
		if monthtodate['prodhours__sum'] > 0:
			monthstats.append(int(monthtodate['calltime__sum'] / (monthtodate['prodhours__sum'] / targets.hours)))
			monthstats.append(monthtodate['calltime__sum'])
			monthstats.append(int(monthtodate['callattempts__sum'] / (monthtodate['prodhours__sum'] / targets.hours)))
			monthstats.append(monthtodate['callattempts__sum'])
			monthstats.append(monthtodate['totalapps__sum'])
			monthstats.append(monthtodate['totalapps__sum'] / ((monthtodate['prodhours__sum']+monthtodate['sickhours__sum']) / targets.hours))
		if weektodate['prodhours__sum'] > 0:
			weekstats.append(int(weektodate['calltime__sum'] / (weektodate['prodhours__sum'] / targets.hours)))
			weekstats.append(weektodate['calltime__sum'])
			weekstats.append(int(weektodate['callattempts__sum'] / (weektodate['prodhours__sum'] / targets.hours)))
			weekstats.append(weektodate['callattempts__sum'])
			weekstats.append(weektodate['totalapps__sum'])
		if weektodate['totalapps__sum'] > 0 and (weektodate['prodhours__sum']+weektodate['sickhours__sum']) > 0:
			weekstats.append(weektodate['totalapps__sum'] / ((weektodate['prodhours__sum']+weektodate['sickhours__sum']) / targets.hours))

		agentweek[each.name] = weekstats
		agentmonth[each.name] = monthstats
		agentyear[each.name] = yearstats

	template = 'team/page.html'
	context = RequestContext(request, {'monthtodate':monthtodate, 'agentavgvol':agentavgvol, 'appstable':appstable, 'agentyear':agentyear, 'agentmonth':agentmonth, 'agentweek':agentweek, 'date':date, 'team':team, 'agent':agent, 'super':super, 'yearfte':yearfte, 'monthfte':monthfte, 'weekfte':weekfte})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def team_page_info(request, team):
	team = get_object_or_404(Teams, slug=team)
	pages = FrontPage.objects.filter(team__pk=team.pk).order_by('-updated_on')[:10]

	template = 'team/info.html'
	context = RequestContext(request, {'team':team, 'pages':pages})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def team_year_review(request, team, year):
	user = request.user.get_profile()
	type = int(user.agenttype)
	if not request.user.has_perm('agents.super'):
		team = Teams.objects.get(name=user.teamid)
		slug = team.slug
		url = "/team/" + slug + "/info"
		return HttpResponseRedirect(url)

	template = ''
	context = RequestContext(request, {})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def team_month_review(request, team, year, month):
	user = request.user.get_profile()
	type = int(user.agenttype)
	if not request.user.has_perm('agents.super'):
		team = Teams.objects.get(name=user.teamid)
		slug = team.slug
		url = "/team/" + slug + "/info"
		return HttpResponseRedirect(url)

	template = ''
	context = RequestContext(request, {})
    
	response = render_to_response(template, context)
    
	return response

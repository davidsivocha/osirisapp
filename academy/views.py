# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from datetime import datetime, timedelta, time
from stats.models import Dstats, QualifiedApps, WeeklyStats, MonthlyStats
from agents.models import Agent 
from team.models import Teams, Targets
from django.db.models import Avg, Max, Min, Count, Sum
from extras.views import month_display, month_number
from django.contrib.auth.decorators import login_required

def sort_inner(inner):
	"""
	inner is each inner list in the list of lists to be sorted
	(here item at index 1 of each inner list is to be sorted)
	"""
	return inner[1]

def academy_month(month, year):
	"""
	This function take the variables for the month and the year and generates the academy based on the
	given month and year.
	"""
	year = int(year)

	ctlist = []
	qalist = []
	volumelist = []
	drawlist = []
	growthlist = []
	academy = []
	winners = {}

	agents = Agent.objects.filter(teamid__teamtype=1).filter(haveleft=0).filter(agenttype=0)
	dstats = Dstats.objects.filter(month=month).filter(year=year)
	wstats = WeeklyStats.objects.filter(isomonth=month).filter(isoyear=year)
	qapps = QualifiedApps.objects.filter(month=month).filter(year=year)

	for agent in agents:
		team = Teams.objects.get(name=agent.teamid)
		targets = Targets.objects.get(name=team.targets)
		agentstats = dstats.filter(agent=agent).aggregate(Sum('calltime'), Sum('prodhours'))
		avgcalltime = int(agentstats['calltime__sum'] / (agentstats['prodhours__sum']/targets.hours))
		volume = wstats.filter(agent=agent).aggregate(Sum('volume'))
		qualified = qapps.filter(agent=agent).aggregate(Sum('qualifiedapps'))
		ctlist.append([agent.name, team.name, ])
		drawlist.append([agent.name, avgcalltime])
		volumelist.append([agent.name, volume['volume__sum']])
		qalist.append([agent.name, qualified['qualifiedapps__sum']])

	ctlist.sort(key=sort_inner, reverse=True)
	qalist.sort(key=sort_inner, reverse=True)
	volumelist.sort(key=sort_inner, reverse=True)

	score = 0
	previous = -1

	for each in ctlist:
		if each[1] == previous:
			score = score
		else:
			score += 1
			previous = each[1]
		winners[each[0]] = score

	score = 0
	previous = -1

	for each in volumelist:
		if each[1] == previous:
			score = score
		else:
			score += 1
			previous = each[1]
		winners[each[0]] += score

	score = 0
	previous = -1

	for each in qalist:
		if each[1] == previous:
			score = score
		else:
			score += 1
			previous = each[1]
		winners[each[0]] += score

	position = sorted(winners, key=winners.get)

	score = 0
	previous = 0
	temp = 0
	place = {}
	for pos in position:
		if winners[pos] == previous:
			score = score
			temp = temp + 1
			place[pos] = score
		else:
			score = score + temp + 1
			previous = winners[pos]
			place[pos] = score
			temp = 0

	for agent in agents:
		team = Teams.objects.get(name=agent.teamid)
		targets = Targets.objects.get(name=team.targets)
		agentstats = dstats.filter(agent=agent)
		#avgcalltime = int(agentstats['calltime__sum'] / (agentstats['prodhours__sum']/targets.hours))
		volume = wstats.filter(agent=agent).aggregate(Sum('volume'))
		qualified = qapps.filter(agent=agent).aggregate(Sum('qualifiedapps'))

		academy.append([1,2])

	return academy


def academy_year(year):
	"""
	This function take the variables for the year and generates the academy for a year to date.
	"""
	year = int(year)

	ctlist = []
	qalist = []
	volumelist = []
	drawlist = []
	growthlist = []
	academy = []
	winners = {}

	agents = Agent.objects.filter(teamid__teamtype=1).filter(haveleft=0).filter(agenttype=0)
	dstats = Dstats.objects.filter(isoyear=year)
	wstats = WeeklyStats.objects.filter(isoyear=year)
	qapps = QualifiedApps.objects.filter(year=year)

	for agent in agents:
		team = Teams.objects.get(name=agent.teamid)
		targets = Targets.objects.get(name=team.targets)
		agentstats = dstats.filter(agent=agent).aggregate(Sum('calltime'), Sum('prodhours'))
		avgcalltime = int(agentstats['calltime__sum'] / (agentstats['prodhours__sum']/targets.hours))
		volume = wstats.filter(agent=agent).aggregate(Sum('volume'))
		qualified = qapps.filter(agent=agent).aggregate(Sum('qualifiedapps'))
		ctlist.append([agent.name, team.name, ])
		drawlist.append([agent.name, avgcalltime])
		volumelist.append([agent.name, volume['volume__sum']])
		qalist.append([agent.name, qualified['qualifiedapps__sum']])

	ctlist.sort(key=sort_inner, reverse=True)
	qalist.sort(key=sort_inner, reverse=True)
	volumelist.sort(key=sort_inner, reverse=True)

	score = 0
	previous = 0


@login_required
def academy_current_winners(request):
	thedate = datetime.today()-timedelta(days=14)
	month = thedate.strftime("%b").lower()
	year = thedate.strftime("%Y").lower()
	display = month_display(month)

	academy = academy_month(month, year)
	academy.sort(key=sort_inner, reverse=True)

	template = 'academy/presentation.html'
	context = RequestContext(request, {'month':display, 'year':year, 'academy':academy})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def academy_year_winners(request, year):
	academy = academy_year(year)
	academy.sort(key=sort_inner, reverse=True)

	template = 'academy/presentation.html'
	context = RequestContext(request, {'year':year, 'academy':academy})
    
	response = render_to_response(template, context)
    
	return response
    
@login_required
def academy_month_winners(request, year, month):
	display = month_display(month)

	academy = academy_month(month, year)
	academy.sort(key=sort_inner, reverse=True)

	template = 'academy/presentation.html'
	context = RequestContext(request, {'year':year, 'month':display, 'academy':academy})
    
	response = render_to_response(template, context)
    
	return response
    
@login_required
def academy_current_leaderboard(request):
	thedate = datetime.today()-timedelta(days=14)
	month = thedate.strftime("%b").lower()
	year = thedate.strftime("%Y").lower()
	display = month_display(month)

	academy = academy_month(month, year)
	academy.sort(key=sort_inner)

	template = 'academy/table.html'
	context = RequestContext(request, {'month':display, 'year':year, 'academy':academy})
    
	response = render_to_response(template, context)
    
	return response
    
@login_required
def academy_year_leaderboard(request, year):
	academy = academy_year(year)
	academy.sort(key=sort_inner)

	template = 'academy/table.html'
	context = RequestContext(request, {'year':year, 'academy':academy })
    
	response = render_to_response(template, context)
    
	return response
    
@login_required
def academy_month_leaderboard(request, year, month):
	display = month_display(month)

	academy = academy_month(month, year)
	academy.sort(key=sort_inner)

	template = 'academy/table.html'
	context = RequestContext(request, {'year':year, 'month':display, 'academy':academy})
    
	response = render_to_response(template, context)
    
	return response
    

@login_required	
def academy_calendar_select(request):
	template = 'academy/calendar.html'
	context = RequestContext(request, {})
    
	response = render_to_response(template, context)
    
	return response

@login_required    
def academy_quarter_leaderboard(request, year, quarter):
	quarters = {1:['jan', 'feb', 'mar'], 2:['apr', 'may', 'jun'], 3:['jul', 'aug', 'sep'], 4:['oct', 'nov', 'dec']}
	run = quarters[int(quarter)]
	display = []
	for month in run:
		display.append(month_display(month))

	academy =[]
	academy.append(['Chris Thomas',	2,	0,	0,	0,	6])
	academy.append(['Daryl Bennett',	2,	0,	0,	0,	6])
	academy.append(['James Wildman',	2,	0,	0,	0,	6])
	academy.append(['Jo Humphreys',	2,	0,	0,	0,	6])
	academy.append(['Jodie Gaul',	2,	0,	0,	0,	6])
	academy.append(['Stacey Taylor',	2,	0,	0,	0,	6])
	academy.append(['Hugh Kitchen',	1,	1,	0,	0,	5])
	academy.append(['Jason Whewell',	1,	1,	0,	0,	5])
	academy.append(['Kelly Heath',	1,	1,	0,	0,	5])
	academy.append(['Lee Weaver',	1,	1,	0,	0,	5])
	academy.append(['Loreen Wilson',	1,	1,	0,	0,	5])
	academy.append(['Daniel Phillips',	0,	2,	0,	0,	4])
	academy.append(['Dean Stower',	0,	2,	0,	0,	4])
	academy.append(['Matt Shaw',	1,	0,	1,	0,	4])
	academy.append(['Mike Brain',	0,	2,	0,	0,	4])
	academy.append(['Sam Bradley',	1,	0,	1,	0,	4])
	academy.append(['Emma Dickinson',	0,	1,	1,	0,	3])
	academy.append(['Gary Kenward',	0,	1,	1,	0,	3])
	academy.append(['James Walley',	0,	1,	1,	0,	3])
	academy.append(['John Leonard',	0,	1,	1,	0,	3])
	academy.append(['Lamont Adams',	1,	0,	0,	1,	3])
	academy.append(['Nicola Carleton',	0,	1,	1,	0,	3])
	academy.append(['Rebecca Shaw',	0,	1,	1,	0,	3])
	academy.append(['Carl Waite',	0,	0,	2,	0,	2])
	academy.append(['Gemma Ball',	0,	0,	2,	0,	2])
	academy.append(['Emma Leslie',	0,	0,	1,	1,	1])
	academy.append(['Emma Robinson',	0,	0,	1,	1,	1])
	academy.append(['Gary Goodwin',	0,	0,	1,	1,	1])
	academy.append(['Lee Nichol',	0,	0,	1,	1,	1])
	academy.append(['Rebecca Hill',	0,	0,	1,	1,	1])
	academy.append(['Alex Widgery',	0,	0,	0,	2,	0])
	academy.append(['Audrey Roberts',	0,	0,	0,	2,	0])
	academy.append(['Chris Dixon',	0,	0,	0,	1,	0])
	academy.append(['Dwayne Patterson',	0,	0,	0,	2,	0])
	academy.append(['Hellen Molyneux',	0,	0,	0,	2,	0])
	academy.append(['Louise Batchelor',	0,	0,	0,	1,	0])
	academy.append(['Louise Gallon',	0,	0,	0,	2,	0])
	academy.append(['Nathan Dyer',	0,	0,	0,	2,	0])

	template = 'academy/quarter.html'
	context = RequestContext(request, {'year':year, 'quarter':quarter, 'display':display, 'academy':academy})
    
	response = render_to_response(template, context)
    
	return response

@login_required
def academy_quarter_winners(request, year, quarter):
	quarters = {1:['jan', 'feb', 'mar'], 2:['apr', 'may', 'jun'], 3:['jul', 'aug', 'sep'], 4:['oct', 'nov', 'dec']}
	run = quarters[int(quarter)]
	display = []
	for month in run:
		display.append(month_display(month))

	academy =[]
	academy.append(['Chris Thomas',	2,	0,	0,	0,	6])
	academy.append(['Daryl Bennett',	2,	0,	0,	0,	6])
	academy.append(['James Wildman',	2,	0,	0,	0,	6])
	academy.append(['Jo Humphreys',	2,	0,	0,	0,	6])
	academy.append(['Jodie Gaul',	2,	0,	0,	0,	6])
	academy.append(['Stacey Taylor',	2,	0,	0,	0,	6])
	academy.append(['Hugh Kitchen',	1,	1,	0,	0,	5])
	academy.append(['Jason Whewell',	1,	1,	0,	0,	5])
	academy.append(['Kelly Heath',	1,	1,	0,	0,	5])
	academy.append(['Lee Weaver',	1,	1,	0,	0,	5])
	academy.append(['Loreen Wilson',	1,	1,	0,	0,	5])
	academy.append(['Daniel Phillips',	0,	2,	0,	0,	4])
	academy.append(['Dean Stower',	0,	2,	0,	0,	4])
	academy.append(['Matt Shaw',	1,	0,	1,	0,	4])
	academy.append(['Mike Brain',	0,	2,	0,	0,	4])
	academy.append(['Sam Bradley',	1,	0,	1,	0,	4])
	academy.append(['Emma Dickinson',	0,	1,	1,	0,	3])
	academy.append(['Gary Kenward',	0,	1,	1,	0,	3])
	academy.append(['James Walley',	0,	1,	1,	0,	3])
	academy.append(['John Leonard',	0,	1,	1,	0,	3])
	academy.append(['Lamont Adams',	1,	0,	0,	1,	3])
	academy.append(['Nicola Carleton',	0,	1,	1,	0,	3])
	academy.append(['Rebecca Shaw',	0,	1,	1,	0,	3])
	academy.append(['Carl Waite',	0,	0,	2,	0,	2])
	academy.append(['Gemma Ball',	0,	0,	2,	0,	2])
	academy.append(['Emma Leslie',	0,	0,	1,	1,	1])
	academy.append(['Emma Robinson',	0,	0,	1,	1,	1])
	academy.append(['Gary Goodwin',	0,	0,	1,	1,	1])
	academy.append(['Lee Nichol',	0,	0,	1,	1,	1])
	academy.append(['Rebecca Hill',	0,	0,	1,	1,	1])
	academy.append(['Alex Widgery',	0,	0,	0,	2,	0])
	academy.append(['Audrey Roberts',	0,	0,	0,	2,	0])
	academy.append(['Chris Dixon',	0,	0,	0,	1,	0])
	academy.append(['Dwayne Patterson',	0,	0,	0,	2,	0])
	academy.append(['Hellen Molyneux',	0,	0,	0,	2,	0])
	academy.append(['Louise Batchelor',	0,	0,	0,	1,	0])
	academy.append(['Louise Gallon',	0,	0,	0,	2,	0])
	academy.append(['Nathan Dyer',	0,	0,	0,	2,	0])

	template = 'academy/quarterwinners.html'
	context = RequestContext(request, {'year':year, 'quarter':quarter, 'display':display, 'academy':academy})

	response = render_to_response(template, context)

	return response

@login_required
def academyboardtemp(request):
	ctlist = []
	qalist = []
	volumelist = []
	drawlist = []
	growthlist = []
	academy = []
	winners = {}
	month = "may"
	months = {'jan': 'January',
		'feb':'February',
		'mar':'March',
		'apr':'April',
		'may':'May',
		'jun':'June',
		'jul':'July',
		'aug':'August',
		'sep':'September',
		'oct':'October',
		'nov':'November',
		'dec':'December',
	}
	display = months[month]
	agents = Agent.objects.filter(haveleft=0).filter(agenttype=0).exclude(teamid__teamtype=3).exclude(teamid__teamtype=4).exclude(teamid__teamtype=5)
	dstats = Dstats.objects.filter(month=month)
	for each in agents:
		winners[each.name]=0
		volume = 0

		team = Teams.objects.get(name=each.teamid)
		targets = Targets.objects.get(name=team.targets)
		agentstats = Dstats.objects.filter(month=month).filter(agent=each).aggregate(Sum('calltime'), Sum('prodhours'))
		if agentstats['prodhours__sum'] > 0:
			avgct = agentstats['calltime__sum'] / (agentstats['prodhours__sum']/targets.hours)
		else:
			avgct = 0
		volume = MonthlyStats.objects.filter(isomonth=month).filter(agent=each)
		count = volume.count()

		if count > 0:
			for vol in volume:
				volumelist.append([each.name, vol.volume])
				drawlist.append([each.name, vol.drawcust])
				growthlist.append([each.name, vol.growth])
		else:
			volumelist.append([each.name, 0])
			drawlist.append([each.name, 0])
			growthlist.append([each.name, 0])

		ctlist.append([each.name, avgct])
		apps = QualifiedApps.objects.filter(month=month).filter(agent=each)
		for app in apps:
			qalist.append([each.name, app.qualifiedapps])

	def sort_inners(inner):
		"""
		inner is each inner list in the list of lists to be sorted
		(here item at index 1 of each inner list is to be sorted)
		"""
		return inner[1]

	ctlist.sort(key=sort_inners, reverse=True)
	qalist.sort(key=sort_inners, reverse=True)
	volumelist.sort(key=sort_inners, reverse=True)
	drawlist.sort(key=sort_inners, reverse=True)
	score = 0
	for each in ctlist:
		
		winners[each[0]]=score
		score +=1
	score = 0
	for each in qalist:
		winners[each[0]]+=score
		score +=1
	score = 0
	for each in volumelist:
		winners[each[0]]+=score
		score +=1
	score = 0
	for each in drawlist:
		winners[each[0]]+=score
		score +=1
	for each in agents:
		team = Teams.objects.get(name=each.teamid)
		targets = Targets.objects.get(name=team.targets)
		agentstats = Dstats.objects.filter(month=month).filter(agent=each).aggregate(Sum('calltime'), Sum('prodhours'))
		if agentstats['prodhours__sum'] > 0:
			avgct = int(agentstats['calltime__sum'] / (agentstats['prodhours__sum']/targets.hours))
		else:
			avgct = 0
		volume = MonthlyStats.objects.filter(isomonth=month).filter(agent=each)
		apps = QualifiedApps.objects.filter(month=month).filter(agent=each)
		qa = 0
		vol = 0
		growth = 0
		draw = 0
		for app in apps:
			qa = app.qualifiedapps
		for vol in volume:
			draw = vol.drawcust
			growth = vol.growth
		academy.append([each.name, winners[each.name], team.name, avgct, growth, qa, draw, each.picture])
	academy.sort(key=sort_inners, reverse=True)

	template = 'osiris/academy/academy_presentation.html'
	context = RequestContext(request, {'month':display, 'academy':academy})

	response = render_to_response(template, context)

	return response

@login_required
def academyleaderboardtemp(request):
	ctlist = []
	qalist = []
	volumelist = []
	drawlist = []
	growthlist = []
	academy = []
	winners = {}
	month = "may"
	months = {'jan': 'January',
		'feb':'February',
		'mar':'March',
		'apr':'April',
		'may':'May',
		'jun':'June',
		'jul':'July',
		'aug':'August',
		'sep':'September',
		'oct':'October',
		'nov':'November',
		'dec':'December',
	}
	display = months[month]
	agents = Agent.objects.filter(haveleft=0).filter(agenttype=0).exclude(teamid__teamtype=3).exclude(teamid__teamtype=4).exclude(teamid__teamtype=5)
	dstats = Dstats.objects.filter(month=month)
	for each in agents:
		winners[each.name]=0
		volume = 0

		team = Teams.objects.get(name=each.teamid)
		targets = Targets.objects.get(name=team.targets)
		agentstats = Dstats.objects.filter(month=month).filter(agent=each).aggregate(Sum('calltime'), Sum('prodhours'))
		if agentstats['prodhours__sum'] > 0:
			avgct = agentstats['calltime__sum'] / (agentstats['prodhours__sum']/targets.hours)
		else:
			avgct = 0
		volume = MonthlyStats.objects.filter(isomonth=month).filter(agent=each)
		count = volume.count()

		if count > 0:
			for vol in volume:
				volumelist.append([each.name, vol.volume])
				drawlist.append([each.name, vol.drawcust])
				growthlist.append([each.name, vol.growth])
		else:
			volumelist.append([each.name, 0])
			drawlist.append([each.name, 0])
			growthlist.append([each.name, 0])

		ctlist.append([each.name, avgct])
		apps = QualifiedApps.objects.filter(month=month).filter(agent=each)
		for app in apps:
			qalist.append([each.name, app.qualifiedapps])

	def sort_inners(inner):
		"""
		inner is each inner list in the list of lists to be sorted
		(here item at index 1 of each inner list is to be sorted)
		"""
		return inner[1]

	ctlist.sort(key=sort_inners, reverse=True)
	qalist.sort(key=sort_inners, reverse=True)
	volumelist.sort(key=sort_inners, reverse=True)
	drawlist.sort(key=sort_inners, reverse=True)
	score = 0
	for each in ctlist:
		winners[each[0]]=score
		score +=1
	score = 0
	for each in qalist:
		winners[each[0]]+=score
		score +=1
	score = 0
	for each in volumelist:
		winners[each[0]]+=score
		score +=1
	score = 0
	for each in drawlist:
		winners[each[0]]+=score
		score +=1
	for each in agents:
		team = Teams.objects.get(name=each.teamid)
		targets = Targets.objects.get(name=team.targets)
		agentstats = Dstats.objects.filter(month=month).filter(agent=each).aggregate(Sum('calltime'), Sum('prodhours'))
		if agentstats['prodhours__sum'] > 0:
			avgct = int(agentstats['calltime__sum'] / (agentstats['prodhours__sum']/targets.hours))
		else:
			avgct = 0
		volume = MonthlyStats.objects.filter(isomonth=month).filter(agent=each)
		apps = QualifiedApps.objects.filter(month=month).filter(agent=each)
		qa = 0
		draw = 0
		growth = 0
		for app in apps:
			qa = app.qualifiedapps
		for vol in volume:
			draw = vol.drawcust
			growth = vol.growth
		academy.append([each.name, winners[each.name], team.name, avgct, growth, qa, draw, each.picture])
	academy.sort(key=sort_inners, reverse=False)

	template = 'osiris/academy/academy_table.html'
	context = RequestContext(request, {'month':display, 'academy':academy})

	response = render_to_response(template, context)

	return response

@login_required
def academyleaderboardtempmonth(request, month):
	ctlist = []
	qalist = []
	volumelist = []
	drawlist = []
	growthlist = []
	academy = []
	winners = {}
	months = {'jan': 'January',
		'feb':'February',
		'mar':'March',
		'apr':'April',
		'may':'May',
		'jun':'June',
		'jul':'July',
		'aug':'August',
		'sep':'September',
		'oct':'October',
		'nov':'November',
		'dec':'December',
	}
	display = months[month]
	agents = Agent.objects.filter(haveleft=0).filter(agenttype=0).exclude(teamid__teamtype=3).exclude(teamid__teamtype=4).exclude(teamid__teamtype=5)
	dstats = Dstats.objects.filter(month=month)
	for each in agents:
		team = Teams.objects.get(name=each.teamid)
		targets = Targets.objects.get(name=team.targets)
		agentstats = Dstats.objects.filter(month=month).filter(agent=each).aggregate(Sum('calltime'), Sum('prodhours'))
		if agentstats['prodhours__sum'] > 0:
			winners[each.name]=0
			volume = 0
			avgct = agentstats['calltime__sum'] / (agentstats['prodhours__sum']/targets.hours)
			volume = MonthlyStats.objects.filter(isomonth=month).filter(agent=each)
			count = volume.count()

			if count > 0:
				for vol in volume:
					volumelist.append([each.name, vol.volume])
					drawlist.append([each.name, vol.drawcust])
					growthlist.append([each.name, vol.growth])
			else:
				volumelist.append([each.name, 0])
				drawlist.append([each.name, 0])
				growthlist.append([each.name, 0])

			ctlist.append([each.name, avgct])
			apps = QualifiedApps.objects.filter(month=month).filter(agent=each)
			for app in apps:
				qalist.append([each.name, app.qualifiedapps])

	def sort_inners(inner):
		"""
		inner is each inner list in the list of lists to be sorted
		(here item at index 1 of each inner list is to be sorted)
		"""
		return inner[1]

	ctlist.sort(key=sort_inners, reverse=True)
	qalist.sort(key=sort_inners, reverse=True)
	volumelist.sort(key=sort_inners, reverse=True)
	drawlist.sort(key=sort_inners, reverse=True)
	score = 0
	for each in ctlist:
		winners[each[0]]=score
		score +=1
	score = 0
	for each in qalist:
		winners[each[0]]+=score
		score +=1
	score = 0
	for each in volumelist:
		winners[each[0]]+=score
		score +=1
	score = 0
	for each in drawlist:
		winners[each[0]]+=score
		score +=1

	for each in agents:
		team = Teams.objects.get(name=each.teamid)
		targets = Targets.objects.get(name=team.targets)
		agentstats = Dstats.objects.filter(month=month).filter(agent=each).aggregate(Sum('calltime'), Sum('prodhours'))
		if agentstats['prodhours__sum'] > 0:
			avgct = int(agentstats['calltime__sum'] / (agentstats['prodhours__sum']/targets.hours))
			volume = MonthlyStats.objects.filter(isomonth=month).filter(agent=each)
			apps = QualifiedApps.objects.filter(month=month).filter(agent=each)
			for app in apps:
				qa = app.qualifiedapps
			for vol in volume:
					draw = vol.drawcust
					growth = vol.growth
			academy.append([each.name, winners[each.name], team.name, avgct, growth, qa, draw, each.picture])
	academy.sort(key=sort_inners, reverse=False)

	template = 'osiris/academy/academy_table.html'
	context = RequestContext(request, {'month':display, 'academy':academy})

	response = render_to_response(template, context)

	return response

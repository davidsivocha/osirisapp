# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from datetime import datetime, timedelta, time
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Avg, Max, Min, Count, Sum
from stats.models import Dstats, QualifiedApps, WeeklyStats
from team.models import Teams, Targets
from extras.views import month_display, month_number, month_list, number_month
from agents.models import Agent

"""
Error controller definitions
"""
def server_error(request):
    template_name = 'core/500.html'
    return render_to_response(template_name,
        context_instance = RequestContext(request)
    )
def permission_error(request):
    template_name = 'core/badpermissions.html'
    return render_to_response(template_name,
        context_instance = RequestContext(request)
    )

"""
Logout controller.
"""
def logout_view(request): #done
    logout(request)
    template = 'core/logout.html'
    context = RequestContext(request, {})

    response = render_to_response(template, context)
    
    return response

"""
Redirects to an agent page when you try to view a username
"""
@login_required
def user_view(request, username): #done
    user = get_object_or_404(User, username=username)
    profile = user.get_profile()
    slug = profile.slug
    url = "/agent/" + slug
    return HttpResponseRedirect(url)

"""
Logic controllers for sauls graph dashboard. 
"""
@login_required
def saul_dashboard(request): 
    if not request.user.has_perm('agents.saul'):
        url = "/"
        return HttpResponseRedirect(url)

    thedate = datetime.today() #gets today's date
    isoweek = thedate.isocalendar()[1] #get today's isoweek
    isoyear = thedate.strftime("%Y") #gets this year

    dstatquery = Dstats.objects.filter(isoyear=isoyear) #the base query to get all the objects in that year
    qappquery = QualifiedApps.objects.filter(year=isoyear) #the base query to get all the objects in that year
    wstatquery = WeeklyStats.objects.filter(isoyear=isoyear) #the base query to get all the objects in that year

    team_list = Teams.objects.filter(teamtype=1) #list of all the teams to display on the charts

    calltimeweeks = OrderedDict() #dict of each weeks containing calltime averages
    callattemptsweeks = OrderedDict() #dict of each week containing call attempt averages

    totalapplicationweeks = OrderedDict() #dict containing total applications by week
    fteapplicationweeks = OrderedDict() #dict containing fte applications by week

    otherhourweeks = OrderedDict() #hours in graph form by week
    sickhourweeks = OrderedDict() #hours in graph form by week
    holidayhourweeks = OrderedDict() #hours in graph form by week

    qualifiedappmonths = OrderedDict() #dict containing monthly qualifed apps

    teamcalls = OrderedDict()
    teamattempts = OrderedDict()
    teamapps = OrderedDict()
    teamfte = OrderedDict()
    teamqa = OrderedDict()
    teamvol = OrderedDict()

    volumemonths =OrderedDict() #dict containing monthly volume totals

    if isoweek > 1:
        startweek = 1
        while startweek < isoweek:
            targets = Targets.objects.get(pk=1)
            teamstats = dstatquery.filter(isoweek=startweek).filter(team__teamtype=1).aggregate(Sum('totalapps'), Sum('callattempts'), Sum('calltime'), Sum('prodhours'), Sum('sickhours'), Sum('holhours'), Sum('otherhours'))
            if teamstats['prodhours__sum'] > 0:
                calltimeavg = int(teamstats['calltime__sum'] / (teamstats['prodhours__sum'] / targets.hours))
                callattemptsavg = teamstats['callattempts__sum'] / (teamstats['prodhours__sum'] / targets.hours)
                appsavg = teamstats['totalapps__sum'] / ((teamstats['prodhours__sum'] + teamstats['sickhours__sum']) / targets.hours)
            else:
                calltimeavg = 0
                callattemptsavg = 0
                appsavg = 0
            teamcalls[startweek] = calltimeavg
            teamattempts[startweek] = callattemptsavg
            teamapps[startweek] = teamstats['totalapps__sum']
            teamfte[startweek] = appsavg
            startweek += 1

    if isoweek > 1 :
        startweek = 1
        while startweek < isoweek:
            ctlist = []
            calist = []
            apps = []
            sick = []
            hol = []
            other = []
            tapps = []
            vol = []
            for teams in team_list:
                targets = Targets.objects.get(name=teams.targets)
                stats = dstatquery.filter(isoweek=startweek).filter(team=teams).aggregate(Sum('totalapps'), Sum('callattempts'), Sum('calltime'), Sum('prodhours'), Sum('sickhours'), Sum('holhours'), Sum('otherhours'))
                if stats['prodhours__sum'] > 0:
                    calltimeavg = stats['calltime__sum'] / (stats['prodhours__sum'] / targets.hours)
                    callattemptsavg = stats['callattempts__sum'] / (stats['prodhours__sum'] / targets.hours)
                    appsavg = stats['totalapps__sum'] / ((stats['prodhours__sum'] + stats['sickhours__sum']) / targets.hours)
                else:
                    calltimeavg = 0
                    callattemptsavg = 0
                    appsavg = 0

                ctlist.append(calltimeavg)
                calist.append(callattemptsavg)
                apps.append(appsavg)
                sick.append(stats['sickhours__sum'])
                hol.append(stats['holhours__sum'])
                other.append(stats['otherhours__sum'])
                tapps.append(stats['totalapps__sum'])

                agents = Agent.objects.filter(teamid=teams).filter(haveleft=0)

                totalvolume = 0
                for agent in agents:
                    volsum = wstatquery.filter(agent=agent).filter(isoweek=startweek).aggregate(Sum('volume'),)
                    volsum = volsum['volume__sum']
                    if not volsum >= 0:
                        volsum = 0
                    totalvolume += volsum
        
                vol.append(totalvolume)
            volumemonths[startweek] = vol

            calltimeweeks[startweek] = ctlist
            callattemptsweeks[startweek] = calist
            fteapplicationweeks[startweek] = apps
            totalapplicationweeks[startweek] = tapps
            sickhourweeks[startweek] = sick
            holidayhourweeks[startweek] = hol
            otherhourweeks[startweek] = other
            
            startweek += 1

    months = month_list()
    for month in months:
        qapps = []
        #vol = []
        for teams in team_list:
            agents = Agent.objects.filter(teamid=teams).filter(haveleft=0)
            totalapps = 0
            #totalvolume = 0
            for agent in agents:
                qappsum = qappquery.filter(agent=agent).filter(month=month).aggregate(Sum('qualifiedapps'),)
                #volsum = wstatquery.filter(agent=agent).filter(isomonth=month).aggregate(Sum('volume'),)
                qappsum = qappsum['qualifiedapps__sum']
                #volsum = volsum['volume__sum']
                if not qappsum >= 0:
                    qappsum = 0
                #if not volsum >= 0:
                #    volsum = 0
                totalapps += qappsum
                #totalvolume += volsum
            qapps.append(totalapps)
            #vol.append(totalvolume)
        qualifiedappmonths[month_display(month)] = qapps
        #volumemonths[month_display(month)] = vol

    cumqualmonths = OrderedDict()
    for month in month_list():
        qappsum = qappquery.filter(agent__teamid__teamtype=1).filter(month=month).aggregate(Sum('qualifiedapps'),)
        cumqualmonths[month_display(month)] = qappsum['qualifiedapps__sum']

    chart_list = Teams.objects.filter(teamtype=5)
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

    template = 'core/saul.html'
    context = RequestContext(request, {
        'teamlist':team_list,
        'calltimeweeks':calltimeweeks,
        'callattemptsweeks':callattemptsweeks,
        'totalapplicationweeks':totalapplicationweeks,
        'fteapplicationweeks':fteapplicationweeks,
        'otherhourweeks':otherhourweeks,
        'sickhourweeks':sickhourweeks,
        'holidayhourweeks':holidayhourweeks,
        'qualifiedappmonths':qualifiedappmonths,
        'volumemonths':volumemonths,
        'teamcalls': teamcalls,
        'teamattempts': teamattempts,
        'teamapps': teamapps,
        'teamfte': teamfte,
        'cumqualmonths': cumqualmonths,
        'year':isoyear,
        'catable':caweeks, 'cttable':ctweeks, 'appstable':appweeks, 'chart_list':chart_list
        })

    response = render_to_response(template, context)

    return response
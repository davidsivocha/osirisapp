from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from agents.models import Agent, Incentive, Training, CoachingAndCompliance
from team.models import Teams, Targets
from stats.models import Dstats, QualifiedApps, WeeklyStats
from datetime import datetime, timedelta, time
from django.db.models import Avg, Max, Min, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, UserManager
from collections import OrderedDict
from extras.views import month_display, month_number, humantime
from decimal import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

@login_required
def agent_select(request): #done
    user = request.user.get_profile()
    type = int(user.agenttype)
    if not request.user.has_perm('agents.super'):
        slug = user.slug
        url = "/agent/" + slug
        return HttpResponseRedirect(url)
    else:
        active = Agent.objects.filter(haveleft=0).filter(agenttype=0).order_by('name')
        inactive = Agent.objects.filter(haveleft=1).filter(permanentleave=0).filter(agenttype=0)
        template = 'agents/list.html'
        context = RequestContext(request, {'active':active, 'inactive':inactive,})
        
        response = render_to_response(template, context)
        
        return response

@login_required
def agent_page(request, agent): #done
    user = request.user.get_profile()
    type = int(user.agenttype)
    agent = get_object_or_404(Agent, slug=agent)
    if not request.user.has_perm('agents.super'):
        if not user.name == agent.name:
            slug = user.slug
            url = "/agent/" + slug
            return HttpResponseRedirect(url) 
    
    globalstats = Dstats.objects.filter(agent=agent)

    if agent.haveleft == 0:
        team = Teams.objects.get(name=agent.teamid)
        targets = Targets.objects.get(name=team.targets)
    else:
        targets = Targets.objects.get(pk=1)

    ill = globalstats.filter(sickhours__gt = 0).order_by('-date')[:10]
    hol = globalstats.filter(holhours__gt = 0).order_by('-date')[:10]
    acheive = Incentive.objects.filter(agent=agent.id)[:20]
    candc = CoachingAndCompliance.objects.filter(agent=agent.id).order_by('-date')[:20]
    training = Training.objects.filter(agent=agent.id).order_by('-date')[:50]

    thedate = datetime.today()
    isoweek = int(thedate.isocalendar()[1])
    isoyear = thedate.isocalendar()[0]
    month = thedate.strftime("%b").lower()

    totals = globalstats.filter(isoyear=isoyear).aggregate(Sum('callattempts'), Sum('calltime'), Sum('prodhours'), Sum('sickhours'), Sum('totalapps'))
    monthtotals = globalstats.filter(isoyear=isoyear).filter(month=month).aggregate(Sum('callattempts'), Sum('calltime'), Sum('prodhours'), Sum('sickhours'), Sum('totalapps'))
    
    fte = {}
    fte["calltime"] = 0
    if totals['calltime__sum'] > 0:
        fte["calltime"] = totals['calltime__sum'] / (totals['prodhours__sum'] / targets.hours)
    if fte["calltime"] > 0:
        fte["calltime"] = int(fte["calltime"])

    fte["callattempts"] = 0
    if totals['callattempts__sum'] > 0:
        fte["callattempts"] = totals['callattempts__sum'] / (totals['prodhours__sum'] / targets.hours)
    if fte["callattempts"] > 0:
        fte["callattempts"] = int(fte["callattempts"])

    fte["totalapps"] = 0
    if totals['totalapps__sum'] > 0:
        fte["totalapps"] = totals['totalapps__sum'] / ((totals['prodhours__sum'] + totals['sickhours__sum']) / targets.hours)
    if fte["totalapps"] > 0:
        fte["totalapps"] = fte["totalapps"]

    monthfte = {}
    monthfte["calltime"] = 0
    if monthtotals['calltime__sum'] > 0:
        monthfte["calltime"] = monthtotals['calltime__sum'] / (monthtotals['prodhours__sum'] / targets.hours)
    if monthfte["calltime"] > 0:
        monthfte["calltime"] = int(monthfte["calltime"])

    monthfte["callattempts"] = 0
    if monthtotals['callattempts__sum'] > 0:
        monthfte["callattempts"] = monthtotals['callattempts__sum'] / (monthtotals['prodhours__sum'] / targets.hours)
    if monthfte["callattempts"] > 0:
        monthfte["callattempts"] = int(monthfte["callattempts"])

    monthfte["totalapps"] = 0
    if monthtotals['totalapps__sum'] > 0:
        monthfte["totalapps"] = monthtotals['totalapps__sum'] / ((monthtotals['prodhours__sum'] + monthtotals['sickhours__sum']) / targets.hours)
    if monthfte["totalapps"] > 0:
        monthfte["totalapps"] = monthfte["totalapps"]

    chartstats = Dstats.objects.filter(agent=agent)
    chartweeks = []
    calltime = []
    callattempts = []
    apps = []
    weeks = OrderedDict()
    weekdata = []
    if isoweek > 1 :    
        startweek = 1 
        while startweek < isoweek:
            statsum = chartstats.filter(isoyear=isoyear).filter(isoweek=startweek).aggregate(Sum('totalapps'), Sum('callattempts'), Sum('calltime'), Sum('prodhours'), Sum('sickhours'))
            if statsum['prodhours__sum'] > 0:
                calltimeavg = statsum['calltime__sum'] / (statsum['prodhours__sum'] / targets.hours)
                callattemptsavg = statsum['callattempts__sum'] / (statsum['prodhours__sum'] / targets.hours)
                appsavg = statsum['totalapps__sum'] / ((statsum['prodhours__sum']+statsum['sickhours__sum']) / targets.hours)
                calltime.append(int(calltimeavg))
                callattempts.append(int(callattemptsavg))
                apps.append(statsum['totalapps__sum'] )
                chartweeks.append(startweek)
                weeks[startweek] = weekdata
                weekdata = []
                statsum = []
            else:
                calltime.append(0)
                callattempts.append(0)
                apps.append(0)
                chartweeks.append(startweek)
                weekdata.append([0, 0, 0])
                weeks[startweek] = weekdata
                weekdata = []
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
    
    qappweeks = OrderedDict()
    volweeks = OrderedDict()
    
    for key,value in months.iteritems():
        qappsum = QualifiedApps.objects.filter(agent=agent).filter(month=key).filter(year=isoyear).aggregate(Sum('qualifiedapps'),)
        volsum = WeeklyStats.objects.filter(agent=agent).filter(isomonth=key).filter(isoyear=isoyear).aggregate(Sum('volume'),)

        qappsum = qappsum['qualifiedapps__sum']
        volsum = volsum['volume__sum']

        if not qappsum >= 0:
            qappsum = 0

        if not volsum >= 0:
            volsum = 0

        qappweeks[value] = qappsum
        volweeks[value] = volsum
        volsum = 0
        qappsum = 0

    template = 'agents/page.html'
    context = RequestContext(request, {'candc':candc, 'vol':volweeks, 'qapps':qappweeks, 'apps':apps,'callattempts':callattempts,'calltime':calltime,'weeks':chartweeks, 'agent':agent, 'sick':ill, 'hol':hol, 'training':training,'acheive':acheive, 'totals':totals, 'fte':fte, 'monthtotals':monthtotals, 'monthfte':monthfte, 'month':month_display(month)})
    
    response = render_to_response(template, context)
    
    return response

@login_required
def agent_year_review(request, agent, year): #done
    user = request.user.get_profile()
    type = int(user.agenttype)
    agent = get_object_or_404(Agent, slug=agent)
    if not request.user.has_perm('agents.super'):
        if not user.name == agent.name:
            slug = user.slug
            url = "/agent/" + slug
            return HttpResponseRedirect(url) 

    response = HttpResponse(mimetype='application/pdf')
    filename = "%s-AgentYearReport-%s.pdf" % (agent.slug, year)
    response['Content-Disposition'] = 'attachment; filename='+filename

    team = Teams.objects.get(name=agent.teamid)
    target = Targets.objects.get(name=team.targets)
    globalstats = Dstats.objects.filter(agent=agent).filter(isoyear=year)
    sick = globalstats.filter(sickhours__gt = 0).count()
    working = globalstats.filter(prodhours__gt = 0).count()
    holiday = globalstats.filter(holhours__gt = 0).count()
    monthtotals = globalstats.aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'))
    if monthtotals['calltime__sum'] > 0:
        calltime = monthtotals['calltime__sum'] / (monthtotals['prodhours__sum'] / target.hours)
        calltime = int(calltime)
        realcalltime = humantime(calltime)

    qappcount = QualifiedApps.objects.filter(agent=agent).filter(year=year).count() 
    qappsum = QualifiedApps.objects.filter(agent=agent).filter(year=year).aggregate(Sum('qualifiedapps'),)
    qappsum = qappsum['qualifiedapps__sum']
    qapptarget = ((target.commission3 / target.days)*agent.parttimedays) * qappcount

    targetct = humantime(target.calltime)
    targetapps = int(((monthtotals['prodhours__sum'] + monthtotals['sickhours__sum']) / target.hours) * Decimal(target.applications))
    targetbuying = str(target.drawingcust) + "%"

    p = canvas.Canvas(response)

    p.setFont("Helvetica", 16)
    titlestring = agent.name + " - Yearly Review: " + year
    p.drawString(50,800, titlestring)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 820, team.name)

    p.setFont("Helvetica", 14)

    workingtext = "Working Days: " + str(working)
    sicktext = "Sick Days: " + str(sick)
    holidaytext = "Holiday Days: " + str(holiday)
    p.drawString(50, 770, workingtext)

    p.drawString(450, 770, holidaytext)

    p.drawString(50, 750, "Academy Year: ")

    p.drawString(250, 770, sicktext)

    p.drawString(250, 750, "Academy Year to Date: ")

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 720, "Yearly")
    p.rect(50,710,500,-125,fill=0)
    
    p.drawString(50, 560, "Review of last years objectives")
    p.rect(50,540,500,-125,fill=0)

    p.drawString(50, 400, "Team and Environment")
    p.rect(50,390,500,-80,fill=0)

    p.drawString(50, 290, "Action Plan")
    p.rect(50,280,500,-140,fill=0)

    p.drawString(50, 120, "Calls")
    p.rect(50,110,500,-50,fill=0)

    p.line(50,685,550,685)
    p.line(50,665,550,665)
    p.line(50,645,550,645)
    p.line(50,625,550,625)
    p.line(50,605,550,605)

    p.line(150,710,150,585)
    p.line(200,710,200,585)
    p.line(250,710,250,585)
    p.line(300,710,300,585)
    p.line(350,710,350,585)

    p.line(295,110,295,60)

    p.setFont("Helvetica", 8)
    p.drawString(155, 700, "Target")
    p.drawString(205, 700, "Actual")
    p.drawString(205, 690, "Month")
    p.drawString(255, 700, "Previous")
    p.drawString(255, 690, "Month")
    p.drawString(305, 700, "Target")
    p.drawString(305, 690, "Met?")
    p.drawString(355, 700, "Comments")

    p.drawString(55, 670, "Average Daily Call Time")
    p.drawString(155, 670, targetct)
    p.drawString(205, 670, realcalltime)
    if calltime >= target.calltime:
        p.drawString(305, 670, "Yes")
    else:
        p.drawString(305, 670, "No")

    p.drawString(55, 650, "New Applications")
    p.drawString(155, 650, str(targetapps))
    p.drawString(205, 650, str(monthtotals['totalapps__sum']))

    if monthtotals['totalapps__sum'] >= targetapps:
        p.drawString(305, 650, "Yes")
    else:
        p.drawString(305, 650, "No")

    p.drawString(55, 630, "Qualified Applications")
    p.drawString(155, 630, str(qapptarget))
    p.drawString(205, 630, str(qappsum))

    if qappsum >= qapptarget:
        p.drawString(305, 630, "Yes")
    else:
        p.drawString(305, 630, "No")

    p.drawString(55, 610, "Monthly Volume")

    p.drawString(55, 590, "Buying Customers")
    p.drawString(155, 590, str(targetbuying))

    p.setFont("Helvetica", 8)
    p.drawString(50, 545, "Please rate your performance:")

    p.setFont("Helvetica", 10)
    p.drawString(170, 545, "Excellent -")
    p.rect(220,545,10,10,fill=0)

    p.drawString(235, 545, "Very Good -")
    p.rect(293,545,10,10,fill=0)

    p.drawString(308, 545, "Good -")
    p.rect(343,545,10,10,fill=0)

    p.drawString(358, 545, "Average -")
    p.rect(405,545,10,10,fill=0)

    p.drawString(420, 545, "Below average -")
    p.rect(495,545,10,10,fill=0)

    p.drawString(510, 545, "Poor -")
    p.rect(540,545,10,10,fill=0)

    p.setFont("Helvetica", 8)
    p.drawString(55, 530, "What went well for you last month?")
    p.drawString(55, 500, "What could you have improved on?")
    p.drawString(55, 470, "How do you feel your performance compares to last month?")
    p.drawString(55, 440, "Would you like any additional training to improve your performance?")

    p.drawString(55, 380, "Do you have any suggestions for improving either the office environment or working procedures?")
    p.drawString(55, 345, "Is there anything else you would like to discuss?")

    p.drawString(55, 270, "Objectives and Goals for next month:")
    p.drawString(55, 220, "How do you intend to achieve this?")
    p.drawString(55, 170, "Additional Comments:")

    p.drawString(450, 270, "FU Date:")
    p.drawString(450, 220, "FU Date:")
    p.drawString(450, 170, "FU Date:")

    p.drawString(55, 100, "Two things to Continue")
    p.drawString(300, 100, "Two things to implement")

    p.drawString(50, 35, "Signed(Agent)")
    p.line(150,34,400,34)
    p.drawString(50, 15, "Signed(Supervisor)")
    p.line(150,14,400,14)

    p.drawString(450, 35, "Date:")
    p.line(480,34,550,34)
    p.drawString(450, 15, "Date")
    p.line(480,14,550,14)

    p.showPage()
    p.save()

    return response

@login_required  
def agent_month_review(request, agent, year, month): #done
    user = request.user.get_profile()
    type = int(user.agenttype)
    agent = get_object_or_404(Agent, slug=agent)
    if not request.user.has_perm('agents.super'):
        if not user.name == agent.name:
            slug = user.slug
            url = "/agent/" + slug
            return HttpResponseRedirect(url) 

    response = HttpResponse(mimetype='application/pdf')
    filename = "%s-AgentMonthReport-%s-%s.pdf" % (agent.slug, month, year)
    response['Content-Disposition'] = 'attachment; filename='+filename

    team = Teams.objects.get(name=agent.teamid)
    target = Targets.objects.get(name=team.targets)
    globalstats = Dstats.objects.filter(agent=agent).filter(isoyear=year).filter(month=month)
    sick = globalstats.filter(sickhours__gt = 0).count()
    working = globalstats.filter(prodhours__gt = 0).count()
    holiday = globalstats.filter(holhours__gt = 0).count()
    monthtotals = globalstats.aggregate(Sum('prodhours'), Sum('totalapps'), Sum('calltime'), Sum('callattempts'), Sum('sickhours'))
    if monthtotals['calltime__sum'] > 0:
        calltime = monthtotals['calltime__sum'] / (monthtotals['prodhours__sum'] / target.hours)
        calltime = int(calltime)
        realcalltime = humantime(calltime)

    qappsum = QualifiedApps.objects.filter(agent=agent).filter(month=month).filter(year=year).aggregate(Sum('qualifiedapps'),)
    qappsum = qappsum['qualifiedapps__sum']
    qapptarget = (target.commission3 / target.days) * agent.parttimedays

    targetct = humantime(target.calltime)
    targetapps = int(((monthtotals['prodhours__sum'] + monthtotals['sickhours__sum']) / target.hours) * Decimal(target.applications))
    targetbuying = str(target.drawingcust) + "%"

    p = canvas.Canvas(response)

    p.setFont("Helvetica", 16)
    titlestring = agent.name + " - Monthly Report: " + month_display(month) + "/" + year
    p.drawString(50,800, titlestring)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 820, team.name)

    p.setFont("Helvetica", 14)

    workingtext = "Working Days: " + str(working)
    sicktext = "Sick Days: " + str(sick)
    holidaytext = "Holiday Days: " + str(holiday)
    p.drawString(50, 770, workingtext)

    p.drawString(450, 770, holidaytext)

    p.drawString(50, 750, "Academy Position: ")

    p.drawString(250, 770, sicktext)

    p.drawString(250, 750, "Academy Year to Date: ")

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 720, "MONTHLY")
    p.rect(50,710,500,-125,fill=0)
    
    p.drawString(50, 560, "Review of last months objectives")
    p.rect(50,540,500,-125,fill=0)

    p.drawString(50, 400, "Team and Environment")
    p.rect(50,390,500,-80,fill=0)

    p.drawString(50, 290, "Action Plan")
    p.rect(50,280,500,-140,fill=0)

    p.drawString(50, 120, "Calls")
    p.rect(50,110,500,-50,fill=0)

    p.line(50,685,550,685)
    p.line(50,665,550,665)
    p.line(50,645,550,645)
    p.line(50,625,550,625)
    p.line(50,605,550,605)

    p.line(150,710,150,585)
    p.line(200,710,200,585)
    p.line(250,710,250,585)
    p.line(300,710,300,585)
    p.line(350,710,350,585)

    p.line(295,110,295,60)

    p.setFont("Helvetica", 8)
    p.drawString(155, 700, "Target")
    p.drawString(205, 700, "Actual")
    p.drawString(205, 690, "Month")
    p.drawString(255, 700, "Previous")
    p.drawString(255, 690, "Month")
    p.drawString(305, 700, "Target")
    p.drawString(305, 690, "Met?")
    p.drawString(355, 700, "Comments")

    p.drawString(55, 670, "Average Daily Call Time")
    p.drawString(155, 670, targetct)
    p.drawString(205, 670, realcalltime)
    if calltime >= target.calltime:
        p.drawString(305, 670, "Yes")
    else:
        p.drawString(305, 670, "No")

    p.drawString(55, 650, "New Applications")
    p.drawString(155, 650, str(targetapps))
    p.drawString(205, 650, str(monthtotals['totalapps__sum']))

    if monthtotals['totalapps__sum'] >= targetapps:
        p.drawString(305, 650, "Yes")
    else:
        p.drawString(305, 650, "No")

    p.drawString(55, 630, "Qualified Applications")
    p.drawString(155, 630, str(qapptarget))
    p.drawString(205, 630, str(qappsum))

    if qappsum >= qapptarget:
        p.drawString(305, 630, "Yes")
    else:
        p.drawString(305, 630, "No")

    p.drawString(55, 610, "Monthly Volume")

    p.drawString(55, 590, "Buying Customers")
    p.drawString(155, 590, str(targetbuying))

    p.setFont("Helvetica", 8)
    p.drawString(50, 545, "Please rate your performance:")

    p.setFont("Helvetica", 10)
    p.drawString(170, 545, "Excellent -")
    p.rect(220,545,10,10,fill=0)

    p.drawString(235, 545, "Very Good -")
    p.rect(293,545,10,10,fill=0)

    p.drawString(308, 545, "Good -")
    p.rect(343,545,10,10,fill=0)

    p.drawString(358, 545, "Average -")
    p.rect(405,545,10,10,fill=0)

    p.drawString(420, 545, "Below average -")
    p.rect(495,545,10,10,fill=0)

    p.drawString(510, 545, "Poor -")
    p.rect(540,545,10,10,fill=0)

    p.setFont("Helvetica", 8)
    p.drawString(55, 530, "What went well for you last month?")
    p.drawString(55, 500, "What could you have improved on?")
    p.drawString(55, 470, "How do you feel your performance compares to last month?")
    p.drawString(55, 440, "Would you like any additional training to improve your performance?")

    p.drawString(55, 380, "Do you have any suggestions for improving either the office environment or working procedures?")
    p.drawString(55, 345, "Is there anything else you would like to discuss?")

    p.drawString(55, 270, "Objectives and Goals for next month:")
    p.drawString(55, 220, "How do you intend to achieve this?")
    p.drawString(55, 170, "Additional Comments:")

    p.drawString(450, 270, "FU Date:")
    p.drawString(450, 220, "FU Date:")
    p.drawString(450, 170, "FU Date:")

    p.drawString(55, 100, "Two things to Continue")
    p.drawString(300, 100, "Two things to implement")

    p.drawString(50, 35, "Signed(Agent)")
    p.line(150,34,400,34)
    p.drawString(50, 15, "Signed(Supervisor)")
    p.line(150,14,400,14)

    p.drawString(450, 35, "Date:")
    p.line(480,34,550,34)
    p.drawString(450, 15, "Date")
    p.line(480,14,550,14)

    p.showPage()
    p.save()

    return response
    
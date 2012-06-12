# Create your views here.
from django.http import HttpResponsePermanentRedirect, Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext, Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from planner.models import Ticket
from planner.forms import TicketForm, NewTicketForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

"""
edits the planner item in it's own display, showing full information
"""
@login_required
def object_detail_edit(request, object_id): #done
    if request.user.has_perm('agents.super'):
        if request.method == 'POST':
            ticket = Ticket.objects.get(pk=object_id)
            form = TicketForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/planner/'+object_id)
        else:
            ticket = Ticket.objects.get(pk=object_id)
            form = TicketForm(instance=ticket)
            
        template = 'planner/edit.html'
        context = RequestContext(request, {'form':form, 'ticket':ticket})
        
        response = render_to_response(template, context)
        
        return response
    else:
        currentUrl = request.get_full_path()
        template = 'general/badpermissions.html'
        context = RequestContext(request, {'currenturl':currentUrl})

        response = render_to_response(template, context)
        
        return response

"""
View used to add a new admin planner item
"""
@login_required
def object_detail_add(request): #done
    if request.user.has_perm('agents.super'):
        if request.method == 'POST':
            form = NewTicketForm(request.POST)
            if form.is_valid():
                new_ticket = form.save()
                object_id = new_ticket.id
                return HttpResponseRedirect('/planner/'+str(object_id))
        else:
            form = NewTicketForm()
            
        template = 'planner/add.html'
        context = RequestContext(request, {'form':form,})
        
        response = render_to_response(template, context)
        
        return response
    else:
        currentUrl = request.get_full_path()
        template = 'general/badpermissions.html'
        context = RequestContext(request, {'currenturl':currentUrl})

        response = render_to_response(template, context)
        
        return response

"""
List display of admin planner items
"""
@login_required 
def get_planner_list(request): #done
    if request.user.has_perm('agents.super'):
        object_list = Ticket.objects.exclude(status='closed').order_by('-priority','-updated_on')
        oldobject_list = Ticket.objects.filter(status='closed').order_by('-created_on')
        template = 'planner/ticket_list.html'
        context = RequestContext(request, {'object_list':object_list, 'oldobject_list':oldobject_list})
        
        response = render_to_response(template, context)
        
        return response
    else:
        currentUrl = request.get_full_path()
        template = 'general/badpermissions.html'
        context = RequestContext(request, {'currenturl':currentUrl})

        response = render_to_response(template, context)
        
        return response

"""
Shows the full details of a planner item.
"""
@login_required        
def ticket_detail(request, object_id): #done
    if request.user.has_perm('agents.super'):
        object = get_object_or_404(Ticket, id=object_id)
        template = 'planner/ticket_detail.html'
        context = RequestContext(request, {'object':object, })
        
        response = render_to_response(template, context)
        
        return response
    else:
        currentUrl = request.get_full_path()
        template = 'general/badpermissions.html'
        context = RequestContext(request, {'currenturl':currentUrl})

        response = render_to_response(template, context)
        
        return response
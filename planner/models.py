from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import admin
from django.utils.html import strip_tags
from django.forms import ModelChoiceField
from django.forms import ModelForm


TICKET_STATUS_CHOICES = (
    ('new', 'New'),
    ('accepted', 'Accepted'),
    ('assigned', 'Assigned'),
    ('reopened', 'Reopened'),
    ('closed', 'Closed'),
)
PRIORITY_STATUS_CHOICES = (
    ('1', 'Low'),
    ('2', 'Normal'),
    ('3', 'High'),
    ('4', 'Urgent'),
    ('5', 'Critical'),
)

# model for Tickets
class Ticket(models.Model):
    assigned_to = models.ForeignKey(User, null=True, blank=True, related_name="assigned_to")
    received_from = models.ForeignKey(User, null=True, blank=True, related_name="received_from")
    status = models.CharField(max_length=20, choices=TICKET_STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_STATUS_CHOICES, default='new')
    description = models.TextField()
    created_on = models.DateTimeField('date created', auto_now_add=True)
    updated_on = models.DateTimeField('date updated', auto_now=True)
    due_on = models.DateField('Due Date')

    def name(self):
        return strip_tags(self.description.split('\n', 1)[0])
    
    def __unicode__(self):
        return strip_tags(self.description.split('\n', 1)[0])
        
    class Meta:
        verbose_name = "Admin Task"
        verbose_name_plural = "Admin Tasks"
        
    def save(self):
        if self.created_on == self.updated_on:
            send_mail('New Task Generated', 'A new task has been created:\n ' + self.description, 'admin@osiris', [self.assigned_to.email], fail_silently=True)
        super(Ticket, self).save()

class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        # Return a string of the format: "firstname lastname (username)"
        return "%s (%s)"%(obj.get_full_name(), obj.username)

class TicketAdminForm(ModelForm):
    assigned_to = UserModelChoiceField(User.objects.filter(groups__name='Supervisors').filter(is_staff=True).order_by('first_name'))
    received_from = UserModelChoiceField(User.objects.filter(groups__name='Supervisors').filter(is_staff=True).order_by('first_name'))
    class Meta:
        model = Ticket
    
# admin meta-data for ticket model
class TicketAdmin(admin.ModelAdmin):
    list_filter = ('status', 'priority')
    list_display = ('name', 'status', 'assigned_to', 'received_from')
    form = TicketAdminForm
    actions = ['mark_accepted', 'mark_assigned', 'mark_reopened', 'mark_closed']

    def mark_accepted(self, request, queryset):
        rows_updated = queryset.update(status="accepted")
        if rows_updated == 1:
            message_bit = "1 Task was"
        else:
            message_bit = "%s Tasks were" % rows_updated
        self.message_user(request, "%s successfully marked as accepted." % message_bit)
    mark_accepted.short_description = "Mark selected Tasks as accepted"

    def mark_assigned(self, request, queryset):
        rows_updated = queryset.update(status="assigned")
        if rows_updated == 1:
            message_bit = "1 Task was"
        else:
            message_bit = "%s Tasks were" % rows_updated
        self.message_user(request, "%s successfully marked as assigned." % message_bit)
    mark_assigned.short_description = "Mark selected Tasks as assigned"

    def mark_reopened(self, request, queryset):
        rows_updated = queryset.update(status="reopened")
        if rows_updated == 1:
            message_bit = "1 Task was"
        else:
            message_bit = "%s Tasks were" % rows_updated
        self.message_user(request, "%s successfully marked as reopened." % message_bit)
    mark_reopened.short_description = "Mark selected Tasks as reopened"

    def mark_closed(self, request, queryset):
        rows_updated = queryset.update(status="closed")
        if rows_updated == 1:
            message_bit = "1 Task was"
        else:
            message_bit = "%s Tasks were" % rows_updated
        self.message_user(request, "%s successfully marked as closed." % message_bit)
    mark_closed.short_description = "Mark selected Tasks as closed"

admin.site.register(Ticket, TicketAdmin)
from django.db import models
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User, UserManager
from django.contrib import admin
from team.models import Teams
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

"""
The agent model acts as a user profile for the users.
"""
class Agent(models.Model):
    AGENT_CHOICES = (
        ('0', 'Agent'),
        ('1', 'Supervisor'),
        ('2', 'Admin'),
        )
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, unique=True)
    birthday = models.DateField('Date of Birth')
    startdate = models.DateField('Date Started')
    academystartdate = models.DateField('Academy Start Date', blank=True, null=True)
    teamid = models.ForeignKey(Teams, blank=True, null=True, on_delete=models.SET_NULL)
    ext = models.CharField('Ext.', max_length=3, blank=True, null=True)
    agenttype = models.CharField('Agent Type', max_length=1, choices=AGENT_CHOICES, default=0)
    haveleft = models.NullBooleanField('On Leave', blank=True, default=0)
    permanentleave = models.NullBooleanField('Permanent Leave', blank=True, default=0)
    leavereason = models.TextField('Reason for Leaving', blank=True, null=True)
    leavedate = models.DateField('Date Left', null=True, blank=True,)
    picture = models.FileField(upload_to="agents/", blank=True, null=True, default="agents/placeholderavatar.jpeg") #Using File Field for now until I can install PyImagLib
    slug = models.SlugField(max_length=120, unique=True)
    parttime = models.BooleanField('Part Time', default=False)
    parttimedays = models.IntegerField('Part Time Days', default=5)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
        permissions = (
            ("agent", "Agent"),
            ("super", "Supervisor"),
            ("admin", "Admin"),
            ("saul", "Saul"),
            )

class Training(models.Model):
    """
    The training model will be used to record training that an agent has undergone. At this time it contains 4 choices
    This may change in the future
    It also has file upload options to allow for the inclusion of pdf documents that are associated to training
    """
    TRAINING_TYPE_CHOICES = (
        ('G', 'General'),
        ('W', 'Return to Work'),
        ('C', 'Compliance'),
        ('R', 'Monthly Review'),
        ('T', 'Coaching/Training'),
        ('I', 'Induction'),
        ('M', 'Customer Maintenance'),
        ('P', 'Personal Files'),
    )
    agent = models.ForeignKey(Agent)
    trainingtype = models.CharField('Type of Training', max_length=1, choices=TRAINING_TYPE_CHOICES)
    date = models.DateField('Date of Training')
    files = models.FileField(upload_to="training/", blank=True, null=True) 
    class Meta:
        verbose_name = "Training"
        verbose_name_plural = "Training"
        ordering = ['-date']
    def __unicode__(self):
        return u'%s Training' % (self.agent)

"""
The incentive model is used to note achievements that the agent has gathered
"""
class Incentive(models.Model):
    INCENTIVE_TYPE_CHOICES = (
        ('A', 'Acheivement'),
        ('W', 'Warning'),
    )
    agent = models.ForeignKey(Agent)
    incentive = models.CharField('Type of Incentive', max_length=1, choices=INCENTIVE_TYPE_CHOICES)
    date = models.DateField('Date')
    comment = models.TextField('Reason', blank=True, null=True)
    class Meta:
        verbose_name = "Incentive"
        verbose_name_plural = "Incentives"
        ordering = ['-date']
    def __unicode__(self):
        return u'%s incentive' % (self.agent)

"""
The coaching and compliance model marks down coaching scores.
"""
class CoachingAndCompliance(models.Model):
    CANDC_TYPE_CHOICES = (
        ('1', 'Coaching'),
        ('2', 'Compliance'),
    )
    agent = models.ForeignKey(Agent)
    date = models.DateField('Date')
    type = models.CharField('Type', max_length=1, choices=CANDC_TYPE_CHOICES)
    score = models.IntegerField('Score')
    notes = models.TextField()
    class Meta:
        verbose_name = "Coaching and Compliance Record"
        verbose_name_plural = "Coaching and Compliance Records"
        ordering = ['-date']
    def __unicode__(self):
        return u'%s Coaching and Compliance Record' % (self.agent)

"""
Below are the various admin objects that are used to manage to models.
"""
class UserProfileInline(admin.StackedInline):
    model = Agent
    max_num = 1
    can_delete = False
    fieldsets = [
        ('Basic Information', {'fields': ['name', 'startdate', 'birthday', 'slug', 'teamid', 'agenttype', 'user', 'ext', 'picture']}),
        ('Working Status', {'fields': [('haveleft', 'permanentleave', 'leavedate'), 'leavereason'], 'classes': ['collapse']}),
    ]
    prepopulated_fields = {"slug": ("name",)}
    
class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]
    ordering = ['-is_staff']

class AgentAdmin(admin.ModelAdmin):
    """
    Currently contains some redundant field sets for information that will be added later
    """
    list_display = ('name', 'teamid', 'ext', 'haveleft', 'startdate', 'birthday')
    fieldsets = [
        ('Basic Information', {'fields': ['name', 'startdate', 'birthday', 'academystartdate', 'slug', 'teamid', 'agenttype', 'user', 'ext', 'picture', 'parttime', 'parttimedays']}),
        ('Working Status', {'fields': ['haveleft', 'permanentleave', 'leavedate', 'leavereason'], 'classes': ['collapse']}),
    ]
    search_fields = ['name']
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ['teamid', 'haveleft']
    ordering = ['-teamid']
    actions = ['mark_onleave', 'mark_onpermanentleave', 'mark_returned']

    def mark_onleave(self, request, queryset):
        queryset.update(haveleft=True)
        rows_updated = queryset.update(leavedate=datetime.today())
        if rows_updated == 1:
            message_bit = "1 Agent was"
        else:
            message_bit = "%s Agents were" % rows_updated
        self.message_user(request, "%s successfully marked as on leave." % message_bit)
    mark_onleave.short_description = "Mark selected Agents as on leave"

    def mark_onpermanentleave(self, request, queryset):
        queryset.update(haveleft=True)
        queryset.update(permanentleave=True)
        rows_updated = queryset.update(leavedate=datetime.today())
        if rows_updated == 1:
            message_bit = "1 Agent was"
        else:
            message_bit = "%s Agents were" % rows_updated
        self.message_user(request, "%s successfully marked as left." % message_bit)
    mark_onpermanentleave.short_description = "Mark selected Agents as left"

    def mark_returned(self, request, queryset):
        queryset.update(haveleft=False)
        rows_updated = queryset.update(permanentleave=False)
        if rows_updated == 1:
            message_bit = "1 Agent was"
        else:
            message_bit = "%s Agents were" % rows_updated
        self.message_user(request, "%s successfully marked as returned." % message_bit)
    mark_returned.short_description = "Mark selected Agents as returned"

class TrainingAdmin(admin.ModelAdmin):
    list_display = ('agent', 'trainingtype', 'date')
    list_filter = ['trainingtype']
    fieldsets = [
        ('Training', {'fields': [('agent', 'trainingtype', 'date', 'files')]}),
    ]
    search_fields = ['agent__name']

class IncentiveAdmin(admin.ModelAdmin):
    list_display = ('agent', 'incentive', 'date')
    search_fields = ['agent__name']

class CandCAdmin(admin.ModelAdmin):
    list_display = ('agent', 'type', 'date', 'score')
    search_fields = ['agent__name']

"""
The User model admin throws a weird error when you unregister it and try to reregister with a custom one.
TODO: Figure out what the hell the user admin is doing.
"""
#admin.site.unregister(User)
#admin.site.register(User, AuthUserAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Training, TrainingAdmin)
admin.site.register(Incentive, IncentiveAdmin)
admin.site.register(CoachingAndCompliance, CandCAdmin)

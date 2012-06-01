from django.db import models
from datetime import datetime, timedelta, time
from django.contrib import admin
from team.models import Teams
from agents.models import Agent

# Create your models here

MONTH_CHOICES = (
    ('jan', 'January'),
    ('feb', 'February'),
    ('mar', 'March'),
    ('apr', 'April'),
    ('may', 'May'),
    ('jun', 'June'),
    ('jul', 'July'),
    ('aug', 'August'),
    ('sep', 'September'),
    ('oct', 'October'),
    ('nov', 'November'),
    ('dec', 'December'),
)

class Dstats(models.Model):
    agent = models.ForeignKey(Agent, blank=True, null=True)
    team = models.ForeignKey(Teams, blank=True, null=True)
    date = models.DateField('Stat Date', default=datetime.today()-timedelta(days=1))
    isoweek = models.IntegerField('ISO Week')
    year = models.IntegerField('Year')
    isoyear = models.IntegerField('ISO Year')
    month = models.CharField('ISO Month', max_length=3, choices=MONTH_CHOICES)
    calltime = models.IntegerField('Call Time', default=0)
    callattempts = models.IntegerField('Call Attempts', default=0)
    prodhours = models.DecimalField('Productive Hours', max_digits=4, decimal_places=2, default=7.5)
    innovhours = models.DecimalField('Innovation Hours', max_digits=4, decimal_places=2, default=0)
    sickhours = models.DecimalField('Sick Hours', max_digits=3, decimal_places=2, default=0)
    holhours = models.DecimalField('Holiday Hours', max_digits=3, decimal_places=2, default=0)
    otherhours = models.DecimalField('Other Hours', max_digits=3, decimal_places=2, default=0)
    brandedapps = models.IntegerField('Branded Card Apps', default=0)
    ukfapps = models.IntegerField('UK Fuel Card Apps', default=0)
    totalapps = models.IntegerField('Total Apps', default=0, editable=False) 
    
    class Meta:
        verbose_name = "Daily Stat"
        verbose_name_plural = "Daily Stats"
        unique_together = ("agent", "date")
    def save(self):
        if not self.team:
            self.team = self.agent.teamid
        self.year = self.date.year
        thedate = self.date
        self.isoweek = thedate.isocalendar()[1]
        self.totalapps = self.brandedapps + self.ukfapps
        super(Dstats, self).save()
    def __unicode__(self):
        return u'%s - %s' % (self.agent, self.date)

class QualifiedApps(models.Model):
    agent = models.ForeignKey(Agent)
    month = models.CharField('ISO Month', max_length=3, choices=MONTH_CHOICES)
    year = models.IntegerField('Year')
    qualifiedapps = models.IntegerField('Qualified Apps', default=0)
    class Meta:
        verbose_name = "Qualified Apps"
        verbose_name_plural = "Qualified Apps"
        ordering = ['agent']
    def __unicode__(self):
        return u'%s %s apps' % (self.agent, self.month)#

class WeeklyStats(models.Model):
    agent = models.ForeignKey(Agent, blank=True, null=True)
    team = models.ForeignKey(Teams, blank=True, null=True)
    isoweek = models.IntegerField('ISO Week')
    isomonth = models.CharField('ISO Month', max_length=3, choices=MONTH_CHOICES)
    isoyear = models.IntegerField('Year')
    volume = models.IntegerField('Volume')
    drawcust = models.IntegerField('Drawing Customers')
    class Meta:
        verbose_name = "Weekly Stat"
        verbose_name_plural = "Weekly Stats"
        ordering = ['-isoyear', 'isoweek', 'agent']
    def __unicode__(self):
        return u'%s Week %s Year %s Volume Stats' % (self.agent, self.isoweek, self.isoyear)
    def save(self):
        self.team = self.agent.teamid
        super(WeeklyStats, self).save()

class MonthlyStats(models.Model):
    agent = models.ForeignKey(Agent)
    team = models.ForeignKey(Teams)
    isomonth = models.CharField('ISO Month', max_length=3, choices=MONTH_CHOICES)
    isoyear = models.IntegerField('ISO Year')
    volume = models.IntegerField('Volume')
    drawcust = models.IntegerField('Drawing Customers')
    growth = models.IntegerField('Volume Growth')
    class Meta:
        verbose_name = "Monthly Stat"
        verbose_name_plural = "Monthly Stats"
        ordering = ['-isoyear', 'isomonth', 'agent']
    def __unicode__(self):
        return u'%s Month %s Year %s Volume Stats' % (self.agent, self.isomonth, self.isoyear)
    def save(self):
        self.team = self.agent.teamid
        super(MonthlyStats, self).save()


class StatsAdmin(admin.ModelAdmin):
    list_display = ('agent', 'team', 'date', 'isoweek', 'year', 'sickhours', 'holhours', 'totalapps')
    list_filter = ['team', 'isoweek', 'isoyear', 'sickhours', 'month']
    fieldsets = [
        ('Daily Stat', {'fields': ['agent', ('calltime', 'callattempts'), ('brandedapps', 'ukfapps'), ('prodhours', 'innovhours', 'otherhours'), ('sickhours', 'holhours'), ('date', 'month', 'isoyear')]}),
    ]
    ordering = ['-date']
    search_fields = ['agent__name']
    #('date', 'isoweek', 'year'),

class QualifiedAdmin(admin.ModelAdmin):
    list_display = ('agent', 'month', 'year', 'qualifiedapps')
    list_filter = ['month', 'year']
    fieldsets = [
        ('Qualified Apps', {'fields': ['agent', 'qualifiedapps', 'month', 'year']})
    ]
    search_fields = ['agent__name']
    ordering = ['month']

class WeeklyAdmin(admin.ModelAdmin):
    list_display = ('agent', 'isoweek', 'isomonth', 'isoyear', 'volume', 'drawcust')
    list_filter = ['isoweek', 'isomonth', 'isoyear']
    fieldsets = [
        ('Weekly Volume', {'fields': ['agent', ('isoweek', 'isomonth', 'isoyear'), ('volume', 'drawcust')]}),
    ]
    search_fields = ['agent__name']
    ordering = ['-isoweek', '-isoyear']

class MonthlyAdmin(admin.ModelAdmin):
    list_display = ('agent', 'isomonth', 'isoyear', 'volume', 'drawcust')
    list_filter = ['isomonth', 'isoyear']
    fieldsets = [
        ('Monthly Volume', {'fields': ['agent', ('isomonth', 'isoyear'), ('volume', 'growth', 'drawcust')]}),
    ]
    search_fields = ['agent__name']
    ordering = ['-isomonth']

admin.site.register(Dstats, StatsAdmin) 
admin.site.register(QualifiedApps, QualifiedAdmin)
admin.site.register(WeeklyStats, WeeklyAdmin)
admin.site.register(MonthlyStats, MonthlyAdmin)

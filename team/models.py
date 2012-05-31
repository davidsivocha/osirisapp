from django.db import models
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User, UserManager
from django.contrib import admin

class Supers(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    extension = models.CharField(max_length=3, blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True)
    class Meta:
        verbose_name = "Supervisor"
        verbose_name_plural = "Supervisors"
    def __unicode__(self):
        return self.name

class Targets(models.Model):
    name = models.CharField(max_length=50)
    volumelower = models.IntegerField('Volume Lower Target')
    volumeupper = models.IntegerField('Volume Upper Target')
    calltime = models.IntegerField('Call Time Target')
    callattempts = models.IntegerField('Call Attempts Target')
    applications = models.DecimalField('Apps Target', max_digits=3, decimal_places=2)
    commission1 = models.IntegerField('Commission Band 1')
    commission2 = models.IntegerField('Commission Band 2')
    commission3 = models.IntegerField('Commission Band 3')
    hours = models.DecimalField('Hours', max_digits=3, decimal_places=2)
    days = models.IntegerField('Days')
    drawingcust = models.DecimalField('Customer Draw Percentage', max_digits=4, decimal_places=2)
    class Meta:
        verbose_name = "Targets"
        verbose_name_plural = "Targets"
    def __unicode__(self):
        return self.name

class Teams(models.Model):
    BUTTON_CHOICES = (
        ('0E59AE', 'Blue'),
        ('91BD09', 'Green'),
        ('000000', 'Black'),
        ('CC0000', 'Red'),
        ('FF5C00', 'Orange'),
        ('2DAEBF', 'Turqoise'),
        ('BBBBBB', 'Grey'),
        )
    TYPE_CHOICES = (
        ('1', 'Internal'),
        ('2', 'Websales'),
        ('3', 'Cust/Maintenance'),
        ('4', 'Administration'),
        ('5', 'Europe'),
        )
    COUNTRY_CHOICES = (
        ('gb', 'Great Britain'),
        ('be', 'Belgium'),
        ('de', 'Germany'),
        ('it', 'Italy'),
        ('es', 'Spain'),
        ('nl', 'Holland'),
        )
    name = models.CharField(max_length=50)
    supervisor = models.ForeignKey(Supers, blank=True, null=True, on_delete=models.SET_NULL)
    products = models.TextField(blank=True, null=True)
    voltarget = models.IntegerField('Volume Target', blank=True, null=True)
    logo = models.FileField(upload_to="logo/", blank=True, null=True)  #Using File Field for now until I can install PyImagLib
    button = models.CharField('Button Type', max_length=6, choices=BUTTON_CHOICES)
    teamtype = models.CharField('Team Type', max_length=1, choices=TYPE_CHOICES, default=1)
    slug = models.SlugField(max_length=120, unique=True)
    targets = models.ForeignKey(Targets, blank=True, null=True, on_delete=models.SET_NULL, default=1)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        ordering = ['teamtype']

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'supervisor')
    fieldsets = [
        ('Team Information', {'fields': [('name', 'supervisor'), 'slug', 'logo', ('teamtype', 'country'), 'button']}),
        ('Targets and Products', {'fields': ['voltarget', 'targets', 'products'], 'classes': ['collapse']}),
    ]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    list_filter = ['supervisor', 'teamtype']
    

class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'extension')
    fieldsets = [
        ('Supervisor Information', {'fields': ['name', ('email', 'extension'), 'slug']}),
    ]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    

class TargetAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Supers, SupervisorAdmin)
admin.site.register(Teams, TeamAdmin)
admin.site.register(Targets, TargetAdmin)
from django.db import models
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User, UserManager
from django.contrib import admin
from team.models import Teams
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from agents.models import Agent

MONTH_CHOICES = (
	('jan', 'January'),
	('feb', 'February'),
	('mar', 'March'),
	('apr', 'April'),
	('may', 'May'),
	('jun', 'June'),
	('jul', 'July'),
	('sep', 'September'),
	('oct', 'October'),
	('nov', 'November'),
	('dec', 'December'),
)

MEDAL_CHOICES = (
	('pla', 'Platinum'),
	('gol', 'Gold'),
	('sil', 'Silver'),
	('bro', 'March'),
)
'''
class Medals(models.Model):
	agent = models.ForeignKey(Agent)
	month = models.CharField('ISO Month', max_length=3, choices=MONTH_CHOICES)
	year = models.IntegerField('Year')
	medal = models.CharField('Medal', max_length=3, choices=MEDAL_CHOICES)
	class Meta:
		verbose_name = "Medal"
		verbose_name_plural = "Medals"
	def __unicode__(self):
		return u'%s %s Medal' % (self.agent, self.month)
	


class MedalAdmin(admin.ModelAdmin):
	list_display = ('agent', 'medal', 'month', 'year')
	list_filter = ['medal', 'month', 'year']
	search_fields = ['agent__name']
	ordering = ['-month']
	def has_add_permission(self, request):
		return False

admin.site.register(Medals, MedalAdmin) 
'''
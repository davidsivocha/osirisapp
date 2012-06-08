from django.db import models
from team.models import Teams
from django.contrib import admin

# Create your models here.

# campaign model
# fields:
# campaign name 
# team 
# # of leads bought
# price
# start date
# end date
# campaign notes

# campaign stats model
# fields:
# date
# # of applications

# campaign week stats model
# fields:
# week
# volume

# admin models
# campaign admin
# campaign stats admin
# campaign weekly stats admin


# functions
# price / #ofapps = cost per applications
# #ofapps / #ofleads = percentage return (what percentage of leads signed up.)
# if enddate < today then assert(campaign over) else assert(campaign running)

# forms
# new campaign form
# dailystats form
# weeklystats form

# analytics integration

class Campaign(models.Model):
	name = models.CharField(max_length=50)
	team = models.ForeignKey(Teams)
	numleads = models.IntegerField('Number of Leads Bought', default=0)
	cost = models.IntegerField('Cost of Data Purchase', default=0)
	startdate = models.DateField('Campaign Start Date')
	enddate = models.DateField('Campaign End Date')
	notes = models.TextField('Campaign Notes', blank=True, null=True)

	class Meta:
		verbose_name = "Campaign"
		verbose_name_plural = "Campaigns" 
	def __unicode__(self):
		return u': %s' % (self.name)

class CampaignStats(models.Model):
	campaign = models.ForeignKey(Campaign)
	date = models.DateField('Stat Date')
	numapps = models.IntegerField('Number of Apps', default=0)

	class Meta:
		verbose_name = "Campaign Stat"
		verbose_name_plural = "Campaign Stats" 
	def __unicode__(self):
		return u'%s Stat: %s' % (self.campaign, self.date)

class CampaignAdmin(admin.ModelAdmin):
	list_display = ('name', 'cost', 'numleads', 'startdate', 'enddate')
	list_filter = ['team', ]
class CampaignStatAdmin(admin.ModelAdmin):
	list_display = ('campaign', 'date', 'numapps')
	list_filter = ['campaign', ]

admin.site.register(Campaign, CampaignAdmin)
admin.site.register(CampaignStats, CampaignStatAdmin)
from django import forms
from django.forms import ModelForm
from django.forms.widgets import *
from datetime import datetime, timedelta, time
from team.models import Teams
from campaign.models import Campaign

"""
Model form for creating campaigns
"""
class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        widgets = {
        	'startdate': TextInput(attrs={'class':'date'}),
        	'enddate': TextInput(attrs={'class':'date'}),
        }
    

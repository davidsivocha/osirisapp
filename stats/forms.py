from django import forms
from django.forms.widgets import *
from datetime import datetime, timedelta, time
from team.models import Targets, Teams
from agents.models import Agent

class QAppsInput(forms.Form):
    pk = forms.IntegerField(widget=forms.HiddenInput)
    agent = forms.CharField(widget=forms.TextInput(attrs={'class':'name', 'readonly':'readonly' }))
    qapps = forms.IntegerField(widget=forms.TextInput(attrs={'required':'required'}))
    
class WstatsInput(forms.Form):
    pk = forms.IntegerField(widget=forms.HiddenInput)
    agent = forms.CharField(widget=forms.TextInput(attrs={'class':'name', 'readonly':'readonly' }))
    volume = forms.IntegerField(widget=forms.TextInput(attrs={'required':'required'}))
    drawcust = forms.IntegerField(widget=forms.TextInput(attrs={'required':'required'}))

class DstatsInput(forms.Form):
    pk = forms.IntegerField(widget=forms.HiddenInput)
    agent = forms.CharField(widget=forms.TextInput(attrs={'class':'name', 'readonly':'readonly' }))
    callin = forms.CharField(widget=forms.TextInput(attrs={'class':'time', 'required':'required'}))
    callout = forms.CharField(widget=forms.TextInput(attrs={'class':'time', 'required':'required'}))
    callattempts = forms.IntegerField(widget=forms.TextInput(attrs={'required':'required'}))
    brandedcardapps = forms.IntegerField(widget=forms.TextInput(attrs={'required':'required'}))
    productivehours = forms.DecimalField(widget=forms.TextInput(attrs={'required':'required'}))
    innovationhours = forms.DecimalField(widget=forms.TextInput(attrs={'required':'required'}))
    otherhours = forms.DecimalField(widget=forms.TextInput(attrs={'required':'required'}))
    sickhours = forms.DecimalField(widget=forms.TextInput(attrs={'required':'required'}))
    holidayhours = forms.DecimalField(widget=forms.TextInput(attrs={'required':'required'}))
    def clean(self):
        cleaned_data = self.cleaned_data
        key = cleaned_data.get("pk")
        callattempts = cleaned_data.get("callattempts")
        prodhours = cleaned_data.get("productivehours")
        innovhours = cleaned_data.get("innovationhours")
        otherhours = cleaned_data.get("otherhours")
        sickhours = cleaned_data.get("sickhours")
        holhours = cleaned_data.get("holidayhours")
        total = prodhours + innovhours + otherhours + sickhours + holhours
        agent = Agent.objects.get(pk=key)
        team = Teams .objects.get(name=agent.teamid)
        targets = Targets.objects.get(name=team.targets)

        if total > targets.hours:
            msg = "Too many hours logged for this agent!"
            self._errors["productivehours"] = self.error_class([msg])
            del cleaned_data["productivehours"]
        if callattempts > (targets.callattempts * 3):
            msg = "Too many call attempts for this agent!"
            self._errors["callattempts"] = self.error_class([msg])
            del cleaned_data["callattempts"]
        # Always return the full collection of cleaned data.
        return cleaned_data
 
class DstatsGlobal(forms.Form):
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
    date = forms.DateField(widget=forms.TextInput(attrs={'class':'date'}))
    isomonth = forms.ChoiceField(choices=MONTH_CHOICES)
    isoyear = forms.IntegerField()

class DstatsGlobalInternal(forms.Form):
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
    date = forms.DateField(widget=forms.TextInput(attrs={'class':'date'}))
    isomonth = forms.ChoiceField(choices=MONTH_CHOICES)
    isoyear = forms.IntegerField()
    noapps = forms.BooleanField(required=False)
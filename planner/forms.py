from django.forms import ModelForm, Textarea, TextInput, Select
from django.forms import ModelChoiceField
from django.contrib.auth.models import User
from planner.models import Ticket

class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        # Return a string of the format: "firstname lastname (username)"
        return "%s (%s)"%(obj.get_full_name(), obj.username)

class TicketForm(ModelForm):
    assigned_to = UserModelChoiceField(User.objects.filter(groups__name='Supervisors').filter(is_staff=True).order_by('first_name'))
    received_from = UserModelChoiceField(User.objects.filter(groups__name='Supervisors').filter(is_staff=True).order_by('first_name'))
    class Meta:
        model = Ticket
        widgets = {
            'description': Textarea(attrs={'class': 'input-xlarge span8', 'rows': 10}),
            'due_on': TextInput(attrs={'class':'date',}),
            'assigned_to': Select(attrs={'class':'typeahead',}),
            'received_from': Select(attrs={'class':'typeahead',}),
        }
        
class NewTicketForm(ModelForm):
    assigned_to = UserModelChoiceField(User.objects.filter(groups__name='Supervisors').filter(is_staff=True).order_by('first_name'))
    received_from = UserModelChoiceField(User.objects.filter(groups__name='Supervisors').filter(is_staff=True).order_by('first_name'))
    class Meta:
        model = Ticket
        exclude = ('status',)
        widgets = {
            'description': Textarea(attrs={'class': 'input-xlarge span8', 'rows': 10}),
            'due_on': TextInput(attrs={'class':'date',}),
            'assigned_to': Select(attrs={'class':'typeahead',}),
            'received_from': Select(attrs={'class':'typeahead',}),
        }
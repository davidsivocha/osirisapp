from django import template
from datetime import datetime, timedelta, time


register = template.Library()

"""
Converts minutes(integer) into a human readable time i.e. 127 minutes becomes 2:07
"""
@register.filter
def humantime(value):
    if value is None:
        return ''
    if not type(value)==int:
        return ''
    value = int(value)
    if value > 0:
        hours = value / 60
        minutes = value - (hours*60)
    
        return "%i:%02i" % (hours, minutes)
    else:
        return

@register.filter(name='lookup')
def lookup(dict, index):
    if index in dict:
        return dict[index]
    return ''

"""
Short tag used to print the site url
"""
@register.simple_tag()    
def print_site_url():
    string = "http://osirisapp.com/"
    return string

"""
Simple tag used to show the current time and date on certain pages.
"""
@register.tag(name='current_time')    
def do_current_time(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return CurrentTimeNode(format_string[1:-1])
 
class CurrentTimeNode(template.Node):
    def __init__(self, format_string):
        self.format_string = format_string
    def render(self, context):
        return datetime.now().strftime(self.format_string)
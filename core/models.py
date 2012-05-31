from django.db import models
from datetime import datetime, timedelta, time
from django.contrib import admin
from team.models import Teams

# Create your models here.
class FrontPage(models.Model):
    title = models.CharField('Title', max_length=50)
    content = models.TextField('Content', blank=True, null=True)
    created_on = models.DateTimeField('date created', auto_now_add=True)
    updated_on = models.DateTimeField('date updated', auto_now=True)
    team = models.ForeignKey(Teams, blank=True, null=True)
    def __unicode__(self):
        return u'%s' % (self.title)
    class Meta:
        verbose_name = "Info page"
        verbose_name_plural = "Info pages"

class FrontPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'team')
    list_filter = ['team']

admin.site.register(FrontPage, FrontPageAdmin)
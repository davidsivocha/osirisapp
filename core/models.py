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

class Uploads(models.Model):
    title = models.CharField('Title', max_length=50)
    description = models.CharField('Description', max_length=50)
    upload = models.FileField(upload_to="uploads/") 
    def __unicode__(self):
        return u'%s' % (self.title)
    class Meta:
        verbose_name = "Upload"
        verbose_name_plural = "Uploads"    
    def file_link(self):
        if self.upload:
            return "<a href='%s'>%s</a>" % (self.upload.url, self.upload.url)
        else:
            return "No Attachment"
    file_link.allow_tags = True

class FrontPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'team')
    list_filter = ['team']
class UploadsAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_link')

admin.site.register(FrontPage, FrontPageAdmin)
admin.site.register(Uploads, UploadsAdmin)
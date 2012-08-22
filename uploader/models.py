import datetime
from django.utils import timezone
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=50, null=True)
    device_id = models.CharField(max_length=200)
    password = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    facebook_token = models.CharField(max_length=100, null=True)
    facebook_id = models.CharField(max_length=100, null=True)
    pub_date = models.DateTimeField('date published')
    def __unicode__(self):
        return self.device_id

class FOF(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    size = models.IntegerField()
    pub_date = models.DateTimeField('date published')
    view_count = models.IntegerField()
    def __unicode__(self):
        return self.name

class Frame(models.Model):
    url = models.CharField(max_length=200)
    fof = models.ForeignKey(FOF)
    index = models.IntegerField()
    focal_point_x = models.IntegerField()
    focal_point_y = models.IntegerField()
    def __unicode__(self):
        return self.url

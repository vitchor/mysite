import datetime
from django.utils import timezone
from django.db import models

class User(models.Model):
    device_id = models.CharField(max_length=200)
    name = models.CharField(max_length=30)
    def __unicode__(self):
        return self.device_id

class FOF(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    size = models.IntegerField()
    def __unicode__(self):
        return self.name

class Frame(models.Model):
    url = models.CharField(max_length=200)
    fof = models.ForeignKey(FOF)
    index = models.IntegerField()
    def __unicode__(self):
        return self.url

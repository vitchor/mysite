import datetime
from django.utils import timezone
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=50, null=True)
    device_id = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    facebook_token = models.CharField(max_length=100, null=True)
    facebook_id = models.CharField(max_length=100, null=True)
    pub_date = models.DateTimeField('date published')
    def __unicode__(self):
        return self.device_id

class Friends(models.Model):
    friend_1 = models.ForeignKey(User, related_name='user_friend_1')
    friend_2 = models.ForeignKey(User, related_name='user_friend_2')
    
class Device(models.Model):
    user = models.ForeignKey(User)
    device_id = models.CharField(max_length=200)
    
class FOF(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    size = models.IntegerField()
    pub_date = models.DateTimeField('date published')
    view_count = models.IntegerField()
    def __unicode__(self):
        return self.name

class Featured_FOF(models.Model):
    fof = models.ForeignKey(FOF)
    rank = models.IntegerField()
    def __unicode__(self):
        return self.fof.name

class Frame(models.Model):
    url = models.CharField(max_length=200)
    fof = models.ForeignKey(FOF)
    index = models.IntegerField()
    focal_point_x = models.IntegerField()
    focal_point_y = models.IntegerField()
    def __unicode__(self):
        return self.url

class Like(models.Model):
    user = models.ForeignKey(User)
    fof = models.ForeignKey(FOF)
    pub_date = models.DateTimeField('date published')

class Comment(models.Model):
    user = models.ForeignKey(User)
    fof = models.ForeignKey(FOF)
    comment = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    
class Device_Notification(models.Model):
    receiver = models.ForeignKey(User, related_name='user_receiver')
    sender = models.ForeignKey(User, related_name='user_sender')
    sender_facebook_id = models.CharField(max_length=200)
    message = models.CharField(max_length=200)
    trigger_type = models.IntegerField() # 0 = liked your fof, 1 = commented on your fof, 2 = started following you, 3 = commented on a fof that you've commented
    trigger_id = models.IntegerField()
    was_read = models.IntegerField() # 0 = no, 1 = yes
    pub_date = models.DateTimeField('date published')
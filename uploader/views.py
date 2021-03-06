# -*- coding: utf-8 -*-

# NOTE: to send something as a log to the server, you must use the code:
# request.META['wsgi.errors].write("TEXT YOU WANT TO STORE")
# it can afterwards be visualized on /var/log/apache2/error.log

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import sys
import os
import cStringIO
import urllib
import boto
import Image
import _imaging
import random
import string
from itertools import chain
from django.db.models import Q
from django.utils import timezone
from django.utils import simplejson as json
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.core.mail import EmailMessage

from uploader.models import User, FOF, Frame, Featured_FOF, Friends, Like, Comment, Device_Notification


@csrf_exempt
def uploade_profile_image(request):
    print 1
    

@csrf_exempt
def send_support_email(request):
    
    #$ curl -d json='{}' http://dyfoc.us/uploader/send_support_email/
    users = User.objects.all().order_by('-id')
    for user in users:
        print user.id
        if user.id > 2249 :
            
            if user.id < 2330:
                reponseString = "Hi "
                reponseString = reponseString + user.name
                reponseString = reponseString + ", <br/><br/>We've just fixed a bug that was blocking the image upload. If you had any problems with the image upload, please try again now."
                reponseString = reponseString + "<br/><br/>Sorry for the incovenience. Thanks,"
                reponseString = reponseString + "<br/><br/> Victor Oliveira<br/>dyfocus co-founder.<br/> <a href=\"https://www.facebook.com/dyfocus\">https://www.facebook.com/dyfocus<a/><br/><a href=\"http://dyfoc.us/\">http://dyfoc.us/<a/>"

                title = "Major bug fixed at image uploading"

                email = EmailMessage(title, reponseString, to=[user.email])
                email.content_subtype = "html"
                email.send()
            
                print user.name
            
        else: 
            break
        
        
    return HttpResponse(json.dumps({"result" : "ok"}), mimetype="aplication/json")

@csrf_exempt
def get_fof_json(request):
    
    json_request = json.loads(request.POST['json'])
    fof_id = json_request["fof_id"]
    user_id = json_request["user_id"]
    response_data = {}
    
    try:
        fof_object = FOF.objects.get(id = fof_id)
        
        fof = {}

        frame_list = fof_object.frame_set.all().order_by('index')[:5]

        frames = []
        for frame in frame_list:
            frames.append({"frame_url":frame.url,"frame_index":frame.index})

        if fof_object.pub_date is None:
            pub_date = "null"
        else:
            raw_pub_date =  json.dumps(fof_object.pub_date, cls=DjangoJSONEncoder)
            pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]

        fof_user = fof_object.user

        likes = fof_object.like_set.all()

        comments = fof_object.comment_set.all()

        try :
            Like.objects.get(fof_id = fof_object.id, user_id = user_id)
            fof["liked"] = "1"
        except (KeyError, Like.DoesNotExist):
            fof["liked"] = "0"            

        fof["user_name"] = fof_user.name
        fof["user_id"] = fof_user.id
        fof["user_facebook_id"] = fof_user.facebook_id
        fof["id"] = fof_object.id
        fof["is_private"] = fof_object.is_private
        fof["fof_name"] = fof_object.name
        fof["frames"] = frames
        fof["pub_date"] = pub_date
        fof["fof_description"] = fof_object.description

        fof["comments"] = len(comments)
        fof["likes"] = len(likes)
        
        response_data["fof"] = fof
    except(KeyError, FOF.DoesNotExist):
        response_data["error"] = "Fof doesn't exist."
        
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    
@csrf_exempt
def set_featured(request):
    
    fof_id_value = request.POST['fof_id']
    rank_value = request.POST['rank']
    
    try:
        featured_fof = Featured_FOF.objects.get(fof_id = fof_id_value)
        featured_fof.rank = rank_value
        featured_fof.save()
    except(KeyError, Featured_FOF.DoesNotExist):
        friend_relation = Featured_FOF(fof_id = fof_id_value, rank = rank_value)
        friend_relation.save()
        
    return HttpResponse(status=204)
    
def flash_fof(request,fof_name):
    
    try:
        fof = FOF.objects.get(name = fof_name)

        index = 0
        
        first_image_url = ""
        second_image_url = ""
        
        for frame in fof.frame_set.all():
            
            if index == 0:
                first_image_url = frame.url
                index = index + 1
            elif index == 1:
                second_image_url = frame.url
                index = index + 1
            else :
                break
        
    except(KeyError, FOF.DoesNotExist):
        response_data["error"] = "FOF does not exist"
        
    return render_to_response('uploader/images.xml', {"first_image_url" : first_image_url, "second_image_url" : second_image_url},
                               context_instance=RequestContext(request))

def flash_fof_share(request, fof_name_value):
    
    try:
         fof = FOF.objects.get(name = fof_name_value)
         
    except(KeyError, FOF.DoesNotExist):
         return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))
    
    else:
        index = 0
        
        fof_thumbnail_url = ""
        fof_id = fof.id
        fof_flash_url = "http://dyfoc.us/static/flash/FlashFOFViewer.swf?fofId=" + str(fof_id)
        
        for frame in fof.frame_set.all():
            if index == 0:
                fof_thumbnail_url = frame.url
                index += 1
            else:
                break
                
        
        return render_to_response('uploader/flash_fof_share.html', {"fof_flash_url" : fof_flash_url, "fof_thumbnail_url" : fof_thumbnail_url, "fof_name" : fof_name_value },
                                    context_instance=RequestContext(request))


def index(request):
    return render_to_response('uploader/index.html', {},
                               context_instance=RequestContext(request))

def privacy_policy(request):
    return render_to_response('uploader/privacy_policy.html', {}, context_instance=RequestContext(request))

@csrf_exempt
def delete_fof(request):
    """ Test Request:
         $ curl -d json='{"fof_id": 664}' http://localhost:8000/uploader/delete_fof/
     """
    json_request = json.loads(request.POST['json'])
    fof_id_value = json_request['fof_id']
    response_data = {}
    
    try:
        user_notifications = Device_Notification.objects.filter(trigger_id = fof_id_value)
        for notification in user_notifications:
            if notification.trigger_type <= 1: 
                notification.delete()
                
        if user_notifications.count() != 0:
            response_data["had_notifications"] = "True"
        else:
            response_data["had_notifications"] = "False"
    except(KeyError, Device_Notification.DoesNotExist):
        response_data["had_notifications"] = "False"
        
    try:
        featured_fof = Featured_FOF.objects.get(fof_id = fof_id_value)
        featured_fof.delete()
        response_data["is_featured"] = "True"
    except(KeyError, Featured_FOF.DoesNotExist):
        response_data["is_featured"] = "False"

    try:
        my_fof = FOF.objects.get(id = fof_id_value)
        frame_list = my_fof.frame_set.all()
        try:
            comment_list = my_fof.comment_set.all()
            comment_list.delete()
            response_data["have_comments"] = "True"
        except(KeyError, Comment.DoesNotExist):
            response_data["have_comments"] = "False"
            
        try:
            like_list = my_fof.like_set.all()
            like_list.delete()
            response_data["have_likes"] = "True"
        except(KeyError, Like.DoesNotExist):
            response_data["have_likes"] = "False"
        frame_list.delete()
        my_fof.delete()
        
        response_data["result"] = "OK"
    except (KeyError, FOF.DoesNotExist):
        response_data["error"] = "FOF Not Found"
        
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

@csrf_exempt
def delete_comment(request):
    """ Test Request:
         $ curl -d json='{"comment_id": 2}' http://localhost:8000/uploader/delete_comment/
     """
    response_data = {}
    
    json_request = json.loads(request.POST['json'])
    comment_id_value = json_request['comment_id']
    
    try:
        comment = Comment.objects.get(id = comment_id_value)
        comment.delete()
        response_data["result"] = "Comment deleted successfully"
    except(KeyError, Comment.DoesNotExist):
        response_data["error"] = "Comment Not Found"

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    
@csrf_exempt
def delete_like(request):
    """ Test Request:
         $ curl -d json='{"user_id": 74, "fof_id": 352}' http://localhost:8000/uploader/delete_like/
     """
    response_data = {}

    json_request = json.loads(request.POST['json'])
    user_id_value = json_request['user_id']
    fof_id_value = json_request['fof_id']
    
    try:
        like = Like.objects.get(user_id = user_id_value, fof_id = fof_id_value)
        like.delete()
        response_data["result"] = "Like deleted successfully"
    except(KeyError, Like.DoesNotExist):
        response_data["error"] = "Like Not Found"

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

@csrf_exempt
def send_forgot_password_email(request):
    """ Test Request:
        $ curl -d json='{"user_email": "vitchor@gmail.com"}' http://localhost:8000/uploader/send_forgot_password_email/
    """
    json_request = json.loads(request.POST['json'])
    user_email = json_request['user_email']
    
    response_data = {}
    
    try:
        user = User.objects.get(email=user_email)
        
        reponseString = "Hello "
        reponseString = reponseString + user.name
        reponseString = reponseString + ", <br/><br/>Your password is: "
        reponseString = reponseString + user.password
        reponseString = reponseString + "<br/><br/>If you have any questions or suggestions we would be glad to hear them. Thanks,"
        reponseString = reponseString + "<br/>Dyfocus Team."
        
        email = EmailMessage("Forgot Password Response", reponseString, to=[user_email])
        email.content_subtype = "html"
        email.send()
        response_data["result"] ="ok"
        
    except (KeyError, User.DoesNotExist):
        response_data["error"] = "Email not registered in our system:"
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

@csrf_exempt
def user_follow(request):
    """ Test Request:
        $ curl -d json='{"person_id": 2, "follower_id":100}' http://localhost:8000/uploader/user_follow/
    """
    
    response_data = {}
    response_data["result"]=[]
    response_data["friend"]=[]
    
    json_request = json.loads(request.POST['json'])
    follower_id = json_request['follower_id']
    person_id = json_request['person_id']
    
    try:
        follower_user = User.objects.get(id=follower_id)
        person_user = User.objects.get(id=person_id)
        
        try:
            test_friends = Friends.objects.get(friend_1_id = follower_user.id, friend_2_id = person_user.id)
            response_data["result"] = "ok: friends row already existed."
            response_data["friend"].append({"facebook_id":person_user.facebook_id, "user_id":person_user.id, "name":person_user.name})
        except (KeyError, Friends.DoesNotExist):
            # It doesn't exist, lets create it:
            friend_relation = Friends(friend_1_id = follower_user.id, friend_2_id = person_user.id)
            friend_relation.save()
            
            notification_message = follower_user.name + " started following you."
            """
            WAIT FOR APP RELASE TO UNCOMMEN IT ////// TODO
            sendAlert(person_id, follower_user.id, follower_user.facebook_id, notification_message, 2, follower_user.id)
            """
            # Updates the Followers and Following counters:
            following_calc(follower_user.id)
            followers_calc(person_user.id)
            response_data["friend"].append({"facebook_id":person_user.facebook_id, "user_id":person_user.id, "name":person_user.name})
            response_data["result"] = "ok: friends row created."
        
    except (KeyError, User.DoesNotExist):
        response_data["result"] = "error: invalid users."

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    
@csrf_exempt
def follow(request):
    """ Test Request:
        $ curl -d json='{"follower_facebook_id": 100001077656862, "feed_facebook_id":640592329}' http://localhost:8000/uploader/follow/
    """
    response_data = {}
    response_data["result"]=[]
    response_data["friend"]=[]
    
    json_request = json.loads(request.POST['json'])
    follower_facebook_id = json_request['follower_facebook_id']
    feed_facebook_id = json_request['feed_facebook_id']
    
    try:
        follower_user = User.objects.get(facebook_id=follower_facebook_id)
        feed_user = User.objects.get(facebook_id=feed_facebook_id)
        try:
            test_friends = Friends.objects.get(friend_1_id = follower_user.id, friend_2_id = feed_user.id)
            response_data["result"] = "ok: friends row already existed."
            response_data["friend"].append({"facebook_id":feed_user.facebook_id,"name":feed_user.name})
        except (KeyError, Friends.DoesNotExist):
            # It doesn't exist, lets create it:
            friend_relation = Friends(friend_1_id = follower_user.id, friend_2_id = feed_user.id)
            friend_relation.save()
            # Updates the Followers and Following counters:
            following_calc(follower_user.id)
            followers_calc(feed_user.id)
            response_data["friend"].append({"facebook_id":feed_user.facebook_id,"name":feed_user.name})
            response_data["result"] = "ok: friends row created."
    except (KeyError, User.DoesNotExist):
        response_data["result"] = "error: invalid users."


    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")


@csrf_exempt
def user_unfollow(request):

    """ Test Request:
        $ curl -d json='{"follower_facebook_id": 100001077656862, "feed_facebook_id":640592329}' http://localhost:8000/uploader/unfollow/
    """

    response_data = {}
    response_data["result"]=[]
    response_data["friend"]=[]

    json_request = json.loads(request.POST['json'])
    unfollower_id = json_request['unfollower_id']
    person_id = json_request['person_id']

    try:
        unfollower_user = User.objects.get(id=unfollower_id)
        feed_user = User.objects.get(id=person_id)

        try:
            test_friends = Friends.objects.get(friend_1_id = unfollower_user.id, friend_2_id = feed_user.id)
            test_friends.delete();
            # Updates the Followers and Following counters:
            following_calc(unfollower_user.id)
            followers_calc(feed_user.id)
            response_data["result"] = "ok: follow relation deleted."
            response_data["friend"].append({"facebook_id":feed_user.facebook_id, "user_id":feed_user.id, "name":feed_user.name})
        except (KeyError, Friends.DoesNotExist):
            # It doesn't exists, lets create it:
            response_data["result"] = "ok: follow relation didn't exist before you tried to delete."

    except (KeyError, User.DoesNotExist):
        response_data["result"] = "error: invalid users."

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    
@csrf_exempt
def unfollow(request):

    """ Test Request:
        $ curl -d json='{"follower_facebook_id": 100001077656862, "feed_facebook_id":640592329}' http://localhost:8000/uploader/unfollow/
    """

    response_data = {}
    response_data["result"]=[]
    response_data["friend"]=[]
    
    json_request = json.loads(request.POST['json'])
    unfollower_facebook_id = json_request['follower_facebook_id']
    feed_facebook_id = json_request['feed_facebook_id']

    try:
        unfollower_user = User.objects.get(facebook_id=unfollower_facebook_id)
        feed_user = User.objects.get(facebook_id=feed_facebook_id)

        try:
            test_friends = Friends.objects.get(friend_1_id = unfollower_user.id, friend_2_id = feed_user.id)
            test_friends.delete();
            # Updates the Followers and Following counters:
            following_calc(unfollower_user.id)
            followers_calc(feed_user.id)
            response_data["result"] = "ok: follow relation deleted."
            response_data["friend"].append({"facebook_id":feed_user.facebook_id,"name":feed_user.name})
        except (KeyError, Friends.DoesNotExist):
            # It doesn't exists, lets create it:
            response_data["result"] = "ok: follow relation didn't exist before you tried to delete."

    except (KeyError, User.DoesNotExist):
        response_data["result"] = "error: invalid users."

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
      
@csrf_exempt
def test(request):
    
    response_data = {}
    
    users = User.objects.all()
    
    for user in users:
        user.id_origin = 1
        user.save()
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

# Converts from Facebook ID to Dyfocus ID (tested and working):
def fb_id_to_df_id(user_fb_id):
    try:
        user = User.objects.get(facebook_id=user_fb_id)
    except (KeyError, User.DoesNotExist):
        return 0
    else:
        return user.id

def update_user_following_and_follower_values(user_object):
    
    if user_object.followers_count is None:
        user_object.followers_count = followers_calc(user_object.id)
        
    if user_object.following_count is None:
        user_object.following_count = following_calc(user_object.id)
        
    user_object.save()
    
    return user_object


# Calculates the number of users the user given by user_id follows:
def following_calc(user_id):
    try:
        user = User.objects.get(id=user_id)
    except (KeyError, User.DoesNotExist):
        return -1
    else:
        #print "Using following_calc for user", user.name
        following = Friends.objects.filter(friend_1_id = user_id).count()
        if following is None:
            user.following_count = 0
        else:
            user.following_count = following
        user.save()
        return following

# Calculates the number of users that follow the user given by user_id:
def followers_calc(user_id):
    try:
        user = User.objects.get(id=user_id)
    except (KeyError, User.DoesNotExist):
        return -1
    else:
        #print "Using followers_calc for user", user.name
        followers = Friends.objects.filter(friend_2_id = user_id).count()
        if followers is None:
            user.followers_count = 0;
        else:
            user.followers_count = followers
        user.save()
        return followers
        
# Returns a JSON object containing the number of followers and folowees of a determined user:
@csrf_exempt
def how_many_follow(request):
    """ Test Request:
           $ curl -d json='{"facebook_id": 100001077656862}' http://localhost:8000/uploader/how_many_follow/
    """
    
    response_data = {}
    response_data["result"]=[]
    response_data["followers"]=[]
    response_data["following"]=[]
    
    
    json_request = json.loads(request.POST['json'])
    user_facebook_id = json_request['facebook_id']
    
    try:
        user = User.objects.get(facebook_id=user_facebook_id)
    except (KeyError, User.DoesNotExist):
        response_data["result"] = "error: user not found"
    else:
        following = user.following_count
        if following is None:
            following = following_calc(user.id)
        
        followers = user.followers_count
        if followers is None:
            followers = followers_calc(user.id)
            
        response_data["result"] = "data fetched with no errors"
        response_data["followers"] = followers
        response_data["following"] = following
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

@csrf_exempt
def upload_private_image(request):

    #Gets fof info
    fof_size = request.POST['fof_size']
    fof_name = request.POST['fof_name']
    user_id = request.POST['user_id']
    is_private_value = request.POST['is_private']
    
    try:
        fof_description = request.POST['fof_description']
    except:
        fof_description = ""

    response_data = {}

    #Get/Creates user
    try:

        user = User.objects.get(id=user_id)

        #Gets/Creates fof
        try:
            frame_FOF = FOF.objects.get(name=fof_name)
        except (KeyError, FOF.DoesNotExist):
            frame_FOF = user.fof_set.create(name = fof_name, size = fof_size, pub_date=timezone.now(), view_count = 0, is_private = is_private_value, description = fof_description)

        #Connect to S3, with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

        conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        b = conn.get_bucket('dyfocus')

        #Creates all frames at once
        for i in range(int(fof_size)):

            #Actual index image key
            key = 'apiupload_' + str(i)

            image = Image.open(cStringIO.StringIO(request.FILES[key].read()))

            out_image = cStringIO.StringIO()
            image.save(out_image, 'jpeg')

            #Gets information from post
            frame_focal_point_x_key = 'frame_focal_point_x_' + str(i)
            frame_focal_point_y_key = 'frame_focal_point_y_' + str(i)

            frame_focal_point_x = request.POST[frame_focal_point_x_key]
            frame_focal_point_y = request.POST[frame_focal_point_y_key]

            #Creates the image key with the following format:
            #frame_name = <user_id>_<fof_name>_<frame_index>.jpeg
            frame_name = user_id
            frame_name += '_'
            frame_name += fof_name
            frame_name += '_'
            frame_name += str(i)
            frame_name += '.jpeg'

            #Creates url:
            #frame_url = <s3_url>/<frame_name>
            frame_url = 'http://s3.amazonaws.com/dyfocus/'
            frame_url += frame_name

            frame = frame_FOF.frame_set.create(url = frame_url, index = str(i), focal_point_x = frame_focal_point_x, focal_point_y = frame_focal_point_y)

            k = b.new_key(frame_name)

            #Note we're setting contents from the in-memory string provided by cStringIO
            k.set_contents_from_string(out_image.getvalue())

            response_data["result"] = "ok"

    except (KeyError, User.DoesNotExist):
        response_data["error"] = "User does not exist."


    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
        
@csrf_exempt
def upload_image(request):

    #Gets fof info
    fof_size = request.POST['fof_size']
    fof_name = request.POST['fof_name']
    user_id = request.POST['user_id']
    
    response_data = {}
    
    #Get/Creates user
    try:
        
        user = User.objects.get(id=user_id)
        
        #Gets/Creates fof
        try:
            frame_FOF = FOF.objects.get(name=fof_name)
        except (KeyError, FOF.DoesNotExist):
            frame_FOF = user.fof_set.create(name = fof_name, size = fof_size, pub_date=timezone.now(), view_count = 0, is_private = 0)
        
        #Connect to S3, with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        conn = S3Connection('AKIAIFPFKLTD5HLWDI2A', 'zrCRXDSD3FKTJwJ3O5m/dsZstL/Ki0NyF6GZKHQi')
        b = conn.get_bucket('dyfocus')
        
        #Creates all frames at once
        for i in range(int(fof_size)):
            
            #Actual index image key
            key = 'apiupload_' + str(i)
            
            image = Image.open(cStringIO.StringIO(request.FILES[key].read()))
            
            out_image = cStringIO.StringIO()
            image.save(out_image, 'jpeg')
            
            #Gets information from post
            frame_focal_point_x_key = 'frame_focal_point_x_' + str(i)
            frame_focal_point_y_key = 'frame_focal_point_y_' + str(i)
            
            frame_focal_point_x = request.POST[frame_focal_point_x_key]
            frame_focal_point_y = request.POST[frame_focal_point_y_key]
            
            #Creates the image key with the following format:
            #frame_name = <user_id>_<fof_name>_<frame_index>.jpeg
            frame_name = user_id
            frame_name += '_'
            frame_name += fof_name
            frame_name += '_'
            frame_name += str(i)
            frame_name += '.jpeg'
            
            #Creates url:
            #frame_url = <s3_url>/<frame_name>
            frame_url = 'http://s3.amazonaws.com/dyfocus/'
            frame_url += frame_name
            
            frame = frame_FOF.frame_set.create(url = frame_url, index = str(i), focal_point_x = frame_focal_point_x, focal_point_y = frame_focal_point_y)
            
            k = b.new_key(frame_name)
            
            #Note we're setting contents from the in-memory string provided by cStringIO
            k.set_contents_from_string(out_image.getvalue())
            
            response_data["result"] = "ok"
                        
    except (KeyError, User.DoesNotExist):
        response_data["error"] = "User does not exist."
        
        
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")


@csrf_exempt
def image(request):
    
    #Gets fof info
    fof_size = request.POST['fof_size']
    fof_name = request.POST['fof_name']
    user_facebook_id = request.POST['facebook_id']
    user_facebook_name = request.POST['facebook_name']
    user_facebook_email = request.POST['facebook_email']
    
    if user_facebook_id is None:
        return render_to_response('uploader/index.html', {},
                                   context_instance=RequestContext(request))
                                   
    #Get/Creates user
    try:
        frame_user = User.objects.get(facebook_id=user_facebook_id)
    except (KeyError, User.DoesNotExist):
        frame_user = User(name=user_facebook_name, facebook_id=user_facebook_id, email=user_facebook_name, pub_date=timezone.now())
        frame_user.save()
    
    #Gets/Creates fof
    try:
        frame_FOF = FOF.objects.get(name=fof_name)
    except (KeyError, FOF.DoesNotExist):
       frame_FOF = frame_user.fof_set.create(name = fof_name, size = fof_size, pub_date=timezone.now(), view_count = 0)

    #Connect to S3, with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    conn = S3Connection('AKIAIFPFKLTD5HLWDI2A', 'zrCRXDSD3FKTJwJ3O5m/dsZstL/Ki0NyF6GZKHQi')
    b = conn.get_bucket('dyfocus')

    #Creates all frames at once
    for i in range(int(fof_size)):

        #Actual index image key
        key = 'apiupload_' + str(i)

        image = Image.open(cStringIO.StringIO(request.FILES[key].read()))

        out_image = cStringIO.StringIO()
        image.save(out_image, 'jpeg')

        #Gets information from post
        frame_focal_point_x_key = 'frame_focal_point_x_' + str(i)
        frame_focal_point_y_key = 'frame_focal_point_y_' + str(i)

        frame_focal_point_x = request.POST[frame_focal_point_x_key]
        frame_focal_point_y = request.POST[frame_focal_point_y_key]

        #Creates the image key with the following format:
        #frame_name = <user_facebook_id>_<fof_name>_<frame_index>.jpeg
        frame_name = user_facebook_id
        frame_name += '_'
        frame_name += fof_name
        frame_name += '_'
        frame_name += str(i)
        frame_name += '.jpeg'

        #Creates url:
        #frame_url = <s3_url>/<frame_name>
        frame_url = 'http://s3.amazonaws.com/dyfocus/'
        frame_url += frame_name

        frame = frame_FOF.frame_set.create(url = frame_url, index = str(i), focal_point_x = frame_focal_point_x, focal_point_y = frame_focal_point_y)

        k = b.new_key(frame_name)

        #Note we're setting contents from the in-memory string provided by cStringIO
        k.set_contents_from_string(out_image.getvalue())

    return render_to_response('uploader/index.html', {},
                               context_instance=RequestContext(request))
                                   
                               
                               
"""def create_FOF(request, user, fof_name, fof_size):

    frame_FOF = user.fof_set.create(name = fof_name, size = fof_size, pub_date=timezone.now(), view_count = 0)

    #Connect to S3, with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    conn = S3Connection('AKIAIFPFKLTD5HLWDI2A', 'zrCRXDSD3FKTJwJ3O5m/dsZstL/Ki0NyF6GZKHQi')
    b = conn.get_bucket('dyfocus')

    #Creates all frames at once
    for i in range(int(fof_size)):
         
        #Actual index image key
        key = 'apiupload_' + str(i)
   
        image = Image.open(cStringIO.StringIO(request.FILES[key].read()))
        
        out_image = cStringIO.StringIO()

        image.save(out_image, 'jpeg')
         
        #Gets information from post
        frame_focal_point_x_key = 'frame_focal_point_x_' + str(i)
        frame_focal_point_y_key = 'frame_focal_point_y_' + str(i)
            
        frame_focal_point_x = request.POST[frame_focal_point_x_key]
        frame_focal_point_y = request.POST[frame_focal_point_y_key]
               
        #Creates the image key with the following format:
        #frame_name = <user_facebook_id>_<fof_name>_<frame_index>.jpeg
        frame_name = user_facebook_id
        frame_name += '_'
        frame_name += fof_name
        frame_name += '_'
        frame_name += str(i)
        frame_name += '.jpeg'
        
        #Creates url:
        #frame_url = <s3_url>/<frame_name>
        frame_url = 'http://s3.amazonaws.com/dyfocus/'
        frame_url += frame_name
        
        frame = frame_FOF.frame_set.create(url = frame_url, index = str(i), focal_point_x = frame_focal_point_x, focal_point_y = frame_focal_point_y)
               
        k = b.new_key(frame_name)
              
        #Note we're setting contents from the in-memory string provided by cStringIO
        k.set_contents_from_string(out_image.getvalue())
       
    
    return True
"""

def fof(request, fof_name):
    fof = get_object_or_404(FOF, name=fof_name)
    
    frame_list = fof.frame_set.all().order_by('index')[:5]
    
    return render_to_response('uploader/fof.html', {'frame_list':frame_list}, context_instance=RequestContext(request))


def featured_fof(request, fof_name_value):
    
    featured_fof_list = Featured_FOF.objects.all().order_by('-rank')
    
    i = 0
    
    if fof_name_value == "0":
        featured_fof = featured_fof_list[0]
        fof = get_object_or_404(FOF, id=featured_fof.fof_id)
        fof.view_count += 1
        fof.save()
        fof_name_value = fof.name;
        frame_list = fof.frame_set.all().order_by('index')[:5]
    else:
        for featured_fof in featured_fof_list:
            if featured_fof.fof.name == fof_name_value:
                featured_fof.fof.view_count += 1
                featured_fof.fof.save()
                frame_list = featured_fof.fof.frame_set.all().order_by('index')[:5]
                break
            i = i + 1
    
    if len(featured_fof_list) - 1 == i:
        next_fof_name = featured_fof_list[0].fof.name
    else:
        next_fof_name = featured_fof_list[i+1].fof.name

    if i == 0:
        prev_fof_name = featured_fof_list[len(featured_fof_list) - 1].fof.name
    else:
        prev_fof_name = featured_fof_list[i - 1].fof.name
        
    if featured_fof.fof.user.name:
        user_name = featured_fof.fof.user.name
    else:
        user_name = "Unknown user"
	
    return render_to_response('uploader/fof_viewer.html', {'type':"featured_fof",'hide_arrows': 0, 'device_id_value':0, 'mobile_link':"/uploader/"+fof_name_value+"/featured_fof/m/",'frame_list':frame_list, 'fof_date':featured_fof.fof.pub_date,'next_fof_name':next_fof_name, 'prev_fof_name':prev_fof_name, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))

def m_featured_fof(request, fof_name_value):

    featured_fof_list = Featured_FOF.objects.all().order_by('-rank')

    i = 0

    if fof_name_value == "0":
        featured_fof = featured_fof_list[0]
        fof = get_object_or_404(FOF, id=featured_fof.fof_id)
        fof.view_count += 1
        fof.save()
        frame_list = fof.frame_set.all().order_by('index')[:5]
    else:
        for featured_fof in featured_fof_list:
            if featured_fof.fof.name == fof_name_value:
                featured_fof.fof.view_count += 1
                featured_fof.fof.save()
                frame_list = featured_fof.fof.frame_set.all().order_by('index')[:5]
                break
            i = i + 1

    if len(featured_fof_list) - 1 == i:
        next_fof_name = featured_fof_list[0].fof.name
    else:
        next_fof_name = featured_fof_list[i+1].fof.name

    if i == 0:
        prev_fof_name = featured_fof_list[len(featured_fof_list) - 1].fof.name
    else:
        prev_fof_name = featured_fof_list[i - 1].fof.name
        
    if featured_fof.fof.user.name:
        user_name = featured_fof.fof.user.name
    else:
        user_name = "Unknown user"

    return render_to_response('uploader/m_fof_featured.html', {'frame_list':frame_list, 'next_fof_name':next_fof_name, 'prev_fof_name':prev_fof_name, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))
                               
def user_fof(request, facebook_id_value, fof_name_value):
    
    try: 
        user = User.objects.get(facebook_id = facebook_id_value)
    except (KeyError, User.DoesNotExist):
        try:
            user = User.objects.get(device_id = facebook_id_value)
        except (KeyError, User.DoesNotExist):
            return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))
    
        
    fof_list = user.fof_set.all().order_by('-pub_date')

    i = 0

    if fof_name_value == "0":
        fof = user.fof_set.all().order_by('-pub_date')[0]
        fof.view_count += 1
        fof.save()
        frame_list = fof.frame_set.all().order_by('index')[:5]
    
    else:    
        for fof in fof_list:
            if fof.name == fof_name_value:
                fof.view_count += 1
                fof.save()
                frame_list = fof.frame_set.all().order_by('index')[:5]
                break
            i = i + 1
        
    if len(fof_list) - 1 == i:
        next_fof_name = fof_list[0].name
    else:
        next_fof_name = fof_list[i+1].name

    if i == 0:
        prev_fof_name = fof_list[len(fof_list) - 1].name
    else:
        prev_fof_name = fof_list[i - 1].name
        
    if fof.user.name:
        user_name = fof.user.name
    else:
        user_name = "Unknown user"
	
    return render_to_response('uploader/fof_viewer.html', {'type':"user_fof",'hide_arrows': 0 ,'mobile_link':"/uploader/"+facebook_id_value+"/user/"+fof_name_value+"/fof_name/m/",'frame_list':frame_list,'fof_date':fof.pub_date, 'device_id_value':facebook_id_value, 'facebook_id_value':facebook_id_value, 'next_fof_name':next_fof_name, 'prev_fof_name':prev_fof_name, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))

def share_fof(request, fof_name_value):

    try: 
        fof = FOF.objects.get(name = fof_name_value)
    except (KeyError, User.DoesNotExist):
        return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))
    else:
		if fof.name == fof_name_value:
			fof.view_count += 1
			fof.save()
			frame_list = fof.frame_set.all().order_by('index')[:5]
		
		if fof.user.name:
			user_name = fof.user.name
		else:
			user_name = "Unknown user"
			
		return render_to_response('uploader/fof_viewer.html', {'type':"share_fof",'hide_arrows': 1, 'device_id_value':0, 'mobile_link':"/uploader/"+fof_name_value+"/share_fof/m/",'frame_list':frame_list,'fof_date':fof.pub_date, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))


def m_share_fof(request, fof_name_value):

    try: 
        fof = FOF.objects.get(name = fof_name_value)
    except (KeyError, User.DoesNotExist):
        return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))
    else:
		if fof.name == fof_name_value:
			fof.view_count += 1
			fof.save()
			frame_list = fof.frame_set.all().order_by('index')[:5]
		
		if fof.user.name:
			user_name = fof.user.name
		else:
			user_name = "Unknown user"
			
		return render_to_response('uploader/m_fof_share.html', {'frame_list':frame_list,'fof_date':fof.pub_date, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))


def m_user_fof(request, facebook_id_value, fof_name_value):
    #user = get_object_or_404(User, device_id=device_id_value)

    try: 
        user = User.objects.get(facebook_id = facebook_id_value)
    except (KeyError, User.DoesNotExist):
        try:
            user = User.objects.get(device_id = facebook_id_value)
        except (KeyError, User.DoesNotExist):
            return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))

    fof_list = user.fof_set.all().order_by('-pub_date')

    i = 0

    if fof_name_value == "0":
        fof = user.fof_set.all().order_by('-pub_date')[0]
        fof.view_count += 1
        fof.save()
        frame_list = fof.frame_set.all().order_by('index')[:5]

    else:    
        for fof in fof_list:
            if fof.name == fof_name_value:
                fof.view_count += 1
                fof.save()
                frame_list = fof.frame_set.all().order_by('index')[:5]
                break
            i = i + 1

    if len(fof_list) - 1 == i:
        next_fof_name = fof_list[0].name
    else:
        next_fof_name = fof_list[i+1].name

    if i == 0:
        prev_fof_name = fof_list[len(fof_list) - 1].name
    else:
        prev_fof_name = fof_list[i - 1].name
        
    if fof.user.name:
        user_name = fof.user.name
    else:
        user_name = "Unknown user"

    return render_to_response('uploader/m_fof.html', {'frame_list':frame_list, 'device_id_value':facebook_id_value, 'facebook_id_value':facebook_id_value, 'next_fof_name':next_fof_name, 'prev_fof_name':prev_fof_name, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))

@csrf_exempt
def user_fb_info(request):
    
   device_id_value = request.POST['device_id']
   user_name = request.POST['name']
   user_facebook_id = request.POST['facebook_id']
   user_email = request.POST['email']

   try:
       user = User.objects.get(device_id = device_id_value)
   except (KeyError, User.DoesNotExist):
       user = User(device_id = device_id_value, name = user_name, facebook_id = user_facebook_id, pub_date=timezone.now(), email = user_email) 
       user.save()
   else:
       user.name = user_name
       user.facebook_id = user_facebook_id
       user.email = user_email
       user.save()

   return render_to_response('uploader/index.html', {}, context_instance=RequestContext(request))
   
   
@csrf_exempt
def user_info(request):
    
    # $ curl -d json='{"user_facebook_id": 2}' http://localhost:8000/uploader/user_info/
    
    json_request = json.loads(request.POST['json'])
    user_id_value = json_request['user_facebook_id']
    
    response_data = {}
    
    try:
        user = User.objects.get(facebook_id=user_id_value)
        
        user = update_user_following_and_follower_values(user)
        
        user_fof_array = get_user_fofs(user)
        response_data['person'] = {"facebook_id":user.facebook_id, "name":user.name, "id_origin":user.id_origin, "followers_count":user.followers_count, "following_count":user.following_count, "id":user.id}
    
        response_data['person_FOF_array'] = user_fof_array
        
    except (KeyError, User.DoesNotExist):
        response_data["result"] = user_id_value
        return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
        

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    

@csrf_exempt
def user_id_info(request):
    # $ curl -d json='{"user_id": 2}' http://localhost:8000/uploader/user_id_info/

    json_request = json.loads(request.POST['json'])
    user_id_value = json_request['user_id']

    response_data = {}

    try:
        user = User.objects.get(id=user_id_value)

        user = update_user_following_and_follower_values(user)

        user_fof_array = get_user_fofs(user)
        response_data['person'] = {"facebook_id":user.facebook_id, "name":user.name, "id_origin":user.id_origin, "followers_count":user.followers_count, "following_count":user.following_count, "id":user.id, "user_id":user.id}

        response_data['person_FOF_array'] = user_fof_array

    except (KeyError, User.DoesNotExist):
        response_data["error"] = "User not found"
        return HttpResponse(json.dumps(response_data), mimetype="aplication/json")


    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")


    
def json_fof(request, device_id_value, fof_name_value):
    
    response_data = {}
    
    try: 
        user = User.objects.get(device_id = device_id_value)
    except (KeyError, User.DoesNotExist):
        response_data['result'] = 'error'
        response_data['message'] = 'User does not exist'
        return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    else:
        
        fof_list = user.fof_set.all().order_by('-pub_date')
    
        i = 0
    
        if fof_name_value == "0":
            fof = user.fof_set.all().order_by('-pub_date')[0]
            fof.view_count += 1
            fof.save()
            frame_list = fof.frame_set.all().order_by('index')[:5]
        
        else:    
            for fof in fof_list:
                if fof.name == fof_name_value:
                    fof.view_count += 1
                    fof.save()
                    frame_list = fof.frame_set.all().order_by('index')[:5]
                    break
                i = i + 1
            
        if len(fof_list) - 1 <= i:
            next_fof_name = fof_list[0].name
        else:
            next_fof_name = fof_list[i+1].name
    
        if i == 0:
            prev_fof_name = fof_list[len(fof_list) - 1].name
        else:
            prev_fof_name = fof_list[i - 1].name
            
        if fof.user.name:
            user_name = fof.user.name
        else:
            user_name = "Unknown user"
        
        response_data['frame_list'] = ''
        
        for frame in frame_list:
            if response_data['frame_list'] == '':
                response_data['frame_list'] = str(frame)
            else:
                response_data['frame_list'] = response_data['frame_list'] + ',' + str(frame)
        
        response_data['device_id_value'] = device_id_value
        response_data['next_fof_name'] = next_fof_name
        response_data['prev_fof_name'] = prev_fof_name
        response_data['current_fof'] = fof_name_value
        response_data['user_name'] = user_name
        response_data['result'] = 'ok'
        response_data['message'] = 'ok'
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

@csrf_exempt
def user_fb_friends(request):
    
    # TEST:
    # $ curl -d json='{"user_facebook_id": "100000370417687", "user_device_id": "28c8ef21c63e7fa857b4e10a10953783cee15c04", "friends": [{"facebook_id": "640592329"},{"facebook_id": "100000754383534"},{"facebook_id": "100000723578122"}]}' http://localhost:8000/uploader/user_fb_friends/
    
    # Parse the JSON
    friends_json = json.loads(request.POST['json'])
    
    print friends_json['user_facebook_id']
    
    user = get_object_or_404(User, facebook_id=friends_json['user_facebook_id'])
   
    # Populate the friends table with the new information
    for friend in friends_json['friends']:
        try: 
            # Is there any user with the same facebook_id as the requesting user friend is?
            user_friend = User.objects.get(facebook_id = friend['facebook_id'])
            
            # Yes! They are friends! Let's add a new row to the friends model!...
            # ...First lets checkout if that friend row doesn't exists already:
            try:
                Friends.objects.get(friend_1_id = user.id, friend_2_id = user_friend.id)
            except (KeyError, Friends.DoesNotExist):
                # It doesn't exists, lets create it:
                friend_relation = Friends(friend_1_id = user.id, friend_2_id = user_friend.id)
                friend_relation.save()
            
        except (KeyError, User.DoesNotExist):
            # Nothing to do here
            j = 0
    
    # Returns the list of the requesting user friends
    response_data = {}
    response_data['friends_list'] = []
    
    for friend in Friends.objects.all():
        if friend.friend_1_id == user.id:
            try:
                user_friend_object = User.objects.get(id = friend.friend_2_id)
                
                response_data['friends_list'].append({"facebook_id":user_friend_object.facebook_id, "user_id":user_friend_object.id})
                
            except (KeyError, User.DoesNotExist):
                # Nothing to do here
                j = 0
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    
def json_fof_featured(request, fof_name_value):

    response_data = {}

    featured_fof_list = Featured_FOF.objects.all().order_by('-rank')

    i = 0

    if fof_name_value == "0":
        featured_fof = featured_fof_list[0]
        fof = get_object_or_404(FOF, id=featured_fof.fof_id)
        fof.view_count += 1
        fof.save()
        frame_list = fof.frame_set.all().order_by('index')[:5]
    else:
        for featured_fof in featured_fof_list:
            if featured_fof.fof.name == fof_name_value:
                featured_fof.fof.view_count += 1
                featured_fof.fof.save()
                frame_list = featured_fof.fof.frame_set.all().order_by('index')[:5]
                break
            i = i + 1

    try:
        frame_list
    except:
        response_data['result'] = 'error'
        response_data['message'] = 'Invalid FOF name'
        return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

    if len(featured_fof_list) - 1 == i:
        next_fof_name = featured_fof_list[0].fof.name
    else:
        next_fof_name = featured_fof_list[i+1].fof.name

    if i == 0:
        prev_fof_name = featured_fof_list[len(featured_fof_list) - 1].fof.name
    else:
        prev_fof_name = featured_fof_list[i - 1].fof.name
        
    if featured_fof.fof.user.name:
        user_name = featured_fof.fof.user.name
    else:
        user_name = "Unknown user"

    response_data['frame_list'] = ''

    for frame in frame_list:
        if response_data['frame_list'] == '':
            response_data['frame_list'] = str(frame)
        else:
            response_data['frame_list'] = response_data['frame_list'] + ',' + str(frame)

    response_data['next_fof_name'] = next_fof_name
    response_data['prev_fof_name'] = prev_fof_name
    response_data['current_fof'] = fof_name_value
    response_data['user_name'] = user_name
    response_data['result'] = 'ok'
    response_data['message'] = 'ok'

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

def fof_not_found(request, fof_name):
    fof = get_object_or_404(FOF, name=fof_name)

    frame_list = fof.frame_set.all().order_by('index')[:5]

    return render_to_response('uploader/fof.html', {'frame_list':frame_list},
                               context_instance=RequestContext(request))

def embedded_fof(request, fof_name_value):     
    return embedded_fof_height(request, fof_name_value, "0")

def embedded_fof_height(request, fof_name_value, fof_height_value):     
    featured_fof_list = Featured_FOF.objects.all().order_by('-rank')

    i = 0

    ## initializes the fof "featured_fof" and the "frame_list"
    if fof_name_value == "0":
        featured_fof = featured_fof_list[0]
        fof = get_object_or_404(FOF, id=featured_fof.fof_id)
        fof.view_count += 1
        fof.save()
        frame_list = fof.frame_set.all().order_by('index')[:5]
    else:
        fof = get_object_or_404(FOF, name=fof_name_value)
        fof.view_count += 1
        fof.save()
        frame_list = fof.frame_set.all().order_by('index')[:5]
        
    if fof.user.name:
        user_name = fof.user.name
    else:
        user_name = "Unknown user"

    return render_to_response('uploader/fof_embedded.html', {'fof_height_value':fof_height_value, 'frame_list':frame_list, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))

@csrf_exempt
def trending_fofs(request):
    """
   curl -d json='{"user_id": "2"}' http://localhost:8000/uploader/trending/
   curl -d json='{"user_id": "2"}' http://dyfoc.us/uploader/trending/
   """

    trending_fof_list = FOF.objects.filter(is_private = 0).order_by('-pub_date')
    
    json_request = json.loads(request.POST['json'])
    user_id = json_request['user_id']
    
    response_data = {}
    
    max_number_of_fofs = 100
    index = 0
    
    trending_fof_array = []
    
    for trending_fof in trending_fof_list:

        index = index + 1
        if index > max_number_of_fofs :
            break
        
        fof = {}

        # Add this fof to the user_fof_array
        frame_list = trending_fof.frame_set.all().order_by('index')[:5]

        frames = []
        for frame in frame_list:
            frames.append({"frame_url":frame.url,"frame_index":frame.index})

        if trending_fof.pub_date is None:
            pub_date = "null"
        else:
            raw_pub_date =  json.dumps(trending_fof.pub_date, cls=DjangoJSONEncoder)
            pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]

        likes = trending_fof.like_set.all()

        comments = trending_fof.comment_set.all()

        try :
            Like.objects.get(fof_id = trending_fof.id, user_id = user_id)
            fof["liked"] = "1"
        except (KeyError, Like.DoesNotExist):
            fof["liked"] = "0"
        
        fof["user_name"] = trending_fof.user.name
        fof["fof_name"] = trending_fof.name
        fof["user_id"] = trending_fof.user.id
        fof["user_facebook_id"] = trending_fof.user.facebook_id
        fof["id"] = trending_fof.id
        fof["is_private"] = trending_fof.is_private
        fof["frames"] = frames
        fof["pub_date"] = pub_date
        fof["fof_description"] = trending_fof.description
        fof["comments"] = len(comments)
        fof["likes"] = len(likes)

        trending_fof_array.append(fof)
        
    response_data["fof_list"] = trending_fof_array
        
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

def power_user_feed(request, index):
    index = int(index)
    
    fof_list = FOF.objects.all().order_by('-pub_date')
    
    try:
        # Determines which is the FOF that needs to be shown
        current_fof = fof_list[index]
    
    except (IndexError):
        # Current user hasn't got any friends. Let's redirect him/her to the featured_fofs page!           
        return HttpResponseRedirect('/uploader/0/featured_fof/') 
                   
    else:
        # Finds the correspondent FOF in the database
        fof = FOF.objects.get(name = current_fof)
        frame_list = fof.frame_set.all().order_by('index')[:5]
    
        # Checks if list reached its end (ring loop)
        if len(fof_list) - 1 == index:
            next_fof_index = 0
        else:
            next_fof_index = index + 1

        # Checks if list is in the first element (ring loop)
        if index == 0:
            prev_fof_index = len(fof_list) - 1
        else:
            prev_fof_index = index - 1
    
        if fof.user.name:
            user_name = fof.user.name
        else:
            user_name = "Unknown user"
        
        fof_date = fof.pub_date
        return render_to_response('uploader/fof_viewer.html', {'type':"power_feed_fof",'hide_arrows': 0, 'frame_list':frame_list,'next_fof_name':next_fof_index, 'prev_fof_name':prev_fof_index, 'fof_date':fof.pub_date, 'current_fof':fof.name, 'user_name':user_name, 'fof_id':fof.id}, context_instance=RequestContext(request))

def feed(request, facebook_id_value, index):
    index = int(index)

    # Attempts to find the user by its facebook ID:
    try: 
        user = User.objects.get(facebook_id = facebook_id_value)

        # Gets a list of friends from this user (assuming the data is not duplicated)
        friends_list = Friends.objects.filter(friend_1_id = user.id)

    except (KeyError, User.DoesNotExist):
        return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))
    else:
        i = 0
        fof_list = ''
        # Gets a list of FOFs from each friend
        for friend in friends_list:
            # if friend_1 is user, friend_2 is the friend id
            if friend.friend_1_id == user.id:
                friend_fof_list = FOF.objects.filter(user_id = friend.friend_2_id)[:1000]
            # if friend_2 is user, friend_1 is the friend id
            else:
                friend_fof_list = FOF.objects.filter(user_id = friend.friend_1_id)[:1000]

            # Populates a general list of FOFs from all friends
            fof_list = chain(fof_list, friend_fof_list)

            i = i + 1

        # Adds user's FOFs to the list
        user_fof_list = FOF.objects.filter(user_id = user.id)[:1000]
        fof_list = chain(fof_list, user_fof_list)

        # Sorts list using the publish date
        # NOTE: this converts from QuerySet to list - some of the methods from QuerySet won't be available!
        # this is the pulo from the gato!
        fof_list = sorted(fof_list, key=lambda instance: instance.pub_date, reverse=True)

        try:
            # Determines which is the FOF that needs to be shown
            current_fof = fof_list[index]

        except (IndexError):
            # Current user hasn't got any friends. Let's redirect him/her to the featured_fofs page!           
            return HttpResponseRedirect('/uploader/0/featured_fof/') 

        else:
            # Finds the correspondent FOF in the database
            fof = FOF.objects.get(name = current_fof)
            frame_list = fof.frame_set.all().order_by('index')[:5]

            # Checks if list reached its end (ring loop)
            if len(fof_list) - 1 == index:
                next_fof_index = 0
            else:
                next_fof_index = index + 1

            # Checks if list is in the first element (ring loop)
            if index == 0:
                prev_fof_index = len(fof_list) - 1
            else:
                prev_fof_index = index - 1

            if fof.user.name:
                user_name = fof.user.name
            else:
                user_name = "Unknown user"

            fof_date = fof.pub_date
            return render_to_response('uploader/fof_viewer.html', {'type':"feed_fof",'hide_arrows': 0, 'device_id_value':facebook_id_value, 'mobile_link':"/uploader/"+facebook_id_value+"/m_feed/"+str(index)+"/",'frame_list':frame_list,'next_fof_name':next_fof_index, 'prev_fof_name':prev_fof_index, 'fof_date':fof.pub_date, 'current_fof':fof.name, 'user_name':user_name}, context_instance=RequestContext(request))


def m_feed(request, facebook_id_value, index):
    index = int(index)

    # Attempts to find the user by its facebook ID:
    try: 
        user = User.objects.get(facebook_id = facebook_id_value)

        # Gets a list of friends from this user (assuming the data is not duplicated)
        friends_list = Friends.objects.filter(friend_1_id = user.id)

    except (KeyError, User.DoesNotExist):
        return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))
    else:
        i = 0
        fof_list = ''
        # Gets a list of FOFs from each friend
        for friend in friends_list:
            # if friend_1 is user, friend_2 is the friend id
            if friend.friend_1_id == user.id:
                friend_fof_list = FOF.objects.filter(user_id = friend.friend_2_id)[:1000]
            # if friend_2 is user, friend_1 is the friend id
            else:
                friend_fof_list = FOF.objects.filter(user_id = friend.friend_1_id)[:1000]

            # Populates a general list of FOFs from all friends
            fof_list = chain(fof_list, friend_fof_list)

            i = i + 1

        # Adds user's FOFs to the list
        user_fof_list = FOF.objects.filter(user_id = user.id)[:1000]
        fof_list = chain(fof_list, user_fof_list)
        
        # Sorts list using the publish date
        # NOTE: this converts from QuerySet to list - some of the methods from QuerySet won't be available!
        # this is the pulo from the gato!
        fof_list = sorted(fof_list, key=lambda instance: instance.pub_date, reverse=True)
        
        try:
            # Determines which is the FOF that needs to be shown
            current_fof = fof_list[index]

        except (IndexError):
            # Current user hasn't got any friends. Let's redirect him/her to the featured_fofs page!           
            return HttpResponseRedirect('/uploader/0/featured_fof/')
        
        else:
            # Finds the correspondent FOF in the database
            fof = FOF.objects.get(name = current_fof)
            frame_list = fof.frame_set.all().order_by('index')[:5]

            # Checks if list reached its end (ring loop)
            if len(fof_list) - 1 == index:
                next_fof_index = 0
            else:
                next_fof_index = index + 1

            # Checks if list is in the first element (ring loop)
            if index == 0:
                prev_fof_index = len(fof_list) - 1
            else:
                prev_fof_index = index - 1

            if fof.user.name:
                user_name = fof.user.name
            else:
                user_name = "Unknown user"

            fof_date = fof.pub_date
            return render_to_response('uploader/m_feed.html', {'frame_list':frame_list, 'facebook_id_value':facebook_id_value, 'next_fof_index':next_fof_index, 'prev_fof_index':prev_fof_index, 'user_name':user_name, 'fof_date':fof_date}, context_instance=RequestContext(request))

def list_featured(request):

    featured_fof_list = Featured_FOF.objects.all().order_by('-rank')

    all_fofs = []
    list_len = len(featured_fof_list)
    list_index = 0
    while list_index < list_len:
        all_fofs.append(featured_fof_list[list_index].fof)
        list_index += 1
    i = 0
    return render_to_response('uploader/fof_list.html', {'fof_list':all_fofs,'type':"my_fof", 'mobile_link':"/uploader/"+str(0)+"/featured_fof/m/"}, context_instance=RequestContext(request))
            

@csrf_exempt
def comment(request):
    """ 
    curl -d json='{
        "facebook_id": "100000370417687",
        "fof_id": "96964.057167",
        "comment_message": "QUE LEGAAAL! "
    }' http://localhost:8000/uploader/comment/
    """

    response_data = {}

    json_request = json.loads(request.POST['json'])
    user_facebook_id = json_request['facebook_id']
    comment_message = json_request['comment_message']
    fof_id = json_request['fof_id']

    try:
        user = User.objects.get(facebook_id=user_facebook_id)

        try:
            fof = FOF.objects.get(id=fof_id)
            
            comment = Comment()
            comment.user_id = user.id
            comment.fof_id = fof.id
            comment.comment = comment_message
            comment.pub_date = timezone.now()
            comment.save()
            response_data["result"] = "ok"
            
            firstname = user.name
            for a in firstname:
                if a == " ":
                    firstname = firstname[0: firstname.index(a)]
                    break
                    
            if len(comment_message) > 20:
                comment_message = comment_message[0:20]
                comment_message = comment_message + "..."
                    
            notification_message = ""
            notification_message = notification_message + firstname
            notification_message = notification_message + " commented on your fof: \""
            notification_message = notification_message + comment_message
            notification_message = notification_message + "\"."
            sendAlert(fof.user_id, user.id, user.facebook_id, notification_message, 1, fof.id)

        except (KeyError, FOF.DoesNotExist):
            # Nothing to do here
            response_data["error"] = "FOF doesn't exist"

    except (KeyError, User.DoesNotExist):
        # Nothing to do here
        response_data["error"] = "User doesn't exist"

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    
@csrf_exempt
def user_comment(request):
    """ 
    curl -d json='{"user_id": "2","fof_id": "418","comment_message": "QUE LEGAAAL! "}' http://localhost:8000/uploader/user_comment/
    """
    
    response_data = {}
    
    json_request = json.loads(request.POST['json'])
    user_id = json_request['user_id']
    comment_message = json_request['comment_message']
    fof_id = json_request['fof_id']
    
    try:
        user = User.objects.get(id=user_id)
        
        try:
            fof = FOF.objects.get(id=fof_id)
            
            firstname = user.name
            for a in firstname:
                if a == " ":
                    firstname = firstname[0: firstname.index(a)]
                    break
            if len(comment_message) > 20:
                    comment_message = comment_message[0:20]
                    comment_message = comment_message + "..."
            
            """
            WAIT FOR APP RELEASE TO UNCOMMENT IT //// TODO
            #Lets send an alert to all users that also commented on this fof.
            users_alerted = []
            notification_message = ""
            notification_message = notification_message + firstname
            notification_message = notification_message + " also commented on a fof: \""
            notification_message = notification_message + comment_message
            notification_message = notification_message + "\"."
            for comment in fof.comment_set.all() :
                if comment.user_id != user.id:
                    print users_alerted
                    try:
                        user_already_there = users_alerted.index(comment.user_id)
                        #do nothing we've already sent an notification
                    except ValueError:                    
                        sendAlert(comment.user_id, user.id, user.facebook_id, notification_message, 3, fof.id)
                        users_alerted.append(comment.user_id)
                        
            
            #Lets send an alert to all users that liked this fof.
            notification_message = ""
            notification_message = notification_message + firstname
            notification_message = notification_message + " commented on a fof that you liked: \""
            notification_message = notification_message + comment_message
            notification_message = notification_message + "\"."
            for like in fof.like_set.all() :
                print users_alerted
                if like.user_id != user.id:
                    try:
                        user_already_there = users_alerted.index(like.user_id)
                        # do nothing, we've already sent an notification
                    except ValueError:
                        sendAlert(like.user_id, user.id, user.facebook_id, notification_message, 4, fof.id)
                        users_alerted.append(like.user_id)
                        
            """
            
            comment = Comment()
            comment.user_id = user.id
            comment.fof_id = fof.id
            comment.comment = comment_message
            comment.pub_date = timezone.now()
            comment.save()
            response_data["result"] = "ok"
            response_data["comment_id"] = comment.id
            
            
            notification_message = ""
            notification_message = notification_message + firstname
            notification_message = notification_message + " commented on your fof: \""
            notification_message = notification_message + comment_message
            notification_message = notification_message + "\"."
            sendAlert(fof.user_id, user.id, user.facebook_id, notification_message, 1, fof.id)
          
        except (KeyError, FOF.DoesNotExist):
            # Nothing to do here
            response_data["error"] = "FOF doesn't exist"
            
    except (KeyError, User.DoesNotExist):
        # Nothing to do here
        response_data["error"] = "User doesn't exist"
        
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")    
        
@csrf_exempt
def like(request):    
    """ 
    curl -d json='{
        "facebook_id": "100000370417687",
        "fof_id": "50"
    }' http://localhost:8000/uploader/like/ 
    """

    response_data = {}
        
    json_request = json.loads(request.POST['json'])
    user_facebook_id = json_request['facebook_id']
    fof_id = json_request['fof_id']
    
    try:
        user = User.objects.get(facebook_id=user_facebook_id)
        
        try:
            fof = FOF.objects.get(id=fof_id)
            
            try:
                Like.objects.get(user_id = user.id, fof_id = fof.id)
                response_data["error"] = "like already exists"
                            
            except (KeyError, Like.DoesNotExist):
                # Nothing to do here
                like = Like()
                like.user_id = user.id
                like.fof_id = fof.id
                like.pub_date = timezone.now()
                like.save()
                response_data["result"] = "ok"
                
                firstname = user.name
                for a in firstname:
                    if a == " ":
                        firstname = firstname[0: firstname.index(a)]
                        break
                        
                notification_message = ""
                notification_message = notification_message + firstname
                notification_message = notification_message + " liked your FOF."
                sendAlert(fof.user_id, user.id, user.facebook_id, notification_message, 0, fof.id)
            
        except (KeyError, FOF.DoesNotExist):
            # Nothing to do here
            response_data["error"] = "FOF doesn't exist"
    
    except (KeyError, User.DoesNotExist):
        # Nothing to do here
        response_data["error"] = "User doesn't exist"
        
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

@csrf_exempt
def user_like(request):    
    """ 
    curl -d json='{
        "user_id": "2",
        "fof_id": "50"
    }' http://localhost:8000/uploader/like/ 
    """
    
    response_data = {}
    
    json_request = json.loads(request.POST['json'])
    user_id = json_request['user_id']
    fof_id = json_request['fof_id']
    
    try:
        user = User.objects.get(id=user_id)
        
        try:
            fof = FOF.objects.get(id=fof_id)
            
            try:
                Like.objects.get(user_id = user.id, fof_id = fof.id)
                response_data["error"] = "like already exists"
                
            except (KeyError, Like.DoesNotExist):
                # Nothing to do here
                like = Like()
                like.user_id = user.id
                like.fof_id = fof.id
                like.pub_date = timezone.now()
                like.save()
                response_data["result"] = "ok"
                
                firstname = user.name
                for a in firstname:
                    if a == " ":
                        firstname = firstname[0: firstname.index(a)]
                        break
                        
                notification_message = ""
                notification_message = notification_message + firstname
                notification_message = notification_message + " liked your FOF."
                sendAlert(fof.user_id, user.id, user.facebook_id, notification_message, 0, fof.id)
                
        except (KeyError, FOF.DoesNotExist):
            # Nothing to do here
            response_data["error"] = "FOF doesn't exist"
            
    except (KeyError, User.DoesNotExist):
        # Nothing to do here
        response_data["error"] = "User doesn't exist"
        
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")


@csrf_exempt
def likes_and_comments(request):
    '''
    curl -d json='{
        "fof_id": "22"
    }' http://localhost:8000/uploader/likes_and_comments/
    '''
    response_data = {}
    
    json_request = json.loads(request.POST['json'])
    
    fof_id = json_request['fof_id']
    
    try:
        fof = FOF.objects.get(id=fof_id)
        
    except (KeyError, FOF.DoesNotExist):
        # Ciao Ciao
        response_data["error"] = "FOF does not exist"
    
    else:
        likes = fof.like_set.all()
        comments = fof.comment_set.all()
        
        response_data["like_list"] = []
        response_data["comment_list"] = []
        
        for like in likes:
            
            raw_pub_date =  json.dumps(timezone.now(), cls=DjangoJSONEncoder)
            print raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]
            
            if like.pub_date is None:
                pub_date = "null"
            else:
                raw_pub_date =  json.dumps(like.pub_date, cls=DjangoJSONEncoder)
                pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]
            
            response_data["like_list"].append({"like_id":like.id, "user_facebook_id":like.user.facebook_id, "user_id":like.user.id, "user_name":like.user.name,"fof_id":fof.id,"pub_date":pub_date})
            
        for comment in comments:
            
            if comment.pub_date is None:
                pub_date = "null"
            else:
                raw_pub_date =  json.dumps(comment.pub_date, cls=DjangoJSONEncoder)
                pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]
            
            response_data["comment_list"].append({"comment_id":comment.id, "user_facebook_id":comment.user.facebook_id, "user_id":comment.user.id, "user_name":comment.user.name,"fof_id":fof.id,"pub_date":pub_date,"comment":comment.comment})
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
        

@csrf_exempt
def signup(request):
    
    '''
    curl -d json='{
           "user_password": "123456",
           "user_name": "Looot",
           "user_email": "l@ls.com",
           "device_id": "123123123123123"
      }' http://localhost:8000/uploader/signup/
    '''
    json_request = json.loads(request.POST['json'])
    
    user_password = json_request['user_password']
    user_name = json_request['user_name']
    user_email = json_request['user_email']
    user_device_id = json_request['device_id']
    
    response_data = {}
    
    try:
        user = User.objects.get(email=user_email)
        response_data['error'] = "Email already taken, try another one:"
        
        return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
        
    except (KeyError, User.DoesNotExist):
        
        user = User(email = user_email, name = user_name, password = user_password, device_id = user_device_id, pub_date=timezone.now())
        
        user.id_origin = 2
        
        user.save()
        
        featured_fof_list = Featured_FOF.objects.all().order_by('-rank')

        featured_fof_array = []

        for featured_fof in featured_fof_list:

            fof = {}

            frame_list = featured_fof.fof.frame_set.all().order_by('index')[:5]

            frames = []
            for frame in frame_list:
                frames.append({"frame_url":frame.url,"frame_index":frame.index})
                
            fof_object = featured_fof.fof
            
            if fof_object.pub_date is None:
                pub_date = "null"
            else:
                raw_pub_date =  json.dumps(fof_object.pub_date, cls=DjangoJSONEncoder)
                pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]
                
            fof_user = fof_object.user
            
            likes = fof_object.like_set.all()
            
            comments = fof_object.comment_set.all()
            
            try :
                Like.objects.get(fof_id = fof_object.id, user_id = user.id)
                fof["liked"] = "1"
            except (KeyError, Like.DoesNotExist):
                fof["liked"] = "0"
                
            fof["user_name"] = fof_user.name
            fof["user_id"] = fof_user.id
            fof["user_facebook_id"] = fof_user.facebook_id
            fof["id"] = fof_object.id
            fof["is_private"] = fof_object.is_private
            fof["fof_name"] = fof_object.name
            fof["frames"] = frames
            fof["pub_date"] = pub_date
            fof["fof_drescription"] = fof_object.description
            fof["comments"] = len(comments)
            fof["likes"] = len(likes)
            
            featured_fof_array.append(fof)
            
        response_data['featured_fof_list'] = featured_fof_array

        response_data['notification_list'] = []
        response_data['friends_list'] = []
        response_data['feed_fof_list'] = []
        response_data['user_fof_list'] = []
        
        firstname = user.name
        for a in firstname:
            if a == " ":
                firstname = firstname[0: firstname.index(a)]
                break
                
        reponseString = "Hi "
        reponseString = reponseString + user.name
        reponseString = reponseString + ", <br/><br/>We're really glad to have you in the family."
        reponseString = reponseString + "<br/>If you have any questions or suggestions we would be glad to hear them. Thanks,"
        reponseString = reponseString + "<br/> Victor Oliveira<br/>dyfocus co-founder.<br/> <a href=\"https://www.facebook.com/dyfocus\">https://www.facebook.com/dyfocus<a/><br/><a href=\"http://dyfoc.us/\">http://dyfoc.us/<a/>"
        
        title = "Welcome " + firstname
        
        email = EmailMessage(title, reponseString, to=[user.email])
        email.content_subtype = "html"
        email.send()
        
        response_data['user_name'] = user_name
        response_data['user_email'] = user_email
        response_data['user_id'] = user.id
        response_data['user_following_count'] = 0
        response_data['user_followers_count'] = 0
            
        return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
            

@csrf_exempt
def login(request):
    
    json_request = json.loads(request.POST['json'])

    device_id_value = json_request['device_id']
    user_name = json_request['name']
    user_facebook_id = json_request['facebook_id']
    user_email = json_request['email']
    #user_id_origin = json_request['id_origin']

    # Lets find this user or create a new one if necessary
    try:
        user = User.objects.get(facebook_id=user_facebook_id)
        user.device_id = device_id_value
        user.save()
    except (KeyError, User.DoesNotExist):
        # if no information about user's origin is sent, he/she is using an older version of the app and therefore came from FB

        # TODO /// ADD AFTER FIXED APP ///
        #if user_id_origin is None:
        #    user_id_origin = 1
        
        # TODO /// REMOVE AFTER FIXED APP ///
        user_id_origin = 1
        
        user = User(device_id = device_id_value, name = user_name, facebook_id = user_facebook_id, pub_date=timezone.now(), email = user_email, id_origin = user_id_origin)

        # TODO /// ADD AFTER FIXED APP ///
        # if the user does not come from facebook, its facebook_id will be equal to its id
        #if user_id_origin == 0:
        #    user.facebook_id = user.id
            
        user.save()
        
    
    response_data = {}
    response_data['notification_list'] = []
    
    user_notifications = Device_Notification.objects.filter(Q(receiver_id = user.id)).order_by('-pub_date')
    
    for notification in user_notifications:
        response_data['notification_list'].append({"message":notification.message,"user_facebook_id":notification.sender_facebook_id, "notification_id":notification.id, "was_read":notification.was_read, "trigger_type":notification.trigger_type, "trigger_id":notification.trigger_id})
        
    # Lets populate the friends table with the new information
    
    user_friends = Friends.objects.filter(Q(friend_1_id = user.id))
    
    for friend in json_request['friends']:
        try: 
            # Is there any user with the same facebook_id as the requesting user friend is?
            user_friend = User.objects.get(facebook_id = friend['facebook_id'])

            # Yes! They are friends! Let's add a new row to the friends model!...
            # ...First lets checkout if that friend row doesn't exists already:
            try:
                user_friends.get(friend_2_id = user_friend.id)
            except (KeyError, Friends.DoesNotExist):
                # It doesn't exists, lets create it:
                friend_relation = Friends(friend_1_id = user.id, friend_2_id = user_friend.id)
                friend_relation.save()
                
                notification_message = user.name + " started following you."
                
                """
                WAIT FOR APP RELEASE TO UNCOMMENT IT //// TODO
                sendAlert(user_friend.id, user.id, user.facebook_id, notification_message, 2, user.id)
                """

        except (KeyError, User.DoesNotExist):
            # Nothing to do here
            j = 0


    # Now lets returns the list of the requesting user dyfocus friends

    response_data['user_following_count'] = following_calc(user.id)
    response_data['user_followers_count'] = followers_calc(user.id)
    
    response_data['friends_list'] = []

    feed_fof_list = ''
    
    for friend in user_friends:
        try:
            #Populates a friends list
            user_friend_object = User.objects.get(id = friend.friend_2_id)
            if user_friend_object.followers_count is None:
                followers = followers_calc(user_friend_object.id)
            else:
                followers = user_friend_object.followers_count
            if user_friend_object.following_count is None:
                following = following_calc(user_friend_object.id)
            else:
                following = user_friend_object.following_count
                
            response_data['friends_list'].append({"id":user_friend_object.id, "facebook_id":user_friend_object.facebook_id, "name":user_friend_object.name, "id_origin":user_friend_object.id_origin, "followers_count":followers, "following_count":following})
            
            #Populates a general list of FOFs from all friends
            
            
            friend_fof_list_values = FOF.objects.filter(user_id = friend.friend_2_id,  is_private = 0).all().order_by('-pub_date')
            friend_fof_list = []
            
            
            max_number_of_fofs = 30
            index = 0
            if friend_fof_list_values.count() > max_number_of_fofs:
                
                while index < max_number_of_fofs:
                    friend_fof_list.append(friend_fof_list_values[index])
                    index = index + 1
                
                
                feed_fof_list = chain(feed_fof_list, friend_fof_list)
            else :
                feed_fof_list = chain(feed_fof_list, friend_fof_list_values)
            
        except (KeyError, User.DoesNotExist):
            # Nothing to do here
            j = 0
    
    featured_fof_list = Featured_FOF.objects.all().order_by('-rank')

    featured_fof_array = []

    for featured_fof in featured_fof_list:

        fof = {}

        frame_list = featured_fof.fof.frame_set.all().order_by('index')[:5]

        frames = []
        for frame in frame_list:
            frames.append({"frame_url":frame.url,"frame_index":frame.index})

        fof_object = featured_fof.fof

        if fof_object.pub_date is None:
            pub_date = "null"
        else:
            raw_pub_date =  json.dumps(fof_object.pub_date, cls=DjangoJSONEncoder)
            pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]

        fof_user = fof_object.user

        likes = fof_object.like_set.all()

        comments = fof_object.comment_set.all()
        
        try :
            Like.objects.get(fof_id = fof_object.id, user_id = user.id)
            fof["liked"] = "1"
        except (KeyError, Like.DoesNotExist):
            fof["liked"] = "0"            

       
        fof["user_name"] = fof_user.name
        fof["user_id"] = fof_user.id
        fof["user_facebook_id"] = fof_user.facebook_id
        fof["id"] = fof_object.id
        fof["is_private"] = fof_object.is_private
        fof["fof_name"] = fof_object.name
        fof["frames"] = frames
        fof["pub_date"] = pub_date
        fof["fof_description"] = fof_object.description
        fof["comments"] = len(comments)
        fof["likes"] = len(likes)

        featured_fof_array.append(fof)

        response_data['featured_fof_list'] = featured_fof_array

    # creating the user fof array
    user_fof_array = []
    user_fof_list = user.fof_set.all().order_by('-pub_date')
    
    
    #if len(user_fof_list) is 0:
    #    user_fof_list = []
    #    hard_coded_fof = FOF.objects.get(id=124)
    #    hard_coded_fof.user_id = user.id
    #     user_fof_list.append(hard_coded_fof)
    
    # Lets create the feed fof list
    
    # Adds user's FOFs to the list
    feed_fof_list = chain(feed_fof_list, user_fof_list)

    #Sorts list using the publish date
	# NOTE: this converts from QuerySet to list - some of the methods from QuerySet won't be available!
	# this is the pulo from the gato!
    feed_fof_list = sorted(feed_fof_list, key=lambda instance: instance.pub_date, reverse=True)
    feed_fof_array = []

    for feed_fof in feed_fof_list:
        
        fof = {}
        
        # Add this fof to the user_fof_array
        frame_list = feed_fof.frame_set.all().order_by('index')[:5]

        frames = []
        for frame in frame_list:
            frames.append({"frame_url":frame.url,"frame_index":frame.index})
        
        if feed_fof.pub_date is None:
            pub_date = "null"
        else:
            raw_pub_date =  json.dumps(feed_fof.pub_date, cls=DjangoJSONEncoder)
            pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]

        likes = feed_fof.like_set.all()

        comments = feed_fof.comment_set.all()
        
        try :
            Like.objects.get(fof_id = feed_fof.id, user_id = user.id)
            fof["liked"] = "1"
        except (KeyError, Like.DoesNotExist):
            fof["liked"] = "0"
            
        fof["user_name"] = feed_fof.user.name
        fof["user_id"] = feed_fof.user.id
        fof["user_facebook_id"] = feed_fof.user.facebook_id
        fof["id"] = feed_fof.id
        fof["fof_name"] = feed_fof.name
        fof["frames"] = frames
        fof["pub_date"] = pub_date
        fof["is_private"] = feed_fof.is_private
        fof["comments"] = len(comments)
        fof["likes"] = len(likes)
        fof["fof_description"] = feed_fof.description
        
        if feed_fof.is_private == 0:
            feed_fof_array.append(fof)
        
        if feed_fof.user == user:
            user_fof_array.append(fof)
        
    response_data['feed_fof_list'] = feed_fof_array
    response_data['user_fof_list'] = user_fof_array
    response_data['user_id'] = user.id  
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    
    
@csrf_exempt
def login_user(request):

    json_request = json.loads(request.POST['json'])
    
    user_device_id = json_request['device_id']
    user_email = json_request['user_email']
    user_password = json_request['user_password']
    
    response_data = {}

    # Lets find this user or create a new one if necessary
    try:
        user = User.objects.get(email=user_email)
        
        if user.password == user_password :
            print "pepepe"
            user.device_id = user_device_id
            user.save()
        else:
            print "pepepealalal"
            response_data["error"] = "Email/Password doesn't match"
            return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
        
    except (KeyError, User.DoesNotExist):
        response_data["error"] = "Email/Password doesn't match"
        return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

    response_data['notification_list'] = []

    user_notifications = Device_Notification.objects.filter(Q(receiver_id = user.id)).order_by('-pub_date')

    for notification in user_notifications:
        response_data['notification_list'].append({"message":notification.message,"user_facebook_id":notification.sender_facebook_id, "notification_id":notification.id, "was_read":notification.was_read, "trigger_type":notification.trigger_type, "trigger_id":notification.trigger_id})


    # Now lets returns the list of the requesting user dyfocus friends

    response_data['user_following_count'] = following_calc(user.id)
    response_data['user_followers_count'] = followers_calc(user.id)

    response_data['friends_list'] = []

    feed_fof_list = ''

    user_friends = Friends.objects.filter(Q(friend_1_id = user.id))
    
    for friend in user_friends:
        try:
            #Populates a friends list
            user_friend_object = User.objects.get(id = friend.friend_2_id)
            if user_friend_object.followers_count is None:
                followers = followers_calc(user_friend_object.id)
            else:
                followers = user_friend_object.followers_count
            if user_friend_object.following_count is None:
                following = following_calc(user_friend_object.id)
            else:
                following = user_friend_object.following_count

            response_data['friends_list'].append({"id":user_friend_object.id, "facebook_id":user_friend_object.facebook_id, "name":user_friend_object.name, "id_origin":user_friend_object.id_origin, "followers_count":followers, "following_count":following})

            #Populates a general list of FOFs from all friends
            friend_fof_list = FOF.objects.filter(user_id = friend.friend_2_id, is_private = 0)[:1000]            
            feed_fof_list = chain(feed_fof_list, friend_fof_list)

        except (KeyError, User.DoesNotExist):
            # Nothing to do here
            j = 0


    featured_fof_list = Featured_FOF.objects.all().order_by('-rank')

    featured_fof_array = [];

    for featured_fof in featured_fof_list:

        fof = {}

        frame_list = featured_fof.fof.frame_set.all().order_by('index')[:5]

        frames = []
        for frame in frame_list:
            frames.append({"frame_url":frame.url,"frame_index":frame.index})

        fof_object = featured_fof.fof

        if fof_object.pub_date is None:
            pub_date = "null"
        else:
            raw_pub_date =  json.dumps(fof_object.pub_date, cls=DjangoJSONEncoder)
            pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]

        fof_user = fof_object.user

        likes = fof_object.like_set.all()

        comments = fof_object.comment_set.all()

        try :
            Like.objects.get(fof_id = fof_object.id, user_id = user.id)
            fof["liked"] = "1"
        except (KeyError, Like.DoesNotExist):
            fof["liked"] = "0"            


        fof["user_name"] = fof_user.name
        fof["user_id"] = fof_user.id
        fof["user_facebook_id"] = fof_user.facebook_id
        fof["id"] = fof_object.id
        fof["is_private"] = fof_object.is_private
        fof["fof_name"] = fof_object.name
        fof["frames"] = frames
        fof["pub_date"] = pub_date
        fof["fof_description"] = fof_object.description

        fof["comments"] = len(comments)
        fof["likes"] = len(likes)

        featured_fof_array.append(fof)

        response_data['featured_fof_list'] = featured_fof_array

    # creating the user fof array
    user_fof_array = []
    user_fof_list = user.fof_set.all().order_by('-pub_date')


    #if len(user_fof_list) is 0:
    #    user_fof_list = []
    #    hard_coded_fof = FOF.objects.get(id=124)
    #    hard_coded_fof.user_id = user.id
    #     user_fof_list.append(hard_coded_fof)

    # Lets create the feed fof list

    # Adds user's FOFs to the list
    feed_fof_list = chain(feed_fof_list, user_fof_list)

    #Sorts list using the publish date
	# NOTE: this converts from QuerySet to list - some of the methods from QuerySet won't be available!
	# this is the pulo from the gato!
    feed_fof_list = sorted(feed_fof_list, key=lambda instance: instance.pub_date, reverse=True)
    feed_fof_array = []

    for feed_fof in feed_fof_list:

        fof = {}

        # Add this fof to the user_fof_array
        frame_list = feed_fof.frame_set.all().order_by('index')[:5]

        frames = []
        for frame in frame_list:
            frames.append({"frame_url":frame.url,"frame_index":frame.index})

        if feed_fof.pub_date is None:
            pub_date = "null"
        else:
            raw_pub_date =  json.dumps(feed_fof.pub_date, cls=DjangoJSONEncoder)
            pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]

        likes = feed_fof.like_set.all()

        comments = feed_fof.comment_set.all()

        try :
            Like.objects.get(fof_id = feed_fof.id, user_id = user.id)
            fof["liked"] = "1"
        except (KeyError, Like.DoesNotExist):
            fof["liked"] = "0"

        fof["user_name"] = feed_fof.user.name
        fof["user_id"] = feed_fof.user.id
        fof["user_facebook_id"] = feed_fof.user.facebook_id
        fof["id"] = feed_fof.id
        fof["is_private"] = feed_fof.is_private
        fof["fof_name"] = feed_fof.name
        fof["frames"] = frames
        fof["pub_date"] = pub_date
        fof["fof_description"] = feed_fof.description

        fof["comments"] = len(comments)
        fof["likes"] = len(likes)

        if feed_fof.is_private == 0:
            feed_fof_array.append(fof)

        if feed_fof.user == user:
            user_fof_array.append(fof)


    response_data['feed_fof_list'] = feed_fof_array
    response_data['user_fof_list'] = user_fof_array
    response_data['user_id'] = user.id  
    response_data['user_name'] = user.name
    response_data['user_email'] = user.email
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")


@csrf_exempt
def user_web_info(request):
    if request.is_ajax():
        if request.method == 'GET':
            message = "This is an XHR GET request"
        elif request.method == 'POST':
            message = "Your email is "+request.POST['email']
            # Here we can access the POST data
            print request.POST
            user_name = request.POST['name']
            user_facebook_id = request.POST['facebook_id']
            user_email = request.POST['email']
            
            try:
                user = User.objects.get(facebook_id = user_facebook_id)
            except (KeyError, User.DoesNotExist):
                user_id_origin = 1 # user came from Facebook
                user = User(name = user_name, device_id = '', facebook_id = user_facebook_id, pub_date=timezone.now(), email = user_email, id_origin = user_id_origin)
                result = "User not found - Creating one"
                print result
                user.save()
            else:
                user.name = user_name
                user.facebook_id = user_facebook_id
                user.email = user_email
                result = "User found - Updating info"
                user.save()
                print result
    else:
        message = "No XHR"
    return HttpResponse()


@csrf_exempt
def user_json_feed(request):
    '''
    curl -d json='{
        "user_facebook_id": "100000370417687"
    }' http://localhost:8080/uploader/json_feed/
    '''

    json_request = json.loads(request.POST['json'])
    user_id = json_request['user_id']

    response_data = {}

    try:
        user = User.objects.get(id=user_id)
        response_data['fof_list'] = get_user_feed_array(user)

    except (KeyError, User.DoesNotExist):
        response_data['error'] = "User could not be found"

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
        
@csrf_exempt
def json_feed(request):
    '''
    curl -d json='{
        "user_facebook_id": "100000370417687"
    }' http://localhost:8080/uploader/json_feed/
    '''
    
    json_request = json.loads(request.POST['json'])
    user_facebook_id = json_request['user_facebook_id']

    response_data = {}

    try:
        user = User.objects.get(facebook_id=user_facebook_id)
        response_data['fof_list'] = get_user_feed_array(user)
        
    except (KeyError, User.DoesNotExist):
        response_data['error'] = "User could not be found"

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")


def get_user_feed_array(user):
    
    user_friends = Friends.objects.filter(Q(friend_1_id = user.id))

    feed_fof_list = ''

    for friend in user_friends:

        #Populates a general list of FOFs from all friends
        friend_fof_list = FOF.objects.filter(user_id = friend.friend_2_id, is_private = 0)[:1000]            
        feed_fof_list = chain(feed_fof_list, friend_fof_list)

    # Adds personal FOFs to the feed list
    user_fof_list = FOF.objects.filter(user_id = user.id, is_private = 0)[:1000]
    feed_fof_list = chain(feed_fof_list, user_fof_list)

    # Sorts the list
    feed_fof_list = sorted(feed_fof_list, key=lambda instance: instance.pub_date, reverse=True)
    feed_fof_array = []

    for feed_fof in feed_fof_list:

        fof = {}

        # Add this fof to the user_fof_array
        frame_list = feed_fof.frame_set.all().order_by('index')[:5]

        frames = []
        for frame in frame_list:
            frames.append({"frame_url":frame.url,"frame_index":frame.index})

        if feed_fof.pub_date is None:
            pub_date = "null"
        else:
            raw_pub_date =  json.dumps(feed_fof.pub_date, cls=DjangoJSONEncoder)
            pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]

        likes = feed_fof.like_set.all()

        comments = feed_fof.comment_set.all()

        try :
            Like.objects.get(fof_id = feed_fof.id, user_id = user.id)
            fof["liked"] = "1"
        except (KeyError, Like.DoesNotExist):
            fof["liked"] = "0"

        fof["user_name"] = feed_fof.user.name
        fof["fof_name"] = feed_fof.name
        fof["user_id"] = feed_fof.user.id
        fof["user_facebook_id"] = feed_fof.user.facebook_id
        fof["id"] = feed_fof.id
        fof["is_private"] = feed_fof.is_private
        fof["frames"] = frames
        fof["pub_date"] = pub_date
        fof["fof_description"] = feed_fof.description

        fof["comments"] = len(comments)
        fof["likes"] = len(likes)

        feed_fof_array.append(fof)

        #if feed_fof.user == user:
        #    user_fof_array.append(fof)
    return feed_fof_array

@csrf_exempt
def json_featured_fof(request):
    '''
    curl -d json='{
        "user_facebook_id": "100000370417687"
    }' http://localhost:8080/uploader/json_featured_fof/
    '''
    json_request = json.loads(request.POST['json'])
    user_facebook_id = json_request['user_facebook_id']
    response_data = {}
    
    try:
        user = User.objects.get(facebook_id=user_facebook_id)

    except (KeyError, User.DoesNotExist):
        response_data['error'] = "User could not be found"
    
    else:
        featured_fof_list = Featured_FOF.objects.all().order_by('-rank')

        featured_fof_array = [];

        for featured_fof in featured_fof_list:

            fof = {}

            frame_list = featured_fof.fof.frame_set.all().order_by('index')[:5]

            frames = []
            for frame in frame_list:
                frames.append({"frame_url":frame.url,"frame_index":frame.index})

            fof_object = featured_fof.fof

            if fof_object.pub_date is None:
                pub_date = "null"
            else:
                raw_pub_date =  json.dumps(fof_object.pub_date, cls=DjangoJSONEncoder)
                pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]
                

            fof_user = fof_object.user

            likes = fof_object.like_set.all()

            comments = fof_object.comment_set.all()
        
            try :
                Like.objects.get(fof_id = fof_object.id, user_id = user.id)
                fof["liked"] = "1"
            except (KeyError, Like.DoesNotExist):
                fof["liked"] = "0"

       
            fof["user_name"] = fof_user.name
            fof["user_id"] = fof_user.id
            fof["user_facebook_id"] = fof_user.facebook_id
            fof["id"] = fof_object.id
            fof["is_private"] = fof_object.is_private
            fof["fof_name"] = fof_object.name
            fof["frames"] = frames
            fof["pub_date"] = pub_date
            fof["fof_description"] = fof_object.description

            fof["comments"] = len(comments)
            fof["likes"] = len(likes)

            featured_fof_array.append(fof)

            response_data['fof_list'] = featured_fof_array
       
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    
    
@csrf_exempt
def user_json_featured_fof(request):
    '''
    curl -d json='{
        "user_facebook_id": "100000370417687"
    }' http://localhost:8080/uploader/json_featured_fof/
    '''
    json_request = json.loads(request.POST['json'])
    user_id = json_request['user_id']
    response_data = {}

    try:
        user = User.objects.get(id=user_id)

    except (KeyError, User.DoesNotExist):
        response_data['error'] = "User could not be found"

    else:
        featured_fof_list = Featured_FOF.objects.all().order_by('-rank')

        featured_fof_array = [];

        for featured_fof in featured_fof_list:

            fof = {}

            frame_list = featured_fof.fof.frame_set.all().order_by('index')[:5]

            frames = []
            for frame in frame_list:
                frames.append({"frame_url":frame.url,"frame_index":frame.index})

            fof_object = featured_fof.fof

            if fof_object.pub_date is None:
                pub_date = "null"
            else:
                raw_pub_date =  json.dumps(fof_object.pub_date, cls=DjangoJSONEncoder)
                pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]


            fof_user = fof_object.user

            likes = fof_object.like_set.all()

            comments = fof_object.comment_set.all()

            try :
                Like.objects.get(fof_id = fof_object.id, user_id = user.id)
                fof["liked"] = "1"
            except (KeyError, Like.DoesNotExist):
                fof["liked"] = "0"


            fof["user_name"] = fof_user.name
            fof["user_id"] = fof_user.id
            fof["user_facebook_id"] = fof_user.facebook_id
            fof["id"] = fof_object.id
            fof["is_private"] = fof_object.is_private
            fof["fof_name"] = fof_object.name
            fof["frames"] = frames
            fof["pub_date"] = pub_date
            fof["fof_description"] = fof_object.description

            fof["comments"] = len(comments)
            fof["likes"] = len(likes)

            featured_fof_array.append(fof)

            response_data['fof_list'] = featured_fof_array

    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    
@csrf_exempt
def json_user_id_fof(request):
    '''
    curl -d json='{
        "user_facebook_id": "100000370417687"
    }' http://localhost:8080/uploader/json_user_fof/
    '''
    json_request = json.loads(request.POST['json'])
    user_id = json_request['user_id']
    response_data = {}

    try:
        user = User.objects.get(id=user_id)

    except (KeyError, User.DoesNotExist):
        response_data['error'] = "User could not be found"

    else:

        user_fof_array = get_user_fofs(user)

        response_data['fof_list'] = user_fof_array

        return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

@csrf_exempt
def json_user_fof(request):
    '''
    curl -d json='{
        "user_facebook_id": "100000370417687"
    }' http://localhost:8080/uploader/json_user_fof/
    '''
    json_request = json.loads(request.POST['json'])
    user_facebook_id = json_request['user_facebook_id']
    response_data = {}
    
    try:
        user = User.objects.get(facebook_id=user_facebook_id)

    except (KeyError, User.DoesNotExist):
        response_data['error'] = "User could not be found"
    
    else:
    
        user_fof_array = get_user_fofs(user)
            
        response_data['fof_list'] = user_fof_array

        return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
        
def get_user_fofs(user):
    
    user_fof_array = []
    user_fof_list = user.fof_set.all().order_by('-pub_date')

    for user_fof in user_fof_list:
        fof = {}

        # Add this fof to the user_fof_array
        frame_list = user_fof.frame_set.all().order_by('index')[:5]

        frames = []
        for frame in frame_list:
            frames.append({"frame_url":frame.url,"frame_index":frame.index})


        if user_fof.pub_date is None:
            pub_date = "null"
        else:
            raw_pub_date =  json.dumps(user_fof.pub_date, cls=DjangoJSONEncoder)
            pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]

        likes = user_fof.like_set.all()

        comments = user_fof.comment_set.all()

        try :
            Like.objects.get(fof_id = user_fof.id, user_id = user.id)
            fof["liked"] = "1"
        except (KeyError, Like.DoesNotExist):
            fof["liked"] = "0"

        fof["user_name"] = user_fof.user.name
        fof["user_id"] = user_fof.user.id
        fof["user_facebook_id"] = user_fof.user.facebook_id
        fof["id"] = user_fof.id
        fof["is_private"] = user_fof.is_private
        fof["fof_name"] = user_fof.name
        fof["frames"] = frames
        fof["pub_date"] = pub_date
        fof["fof_description"] = user_fof.description

        fof["comments"] = len(comments)
        fof["likes"] = len(likes)

        user_fof_array.append(fof)

    return user_fof_array
        
def sendAlertExample(request):
    
    sendAlert(2, 7, 640592329, "Dan commented on your fof: asdasd", 1, 372)
    
    return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))
    
def sendAlert(receiver_id_value, sender_id_value, sender_facebook_id_value, message_value, trigger_type_value, trigger_id_value):
    import socket, ssl, json, struct
    # device token returned when the iPhone application
    # registers to receive alerts
    
    if not receiver_id_value == sender_id_value:
        try:
            user = User.objects.get(id=receiver_id_value)
            deviceToken = user.device_id

            #Add new row for the table Device_Notification
            if sender_facebook_id_value :
                notification = Device_Notification(receiver_id = receiver_id_value, sender_id = sender_id_value, sender_facebook_id = sender_facebook_id_value, message = message_value, trigger_type = trigger_type_value, trigger_id = trigger_id_value,  pub_date=timezone.now(), was_read = 0)
            else:
                notification = Device_Notification(receiver_id = receiver_id_value, sender_id = sender_id_value, message = message_value, trigger_type = trigger_type_value, trigger_id = trigger_id_value,  pub_date=timezone.now(), was_read = 0)                

            notification.save()

            notifications = Device_Notification.objects.filter(Q(receiver_id = user.id)).order_by('-pub_date')

            read_notifications = 0
            for notification in notifications:
                if not notification.was_read:
                    read_notifications = read_notifications + 1

            #deviceToken = '23d9e172dee23a7e42fa148b4dcd621f5a8931c96e2e336d72662984ff007979'
            #23d9e172 dee23a7e 42fa148b 4dcd621f 5a8931c9 6e2e336d 72662984 ff007979
            #d65d75d a4cedd23 774c0e88 28a9aab6 b5e9470e a7ad1ad8 dc1e9629 2c585090
            thePayLoad = {
                 'aps': {
                      'alert': message_value,
                      'sound':'k1DiveAlarm.caf',
                      'badge':read_notifications,
                      },
                 'test_data': { 'foo': 'bar' },
                 }

            # Certificate issued by apple and converted to .pem format with openSSL
            # Per Apple's Push Notification Guide (end of chapter 3), first export the cert in p12 format
            # openssl pkcs12 -in cert.p12 -out cert.pem -nodes 
            #   when prompted "Enter Import Password:" hit return
            #
            #theCertfile = '/Users/mac/mysite/uploader/apple_push_notification_dev.pem'

            if not deviceToken == "null":
                
                theCertfile = '/home/ubuntu/mysite/uploader/prod_cert.pem'
                # 
                theHost = ( 'gateway.push.apple.com', 2195 )
                # 
                data = json.dumps( thePayLoad )
                # Clear out spaces in the device token and convert to hex
                deviceToken = deviceToken.replace(' ','')
                #byteToken = bytes.fromhex( deviceToken ) # Python 3
                byteToken = deviceToken.decode('hex') # Python 2
                theFormat = '!BH32sH%ds' % len(data)
                theNotification = struct.pack( theFormat, 0, 32, byteToken, len(data), data )

                # Create our connection using the certfile saved locally
                ssl_sock = ssl.wrap_socket( socket.socket( socket.AF_INET, socket.SOCK_STREAM ), certfile = theCertfile )
                ssl_sock.connect( theHost )

                # Write out our data
                ssl_sock.write( theNotification )

                # Close the connection -- apple would prefer that we keep
                # a connection open and push data as needed.
                ssl_sock.close()
            
        except (KeyError, User.DoesNotExist):
            i = 0
        
    
@csrf_exempt
def user_read_notification(request):
    
    json_request = json.loads(request.POST['json'])
    notification_id = json_request['notification_id']
    user_id = json_request['user_id']
    read_all = json_request['read_all'] == "1"
    
    if read_all:
        try:
            user = User.objects.get(id=user_id)
            
            return read_user_notifications(user, notification_id)
        
        except (KeyError, User.DoesNotExist):
            response_data = {}
            response_data['notification_list'] = []
            response_data["result"] = "error"
            
            return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    else:
        return read_notification_object(notification_id)
    

@csrf_exempt
def read_notification(request):
    
    json_request = json.loads(request.POST['json'])
    notification_id = json_request['notification_id']
    user_id = json_request['user_id']
    read_all = json_request['read_all'] == "1"
    
    if read_all:
        try:
            user = User.objects.get(facebook_id=user_id)
            
            return read_user_notifications(user, notification_id)
       
        except (KeyError, User.DoesNotExist):
            response_data = {}
            response_data['notification_list'] = []
            response_data["result"] = "error"
            
            return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
            
    else:
        return read_notification_object(notification_id)
        

@csrf_exempt
def read_user_notifications(user, notification_id):
    response_data = {}
    response_data['notification_list'] = []

    notifications = Device_Notification.objects.filter(Q(receiver_id = user.id)).order_by('-pub_date')
    
    if len(notifications) > 0 :
        
        if not str(notifications[0].id) == str(notification_id):
            for notification in notifications:
                response_data['notification_list'].append({"message":notification.message,"user_facebook_id":notification.sender_facebook_id, "notification_id":notification.id, "was_read":notification.was_read,"trigger_id":notification.trigger_id,"trigger_type":notification.trigger_type})
                
        notification_was_reached = False
        for notification in notifications:
            #print "LOOP"
            if not notification_was_reached:
                #print "IDS"
                if str(notification.id) == str(notification_id):
                    notification_was_reached = True
                    notification.was_read = 1
                    notification.save()
                    
            else:
                notification.was_read = 1
                notification.save()
                
    
    response_data["result"] = "ok"
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
            
@csrf_exempt
def read_notification_object(notification_id):
    response_data = {}
    response_data['notification_list'] = []
    
    try:
        notification = Device_Notification.objects.get(id = notification_id)
        notification.was_read = 1
        notification.save()
        response_data["result"] = "ok"
    except (KeyError, Device_Notification.DoesNotExist):
        response_data["result"] = "error"
    
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")

@csrf_exempt
def retrieve_user_info(request):
    """ Test Request:
           $ curl -d json='{"facebook_id": 100000754383534}' http://localhost:8000/uploader/retrieve_user_info/
    """
    
    # Gets facebook_id from POST request
    json_request = json.loads(request.POST['json'])
    user_facebook_id = json_request['facebook_id']
    
    # Initializes response data vector
    response_data = {}
    
    try:
        user = User.objects.get(facebook_id=user_facebook_id)
    
    except (KeyError, User.DoesNotExist):
        response_data['result'] = "error: user not found"
        
    else:
        response_data['name'] = user.name
        response_data['facebook_id'] = user.facebook_id
        response_data['id_origin'] = user.id_origin
        response_data['following'] = user.following_count
        response_data['followers'] = user.followers_count
        
        user_fof_list = user.fof_set.all().order_by('-pub_date')
        user_fof_array = []
        
        for user_fof in user_fof_list:
            fof = {}
            
            frame_list = user_fof.frame_set.all().order_by('index')[:5]
            frames = []
            for frame in frame_list:
                frames.append({"frame_url":frame.url,"frame_index":frame.index})
            
            if user_fof.pub_date is None:
                pub_date = "null"
            else:
                raw_pub_date =  json.dumps(user_fof.pub_date, cls=DjangoJSONEncoder)
                pub_date = raw_pub_date[6:8] + "/" + raw_pub_date[9:11] + "/" + raw_pub_date[1:5]
                
            likes = user_fof.like_set.all()
            comments = user_fof.comment_set.all()
            
            try:
                Like.objects.get(fof_id = user_fof.id, user_id = user.id)
                fof['liked'] = "1"
            except (KeyError, Like.DoesNotExist):
                fof['liked'] = "0"
            
            fof['user_name'] = user_fof.user.name
            fof['user_facebook_id'] = user_fof.user.facebook_id
            fof['id'] = user_fof.id
            fof['is_private'] = user_fof.is_private
            fof['fof_name'] = user_fof.name
            fof['frames'] = frames
            fof['pub_date'] = pub_date
            fof['fof_description'] = user_fof.description
            
            fof['comments'] = len(comments)
            fof['likes'] = len(likes)
            
            user_fof_array.append(fof)
        
        response_data['user_fof_list'] = user_fof_array
        response_data['result'] = "Fetched data with no errors"
        
    return HttpResponse(json.dumps(response_data), mimetype="aplication/json")
    

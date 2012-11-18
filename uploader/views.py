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
from django.utils import timezone
from django.utils import simplejson as json
from django.http import HttpResponse

from uploader.models import User, FOF, Frame, Featured_FOF, Friends, Device

def index(request):
    return render_to_response('uploader/index.html', {},
                               context_instance=RequestContext(request))


@csrf_exempt
def image(request):
    
    #Gets fof info
    fof_size = request.POST['fof_size']
    user_device_id = request.POST['device_id']
    fof_name = request.POST['fof_name']
    
    #Let's checkout if this device is registered already:
    try:
        device = Device.objects.get(device_id=user_device_id)
        # Device exists, so does the user. Let's get the correct user:
        frame_user = get_object_or_404(User, id = device.user_id)
        
    except (KeyError, Device.DoesNotExist):
        # Device, and user, doesn't exist. Let's create them:
        frame_user = User(name='', device_id=user_device_id, pub_date=timezone.now())
        frame_user.save()
        user.device_set.create(device_id = user.device_id)
    
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
        #frame_name = <device_id>_<fof_name>_<frame_index>.jpeg
        frame_name = user_device_id
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
                               
                               
def fof(request, fof_name):
    fof = get_object_or_404(FOF, name=fof_name)
    
    frame_list = fof.frame_set.all().order_by('index')[:5]
    
    return render_to_response('uploader/fof.html', {'frame_list':frame_list},
                               context_instance=RequestContext(request))


def featured_fof(request, fof_name_value):
    
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

    return render_to_response('uploader/fof_featured.html', {'frame_list':frame_list, 'next_fof_name':next_fof_name, 'prev_fof_name':prev_fof_name, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))

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
                               
def user_fof(request, device_id_value, fof_name_value):
    #user = get_object_or_404(User, device_id=device_id_value)
    
    try: 
        device = Device.objects.get(device_id = device_id_value)
        user = get_object_or_404(User, id=device.user_id)
        
    except (KeyError, Device.DoesNotExist):
        return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))
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
    
        return render_to_response('uploader/fof.html', {'frame_list':frame_list, 'device_id_value':device_id_value, 'next_fof_name':next_fof_name, 'prev_fof_name':prev_fof_name, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))

def m_user_fof(request, device_id_value, fof_name_value):
    #user = get_object_or_404(User, device_id=device_id_value)

    try: 
        device = Device.objects.get(device_id = device_id_value)
        user = get_object_or_404(User, id=device.user_id)

    except (KeyError, Device.DoesNotExist):
        return render_to_response('uploader/fof_not_found.html', {}, context_instance=RequestContext(request))
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

        return render_to_response('uploader/m_fof.html', {'frame_list':frame_list, 'device_id_value':device_id_value, 'next_fof_name':next_fof_name, 'prev_fof_name':prev_fof_name, 'current_fof':fof_name_value, 'user_name':user_name}, context_instance=RequestContext(request))

@csrf_exempt
def user_fb_info(request):
    device_id_value = request.POST['device_id']
    user_name = request.POST['name']
    user_facebook_id = request.POST['facebook_id']
    user_email = request.POST['email']
    
    try:
        
        device = Device.objects.get(device_id = device_id_value)
        #Device already exists, but maybe this is not the first device from this user. Let's check it out:
        try:
            user = User.objects.get(facebook_id = user_facebook_id)
            
            # The user, with FB info, also exists. They should be the same. Are they?
            device_user = get_object_or_404(User, id=device.user_id)
            
            if user.id == device_user:
                # No problems here, the user from the device is the same from the facebook info.
                j = 0
            else:
                #FUCK! We have two different users, one with the correct FB info and another with the correct device.
                #The image method was called twice, with different device_ids, before the fb_info method.
                #We need to add this device to the correct user (with FB info) and destroy the other user (without FB info):
                #First, lets point this device to the correct user:
                device.user_id = user.id
                device.save()
                #Second, lets transfer his fofs and friends to the new user and invalidate the old user:
                
                fof_list = device_user.fof_set.all()
                for fof in fof_list:
                    fof.user_id = user.id
                    fof.save()
                
                
                for friend in Friends.objects.all():
                    if friend.friend_1_id == device_user.id:
                        friend.friend_1_id = user.id
                        friend.save()
                        
                    if friend.friend_2_id == device_user.id:
                        friend.friend_2_id = user.id
                        friend.save()
                
                device_user.facebook_id = 'null'
                device_user.device_id = 'null'
                device_user.save()
                
        except (KeyError, User.DoesNotExist):
            # The device exists but there's no user with his FB information. Let's add the FB info to the user that owns this device
            device_user = get_object_or_404(User, id=device.user_id)
            device_user.facebook_id = user_facebook_id
            device_user.name = user_name
            device_user.email = user_email
            device_user.save()
            
    except (KeyError, Device.DoesNotExist):
        # The device doesn't exist. That means we need to create everything from scratch:
        # Let's create the user:
        user = User(device_id = device_id_value, name = user_name, facebook_id = user_facebook_id, pub_date=timezone.now(), email = user_email) 
        user.save()
        #Let's create the device:
        user_device = user.device_set.create(device_id = user.device_id)
        
    return render_to_response('uploader/index.html', {}, context_instance=RequestContext(request))

@csrf_exempt
def user_fb_friends(request):
    
    # TEST:
    # $ curl -d json='{"user_device_id": "28c8ef21c63e7fa857b4e10a10953783cee15c04","friends": [{"facebook_id": "640592329"},{"facebook_id": "100000754383534"},{"facebook_id": "100000723578122"}]}' http://localhost:8000/uploader/user_fb_friends/
    
    # Parse the JSON
    friends_json = json.loads(request.POST['json'])
    
    user = get_object_or_404(User, device_id=friends_json['user_device_id'])
   
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
    response_data['friends_list'] = ''
    
    for friend in Friends.objects.all():
        if friend.friend_1_id == user.id:
            try:
                user_friend_object = User.objects.get(id = friend.friend_2_id)
                
                if response_data['friends_list'] == '':
                    response_data['friends_list'] = user_friend_object.facebook_id
                else:
                    response_data['friends_list'] = response_data['friends_list'] + ',' + user_friend_object.facebook_id
                
            except (KeyError, User.DoesNotExist):
                # Nothing to do here
                j = 0
    
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

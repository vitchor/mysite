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

from uploader.models import User, FOF, Frame

def index(request):
    return render_to_response('uploader/index.html', {},
                               context_instance=RequestContext(request))


@csrf_exempt
def image(request):
    
    image = Image.open(cStringIO.StringIO(request.FILES['apiupload'].read()))
    
    out_image = cStringIO.StringIO()
    image.save(out_image, 'jpeg')
    
    #Connect to S3, with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    conn = S3Connection('AKIAIFPFKLTD5HLWDI2A', 'zrCRXDSD3FKTJwJ3O5m/dsZstL/Ki0NyF6GZKHQi')
    
    #Gets information from post
    user_device_id = request.POST['device_id']
    frame_index = request.POST['frame_index']
    fof_name = request.POST['fof_name']
    fof_size = request.POST['fof_size']    
    
    try:
        frame_user = User.objects.get(device_id=user_device_id)
    except (KeyError, User.DoesNotExist):
        frame_user = User(name='', device_id=user_device_id)
        frame_user.save()
        
    try:
        frame_FOF = FOF.objects.get(name=fof_name)
    except (KeyError, FOF.DoesNotExist):
        frame_FOF = frame_user.fof_set.create(name = fof_name, size = fof_size)
    
    ###TODO###
    #focal point
    
    #Creates the image key with the following format:
    #frame_name = <device_id>_<fof_name>_<frame_index>.jpeg
    frame_name = user_device_id
    frame_name += '_'
    frame_name += fof_name
    frame_name += '_'
    frame_name += frame_index
    frame_name += '.jpeg'
        
    #Creates url:
    #frame_url = <s3_url>/<frame_name>
    frame_url = 'http://s3.amazonaws.com/dyfocus/'
    frame_url += frame_name
    
    frame = frame_FOF.frame_set.create(url = frame_url, index = frame_index)
    
    b = conn.get_bucket('dyfocus')
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

def user_fof(request, device_id_value, fof_name_value):
    user = get_object_or_404(User, device_id=device_id_value)
    
    fof_list = user.fof_set.all()
    
    i = 0
    
    if fof_name_value == "0":
        fof = user.fof_set.all()[0]
        frame_list = fof.frame_set.all().order_by('index')[:5]
        
    else:    
        for fof in fof_list:
            if fof.name == fof_name_value:
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
    
    return render_to_response('uploader/fof_navigator.html', {'frame_list':frame_list, 'device_id_value':device_id_value, 'next_fof_name':next_fof_name, 'prev_fof_name':prev_fof_name},
                               context_instance=RequestContext(request))
        
from django.conf.urls import patterns, include, url

urlpatterns = patterns('uploader.views',
    url(r'^$', 'index'),
    url(r'^image/$', 'image'),
    url(r'^user_fb_info/$', 'user_fb_info'),
    url(r'^(?P<fof_name>\S+)/fof/$', 'fof'),
    url(r'^(?P<fof_name_value>\S+)/featured_fof/$', 'featured_fof'),    
    url(r'^(?P<device_id_value>\S+)/user/(?P<fof_name_value>\S+)/fof_name/$', 'user_fof'),
    url(r'^(?P<fof_name_value>\S+)/featured_fof/m/$', 'm_featured_fof'),   
    url(r'^(?P<device_id_value>\S+)/user/(?P<fof_name_value>\S+)/fof_name/m/$', 'm_user_fof'),   
    url(r'^fof_not_found/$', 'fof_not_found')    
)
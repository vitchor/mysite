from django.conf.urls import patterns, include, url

urlpatterns = patterns('uploader.views',
    url(r'^$', 'index'),
    url(r'^image/$', 'image'),
    url(r'^(?P<fof_name>\S+)/fof/$', 'fof'),    
    url(r'^(?P<device_id_value>\S+)/user/(?P<fof_name_value>\S+)/fof_name/$', 'user_fof'),    
)
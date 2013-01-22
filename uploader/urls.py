from django.conf.urls import patterns, include, url

urlpatterns = patterns('uploader.views',
    url(r'^$', 'index'),
    url(r'^image/$', 'image'),
    url(r'^login/$', 'login'),
    url(r'^user_info/$', 'user_info'),
    url(r'^user_web_info/$', 'user_web_info'),
    url(r'^user_fb_info/$', 'user_fb_info'),
    url(r'^user_fb_friends/$', 'user_fb_friends'),
    url(r'^(?P<fof_name>\S+)/fof/$', 'fof'),
    url(r'^(?P<fof_name_value>\S+)/featured_fof/$', 'featured_fof'),
    url(r'^(?P<facebook_id_value>\S+)/user/(?P<fof_name_value>\S+)/fof_name/$', 'user_fof'),
    url(r'^(?P<fof_name_value>\S+)/featured_fof/m/$', 'm_featured_fof'),
    url(r'^(?P<facebook_id_value>\S+)/user/(?P<fof_name_value>\S+)/fof_name/m/$', 'm_user_fof'),
    url(r'^fof_not_found/$', 'fof_not_found'),
    url(r'^(?P<device_id_value>\S+)/(?P<fof_name_value>\S+)/j/?$', 'json_fof'),
    url(r'^(?P<fof_name_value>\S+)/j_featured/?$', 'json_fof_featured'),
    url(r'^(?P<fof_name_value>\S+)/embedded_fof/$', 'embedded_fof'),
    url(r'^(?P<fof_name_value>\S+)/embedded_fof/(?P<fof_height_value>\S+)/height/$', 'embedded_fof_height'),
    url(r'^(?P<fof_name_value>\S+)/share_fof/$', 'share_fof'),
    url(r'^(?P<fof_name_value>\S+)/share_fof/m/$', 'm_share_fof'),
    url(r'^(?P<facebook_id_value>\S+)/feed/(?P<index>\S+)/$', 'feed'),
    url(r'^(?P<facebook_id_value>\S+)/m_feed/(?P<index>\S+)/$', 'm_feed'),
    url(r'^featured/$', 'list_featured'),    
)

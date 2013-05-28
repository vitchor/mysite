from django.conf.urls import patterns, include, url

urlpatterns = patterns('uploader.views',
    url(r'^$', 'index'),
    url(r'^image/$', 'image'),
    url(r'^upload_image/$', 'upload_image'),
    url(r'^login/$', 'login'),
    url(r'^signup/$', 'signup'),
    url(r'^retrieve_user_info/$', 'retrieve_user_info'), 
    url(r'^like/$', 'like'),
    url(r'^follow/$', 'follow'),
    url(r'^user_follow/$', 'user_follow'),
    url(r'^unfollow/$', 'unfollow'),
    url(r'^user_unfollow/$', 'user_unfollow'),
    url(r'^how_many_follow/$', 'how_many_follow'),
    url(r'^privacy_policy/$', 'privacy_policy'),
    url(r'^alert/$', 'sendAlertExample'),
    url(r'^notifications/$', 'get_notifications'),
    url(r'^read_notification/$', 'read_notification'),
    url(r'^user_read_notification/$', 'user_read_notification'),
    url(r'^json_feed/$', 'json_feed'),
    url(r'^user_json_feed/$', 'user_json_feed'),    
    url(r'^powerfeed/(?P<index>\S+)/$', 'power_user_feed'),
    url(r'^json_featured_fof/$', 'json_featured_fof'),
    url(r'^json_user_fof/$', 'json_user_fof'),
    url(r'^json_user_id_fof/$', 'json_user_id_fof'),
    url(r'^comment/$', 'comment'),
    url(r'^likes_and_comments/$', 'likes_and_comments'),
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
    #url(r'^saywhat/$', 'test'),
)

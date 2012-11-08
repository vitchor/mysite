from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/', include('polls.urls')),
    url(r'^uploader/', include('uploader.urls')),    
    url(r'^admin/', include(admin.site.urls)),
    url(r"^$", direct_to_template, {"template": "index.html"}),
)

#urlpatterns += patterns('', (
#        r'^static/(?P<path>.*)$',
#        'django.views.static.serve',
#        {'document_root': 'static'}
#))

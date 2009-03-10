from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#handler404 = 'apps.core.views.page_not_found'
urlpatterns = patterns('apps.wantown.views',
    # Example:
    # (r'^mindgames/', include('mindgames.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    
    # Core App
    #(r'^$', 'index'),
    (r'^accounts/login/$', 'login'),
    (r'^wantown/post/step/(?P<step>.*)/', 'post'),
    (r'^wantown/view/id/(?P<id>.*)/', 'view'),
    (r'^wantown/login/$', 'login'),
    (r'^wantown/login/(?P<by>.*)/', 'login_by'),
    (r'^wantown/logout/', 'logout'),
    (r'^wantown/register/$', 'register'),
    (r'^wantown/register/submit/$', 'register_submit'),
    (r'^wantown/clone/object/(?P<id>.*)/', 'clone'),
    (r'^wantown/search/who/(?P<which>.*)/(?P<what>.*)/', 'search'),
    (r'^wantown/upload/', 'upload'),
)

urlpatterns += patterns('',
    (r'^resource/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_MEDIA_PREFIX}),
                        
) 

urlpatterns += patterns('views',
                       (r'^$','index'),
                       (r'^x/query/$','query'),
                       (r'^x/(?P<category_id>\d*)/(?P<keyword>.*)/redirect/(?P<url>.*)','redirect'),
                       )

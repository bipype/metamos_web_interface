from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'metAMOS_web_interface.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'http://adz.ibb.waw.pl:2555/biogaz/admin/', include(admin.site.urls)),
    url(r'^$', 'metAMOS_web.views.index'),
    url(r'^index/$', 'metAMOS_web.views.index'),
    url(r'^new/$', 'metAMOS_web.views.new'),
    url(r'^result_post/$', 'metAMOS_web.views.result_redirect'),
    url(r'^result/(?P<sample_id>.*)/(?P<bipype_variant>.*)$', 'metAMOS_web.views.result'),
    url(r'^biogaz/index/$', 'metAMOS_web.views.index'),
    url(r'^biogaz/new/$', 'metAMOS_web.views.new'),
    url(r'^biogaz/result_post/$', 'metAMOS_web.views.result_redirect'),
    url(r'^biogaz/result/(?P<sample_id>.*)/(?P<bipype_variant>.*)$', 'metAMOS_web.views.result'),
    url(r'^new_outanal/$', 'metAMOS_web.views.show_krona_list'),
    url(r'^result_outanal/(?P<krona_name>.*)$', 'metAMOS_web.views.show_single_krona'),
    url(r'^biogaz/new_outanal/$', 'metAMOS_web.views.show_krona_list'),
    url(r'^biogaz/result_outanal/(?P<krona_name>.*)$', 'metAMOS_web.views.show_single_krona'),

    url(r'^test/$', 'metAMOS_web.views.test'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

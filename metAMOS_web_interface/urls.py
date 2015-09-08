from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'metAMOS_web.views.index'),
    url(r'^index/$', 'metAMOS_web.views.index'),
    url(r'^new/$', 'metAMOS_web.views.new'),
    url(r'^result_post/$', 'metAMOS_web.views.result_redirect'),
    url(r'^result/(?P<sample_id>.*)/(?P<bipype_variant>.*)$', 'metAMOS_web.views.result'),
    url(r'^get_status/(?P<sample_id>.*)/(?P<bipype_variant>.*)$', 'metAMOS_web.views.get_status'),
    url(r'^new_outanal/$', 'metAMOS_web.views.show_krona_list'),
    url(r'^result_outanal/(?P<krona_name>.*)$', 'metAMOS_web.views.show_single_krona'),
    url(r'^remove/$', 'metAMOS_web.views.remove'),
    url(r'^test/$', 'metAMOS_web.views.test'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

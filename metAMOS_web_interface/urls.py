from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'metAMOS_web.views.index'),
    url(r'^index/$', 'metAMOS_web.views.index'),
    url(r'^new/$', 'metAMOS_web.views.new'),
    url(r'^new_meta/$', 'metAMOS_web.views.new_meta'),
    url(r'^result/(?P<path>.*)/(?P<type_of_analysis>.*)$', 'metAMOS_web.views.result'),
    url(r'^get_status/(?P<path>.*)/(?P<type_of_analysis>.*)$', 'metAMOS_web.views.get_status'),
    url(r'^remove/$', 'metAMOS_web.views.remove'),
    url(r'^result_html/(?P<path>.*)/(?P<type_of_analysis>.*)/(?P<file_path>.*)$', 'metAMOS_web.views.result_html'),
    url(r'^result_download/(?P<path>.*?)/(?P<type_of_analysis>.*?)/(?P<file_path>.*)$', 'metAMOS_web.views.result_download'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

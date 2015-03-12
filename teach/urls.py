from django.conf.urls import patterns, include, url
from django.contrib import admin

from .admin import site as teach_admin
teach_admin.copy_registry(admin.site)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'teach.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'example.views.login'),
    url(r'', include('django_browserid.urls')),
    url(r'^admin/', include(teach_admin.urls)),
)

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from . import views
from credly.views import CredlyAuthinticate, CredlyEvent, CredlyList, CredlyProfile, \
    CredlyMemberPadge, CredlyEvidance, CredlyBadge, CredlyMember


urlpatterns = [

    url(r'^members(?:/(?P<id>\w{0,50}))?(?:/(?P<resource1>\w{0,50}))?(?:/(?P<resource2>\w{0,50}))?',
        csrf_exempt(CredlyMember.as_view())),
    url(r'^badges(?:/(?P<id>\w{0,50}))?(?:/(?P<resource1>\w{0,50}))?(?:/(?P<resource2>\w{0,50}))?',
        csrf_exempt(CredlyBadge.as_view())),
    url(r'^me(?:/(?P<id>\w{0,50}))?(?:/(?P<resource1>\w{0,50}))?(?:/(?P<resource2>\w{0,50}))?',
        csrf_exempt(CredlyProfile.as_view())),
    url(r'^member_badges(?:/(?P<id>\w{0,50}))?(?:/(?P<resource1>\w{0,50}))?(?:/(?P<resource2>\w{0,50}))?',
        csrf_exempt(CredlyMemberPadge.as_view())),
    url(r'^evidence(?:/(?P<id>\w{0,50}))?(?:/(?P<resource1>\w{0,50}))?(?:/(?P<resource2>\w{0,50}))?',
        csrf_exempt(CredlyEvidance.as_view())),
    url(r'^lists(?:/(?P<id>\w{0,50}))?(?:/(?P<resource1>\w{0,50}))?(?:/(?P<resource2>\w{0,50}))?',
        csrf_exempt(CredlyList.as_view())),
    url(r'^events(?:/(?P<id>\w{0,50}))?(?:/(?P<resource1>\w{0,50}))?(?:/(?P<resource2>\w{0,50}))?',
        csrf_exempt(CredlyEvent.as_view())),
    url(r'^authenticate(?:/(?P<id>\w{0,50}))?(?:/(?P<resource1>\w{0,50}))?(?:/(?P<resource2>\w{0,50}))?',
        csrf_exempt(CredlyAuthinticate.as_view())),

]
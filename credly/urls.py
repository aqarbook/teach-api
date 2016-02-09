from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from . import views
from credly.views import CredlyAuthenticate, CredlyEvent, CredlyList, CredlyProfile, \
    CredlyMemberPadge, CredlyEvidance, CredlyBadge, CredlyMember


urlpatterns = [

    url(r'^members(?:/(?P<arg1>\w{0,50}))?(?:/(?P<arg2>\w{0,50}))?(?:/(?P<arg3>\w{0,50}))?',
        csrf_exempt(CredlyMember.as_view())),
    url(r'^badges(?:/(?P<arg1>\w{0,50}))?(?:/(?P<arg2>\w{0,50}))?(?:/(?P<arg3>\w{0,50}))?',
        csrf_exempt(CredlyBadge.as_view())),
    url(r'^me(?:/(?P<arg1>\w{0,50}))?(?:/(?P<arg2>\w{0,50}))?(?:/(?P<arg3>\w{0,50}))?',
        csrf_exempt(CredlyProfile.as_view())),
    url(r'^member_badges(?:/(?P<arg1>\w{0,50}))?(?:/(?P<arg2>\w{0,50}))?(?:/(?P<arg3>\w{0,50}))?',
        csrf_exempt(CredlyMemberPadge.as_view())),
    url(r'^evidence(?:/(?P<arg1>\w{0,50}))?(?:/(?P<arg2>\w{0,50}))?(?:/(?P<arg3>\w{0,50}))?',
        csrf_exempt(CredlyEvidance.as_view())),
    url(r'^lists(?:/(?P<arg1>\w{0,50}))?(?:/(?P<arg2>\w{0,50}))?(?:/(?P<arg3>\w{0,50}))?',
        csrf_exempt(CredlyList.as_view())),
    url(r'^events(?:/(?P<arg1>\w{0,50}))?(?:/(?P<arg2>\w{0,50}))?(?:/(?P<arg3>\w{0,50}))?',
        csrf_exempt(CredlyEvent.as_view())),
    url(r'^authenticate(?:/(?P<arg1>\w{0,50}))?(?:/(?P<arg2>\w{0,50}))?(?:/(?P<arg3>\w{0,50}))?',
        csrf_exempt(CredlyAuthenticate.as_view())),

]
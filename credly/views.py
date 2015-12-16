from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.

import base64
from django.views.decorators.csrf import csrf_exempt
from requests.auth import AuthBase
import slumber
from django.http import JsonResponse
from django.views.generic import View
from slumber.exceptions import HttpNotFoundError


class ApiAuth(AuthBase):
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def __call__(self, r):
        base64string = base64.encodestring('%s:%s' % ("issa.mh.khalil@gmail.com", "5668c9ded6745"))[:-1]
        auth_header = "Basic %s" % base64string

        r.headers['X-Api-Key'] = self.username
        r.headers['X-Api-Secret'] = self.api_key
        r.headers['Authorization'] = auth_header

        return r


class CredlyView(View):
    credly = None
    route_base = None

    def __init__(self):
        key = "64166cde88e2816feaef7f7ff74a5687"
        secret = "iZGR1FZ6KAKxhj3QWUu1iNmXhjs0wZbEbnYTKng5Np0r9t/mtyofqfIAjTKfVmV2cdTw1o7nH6rp4u1CGq8hPEiWhZecEOTGyAX7XAaPPnTh+1MVGADHYJgeqdR0snyOAJbkODA2LOhW9n+2eLMnlmGDA3fUbCdk6oZbPnYJqP4="
        self.credly = slumber.API("https://api.credly.com/v1.1/", auth=ApiAuth(key, secret),
                                  append_slash=False)

    def get(self, request, id, resource1, resource2):

        query_parameters = request.GET.copy()
        if "credly_token" in request.session:
            query_parameters["access_token"] = request.session["credly_token"]

        try:
            fun = getattr(self.credly, self.route_base)(id)
            if resource1:
                fun = getattr(fun, resource1)

            if resource2:
                if type(resource2) == int:
                    fun = fun(resource2)
                else:
                    fun = getattr(fun, resource2)

            result = fun.get(**query_parameters)

        except HttpNotFoundError as error:
            raise error
            result = {"err": "API not found"}

        return JsonResponse(result)

    def post(self, request, id, resource1, resource2):

        form_parameters = request.POST.copy()
        if "credly_token" in request.session:
            form_parameters["access_token"] = request.session["credly_token"]

        try:
            fun = getattr(self.credly, self.route_base)(id)
            if resource1:
                fun = getattr(fun, resource1)

            if resource2:
                if type(resource2) == int:
                    fun = fun(resource2)
                else:
                    fun = getattr(fun, resource2)

            result = fun.post(**form_parameters)
            if "token" in result["meta"]:
                request.session["credly_token"] = result["data"]["token"]


        except HttpNotFoundError as error:
            result = {"err": "API not found"}

        return JsonResponse(result)


class CredlyMember(CredlyView):
    route_base = "members"


class CredlyBadge(CredlyView):
    route_base = "badges"


class CredlyMember(CredlyView):
    route_base = "members"


class CredlyProfile(CredlyView):
    route_base = "me"


class CredlyMemberPadge(CredlyView):
    route_base = "member_badges"


class CredlyEvidance(CredlyView):
    route_base = "evidence"


class CredlyList(CredlyView):
    route_base = "lists"


class CredlyEvent(CredlyView):
    route_base = "events"


class CredlyAuthinticate(CredlyView):
    route_base = "authenticate"
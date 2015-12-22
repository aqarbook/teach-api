from credly.models import UserCredlyProfile
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


# read credly API key and app secret key from env
from teach.settings import CREDLY_API_KEY, CREDLY_APP_SECRET


class ApiAuth(AuthBase):
    def __init__(self, api_key, api_secret, email=None, password=None):
        self.api_key = api_key
        self.api_secret = api_secret

        self.email = email
        self.password = password

    def __call__(self, r):
        r.headers['X-Api-Key'] = self.api_key
        r.headers['X-Api-Secret'] = self.api_secret

        print [self.email and self.password]

        if self.email and self.password:
            base64string = base64.encodestring('%s:%s' % (self.email, self.password))[:-1]
            auth_header = "Basic %s" % base64string
            r.headers['Authorization'] = auth_header

        print r.headers
        return r


class CredlyView(View):
    credly = None
    route_base = None
    is_public_api = True
    api_endpoint = "https://api.credly.com/v1.1/"
    api_auth = None
    api_sub_paths = []
    http_method_names = ["get", "post", "delete"]

    def __init__(self):
        self.credly = slumber.API(self.api_endpoint, auth=ApiAuth(CREDLY_API_KEY, CREDLY_APP_SECRET),
                                  append_slash=False)

    def attach_access_token(self, request):
        if "credly_token" in request.session:
            if request.method.lower() == "get":
                request.GET["credly_token"] = request.session["credly_token"]
            else:
                request.POST["credly_token"] = request.session["credly_token"]

    def build_api_request(self, **args):
        fun = getattr(self.credly, self.route_base)
        for key in args.keys():
            if args[key]:
                if args[key] in self.api_sub_paths:
                    fun = getattr(fun, args[key])
                else:
                    fun = fun(args[key])
        return fun

    def get(self, request, **args):
        self.attach_access_token(request)
        try:
            result = self.build_api_request(**args).get(**request.GET)
        except HttpNotFoundError as error:
            raise error
            result = {"err": "API not found"}

        return JsonResponse(result)

    def post(self, request, args):
        self.attach_access_token(request)
        try:
            result = self.build_api_request(**args).post(**request.POST)
            if "token" in result["meta"]:
                request.session["credly_token"] = result["data"]["token"]

        except HttpNotFoundError as error:
            result = {"err": "API not found"}

        return JsonResponse(result)


class CredlyMember(CredlyView):
    http_method_names = ["get"]
    route_base = "members"
    api_sub_paths = ["avatar", "badges", "badges", "given", "created", "categories", "followers", "following",
                     "trusted"]


class CredlyBadge(CredlyView):
    route_base = "badges"


class CredlyProfile(CredlyView):
    http_method_names = ["get", "post", "delete"]
    route_base = "me"
    api_sub_paths = ["avatar", "emails", "managed", "managers", "search_managers"]


class CredlyMemberPadge(CredlyView):
    route_base = "member_badges"


class CredlyEvidance(CredlyView):
    route_base = "evidence"


class CredlyList(CredlyView):
    route_base = "lists"


class CredlyEvent(CredlyView):
    route_base = "events"


class CredlyAuthenticate(CredlyView):
    http_method_names = ["get", "post"]
    route_base = "authenticate"
    api_sub_paths = ["register", "verify_email", "password", "refresh"]

    def post(self, request, **args):

        if not args["arg1"]:
            CREDLY_USER_EMAIL = request.POST['email']
            CREDLY_USER_PASSWORD = request.POST['password']
            self.credly = slumber.API(self.api_endpoint,
                                      auth=ApiAuth(CREDLY_API_KEY, CREDLY_APP_SECRET, email=CREDLY_USER_EMAIL,
                                                   password=CREDLY_USER_PASSWORD), append_slash=False)

        try:
            result = self.build_api_request(**args).post(**request.POST)
            if "token" in result["meta"]:
                request.session["credly_token"] = result["data"]["token"]
                user_credly_profile, created = UserCredlyProfile.get_or_create(user_id=request.user.id)
                user_credly_profile.access_token = result["data"]["token"]
                user_credly_profile.refresh_token = result["data"]["refresh_token"]
                user_credly_profile.save()

        except HttpNotFoundError as error:
            result = {"err": "API not found"}

        return JsonResponse(result)


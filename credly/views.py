from credly.models import UserCredlyProfile, save_user_token, get_credly_access_token
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.

import base64
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from requests.auth import AuthBase
import slumber
from django.http import JsonResponse
from django.views.generic import View
from slumber.exceptions import HttpNotFoundError


# read credly API key and app secret key from env
from teach.settings import CREDLY_API_KEY, CREDLY_APP_SECRET, CREDLY_API_URL, MozillaAccountId


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

    api_endpoint = CREDLY_API_URL
    api_auth = None
    api_sub_paths = []
    http_method_names = ["get", "post", "delete"]
    require_access_token = False

    def __init__(self):
        self.credly = slumber.API(self.api_endpoint, auth=ApiAuth(CREDLY_API_KEY, CREDLY_APP_SECRET),
                                  append_slash=False)

    #un comment this line to limit functionality to logged in users
    #@method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CredlyView, self).dispatch(*args, **kwargs)

    def attach_access_token(self, request):

        # if request.method.lower() == "get":
        #     request.GET = request.GET.copy()
        #     request.GET["access_token"] = "0db5ca0eda70b80ec637e91ea6f509a1f12d5360080a08dbb8d1da56cc971e35da314190cc58406310911357f0131a71ed578f25ebadb058c4b028c2cdd95cb8"
        # else:
        #     request.POST = request.POST.copy()
        #     request.POST["access_token"] = "0db5ca0eda70b80ec637e91ea6f509a1f12d5360080a08dbb8d1da56cc971e35da314190cc58406310911357f0131a71ed578f25ebadb058c4b028c2cdd95cb8"
        #

        if self.require_access_token:
            if "credly_token" in request.session:
                if request.method.lower() == "get":
                    request.GET = request.GET.copy()
                    request.GET["access_token"] = request.session["credly_token"]
                else:
                    request.POST = request.POST.copy()
                    request.POST["access_token"] = request.session["credly_token"]

    def build_api_request(self,route_base= None, **args ):

        if not route_base:
            route_base = self.route_base
        fun = getattr(self.credly, route_base)
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
            print args
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



class MozillaCredly(CredlyView):
    http_method_names = ["get"]
    route_base = "badges"
    api_sub_paths = ["avatar", "badges", "badges", "given", "created", "categories", "followers", "following",
                     "trusted"]

    def get(self, request, **args):

        #set add mozilla id to get query
        get_data = request.GET.copy()
        get_data["member_id"] = MozillaAccountId #19331
        request.GET = get_data
        self.attach_access_token(request)
        try:

            #get mozilla badges
            result = self.build_api_request(**args).get(**request.GET)

            print result

            if request.user.is_authenticated():

                pending_badges_ids = []
                accepted_badges_ids = []

                #change limit to get all user pending and accepted badges
                request.GET['page'] = 1
                request.GET['per_page'] = 1000

                #get accepted and pending badges for logged in user
                accepted_badges = self.build_api_request(route_base="me",arg1='badges', arg2=None, arg3=None).get(**request.GET)
                pending_badges = self.build_api_request(route_base="me",arg1='badges', arg2='pending', arg3=None).get(**request.GET)

                #extract ids
                if accepted_badges['data']:
                    accepted_badges_ids = [ credit['id'] for credit in accepted_badges['data'] ]
                if pending_badges['data']:
                    pending_badges_ids = [ credit['id'] for credit in pending_badges['data'] ]

                #match extracted ids with mozilla badges
                index = 0
                for mozilla_credit in result['data']:
                    if mozilla_credit['id'] in pending_badges_ids:
                        result['data'][index]['achieved'] = "pending"
                    elif mozilla_credit['id'] in accepted_badges_ids:
                        result['data'][index]['achieved'] = "accepted"
                    else:
                        result['data'][index]['achieved'] = False
                    index += 1

        except HttpNotFoundError as error:
            raise error
            result = {"err": "API not found"}

        return JsonResponse(result)



class CredlyMember(CredlyView):
    http_method_names = ["get"]
    route_base = "members"
    api_sub_paths = ["avatar", "badges", "badges", "given", "created", "categories", "followers", "following",
                     "trusted"]


    def get_user_by_email(self, email):
        try:
            member = self.credly.members().get(email=email)
            print member
        except Exception as error:
            member = None
        return member



class CredlyBadge(CredlyView):
    route_base = "badges"

    def get(self, request, **args):
        self.attach_access_token(request)

        try:
            result = self.build_api_request(**args).get(**request.GET)
        except HttpNotFoundError as error:
            raise error
            result = {"err": "API not found"}

        return JsonResponse(result)

class CredlyProfile(CredlyView):
    require_access_token = True
    http_method_names = ["get", "post", "delete"]
    route_base = "me"

    api_sub_paths = ["avatar", "emails", "managed", "managers", "search_managers","badges","created"]


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
            if request.user.is_authenticated():
                save_user_token(request.user.id,result["data"])

        except HttpNotFoundError as error:
            result = {"err": "API not found"}

        return JsonResponse(result)



    def create_credly_user(self, user ):

        #first check if user already exist
        members_api = CredlyMember()
        member = members_api.get_user_by_email(user.email)

        if member:
            return False

        #if user not exist build request and created new one
        try:
            result = self.credly.authenticate().register().post(email=user.email, password=user.password)
            #save it to credly table
            save_user_token(user.id,result["data"])
        except HttpNotFoundError as error:
            print error
            pass
        return True
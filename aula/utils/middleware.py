import datetime
from django.contrib.auth import logout

from aula.utils.tools import calculate_my_time_off


class MultipleProxyMiddleware:
    FORWARDED_FOR_FIELDS = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_FORWARDED_HOST',
        'HTTP_X_FORWARDED_SERVER',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        """
        Rewrites the proxy headers so that only the most
        recent proxy is used.
        """
        for field in self.FORWARDED_FOR_FIELDS:
            if field in request.META:
                if ',' in request.META[field]:
                    parts = request.META[field].split(',')
                    request.META[field] = parts[-1].strip()


class NoCacheMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_response(self, request, response):
        if response and type( response ) != type:
            #if hasattr(request, 'session'): request.session.set_expiry(1500) 
            response['Pragma'] = 'no-cache'
            response['Cache-Control'] = 'no-cache must-revalidate proxy-revalidate no-store'
        return response
    

class timeOutMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        if request.user.is_authenticated:
            if 'lastRequest' in request.session:            
                elapsedTime = datetime.datetime.now() - datetime.datetime.strptime(request.session['lastRequest'], '%c')
                maxim_timeout = calculate_my_time_off(request.user)
                if elapsedTime.seconds > maxim_timeout:
                    del request.session['lastRequest'] 
                    logout(request)

            request.session['lastRequest'] = datetime.datetime.now().strftime( '%c' )
        else:
            if 'lastRequest' in request.session:
                del request.session['lastRequest'] 

        return None

class IncludeLoginInErrors:  

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    #http://stackoverflow.com/questions/9294043/include-django-logged-user-in-django-traceback-error
    def process_exception(self, request, exception):
        """
        Process the request to add some variables to it.
        """

        # Add other details about the user to the META CGI variables.
        try:
            if request.user.is_anonymous:
                request.META['AUTH_NAME'] = "Anonymous User"
                request.META['AUTH_USER'] = "Anonymous User"
                request.META['AUTH_USER_EMAIL'] = ""
                request.META['AUTH_USER_ID'] = 0
                request.META['AUTH_USER_IS_ACTIVE'] = False
                request.META['AUTH_USER_IS_SUPERUSER'] = False
                request.META['AUTH_USER_IS_STAFF'] = False
                request.META['AUTH_USER_LAST_LOGIN'] = ""
            else:
                request.META['AUTH_NAME'] = str(request.user.first_name) + " " + str(request.user.last_name)
                request.META['AUTH_USER'] = str(request.user.username)
                request.META['AUTH_USER_EMAIL'] = str(request.user.email)
                request.META['AUTH_USER_ID'] = str(request.user.id)
                request.META['AUTH_USER_IS_ACTIVE'] = str(request.user.is_active)
                request.META['AUTH_USER_IS_SUPERUSER'] = str(request.user.is_superuser)
                request.META['AUTH_USER_IS_STAFF'] = str(request.user.is_staff)
                request.META['AUTH_USER_LAST_LOGIN'] = str(request.user.last_login)
        except:
            pass
    
    
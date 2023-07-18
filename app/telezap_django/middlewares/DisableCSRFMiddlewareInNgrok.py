from django.conf import settings
from django.middleware.csrf import get_token

class DisableCSRFMiddlewareInNgrok:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG and 'ngrok-free.app' in request.META.get('HTTP_HOST', ''):
            csrf_trusted_origins = settings.CSRF_TRUSTED_ORIGINS
            if 'ngrok-free.app' not in csrf_trusted_origins:
                csrf_trusted_origins.append('ngrok-free.app')
                settings.CSRF_TRUSTED_ORIGINS = csrf_trusted_origins

            setattr(request, '_dont_enforce_csrf_checks', True)
        else:
            # Garante que o token CSRF ainda seja definido para outras solicitações
            get_token(request)  

        response = self.get_response(request)
        return response

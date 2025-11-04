import os
from django.urls import reverse
from django.conf import settings
from django.shortcuts import redirect


class AuthenticationRequiredMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info.rstrip('/')  
    
        if path.startswith(settings.STATIC_URL.rstrip('/')) or path.startswith(settings.MEDIA_URL.rstrip('/')):
            return self.get_response(request)
    
        if not path.startswith(settings.LOGIN_URL) and not self._is_public_route(path):
            if not request.user.is_authenticated:
                return redirect(f'{settings.LOGIN_URL}?next={request.path_info}')

        return self.get_response(request)

    def _is_public_route(self, path):
        public_routes = {
            reverse('sign_in').rstrip('/'),
            reverse('sign_out').rstrip('/')
        }

        if settings.ENVIRONMENT in ['development', 'homolog', 'local']:
            public_routes.update({
                reverse('run_migrations').rstrip('/'),
                reverse('run_collectstatic').rstrip('/'),
                reverse('create_superuser').rstrip('/')
            })

        return path in public_routes

from apps.utils.get_current_user import set_current_user
from django.utils.deprecation import MiddlewareMixin


class GetCurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        set_current_user(getattr(request, 'user', None))

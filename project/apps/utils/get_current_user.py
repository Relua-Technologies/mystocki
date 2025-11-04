import threading
from django.contrib.auth.models import AnonymousUser

_thread_locals = threading.local()

def set_current_user(user):
    _thread_locals.user=user

def get_current_user():
    return getattr(_thread_locals, 'user', None)

def get_current_user_or_null():
    user = get_current_user()
    if isinstance(user, AnonymousUser):
        return None
    else:
        return user
    
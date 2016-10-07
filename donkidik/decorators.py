from django.http import JsonResponse
from shotgun import settings
import hashlib
from datetime import datetime


def api_login_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user and request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({'status': 'FAIL', 'error': 'permission_denied'})
    return _wrapped_view_func

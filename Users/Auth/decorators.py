import jwt
import os
import datetime
from django.http import JsonResponse
from Users.models import Users

def jwt_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('Authorization')
        if not token:
            return JsonResponse({'detail': 'Unauthorized'}, status=401)

        try:
            payload = jwt.decode(token, os.getenv('SECRET'), algorithms=['HS256'])
            if datetime.datetime.now().timestamp() > payload['exp']:
                return JsonResponse({'detail': 'Token expired'}, status=401)

            request.user_id = payload.get('user_id')

        except (jwt.ExpiredSignatureError, jwt.DecodeError, Users.DoesNotExist):
            return JsonResponse({'detail': 'Unauthorized'}, status=401)

        return view_func(request, *args, **kwargs)
    return wrapped_view
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser

from Users.models import Users
from Users.serializers import UsersSerializer


@csrf_exempt
def users_api(request, user_id=0):
    if request.method == 'GET':
        users = Users.objects.all()
        users_serializer = UsersSerializer(users, many=True)
        return JsonResponse(users_serializer.data, safe=False)
    elif request.method == 'POST':
        users_data = JSONParser().parse(request)
        users_serializer = UsersSerializer(data=users_data)
        if users_serializer.is_valid():
            users_serializer.save()
            return JsonResponse("Added Successfully!!", safe=False)
        return JsonResponse("Failed to Add.", safe=False)
    elif request.method == 'PUT':
        users_data = JSONParser().parse(request)
        users = Users.objects.get(user_id=users_data['user_id'])
        users_serializer = UsersSerializer(users, data=users_data)
        if users_serializer.is_valid():
            users_serializer.save()
            return JsonResponse("Updated Successfully!!", safe=False)
        return JsonResponse("Failed to Update.", safe=False)
    elif request.method == 'DELETE':
        users = Users.objects.get(user_id=user_id)
        users.delete()
        return JsonResponse("Deleted Successfully!!", safe=False)

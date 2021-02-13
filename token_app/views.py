import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid

# Create your views here.
from rest_framework.parsers import JSONParser

from token_app.models import Tokens
from token_app.serializer import TokenSerializer


@csrf_exempt
def generate_token(request):
    data = {}
    if request.method == 'GET':
        data['token'] = str(uuid.uuid4())
        data['user'] = None
        data['time'] = datetime.datetime.now(datetime.timezone.utc)
    serializer = TokenSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        response = {'message': "successfully created token"}
        return JsonResponse(response, status=200)
    return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def assign_token(request, user_id):
    if request.method == 'GET':
        tokens = Tokens.objects.filter(user=None)
        if len(tokens) == 0:
            return JsonResponse({"error": "no token available"}, status=404)

        try:
            if Tokens.objects.get(user=user_id) is not None:
                return JsonResponse({"error": "Token already assigned"}, status=400)
        except Tokens.DoesNotExist:
            for obj in tokens:
                if not check_token(obj.token):
                    continue
                obj.user = user_id
                obj.time = datetime.datetime.now(datetime.timezone.utc)
                obj.save()
                break
            response = {'message': "successfully assigned token"}
            return JsonResponse(response, status=200)
    return JsonResponse({"error": "some error occured"}, status=400)


@csrf_exempt
def delete_token(request, token):
    if request.method == 'DELETE':
        try:
            token = Tokens.objects.get(token=token)
            token.delete()
            return JsonResponse({"message": "token deleted"}, status=200)
        except Tokens.DoesNotExist:
            response = {'message': "no token found"}
            return JsonResponse(response, status=400)


@csrf_exempt
def unblock_token(request, token):
    if request.method == 'PUT':
        try:
            token = Tokens.objects.get(token=token)
            if check_token(token):
                token.user = None
                token.time = datetime.datetime.now(datetime.timezone.utc)
                token.save()
                return JsonResponse({"message": "Token freed"}, status=200)
            else:
                return JsonResponse({"message": "No token exists"}, status=400)
        except Tokens.DoesNotExist:
            return JsonResponse({"error": "no token exists"}, status=400)


@csrf_exempt
def refresh_token(request, token):
    if request.method == 'PUT':
        try:
            token = Tokens.objects.get(token=token)
            if token.user is None:
                time_now = datetime.datetime.now(datetime.timezone.utc)
                token_time = token.time
                dt = time_now - token_time
                if dt.seconds < 300:
                    token.time = datetime.datetime.now(datetime.timezone.utc)
                    token.save()
                    return JsonResponse({"message": "Refreshed token"}, status=200)
                else:
                    token.delete()
                    return JsonResponse({"message": "No token exists"}, status=200)
            else:
                return JsonResponse({"message": "Token is associated with a user"}, status=400)
        except Tokens.DoesNotExist:
            return JsonResponse({"error": "no token exists"}, status=400)


@csrf_exempt
def refresh_user_token(request, user_id, token):
    if request.method == 'PUT':
        try:
            token = Tokens.objects.get(token=token, user=user_id)
            time_now = datetime.datetime.now(datetime.timezone.utc)
            token_time = token.time
            dt = time_now - token_time
            if dt.seconds < 60:
                token.time = datetime.datetime.now(datetime.timezone.utc)
                token.save()
                return JsonResponse({"message": "Refreshed token"}, status=200)
            else:
                token.user = None
                token.time = datetime.datetime.now(datetime.timezone.utc)
                token.save()
                return JsonResponse({"message": "No token associated with this user"}, status=400)
        except Tokens.DoesNotExist:
            return JsonResponse({"error": "no token exists"}, status=400)


def check_token(token):
    token = Tokens.objects.get(token=token)
    if token.user is None:
        time_now = datetime.datetime.now(datetime.timezone.utc)
        token_time = token.time
        dt = time_now - token_time
        if dt.seconds < 300:
            return True
        else:
            token.delete()
            return False
    else:
        time_now = datetime.datetime.now(datetime.timezone.utc)
        token_time = token.time
        dt = time_now - token_time
        if dt.seconds < 60:
            return True
        else:
            token.user = None
            token.time = datetime.datetime.now(datetime.timezone.utc)
            token.save()
            return True

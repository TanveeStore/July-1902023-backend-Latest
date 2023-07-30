from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, logout
import jwt
import requests
import json
import time
from django.db.models import Max
import re
from rest_framework_simplejwt.tokens import RefreshToken
from common.models import User
from common.serializer import user_serializers
from CartSystem import models
from common import utils
from products.models import Product



# Google Login ApiView
class GoogleLogin(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = user_serializers.GoogleLoginSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        id_token = request.data['idToken']
        print(id_token)
        url = "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=" + id_token
        response = requests.get(url)
        info = json.loads(response.text)
        if 'error_description' in info:
            return Response({"status": False, "data": {"message": info}}, status=status.HTTP_404_NOT_FOUND)
        email = info['email']
        try:
            user = User.objects.get(email=email)
            token = RefreshToken.for_user(user)
            data = {
                'userId': user.id,
                'email': user.email,
                'isVerified': user.is_verified,
                'accessToken': str(token.access_token),
                'refreshToken': str(token),
            }
            if not user.google_id:
                user.google_id = info['sub']
                user.is_verified = True
                user.save()
            return Response({"status": True, "data": data}, status=status.HTTP_200_OK)

        except (Exception, User.DoesNotExist) as e:
            data = {
                'first_name': info['given_name'],
                'last_name': info['family_name'],
                'email': email,
                'username': email
            }
            try:
                user = User.objects.create(**data)
                user.is_verified = True
                user.google_id = info['sub']
                token = RefreshToken.for_user(user)
                res = {
                    "userId": user.id,
                    "email": user.email,
                    "isVerified": user.is_verified,
                    "accessToken": str(token.access_token),
                    "refreshToken": str(token)
                }
                return Response({"status": True, "data": res}, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response({"status": False, "data": {"message": 'Could not login with google.Please Try again'}},
                                status=status.HTTP_409_CONFLICT)

# Facebook Login ApiView
class FacebookLogin(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = user_serializers.FacebookLoginSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        access_token = request.data.get('accessToken', False)
        print(str(access_token))
        url = "https://graph.facebook.com/v3.3/me?fields=id,first_name,last_name,email&access_token=" + str(access_token)
        response = requests.get(url)
        print(url)
        info = json.loads(response.text)
        print(info)
        if 'error' in info:
            return Response({"status": False, "data": {"message": info}}, status=status.HTTP_404_NOT_FOUND)
        email = info['email']
        try:
            user = User.objects.get(email=email)
            token = RefreshToken.for_user(user)
            data = {
                'userId': user.id,
                'email': user.email,
                'isVerified': user.is_verified,
                'accessToken': str(token.access_token),
                'refreshToken': str(token),
            }
            if not user.facebook_id:
                user.facebook_id = info['id']
                user.is_verified = True
                user.save()
            return Response({"status": True, "data": data}, status=status.HTTP_200_OK)
        except (Exception, User.DoesNotExist) as e:
            data = {
                'first_name': info['first_name'],
                'last_name': info['last_name'],
                'email': email,
                'username': email
            }
            try:
                user = User.objects.create(**data)
                user.is_verified = True
                user.facebook_id = info['id']
                token = RefreshToken.for_user(user)
                res = {
                    "userId": user.id,
                    "email": user.email,
                    "isVerified": user.is_verified,
                    "accessToken": str(token.access_token),
                    "refreshToken": str(token)
                }
                return Response({"status": True, "data": res}, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response({"status": False, "data": {"message": 'Could not login with facebook.Please Try again'}}, status=status.HTTP_409_CONFLICT)

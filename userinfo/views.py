from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserInfo
from user.models import User
import jwt
from django.conf import settings
# Create your views here.
@api_view(['POST'])
def create_user_info(request):
    try:
        data = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        resume = request.FILES.get('resume')
        current_role = data.get('current_role')
        current_company = data.get('current_company')
        target_role = data.get('target_role')
        years_of_experience = data.get('years_of_experience')
        print(resume)
        print(current_role)
        print(current_company)
        print(target_role)
        print(years_of_experience)
        print(user)
        user_info = UserInfo.objects.create(user=user, resume=resume, current_role=current_role, current_company=current_company, target_role=target_role, years_of_experience=years_of_experience)
        return Response(status=status.HTTP_201_CREATED, data={"message": "User info created successfully"})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "User info creation failed", "error": str(e)})

@api_view(['PATCH'])
def update_user_info(request):
    try:
        data = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        resume = request.FILES.get('resume')
        current_role = data.get('current_role')
        current_company = data.get('current_company')
        target_role = data.get('target_role')
        years_of_experience = data.get('years_of_experience')
        user_info = UserInfo.objects.get(user=user)
        user_info.resume = resume
        user_info.current_role = current_role
        user_info.current_company = current_company
        user_info.target_role = target_role
        user_info.years_of_experience = years_of_experience
        user_info.save()
        return Response(status=status.HTTP_200_OK, data={"message": "User info updated successfully"})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "User info update failed", "error": str(e)})
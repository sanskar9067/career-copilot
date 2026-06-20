from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .ats_agent import score_resume
import jwt
from django.conf import settings
from userinfo.models import UserInfo
from user.models import User
@api_view(['GET'])
def score_resume_view(request):
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        user_info = UserInfo.objects.get(user=user)
        resume_path = user_info.resume.path
        score = score_resume(resume_path, user_info.current_role, user_info.target_role)
        return Response(status=status.HTTP_200_OK, data={"message": "Resume scored successfully", "score": score})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "views: Resume scoring failed", "error": str(e)})
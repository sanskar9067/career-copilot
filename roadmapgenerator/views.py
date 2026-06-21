from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .roadmap_agent import graph, State
import jwt
from django.conf import settings
from user.models import User
from userinfo.models import UserInfo
# Create your views here.
@api_view(['POST'])
def roadmap_generator_view(request):
    try:
        data = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        user_info = UserInfo.objects.get(user=user)
        user_query = data.get('user_query')
        current_role = user_info.current_role
        target_role = user_info.target_role
        duration = data.get('duration')
        hours_per_day = data.get('hours_per_day')
        job_description = data.get('job_description')
        roadmap = graph.invoke(State(user_id=user.id, current_role=current_role, target_role=target_role, job_description=job_description, duration=duration, hours_per_day=hours_per_day, user_query=user_query))
        return Response(roadmap, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
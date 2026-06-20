from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .interviewer_agent import interviewer_agent
import jwt
from django.conf import settings
from user.models import User
from userinfo.models import UserInfo
from careercopilot.utils.redis_client import get_redis_client
import json
from intervieweragent.interviewer_agent import generate_results
@api_view(['POST'])
def interviewer_agent_view(request):
    try:
        data = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        user_info = UserInfo.objects.get(user=user)
        current_role = user_info.current_role
        target_role = user_info.target_role
        resume_data = open(user_info.resume.path, 'rb').read()
        job_description = data.get('job_description')
        interview_plan = interviewer_agent(current_role, target_role, resume_data, job_description)
        redis_client = get_redis_client()
        redis_client.set(f"interview_plan_{user.id}", json.dumps(interview_plan))
        return Response(status=status.HTTP_200_OK, data={"message": "Interview plan generated successfully", "interview_plan": interview_plan})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Interview plan generation failed", "error": str(e)})

@api_view(['GET'])
def get_interview_plan_view(request):
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        redis_client = get_redis_client()
        interview_plan = redis_client.get(f"interview_plan_{user.id}")
        return Response(status=status.HTTP_200_OK, data={"message": "Interview plan retrieved successfully", "interview_plan": interview_plan})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Interview plan retrieval failed", "error": str(e)})

@api_view(['POST'])
def generate_results_view(request):
    try:
        data = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        redis_client = get_redis_client()
        questions = redis_client.get(f"questions_{user.id}")
        answers = data.get('answers')
        interview_plan = json.loads(redis_client.get(f"interview_plan_{user.id}"))
        job_description = data.get('job_description')
        results = generate_results(interview_plan, job_description, questions, answers)
        return Response(status=status.HTTP_200_OK, data={"message": "Results generated successfully", "results": results})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Results generation failed", "error": str(e)})
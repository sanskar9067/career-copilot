
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .rag_indexing import index_resume
from .rag_retrieval import retrieve_resume
import jwt
from django.conf import settings
from userinfo.models import UserInfo
from user.models import User

@api_view(['POST'])
def index_resume_view(request):
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        resume = UserInfo.objects.get(user=user).resume.path
        print(resume)
        index_resume(resume, user.id)
        return Response(status=status.HTTP_200_OK, data={"message": "Resume indexed successfully"})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Resume indexing failed", "error": str(e)})

@api_view(['POST'])
def retrieve_resume_view(request):
    try:
        data = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        query = data.get('query')
        res = retrieve_resume(query, user.id)
        return Response(status=status.HTTP_200_OK, data={"message": "Resume retrieved successfully", "response": res})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Resume retrieval failed", "error": str(e)})
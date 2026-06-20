from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
import jwt
from django.conf import settings
@api_view(['POST'])
def signup(request):
    try:
        data = request.data
        print(data)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        if User.objects.filter(email=email).exists():
            return Response({"message": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create(first_name=first_name, last_name=last_name, email=email, password=password)
        return Response(status=status.HTTP_201_CREATED, data={"message": "User created successfully"})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "User creation failed", "error": str(e)})

@api_view(['POST'])
def login(request):
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')
        user = User.objects.get(email=email)
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "User not found"})
        if user.password != password:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Invalid password"})
        token = jwt.encode({'user_id': user.id}, settings.SECRET_KEY, algorithm='HS256')
        print(token)
        return Response(status=status.HTTP_200_OK, data={"message": "Login successful", "token": str(token)})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Login failed", "error": str(e)})
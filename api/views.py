from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, ProfileSerializer, PendingRequestSerializer, SuccessRequestSerializer, RequestSerializer, RequestCountSerializer, ProfilePictureSerializer, PendingRequestSerializer
from .models import Profile, Request
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterUserView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]



class ProfileDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, user_id):
        profile = get_object_or_404(Profile, user__id=user_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class RequestUploadView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ProfileDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.select_related("user")

    def get_object(self):
        user_id = self.kwargs.get("user_id")
        return self.get_queryset().get(user__id=user_id)


class RequestCountView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        count = Request.objects.filter(user=user).count()
        serializer = RequestCountSerializer({
            "user_id": user.id,
            "request_count": count
        })
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UpdateProfilePictureView(APIView):
    permission_classes = [AllowAny]
    def put(self, request, user_id):
        profile = get_object_or_404(Profile, user__id=user_id)
        serializer = ProfilePictureSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile picture updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PendingRequestsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, user_id):
        requests = Request.objects.filter(user_id=user_id, status="Pending")
        serializer = PendingRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
class SuccessRequestsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, user_id):
        requests = Request.objects.filter(user_id=user_id, status="Success")
        serializer = SuccessRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
class PendingRequestListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PendingRequestSerializer

    def get_queryset(self):
        return Request.objects.filter(status='Pending')
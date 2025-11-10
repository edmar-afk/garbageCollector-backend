from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import PickUpRequestSerializer, GarbageCountSerializer, RegisterSerializer, ProfileSerializer, PendingRequestSerializer, SuccessRequestSerializer, RequestSerializer, RequestCountSerializer, ProfilePictureSerializer, PendingRequestSerializer
from .models import Profile, Request
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from django.db.models import Count
from rest_framework import views, status
import requests
import random
import time
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class SendNotificationAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, request_id):
        print("========================================")
        print(f"📩 Received POST request to /api/send-sms/{request_id}/")
        print(f"➡️ Request data: {request.data}")

        pickup_request = get_object_or_404(Request, id=request_id)
        user = pickup_request.user
        phone_number = user.username.strip()
        print(f"✅ Found Request object: {pickup_request.id}")
        print(f"👤 Associated user: {user.username}")

        random_suffix = random.randint(1000, 9999)
        combined_id = f"{pickup_request.id}-{random_suffix}"
        current_datetime = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %I:%M %p")

        api_key = 'LIZSLQ8lBg3GeGUtgEI9OHAgZHk8KBweehDNgHCT1e46d190'
        name = user.first_name or "Resident"
        message = (
            f"Hello, {name}! Your garbage pickup request (ID: {combined_id}) "
            f"at {pickup_request.location} is now Picked Up by the Garbage Collector. "
            f"\n📅 Picked up on: {current_datetime}"
        )

        data = {
            'sims': [390],
            'random_sender': False,
            'contact_lists': [],
            'mobile_numbers': [f'+63{phone_number[1:]}' if phone_number.startswith('0') else phone_number],
            'type': 'SMS',
            'message': message
        }

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }

        print("➡️ Sending SMS Request")
        print("➡️ URL: https://smsgateway.rbsoft.org/api/v1/messages/send")
        print(f"➡️ Payload: {data}")

        success_count = 0
        fail_count = 0
        fail_reasons = []

        try:
            response = requests.post(
                'https://smsgateway.rbsoft.org/api/v1/messages/send',
                json=data,
                headers=headers,
                timeout=10
            )

            print(f"✅ Response Status Code: {response.status_code}")
            print(f"✅ Raw Response Text: {response.text}")

            response_data = response.json()
            print(f"✅ Parsed JSON Response: {response_data}")

            if response.status_code in [200, 201]:
                success_count += 1
                print("🎉 SMS request sent successfully and queued for delivery!")

                # ✅ Update request status to 'Picked up'
                pickup_request.status = 'Picked up'
                pickup_request.save()
                print(f"📦 Request ID {pickup_request.id} status updated to 'Picked up'")

            else:
                fail_count += 1
                fail_reasons.append(response_data)
                print("❌ SMS failed to send.")
        except Exception as e:
            fail_count += 1
            fail_reasons.append({'error': str(e)})
            print(f"💥 Exception occurred: {e}")

        time.sleep(2)
        print("⏱️ Waiting 2 seconds before responding...")
        print("========================================")

        return Response(
            {
                'request_id': combined_id,
                'sent_to': phone_number,
                'message': message,
                'success_count': success_count,
                'fail_count': fail_count,
                'fail_reasons': fail_reasons,
            },
            status=status.HTTP_200_OK if success_count > 0 else status.HTTP_400_BAD_REQUEST
        )
            
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
    
    
class GarbageCountView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        requests = Request.objects.filter(status='Picked up')
        counts = {}

        for req in requests:
            if req.garbage_type:
                types = [t.strip().lower() for t in req.garbage_type.split(',')]
                for t in types:
                    counts[t] = counts.get(t, 0) + 1

        data = [{'garbage_type': k, 'count': v} for k, v in counts.items()]
        serializer = GarbageCountSerializer(data, many=True)
        return Response(serializer.data)
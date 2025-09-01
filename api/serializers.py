# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Request


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_picture = serializers.ImageField(use_url=True)

    class Meta:
        model = Profile
        fields = ['username', 'address', 'profile_picture']

    
    
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    address = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'address', 'profile_picture']

    def create(self, validated_data):
        address = validated_data.pop('address', '')
        profile_picture = validated_data.pop('profile_picture', None)
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name
        )

        Profile.objects.create(
            user=user,
            address=address,
            profile_picture=profile_picture
        )
        return user



class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'user', 'garbage_type', 'location', 'date_requested']
        read_only_fields = ['id', 'date_requested', 'user']
        


class RequestCountSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    request_count = serializers.IntegerField()
    
class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture']
        
        
class PendingRequestSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    class Meta:
        model = Request
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'id',
            'garbage_type',
            'location',
            'status',
            'date_requested'
        ]


        
class SuccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'garbage_type', 'location', 'status', 'date_requested']
        
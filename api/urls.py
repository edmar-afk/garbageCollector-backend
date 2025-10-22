from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
# ssd
urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('profile/<int:user_id>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('upload-request/<int:user_id>/', views.RequestUploadView.as_view(), name='upload-request'),
   
    path("profile/<int:user_id>/", views.ProfileDetailView.as_view(), name="profile-detail"),
    path("request-count/<int:user_id>/", views.RequestCountView.as_view(), name="request-count"),
    
    path('update-profile-picture/<int:user_id>/', views.UpdateProfilePictureView.as_view(), name='update-profile-picture'),
    
    path('pending-requests/<int:user_id>/', views.PendingRequestsView.as_view(), name='pending-requests'),
    path('success-requests/<int:user_id>/', views.SuccessRequestsView.as_view(), name='success-requests'),
    
    path('pending-requests/', views.PendingRequestListView.as_view(), name='pending-requests'),
    path('garbage-counts/', views.GarbageCountView.as_view(), name='garbage-count'),

    
    path('send-sms/<int:request_id>/', views.SendNotificationAPIView.as_view(), name='send_sms'),
]

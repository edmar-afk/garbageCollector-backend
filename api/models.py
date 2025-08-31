from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"



class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    garbage_type = models.TextField(blank=True, null=True)
    location = models.TextField()
    status = models.TextField(default='Pending')
    date_requested = models.DateTimeField(auto_now_add=True)
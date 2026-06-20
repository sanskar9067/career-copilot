from django.db import models
from user.models import User

# Create your models here.
class UserInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resume/', null=True, blank=True)
    current_role = models.CharField(max_length=255, null=True, blank=True)
    current_company = models.CharField(max_length=255, null=True, blank=True)
    target_role = models.CharField(max_length=255, null=True, blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
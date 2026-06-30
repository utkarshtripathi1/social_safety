from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='reports/', blank=True, null=True)
    status = models.CharField(max_length=50, default="Pending Review")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

   
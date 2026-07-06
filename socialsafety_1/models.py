from django.db import models
from django.contrib.auth.models import User


# ===================== REPORT =====================
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
        return self.name or "Report"


# ===================== CONTACT =====================
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    priority = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or "Contact"


# ===================== PROFILE =====================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=15, blank=True, default="")
    image = models.ImageField(upload_to="profiles/", default="default.png")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.user.username if self.user else "Profile"


# ===================== SOS =====================
class SOS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username if self.user else "Anonymous SOS"
from django.contrib import admin
from .models import Report, Contact, Profile, SOS


# ===================== REPORT =====================
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "category", "status", "created_at")
    search_fields = ("name", "location", "category")
    list_filter = ("status", "category")


# ===================== CONTACT =====================
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "phone", "priority", "created_at")
    search_fields = ("name", "phone")


# ===================== PROFILE =====================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "email", "phone")


# ===================== SOS =====================
@admin.register(SOS)
class SOSAdmin(admin.ModelAdmin):
    list_display = ("user", "latitude", "longitude", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username",)
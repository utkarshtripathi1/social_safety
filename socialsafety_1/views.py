from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from twilio.rest import Client

from .forms import SignupForm
from .models import Report, Contact, Profile, SOS

import json
from django.views.decorators.csrf import csrf_exempt

from django.core.mail import send_mail
from math import radians, sin, cos, sqrt, atan2


# ===================== HOME =====================
@login_required
def Home(request):
    return render(request, "Home.html")


# ===================== LOGIN =====================
def login_view(request):
    if request.user.is_authenticated:
        return redirect("Home")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("Home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html", {"form": form})


# ===================== DASHBOARD =====================
@login_required
def dashboard(request):
    return render(request, "dashboard.html")


# ===================== LOGOUT =====================
def logout_view(request):
    logout(request)
    return redirect("login")


# ===================== PROFILE =====================
@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        profile.name = request.POST.get("name")
        profile.email = request.POST.get("email")
        profile.phone = request.POST.get("phone")

        # location from browser
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        if latitude and longitude:
            try:
                profile.latitude = float(latitude)
                profile.longitude = float(longitude)
            except:
                pass

        if "image" in request.FILES:
            profile.image = request.FILES["image"]

        profile.save()
        return redirect("profile")

    return render(request, "profile.html", {"profile": profile})


# ===================== SIGNUP =====================
def signup(request):
    form = SignupForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            messages.success(request, "Account created successfully!")
            return redirect("login")

    return render(request, "signup.html", {"form": form})


# ===================== LOCATION PAGE =====================
@login_required
def location(request):
    return render(request, "location.html")


# ===================== REPORT INCIDENT =====================
@login_required
def report(request):
    if request.method == "POST":
        Report.objects.create(
            user=request.user,
            name=request.POST.get("fullname"),
            location=request.POST.get("location"),
            category=request.POST.get("category"),
            description=request.POST.get("description"),
            image=request.FILES.get("image")
        )
        return redirect("report")

    reports = Report.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "report.html", {"reports": reports})


# ===================== CONTACTS =====================
@login_required
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        priority = request.POST.get("priority")

        if name and phone:
            Contact.objects.create(
                user=request.user,
                name=name,
                phone=phone,
                email=email,
                priority=priority,
            )

        return redirect("contacts")

    contacts = Contact.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "contacts.html", {"contacts": contacts})


# ===================== DELETE CONTACT =====================
@login_required
def delete_contact(request, contact_id):
    if request.method == "POST":
        Contact.objects.filter(id=contact_id, user=request.user).delete()

    return redirect("contacts")


# ===================== DISTANCE FUNCTION =====================
def distance(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# ===================== SOS API =====================
# ===================== SOS API =====================
@csrf_exempt
@login_required
def receive_sos(request):

    if request.method != "POST":
        return JsonResponse({"message": "Only POST allowed"}, status=405)

    # Read JSON
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"message": "Invalid JSON"}, status=400)

    # Get location
    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
    except (TypeError, ValueError):
        return JsonResponse({"message": "Invalid coordinates"}, status=400)

    map_link = f"https://www.google.com/maps?q={lat},{lon}"

    # Save SOS
    SOS.objects.create(
        user=request.user,
        latitude=lat,
        longitude=lon
    )

    # Twilio Client
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    # ===========================================
    # SEND SMS TO TRUSTED CONTACTS
    # ===========================================

    trusted_numbers = list(
        Contact.objects.filter(user=request.user)
        .exclude(phone__isnull=True)
        .exclude(phone="")
        .values_list("phone", flat=True)
    )

    trusted_sms_sent = 0

    print("Trusted numbers:", trusted_numbers)

    for phone in trusted_numbers:

        # Add +91 automatically
        if phone and not phone.startswith("+"):
            phone = "+91" + phone

        try:
            client.messages.create(
                body=f"""
🚨 SOS ALERT 🚨

Someone needs immediate help!

Current Location:
{map_link}

Please contact them immediately.
                """,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )

            trusted_sms_sent += 1
            print(f"SMS sent to {phone}")

        except Exception as e:
            print(f"Trusted SMS Error ({phone}): {e}")

    # ===========================================
    # SEND SMS TO NEARBY USERS
    # ===========================================

    profiles = Profile.objects.exclude(user=request.user)

    nearby_count = 0
    nearby_sms_sent = 0

    for p in profiles:

        if p.latitude is None or p.longitude is None:
            continue

        d = distance(lat, lon, p.latitude, p.longitude)

        print(f"Checking {p.user.username}")
        print(f"Distance: {d:.2f} KM")

        if d <= 5:

            nearby_count += 1

            phone = p.phone

            if not phone:
                continue

            # Add +91 automatically
            if not phone.startswith("+"):
                phone = "+91" + phone

            try:

                client.messages.create(
                    body=f"""
🚨 NEARBY SOS ALERT 🚨

A person within {d:.2f} KM needs immediate help.

Location:
{map_link}

Please help if possible.
                    """,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=phone
                )

                nearby_sms_sent += 1
                print(f"Nearby SMS sent to {phone}")

            except Exception as e:
                print(f"Nearby SMS Error ({phone}): {e}")

    return JsonResponse({
        "message": "SOS triggered successfully",
        "trusted_contacts": len(trusted_numbers),
        "trusted_sms_sent": trusted_sms_sent,
        "nearby_users_found": nearby_count,
        "nearby_sms_sent": nearby_sms_sent,
    })
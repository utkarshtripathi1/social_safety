from django.shortcuts import render ,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignupForm
from .models import Report
# Create your views here.
@login_required
def Home(request):
    return render(request , "Home.html")

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


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def profile(request):
    return render(request , "profile.html")
@login_required
def contact(request):
    return render(request , "contacts.html")





def signup(request):
   

    form = SignupForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            messages.success(request, "Account created successfully!")
            return redirect('login')

    return render(request, "signup.html", {"form": form})
@login_required


def report(request):

    if request.method == "POST":

        Report.objects.create(
            user=request.user,
            name=request.POST["fullname"],
            location=request.POST["location"],
            category=request.POST["category"],
            description=request.POST["description"],
            image=request.FILES.get("image")
        )

        return redirect("report")

    reports = Report.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "report.html", {
        "reports": reports
    })
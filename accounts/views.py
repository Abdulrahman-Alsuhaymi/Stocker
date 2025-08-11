from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.contrib import messages
from .models import Profile
from .forms import UserRegistrationForm, ProfileForm

# Create your views here.

def login_view(request: HttpRequest):

    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            messages.success(request, "logged in successfully", "alert-success")
            return redirect(request.GET.get("next", "/"))
        else:
            messages.error(request, "username or password is wrong", "alert-danger")

    return render(request, "accounts/login.html", {})


def register_view(request: HttpRequest):

    if request.method == "POST":

        try:
            with transaction.atomic():
                new_user = User.objects.create_user(username=request.POST["username"],password=request.POST["password"],email=request.POST["email"], first_name=request.POST["first_name"], last_name=request.POST["last_name"])
                new_user.save()

                
                profile = Profile(user=new_user, phone=request.POST.get("phone", ""), department=request.POST.get("department", ""), position=request.POST.get("position", ""), avatar=request.FILES.get("avatar", Profile.avatar.field.get_default()))
                profile.save()

            messages.success(request, "Registered User Successfully", "alert-success")
            return redirect("accounts:login")
        
        except IntegrityError as e:
            messages.error(request, "Please choose another username", "alert-danger")
        except Exception as e:
            messages.error(request, "Couldn't register user. Try again", "alert-danger")
            print(e)
    

    return render(request, "accounts/register.html", {})


def profile_view(request:HttpRequest):

    if not request.user.is_authenticated:
        messages.warning(request, "Only registered users can view their profile", "alert-warning")
        return redirect("accounts:login")

    return render(request, 'accounts/profile.html', {"user" : request.user})


def profile_update_view(request:HttpRequest):

    if not request.user.is_authenticated:
        messages.warning(request, "Only registered users can update their profile", "alert-warning")
        return redirect("accounts:login")
    

    if request.method == "POST":

        try:
            with transaction.atomic():
                user:User = request.user

                user.first_name = request.POST["first_name"]
                user.last_name = request.POST["last_name"]
                user.email = request.POST["email"]
                user.save()

                profile:Profile = user.profile
                profile.phone = request.POST.get("phone", "")
                profile.department = request.POST.get("department", "")
                profile.position = request.POST.get("position", "")
                profile.is_manager = "is_manager" in request.POST
                profile.notification_email = request.POST.get("notification_email", "")
                if "avatar" in request.FILES: 
                    profile.avatar = request.FILES["avatar"]
                profile.save()

            messages.success(request, "updated profile successfully", "alert-success")
        except Exception as e:
            messages.error(request, "Couldn't update profile", "alert-danger")
            print(e)

    return render(request, "accounts/update_profile.html")


def log_out(request: HttpRequest):

    logout(request)
    messages.success(request, "logged out successfully", "alert-warning")

    return redirect(request.GET.get("next", "/"))
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProfileForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                return redirect("login")
            except Exception as e:
                return render(request, "mainapp/register.html", {
                    "form": form,
                    "errors": f"Registration failed: {str(e)}. Please try again."
                })
        else:
            return render(request, "mainapp/register.html", {
                "form": form,
                "errors": "Please correct the errors below."
            })
    else:
        form = RegisterForm()
    return render(request, "mainapp/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return render(request, "mainapp/login.html", {"error": "Please provide both username and password."})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("dashboard")
            else:
                return render(request, "mainapp/login.html",
                              {"error": "Your account is disabled. Please contact support."})
        else:
            return render(request, "mainapp/login.html", {"error": "Invalid username or password."})
    return render(request, "mainapp/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def home_view(request):
    """Home view that displays the landing page"""
    return render(request, "mainapp/home.html")


@login_required
def dashboard_view(request):
    return render(request, "mainapp/dashboard.html")


@login_required
def complete_profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
        else:
            return render(request, "mainapp/complete_profile.html", {
                "form": form,
                "errors": "Please correct the errors below."
            })
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, "mainapp/complete_profile.html", {"form": form})

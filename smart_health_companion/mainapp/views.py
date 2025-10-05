from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .forms import RegisterForm, ProfileForm
from .models import Tip, Doctor
from .ai_service import AIPlan


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # success message to session for display on login page
                request.session[
                    'registration_success'] = f"Your account has been successfully created for {user.username}. Please log in to continue."
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

    # Check for registration success message
    success_message = None
    if 'registration_success' in request.session:
        success_message = request.session.pop('registration_success')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return render(request, "mainapp/login.html", {
                "error": "Please provide both username and password.",
                "success_message": success_message
            })

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("dashboard")
            else:
                return render(request, "mainapp/login.html", {
                    "error": "Your account is disabled. Please contact support.",
                    "success_message": success_message
                })
        else:
            return render(request, "mainapp/login.html", {
                "error": "Invalid username or password.",
                "success_message": success_message
            })

    return render(request, "mainapp/login.html", {"success_message": success_message})


def logout_view(request):
    logout(request)
    return redirect("login")


def home_view(request):
    """Home view that displays the landing page"""
    return render(request, "mainapp/home.html")


@login_required
def dashboard_view(request):
    calories = None
    calorie_message = ""
    sleep_recommendation = ""
    sleep_message = ""

    profile = getattr(request.user, "profile", None)
    if profile and profile.age and profile.height and profile.current_weight and profile.gender:

        height_cm = profile.height
        weight_kg = profile.current_weight
        age_years = profile.age

        # Map gender char to string for BMR
        gender_code = profile.gender
        is_male = gender_code == 'M'

        # BMR
        if is_male:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161

        # Assume moderate activity if not specified in profile
        activity_factor = 1.55
        tdee = bmr * activity_factor

        goal = profile.goal or ''
        if goal == 'lose_weight':
            calories = tdee - 500
            calorie_message = "Recommended ~500 kcal deficit for weight loss."
        elif goal == 'maintain_weight':
            calories = tdee
            calorie_message = "Maintain around your TDEE to keep current weight."
        elif goal == 'build_muscle':
            calories = tdee + 300
            calorie_message = "Slight surplus (~+300 kcal) with higher protein for muscle gain."
        elif goal == 'both':
            calories = tdee
            calorie_message = "Recomposition: around TDEE with high protein and resistance training."
        else:
            calories = tdee
            calorie_message = "Balanced intake to support overall fitness."

        calories = round(calories) if calories is not None else None

        # Sleep based on age
        if 16 <= age_years <= 18:
            base_sleep = "8–10 hours/night"
        elif 19 <= age_years <= 64:
            base_sleep = "7–9 hours/night"
        elif 65 <= age_years <= 80:
            base_sleep = "7–8 hours/night"
        else:
            base_sleep = "7–9 hours/night"

        goal_note = ""
        if goal == 'build_muscle':
            goal_note = "Aim toward upper end (8–9h) to support muscle recovery."
        elif goal == 'lose_weight':
            goal_note = "Consistent 7–9h improves appetite control and fat loss."
        elif goal == 'both':
            goal_note = "Prioritize 8h for recomposition and training performance."
        elif goal == 'maintain_weight':
            goal_note = "Keep a steady schedule in the mid-range."
        elif goal == 'improve_fitness':
            goal_note = "7–9h supports training adaptation and recovery."

        sleep_recommendation = base_sleep
        sleep_message = goal_note

    return render(request, "mainapp/dashboard.html", {
        "calories": calories,
        "calorie_message": calorie_message,
        "sleep_recommendation": sleep_recommendation,
        "sleep_message": sleep_message,
        "weight_loss_plan": profile.weight_loss_plan if profile else None,
    })


@login_required
def complete_profile_view(request):
    # Ensure profile exists
    profile, created = request.user.profile, False
    if not hasattr(request.user, 'profile'):
        from .models import Profile
        profile = Profile.objects.create(user=request.user)
        created = True

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()

            # Generate and save weight loss plan
            try:
                profile_data = {
                    'age': profile.age,
                    'height': profile.height,
                    'current_weight': profile.current_weight,
                    'target_weight': profile.target_weight,
                    'gender': profile.gender,
                    'goal': profile.goal,
                    'exercise_place': profile.exercise_place,
                    'activity_level': profile.activity_level,
                    'food_allergies': profile.food_allergies or 'None',
                    'health_problems': profile.health_problems or [],
                    'other_health_problems': profile.other_health_problems or 'None',
                    'bmi': profile.bmi
                }

                ai_service = AIPlan()
                weight_loss_plan = ai_service.generate_plan(profile_data)

                profile.weight_loss_plan = weight_loss_plan
                profile.save()

            except Exception as e:
                # Handle exceptions during plan generation
                print(f"Error generating weight loss plan: {e}")

            return redirect("dashboard")
        else:
            return render(request, "mainapp/complete_profile.html", {
                "form": form,
                "errors": "Please correct the errors below."
            })
    else:
        form = ProfileForm(instance=profile)
    return render(request, "mainapp/complete_profile.html", {"form": form})


def tips_list_view(request):
    tips = Tip.objects.filter(is_published=True)
    return render(request, "mainapp/tips_list.html", {"tips": tips})


def doctor_view(request):
    doctors = Doctor.objects.filter(is_published=True)
    return render(request, "mainapp/doctor.html", {"doctors": doctors})


@login_required
def download_plan_view(request):
    try:
        profile = request.user.profile
    except:
        return redirect("dashboard")

    plan_content = profile.weight_loss_plan

    if not plan_content:
        return redirect("dashboard")

    response = HttpResponse(plan_content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="weight_loss_plan.html"'
    return response



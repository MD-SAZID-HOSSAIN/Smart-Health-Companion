from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .forms import RegisterForm, ProfileForm, DailyLogForm
from .models import Tip, Doctor, DailyLog
from django.core.paginator import Paginator
import calendar
from datetime import date as dt_date
from .ai_service import AIPlan
from django.contrib.auth.models import User
from django.contrib import messages
from .models import PasswordResetOTP
from .utils import send_otp_email

def calculate_calorie_target(profile):
    """Calculate recommended daily calories based on profile data"""
    if not (profile and profile.age and profile.height and profile.current_weight and profile.gender):
        return None, None
    
    # BMR calculation
    height_cm = profile.height
    weight_kg = profile.current_weight
    age_years = profile.age
    is_male = profile.gender == 'M'
    
    if is_male:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161
    
    # Activity level multipliers
    activity_factors = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extra_active': 1.9
    }
    activity_level = profile.activity_level or 'moderately_active'
    activity_factor = activity_factors.get(activity_level, 1.55)
    tdee = bmr * activity_factor
    
    # Goal-based calorie adjustment
    goal = profile.goal or ''
    if goal == 'lose_weight':
        calories = tdee - 500
    elif goal == 'maintain_weight':
        calories = tdee
    elif goal == 'build_muscle':
        calories = tdee + 300
    elif goal == 'both':
        calories = tdee
    else:
        calories = tdee
    
    return round(calories), tdee


def calculate_sleep_target(profile):
    """Calculate recommended sleep hours based on age"""
    if not (profile and profile.age):
        return None
    
    age_years = profile.age
    if 16 <= age_years <= 18:
        return 8
    elif 19 <= age_years <= 64:
        return 7
    elif 65 <= age_years <= 80:
        return 7.5
    else:
        return 8


def estimate_goal_time(profile, calorie_target):
    """
    Estimate time (in weeks and months) to reach the target weight
    based on calorie difference and goal type.
    """
    if not (profile and profile.current_weight and profile.target_weight and calorie_target):
        return None, None

    # Calculate total weight difference
    weight_diff = profile.target_weight - profile.current_weight

    # If already at target
    if abs(weight_diff) < 0.1:
        return "Already at target weight", None

    # Determine direction and calorie change per day
    goal = profile.goal
    if goal == 'lose_weight' and weight_diff < 0:
        daily_diff = 500  # kcal deficit
    elif goal == 'build_muscle' and weight_diff > 0:
        daily_diff = 300  # kcal surplus
    elif goal == 'both':
        daily_diff = 400  # mixed recomposition rate
    else:
        daily_diff = 300  # default mild rate

    # Calculate estimated days
    total_kcal_needed = abs(weight_diff) * 7700
    estimated_days = total_kcal_needed / daily_diff
    estimated_weeks = estimated_days / 7
    estimated_months = estimated_days / 30.44

    return round(estimated_weeks, 1), round(estimated_months, 1)


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
        next_url = request.POST.get("next") or request.GET.get("next")

        if not username or not password:
            return render(request, "mainapp/login.html", {
                "error": "Please provide both username and password.",
                "success_message": success_message
            })

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if next_url:
                    return redirect(next_url)
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
    return redirect("home")


def home_view(request):
    """Home view that displays the landing page"""
    return render(request, "mainapp/home.html")


def about_view(request):
    """About page with creators info"""
    return render(request, "mainapp/about.html")


@login_required
def dashboard_view(request):
    calories = None
    calorie_message = ""
    sleep_recommendation = ""
    sleep_message = ""

    # Handle DailyLog submission
    if request.method == 'POST':
        log_form = DailyLogForm(request.POST)
        if log_form.is_valid():
            date = log_form.cleaned_data['date']
            calories_val = log_form.cleaned_data['calories']
            sleep_hours = log_form.cleaned_data['sleep_hours']
            exercise_minutes = log_form.cleaned_data['exercise_minutes']

            # Create or update the log for this user and date
            DailyLog.objects.update_or_create(
                user=request.user,
                date=date,
                defaults={
                    'calories': calories_val,
                    'sleep_hours': sleep_hours,
                    'exercise_minutes': exercise_minutes,
                }
            )
            # Set start tracking date on first submission
            try:
                profile = request.user.profile
                if not profile.start_tracking_date:
                    profile.start_tracking_date = date
                    profile.save(update_fields=["start_tracking_date"])
            except Exception:
                pass

            # Check if plan needs updating based on log deviation
            try:
                profile = request.user.profile
                calories_target, _ = calculate_calorie_target(profile)
                recommended_sleep_hours = calculate_sleep_target(profile)
                
                latest_log = DailyLog.objects.filter(user=request.user).order_by('-date').first()
                
                # Check deviation thresholds
                if latest_log and calories_target and recommended_sleep_hours:
                    calorie_diff = abs(latest_log.calories - calories_target)
                    sleep_diff = abs(float(latest_log.sleep_hours) - recommended_sleep_hours)
                    
                    if calorie_diff > 100 or sleep_diff > 1.0:  # Significant deviation
                        # Regenerate plan with log data
                        profile_data = {
                            'age': profile.age, 'height': profile.height, 'current_weight': profile.current_weight,
                            'target_weight': profile.target_weight, 'gender': profile.gender, 'goal': profile.goal,
                            'exercise_place': profile.exercise_place, 'activity_level': profile.activity_level,
                            'food_allergies': profile.food_allergies or 'None', 'health_problems': profile.health_problems or [],
                            'other_health_problems': profile.other_health_problems or 'None', 'bmi': profile.bmi,
                            'daily_log': {
                                'date': str(latest_log.date), 'calories': latest_log.calories,
                                'sleep_hours': float(latest_log.sleep_hours), 'exercise_minutes': latest_log.exercise_minutes,
                                'recommended_calories': calories_target, 'recommended_sleep': recommended_sleep_hours,
                            }
                        }
                        # Attach estimated goal timeline
                        try:
                            goal_weeks, goal_months = estimate_goal_time(profile, calories_target)
                            profile_data['goal_timeline_weeks'] = goal_weeks
                            profile_data['goal_timeline_months'] = goal_months
                        except Exception:
                            pass
                        try:
                            new_plan = AIPlan().generate_plan(profile_data)
                            profile.weight_loss_plan = new_plan
                            profile.save(update_fields=["weight_loss_plan"])
                        except Exception:
                            pass  # Don't break logging if AI fails
            except Exception:
                pass  # Don't break logging flow
            return redirect('dashboard')
    else:
        log_form = DailyLogForm()

    profile = getattr(request.user, "profile", None)
    
    # Calculate calorie and sleep recommendations
    calories, _ = calculate_calorie_target(profile)
    recommended_sleep_hours = calculate_sleep_target(profile)
    goal_weeks, goal_months = estimate_goal_time(profile, calories)
    
    # Set calorie message based on goal
    calorie_message = ""
    if calories and profile:
        goal = profile.goal or ''
        if goal == 'lose_weight':
            calorie_message = "Recommended ~500 kcal deficit for weight loss."
        elif goal == 'maintain_weight':
            calorie_message = "Maintain around your TDEE to keep current weight."
        elif goal == 'build_muscle':
            calorie_message = "Slight surplus (~+300 kcal) with higher protein for muscle gain."
        elif goal == 'both':
            calorie_message = "Recomposition: around TDEE with high protein and resistance training."
        else:
            calorie_message = "Balanced intake to support overall fitness."
    
    # Set sleep recommendation and message
    sleep_recommendation = ""
    sleep_message = ""
    if recommended_sleep_hours and profile:
        age_years = profile.age
        if 16 <= age_years <= 18:
            sleep_recommendation = "8 hours/night"
        elif 19 <= age_years <= 64:
            sleep_recommendation = "7 hours/night"
        elif 65 <= age_years <= 80:
            sleep_recommendation = "7–8 hours/night"
        else:
            sleep_recommendation = "7–9 hours/night"
        
        goal = profile.goal or ''
        if goal == 'build_muscle':
            sleep_message = "Aim toward upper end (8–9h) to support muscle recovery."
        elif goal == 'lose_weight':
            sleep_message = "Consistent 7–9h improves appetite control and fat loss."
        elif goal == 'both':
            sleep_message = "Prioritize 8h for recomposition and training performance."
        elif goal == 'maintain_weight':
            sleep_message = "Keep a steady schedule in the mid-range."
        elif goal == 'improve_fitness':
            sleep_message = "7–8h supports training adaptation and recovery."

    return render(request, "mainapp/dashboard.html", {
        "calories": calories,
        "calorie_message": calorie_message,
        "sleep_recommendation": sleep_recommendation,
        "sleep_message": sleep_message,
        "weight_loss_plan": profile.weight_loss_plan if profile else None,
        "log_form": log_form,
        "goal_weeks": goal_weeks,
        "goal_months": goal_months,
    })


@login_required
def complete_profile_view(request):
    # Ensure profile exists
    if not hasattr(request.user, 'profile'):
        from .models import Profile
        profile = Profile.objects.create(user=request.user)
    else:
        profile = request.user.profile

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

                # Attach estimated goal timeline
                try:
                    calories_target, _ = calculate_calorie_target(profile)
                    goal_weeks, goal_months = estimate_goal_time(profile, calories_target)
                    profile_data['goal_timeline_weeks'] = goal_weeks
                    profile_data['goal_timeline_months'] = goal_months
                except Exception:
                    pass

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


@login_required
def logs_view(request):
    logs_qs = DailyLog.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(logs_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    #  month calendar highlighting the start tracking date
    profile = getattr(request.user, 'profile', None)
    start_date = getattr(profile, 'start_tracking_date', None) if profile else None
    base_date = start_date or dt_date.today()

    cal = calendar.Calendar(firstweekday=6)  # 6 = Sunday
    month_days = cal.monthdayscalendar(base_date.year, base_date.month)
    #  for start date
    month_weeks = []
    for week in month_days:
        week_cells = []
        for day in week:
            cell = {
                'num': day,
                'is_blank': day == 0,
                'is_start': bool(start_date and day == start_date.day and base_date.month == start_date.month and base_date.year == start_date.year)
            }
            week_cells.append(cell)
        month_weeks.append(week_cells)

    month_name = calendar.month_name[base_date.month]

    return render(request, "mainapp/logs.html", {
        "page_obj": page_obj,
        "total_count": logs_qs.count(),
        "calendar_weeks": month_weeks,
        "calendar_month_name": month_name,
        "calendar_year": base_date.year,
    })
#Forgot password OTP
def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            send_otp_email(user)
            messages.success(request, "OTP sent to your email.")
            return redirect("verify_otp", user_id=user.id)
        except User.DoesNotExist:
            messages.error(request, "No user found with that email.")
    return render(request, "mainapp/forgot_password.html")

from django.contrib.auth.hashers import make_password

def verify_otp_view(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        otp_input = request.POST.get("otp")
        new_password = request.POST.get("new_password")
        try:
            otp_record = PasswordResetOTP.objects.get(user=user, otp=otp_input, is_used=False)
            if otp_record.is_expired():
                messages.error(request, "OTP expired.")
            else:
                user.password = make_password(new_password)
                user.save()
                otp_record.is_used = True
                messages.success(request, "Password changed successfully.")
                return redirect("login")
        except PasswordResetOTP.DoesNotExist:
            messages.error(request, "Invalid OTP.")
    return render(request, "mainapp/verify_otp.html")


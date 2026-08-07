from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime

# user profile
class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    GOAL_CHOICES = [
        ('lose_weight', 'Lose Weight'),
        ('maintain_weight', 'Maintain Weight'),
        ('build_muscle', 'Gain Muscle'),
        ('both', 'Gain Muscle & Lose Fat'),
        ('improve_fitness', 'Improve Fitness'),
    ]

    EXERCISE_PLACE_CHOICES = [
        ('gym', 'Gym'),
        ('home', 'Home'),
        ('outdoor', 'Outdoor'),
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary – little or no exercise'),
        ('lightly_active', 'Lightly Active – light exercise 1–3 days/week'),
        ('moderately_active', 'Moderately Active – moderate exercise 3–5 days/week'),
        ('very_active', 'Very Active – hard exercise 6–7 days/week'),
        ('extra_active', 'Extra Active – intense training or physical job'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    current_weight = models.FloatField(null=True, blank=True, help_text='Current weight in kg')
    target_weight = models.FloatField(null=True, blank=True, help_text='Target weight in kg')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    food_allergies = models.TextField(max_length=500, blank=True, null=True)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, null=True, blank=True)
    exercise_place = models.CharField(max_length=10, choices=EXERCISE_PLACE_CHOICES, null=True, blank=True, help_text='Preferred exercise location')
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, null=True, blank=True, help_text='Your current activity level')
    health_problems = models.JSONField(default=list, blank=True, help_text='List of health problems/conditions')
    other_health_problems = models.TextField(max_length=500, blank=True, null=True,
                                             help_text='Specify other health problems not listed above')
    weight_loss_plan = models.TextField(blank=True, null=True)
    start_tracking_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def bmi(self):
        """Calculate BMI if height and current_weight are available"""
        if self.height and self.current_weight and self.height > 0:
            # Convert height from cm to meters
            height_m = self.height / 100
            return self.current_weight / (height_m ** 2)
        return None


# Signal to create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)


class Tip(models.Model):
    CATEGORY_CHOICES = [
        ("fitness", "Fitness"),
        ("exercise", "Exercise"),
        ("nutrition", "Nutrition"),
        ("recovery", "Recovery"),
        ("lifestyle", "Lifestyle"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="fitness")
    summary = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="tips/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Doctor(models.Model):
    name = models.CharField(max_length=120)
    specialty = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="doctors/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dr. {self.name} — {self.specialty}"

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField()
    calories = models.IntegerField(default=0)
    sleep_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    exercise_minutes = models.IntegerField(default=0)
    is_ai_estimated = models.BooleanField(default=False, help_text='Whether calories were estimated by AI food recognition')

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} — {self.date}: {self.calories} kcal, {self.sleep_hours}h, {self.exercise_minutes} min"

# Forgot Password OTP
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + datetime.timedelta(minutes=5)  # 5 min expiry
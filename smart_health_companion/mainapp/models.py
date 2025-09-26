from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    food_allergies = models.TextField(max_length=500, blank=True, null=True)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, null=True, blank=True)
    health_problems = models.JSONField(default=list, blank=True, help_text='List of health problems/conditions')
    other_health_problems = models.TextField(max_length=500, blank=True, null=True,
                                             help_text='Specify other health problems not listed above')

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.weight and self.height > 0:
            # Convert height from cm to meters
            height_m = self.height / 100
            return self.weight / (height_m ** 2)
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
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dr. {self.name} — {self.specialty}"
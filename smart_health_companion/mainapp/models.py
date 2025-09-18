from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Extend user profile
class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    GOAL_CHOICES = [
        ('lose_weight', 'Lose Weight'),
        ('gain_weight', 'Gain Weight'),
        ('maintain_weight', 'Maintain Weight'),
        ('build_muscle', 'Build Muscle'),
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

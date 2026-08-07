from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, DailyLog


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('', 'Select Gender'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    GOAL_CHOICES = [
        ('', 'Select Goal'),
        ('lose_weight', 'Lose Weight'),
        ('maintain_weight', 'Maintain Weight'),
        ('build_muscle', 'Gain Muscle'),
        ('both', 'Gain Muscle & Lose Fat'),
        ('improve_fitness', 'Improve Fitness'),
    ]

    EXERCISE_PLACE_CHOICES = [
        ('', 'Select Exercise Place'),
        ('gym', 'Gym'),
        ('home', 'Home'),
        ('outdoor', 'Outdoor'),
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ('', 'Select Activity Level'),
        ('sedentary', 'Sedentary – little or no exercise'),
        ('lightly_active', 'Lightly Active – light exercise 1–3 days/week'),
        ('moderately_active', 'Moderately Active – moderate exercise 3–5 days/week'),
        ('very_active', 'Very Active – hard exercise 6–7 days/week'),
        ('extra_active', 'Extra Active – intense training or physical job'),
    ]

    HEALTH_PROBLEM_CHOICES = [
        ('diabetes', 'Diabetes'),
        ('blood_pressure', 'Blood Pressure'),
        ('kidney', 'Kidney Disease'),
        ('thyroid', 'Thyroid Problems'),
        ('asthma', 'Asthma'),
        ('other', 'Other'),
    ]

    age = forms.IntegerField(
        required=True,
        min_value=16,
        max_value=80,
        help_text="Enter your age (16-80)"
    )
    height = forms.FloatField(
        required=True,
        min_value=50.0,
        max_value=300.0,
        help_text="Enter your height in cm (50-300)"
    )
    current_weight = forms.FloatField(
        required=True,
        min_value=20.0,
        max_value=500.0,
        help_text="Enter your current weight in kg (20-500)"
    )
    target_weight = forms.FloatField(
        required=False,
        min_value=20.0,
        max_value=500.0,
        help_text="Enter your target weight in kg (20-500) - Optional"
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=True,
        help_text="Select your gender"
    )
    food_allergies = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="List any food allergies or dietary restrictions (optional)"
    )
    goal = forms.ChoiceField(
        choices=GOAL_CHOICES,
        required=True,
        help_text="What is your primary health goal?"
    )
    exercise_place = forms.ChoiceField(
        choices=EXERCISE_PLACE_CHOICES,
        required=False,
        help_text="Where do you prefer to exercise? (Optional)"
    )
    activity_level = forms.ChoiceField(
        choices=ACTIVITY_LEVEL_CHOICES,
        required=False,
        help_text="What is your current activity level? (Optional)"
    )

    health_problems = forms.MultipleChoiceField(
        choices=HEALTH_PROBLEM_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text="Select any health problems you have (optional)"
    )

    other_health_problems = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text="If 'Other', please specify (optional)"
    )

    class Meta:
        model = Profile
        fields = ['age', 'height', 'current_weight', 'target_weight', 'gender', 'food_allergies', 'goal', 'exercise_place', 'activity_level', 'health_problems',
                  'other_health_problems']

    def clean_health_problems(self):
        values = self.cleaned_data.get('health_problems') or []
        return list(values)


class HealthForm(forms.Form):
    gender_choices = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    activity_choices = [
        ("sedentary", "Sedentary"),
        ("light", "Light"),
        ("moderate", "Moderate"),
        ("active", "Active"),
        ("very_active", "Very Active"),
    ]
    goal_choices = [
        ("Lose Weight", "Lose Weight"),
        ("Maintain Weight", "Maintain Weight"),
        ("Gain Muscle", "Gain Muscle"),
        ("Gain Muscle & Lose Fat", "Gain Muscle & Lose Fat"),
        ("Improve Fitness", "Improve Fitness"),
    ]

    gender = forms.ChoiceField(choices=gender_choices)
    age = forms.IntegerField(min_value=16, max_value=80)
    height = forms.FloatField(help_text="Height in cm")
    weight = forms.FloatField(help_text="Weight in kg")
    activity = forms.ChoiceField(choices=activity_choices)
    goal = forms.ChoiceField(choices=goal_choices)


class DailyLogForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    calories = forms.IntegerField(min_value=0)
    sleep_hours = forms.DecimalField(min_value=0, max_digits=4, decimal_places=1)
    exercise_minutes = forms.IntegerField(min_value=0)

    class Meta:
        model = DailyLog
        fields = ['date', 'calories', 'sleep_hours', 'exercise_minutes']


class FoodPhotoForm(forms.Form):
    """Form for the food photo calorie scanner."""
    image = forms.ImageField(
        required=True,
        help_text="Upload a photo of your food"
    )
    weight_grams = forms.FloatField(
        required=True,
        min_value=1,
        help_text="Enter the weight of the food in grams"
    )



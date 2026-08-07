<h1 align="center">
  <img src="https://img.shields.io/badge/Smart%20Health-Companion-00b894?style=for-the-badge&logo=heart&logoColor=white" alt="Smart Health Companion" />
</h1>

<p align="center">
  <strong>A Django-powered personal health management web application with AI-driven fitness planning and ML-based Bangladeshi food calorie recognition.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-4.2%2B-092E20?style=flat-square&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenRouter-AI-6C63FF?style=flat-square&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>


---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
  - [User Onboarding & Profile](#user-onboarding--profile)
  - [AI-Powered Health Plan](#ai-powered-health-plan)
  - [Food Calorie Recognition (ML)](#food-calorie-recognition-ml)
  - [Daily Activity Logging](#daily-activity-logging)
  - [Health Tips & Doctors](#health-tips--doctors)
  - [Password Reset via OTP](#password-reset-via-otp)
- [Data Models](#data-models)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
  - [Running the Application](#running-the-application)
- [URL Routes](#url-routes)
- [Screenshots](#screenshots)
- [Contributing](#contributing)

---

## Overview

**Smart Health Companion** is a full-stack web application built with Django that helps users actively manage their health journey. It combines traditional health tracking (calories, sleep, exercise) with cutting-edge AI — an LLM-powered personalized fitness planner and a custom-trained computer vision model capable of recognizing **16 Bangladeshi/South Asian food dishes** and estimating their calorie content from a photo.

Whether you're trying to lose weight, build muscle, or simply improve your lifestyle, Smart Health Companion gives you:
- A data-driven starting point from your health profile
- A fully personalized, AI-generated plan
- Tools to log and track your daily progress
- Visual feedback on how you're trending toward your goal

---

## Key Features

| Feature | Description |
|---|---|
| 🔐 **Authentication** | Secure registration, login, and logout with session management |
| 👤 **Health Profile** | Detailed user profile: age, height, weight, gender, fitness goals, activity level, food allergies, and health conditions |
| 📊 **BMI Calculation** | Automatic BMI computation from height and current weight |
| 🤖 **AI Health Plan** | Personalized weekly/monthly plan (meal & exercise) generated via OpenRouter LLM (GPT-class models) |
| 📅 **Goal Timeline** | Estimated weeks/months to reach target weight using safe calorie deficit/surplus math |
| 🍽️ **Food Calorie Recognition** | Upload a food photo → ML model (EfficientNet-B0) identifies the dish and estimates calories based on entered weight |
| 📝 **Daily Logging** | Log daily calorie intake, sleep hours, and exercise minutes |
| 📈 **Progress Dashboard** | Interactive charts showing calorie, sleep, and exercise trends over time |
| 💡 **Health Tips** | Curated tip articles categorized by fitness, nutrition, exercise, recovery, and lifestyle |
| 🩺 **Doctor Directory** | Browse healthcare professionals with contact details |
| 📧 **Password Reset** | OTP-based forgot password flow via Gmail SMTP |
| 📄 **Plan Download** | Export your AI-generated health plan as a file |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Django 4.2+ |
| **Database** | SQLite (default), easily swappable to PostgreSQL |
| **AI / LLM** | OpenRouter API (OpenAI-compatible) — GPT-class model |
| **Computer Vision** | PyTorch 2.0+, TorchVision, EfficientNet-B0 |
| **Image Processing** | Pillow |
| **Email** | Django SMTP via Gmail |
| **Frontend** | Django Templates, HTML5, CSS3, JavaScript |
| **Admin** | Django Admin Panel |

---

## Project Structure

```
Smart-Health-Companion-with-food-calorie-/
└── Smart-Health-Companion/
    └── smart_health_companion/          # Django project root
        ├── manage.py
        ├── requirements.txt
        ├── db.sqlite3                   # SQLite database
        ├── smart_health_companion/      # Django settings & URLs
        │   ├── settings.py
        │   ├── urls.py
        │   └── wsgi.py
        └── mainapp/                     # Core application
            ├── models.py                # DB models: Profile, DailyLog, Tip, Doctor, PasswordResetOTP
            ├── views.py                 # All view logic (~664 lines)
            ├── forms.py                 # Django forms
            ├── urls.py                  # URL routing
            ├── ai_service.py            # OpenRouter / LLM integration
            ├── food_calories.py         # Calorie lookup table (16 dishes)
            ├── apps.py                  # App config + ML model loader
            ├── utils.py                 # OTP email helper
            ├── admin.py                 # Django admin registration
            ├── ml_models/
            │   └── food_model.pt        # Trained EfficientNet-B0 checkpoint (~16 MB)
            └── templates/mainapp/
                ├── home.html
                ├── dashboard.html
                ├── complete_profile.html
                ├── logs.html
                ├── tips_list.html
                ├── doctor.html
                ├── login.html
                ├── register.html
                ├── forgot_password.html
                ├── verify_otp.html
                └── about.html
```

---

## How It Works

### User Onboarding & Profile

1. A new visitor **registers** an account (username, email, password).
2. After logging in they are directed to **Complete Profile** where they fill in:
   - Personal stats: age, height, current weight, target weight, gender
   - Fitness goal: *Lose Weight / Maintain / Build Muscle / Both / Improve Fitness*
   - Activity level: sedentary → extra active
   - Preferred exercise location: gym, home, or outdoor
   - Food allergies and known health conditions
3. A `Profile` record is automatically created for every new user via a Django signal.
4. **BMI** is computed on the fly as a model property: `weight_kg / (height_m)²`

### AI-Powered Health Plan

The `AIPlan` class in [`ai_service.py`](Smart-Health-Companion/smart_health_companion/mainapp/ai_service.py) communicates with the **OpenRouter API** (OpenAI-compatible endpoint):

1. User profile data is formatted into a detailed prompt that includes personal stats, fitness goal, activity level, allergies, and health conditions.
2. If the user has recent daily log data, that is appended so the AI can adjust the plan to correct any deviations (e.g., under-eating or insufficient exercise).
3. An **estimated goal timeline** (weeks/months) is calculated using:
   - Safe calorie deficit of **500 kcal/day** for weight loss → ~0.45 kg/week
   - Safe calorie surplus of **300 kcal/day** for muscle gain
4. The LLM returns a full **HTML-formatted plan** with:
   - Personalised meal plan (breakfast, lunch, dinner, snacks)
   - Exercise schedule (3–4 days/week)
   - Hydration and sleep guidelines
   - Weekly milestones aligned to the estimated timeline
5. The plan can be **downloaded** from the dashboard.

### Food Calorie Recognition (ML)

The app ships with a custom-trained **EfficientNet-B0** model (`food_model.pt`, ~16 MB) that classifies **16 Bangladeshi and South Asian dishes**:

| Dish | Dish | Dish | Dish |
|---|---|---|---|
| Khichuri | Biryani | Haleem | Kabab |
| Chickpeas (Cholar Dal) | Egg Omelette | Roshgolla | Nehari |
| Morog Polao | Roshmalai | Hilsha Fish | Yogurt (Doi) |
| Beguni | Kala Bhuna | Porota | Bakorkhani |

**Flow:**
1. The model is loaded **once at startup** via `MainappConfig.ready()` and stored in module-level globals to avoid repeated disk I/O.
2. The user visits `/food-calorie/`, uploads a photo, and enters the food weight in grams.
3. The image is pre-processed (resize to 224×224, ImageNet normalization) and fed through the model.
4. If **confidence ≥ 60%** → the predicted dish name and estimated calories (`cal_per_100g / 100 × weight_g`) are returned immediately.
5. If **confidence < 60%** → a manual selection fallback is offered, listing all 16 dish options with their calorie values.
6. The user can save the estimated calories directly to today's **Daily Log**.

### Daily Activity Logging

- Users log **calories consumed**, **sleep hours**, and **exercise minutes** for any date.
- Each `(user, date)` pair is unique — re-submitting updates the existing record.
- The **Dashboard** displays:
  - Today's vs. recommended calorie target (Mifflin-St Jeor BMR × activity factor, ± goal adjustment)
  - Recommended sleep hours based on age bracket
  - Progress charts showing the last N days of activity
  - Calorie, sleep, and exercise history in a calendar-style log view

### Health Tips & Doctors

- **Tips** are content articles managed via the Django Admin panel.
  - Categories: Fitness, Exercise, Nutrition, Recovery, Lifestyle
  - Paginated list view with images
- **Doctors** are likewise admin-managed entries containing name, specialty, contact info, bio, and photo.

### Password Reset via OTP

1. User visits `/forgot-password/` and enters their email.
2. A 6-digit OTP is generated and sent to the email via Gmail SMTP.
3. OTP expires in **5 minutes**.
4. User verifies the OTP at `/verify-otp/<user_id>/` and resets their password.

---

## Data Models

```
Profile          — One-to-one with Django User; stores all health & goal data
DailyLog         — Per-user per-date record of calories, sleep, and exercise
Tip              — Health tip article with category, slug, image, and publish flag
Doctor           — Healthcare professional directory entry
PasswordResetOTP — Short-lived OTP token for email-based password reset
```

---

## Getting Started

### Prerequisites

- Python **3.10+**
- pip
- Git
- A Gmail account (for OTP emails) — or any SMTP provider
- An [OpenRouter](https://openrouter.ai/) API key (free tier available)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/MD-SAZID-HOSSAIN/Smart-Health-Companion-with-food-calorie-.git
cd Smart-Health-Companion-with-food-calorie-/Smart-Health-Companion/smart_health_companion

# 2. Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Open `smart_health_companion/settings.py` and update the following sections, or set them as environment variables:

```python
# AI Plan Generation — get a free key at https://openrouter.ai/
OPENAI_API_KEY  = "your-openrouter-api-key"
OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
OPENAI_MODEL    = "openai/gpt-4o-mini"   # or any supported model

# Email (OTP password reset)
EMAIL_HOST_USER     = "your-gmail@gmail.com"
EMAIL_HOST_PASSWORD = "your-app-password"   # Gmail App Password, not your account password
```

> **Tip:** For Gmail, generate an **App Password** under *Google Account → Security → 2-Step Verification → App Passwords*.

### Running the Application

```bash
# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# (Optional) Create a superuser to access the Django Admin panel
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Open your browser and navigate to **http://127.0.0.1:8000/**

Django Admin is available at **http://127.0.0.1:8000/admin/**

---

## URL Routes

| URL | View | Description |
|---|---|---|
| `/` | `home_view` | Public landing page |
| `/about/` | `about_view` | About the project & team |
| `/register/` | `register_view` | New user registration |
| `/login/` | `login_view` | User login |
| `/logout/` | `logout_view` | Session logout |
| `/dashboard/` | `dashboard_redirect_self` | Redirects to `/dashboard/<username>/` |
| `/dashboard/<username>/` | `dashboard_view` | Personal health dashboard |
| `/complete-profile/` | `complete_profile_view` | Health profile setup |
| `/tips/` | `tips_list_view` | Browse health tips |
| `/doctors/` | `doctor_view` | Browse doctor directory |
| `/logs/` | `logs_view` | Daily activity log history |
| `/download-plan/` | `download_plan_view` | Download AI health plan |
| `/food-calorie/` | `food_calorie_view` | Upload food photo for calorie estimate (AJAX) |
| `/food-calorie/save/` | `food_calorie_save_view` | Save AI-estimated calories to log (AJAX) |
| `/forgot-password/` | `forgot_password_view` | Request password reset OTP |
| `/verify-otp/<user_id>/` | `verify_otp_view` | OTP verification & password reset |

---

## Screenshots

> *(Add screenshots here by placing images in the repo and linking them below)*

```
docs/screenshots/
├── home.png
├── dashboard.png
├── food-calorie.png
└── ai-plan.png
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a **Pull Request**

Please make sure your code follows PEP 8 style guidelines and that existing functionality is not broken.

---
### Food-classifier model link - https://github.com/MD-SAZID-HOSSAIN/Food-classifier



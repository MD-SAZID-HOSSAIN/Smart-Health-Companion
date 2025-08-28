# Smart Health Companion

A Django-based web application for health and fitness tracking with user authentication and profile management.

## Features

- User registration and login system
- Extended user profiles with health information
- Fitness goal tracking
- Secure authentication

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Register a new account or login with existing credentials

## Project Structure

```
smart_health_companion/
├── smart_health_companion/   # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── mainapp/                  # Main application
│   ├── models.py            # User Profile model
│   ├── views.py             # Authentication views
│   ├── urls.py              # App URL patterns
│   ├── forms.py             # User forms
│   └── templates/mainapp/   # HTML templates
│       ├── login.html
│       ├── register.html
│       └── dashboard.html
└── manage.py
```

## Models

- **Profile**: Extends Django's User model with health-related fields
  - Age, Height, Weight
  - Fitness goals (Stay Fit, Lose Fat, Gain Muscle, Do Both)

## Views

- **register_view**: User registration with profile creation
- **login_view**: User authentication
- **logout_view**: User logout
- **dashboard_view**: Protected dashboard (requires login)

## URLs

- `/register/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/dashboard/` - User dashboard (protected)
- `/admin/` - Django admin interface








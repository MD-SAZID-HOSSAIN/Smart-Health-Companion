from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("complete-profile/", views.complete_profile_view, name="complete_profile"),
    path("tips/", views.tips_list_view, name="tips_list"),
]


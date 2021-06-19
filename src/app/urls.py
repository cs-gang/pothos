from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("user/login", views.login, name="login"),
    path("user/signup", views.signup, name="signup"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("user/logout", views.logout, name="logout"),
]

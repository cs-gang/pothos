from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("/users/login", views.login, name="login"),
    path("/users/signup", views.signup, name="signup"),
]
